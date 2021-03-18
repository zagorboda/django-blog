from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import generics, status, permissions, pagination, filters
from rest_framework.decorators import api_view, permission_classes
# from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from blog_app.models import Post, Comment, Tag, ReportPost, ReportComment
from .permissions import IsOwnerOrReadOnly, IsOwnerOrIsAuthenticatedOrReadOnly
from .serializers import (
    UserSerializer, PostListSerializer, PostDetailSerializer, CommentSerializer, RegisterUserSerializer,
    ChangePasswordSerializer, ResetPasswordSerializer, ResetPasswordEmailSerializer, EditProfileSerializer
)

from datetime import datetime

from hitcount.views import HitCountDetailView, HitCountMixin
from hitcount.models import HitCount

from rest_framework_swagger.views import get_swagger_view

from .tokens import account_activation_token, password_reset_token


@permission_classes((AllowAny,))
def schema_view():
    return get_swagger_view(title='Blog API')


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'blog': reverse('api:blog_main_page', request=request, format=format),
        'user': reverse('api:schema', request=request, format=format),
        'schema': reverse('api:schema', request=request, format=format),
    })


class PostListPagination(pagination.PageNumberPagination):
    """ Custom pagination for posts """
    page = 1
    page_size = 15
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        response_data = {
            'links': {
               'next': self.get_next_link(),
               'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page': int(self.request.GET.get('page', 1)),  # can not set default = self.page
            'page_size': int(self.request.GET.get('page_size', self.page_size)),
        }

        if self.request.user.is_authenticated:
            response_data['user_profile_url'] = self.request.build_absolute_uri(
                reverse('api:user-detail', kwargs={'username': self.request.user})
            )
            response_data['create_new_post_url'] = self.request.build_absolute_uri(
                reverse('api:new-post')
            )
        else:
            response_data['reset_password'] = self.request.build_absolute_uri(
                reverse('api:email_reset_password')
            )
            response_data['token_obtain_pair'] = self.request.build_absolute_uri(
                reverse('api:token_obtain_pair')
            )
            response_data['sign_up_url'] = self.request.build_absolute_uri(
                reverse('api:signup')
            )

        response_data['results'] = data

        return Response(response_data)


class PostDetail(APIView):
    """ Return all information about post.

    GET : return information.
    POST : add new comment (user must be logged in, requires comment body).
    """
    permission_classes = (IsOwnerOrIsAuthenticatedOrReadOnly, )

    def get_object(self, *args, **kwargs):
        """ Return object or 404 """

        try:
            post = Post.objects.get(slug=args[0], status=1)
            self.check_object_permissions(self.request, post)
            return post
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, slug):
        """ Return detail post information """

        post = self.get_object(slug)
        serializer = PostDetailSerializer(post, context={'request': request})

        hit_count = HitCount.objects.get_for_object(post)
        hit_count_response = HitCountMixin.hit_count(request, hit_count)

        return Response(serializer.data)

    def post(self, request, slug):
        """Add new comment to post"""

        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            post = self.get_object(slug)
            serializer.save(author=self.request.user, created_on=datetime.now(), post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, slug):
        """ Edit post fields """

        post = self.get_object(slug)
        data = request.data.copy()

        serializer = PostDetailSerializer(post, data=data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostLikeAPIToggle(APIView):
    """ View to like/unlike post """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, slug):
        obj = get_object_or_404(Post, slug=slug)
        user = request.user
        updated = False
        liked = False
        if user.is_authenticated:
            if user in obj.likes.all():
                liked = False
                obj.likes.remove(user)
            else:
                liked = True
                obj.likes.add(user)
            updated = True
        data = {
            "updated": updated,
            "liked": liked
        }
        return Response(data)


class PostReportToggle(APIView):
    """ View to report post """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        post = get_object_or_404(Post, slug=slug)
        user = self.request.user

        if ReportPost.objects.filter(post=post).exists():
            report = ReportPost.objects.get(post=post)
            if not report.reports.filter(username=user.username).exists():
                report.total_reports += 1
                report.reports.add(user)
                report.save()
                data = {'updated': True}
            else:
                data = {'updated': False, 'message': 'Post already reported'}
        else:
            report = ReportPost.objects.create(post=post)
            report.total_reports += 1
            report.reports.add(user)
            report.save()
            data = {'updated': True}
        return Response(data)


class CommentReportToggle(APIView):
    """ View to report comment """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, *args, **kwargs):
        id = self.kwargs.get("id")
        comment = Comment.objects.get(id=id)
        user = self.request.user

        if ReportComment.objects.filter(comment=comment).exists():
            report = ReportComment.objects.get(comment=comment)
            if not report.reports.filter(username=user.username).exists():
                report.total_reports += 1
                report.reports.add(user)
                report.save()
                data = {'updated': True}
            else:
                data = {'updated': False, 'message': 'Comment already reported'}
        else:
            report = ReportComment.objects.create(comment=comment)
            report.total_reports += 1
            report.reports.add(user)
            report.save()
            data = {'updated': True}
        return Response(data)


class UserDetail(APIView):
    """ GET: return user information
        PATCH: edit user profile"""
    permission_classes = (IsOwnerOrReadOnly, )

    lookup_field = 'username'

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username')
        User = get_user_model()
        try:
            queryset = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404

        serializer = UserSerializer(queryset, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        request_user = request.user
        username = kwargs.get('username')

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        if request_user.id == user.id:
            serializer = EditProfileSerializer(request_user, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        return Response()


class BlogMainPage(generics.ListAPIView):
    """ Return most recent posts """
    queryset = Post.objects.all().filter(status=1)
    serializer_class = PostListSerializer

    pagination_class = PostListPagination

    filter_backends = (filters.SearchFilter,)
    search_fields = ('title', 'tags__tagline')

    # filter_backends = (DynamicSearchFilter,)


class CreateNewPost(APIView):
    """ Create new post.

    POST : user must be logged in.
    Requires : title, content(HTML markup).
    Additional fields: tags(list of items).
    """
    serializer_class = PostDetailSerializer
    # parser_class = (MultiPartParser,)
    # parser_classes = [gen_MultipartJsonParser(['title', 'content'])]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request):
        """ Create new blogpost """

        data = request.data.copy()

        serializer = PostDetailSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreateApiView(APIView):
    """ Create new user

    POST : create new user.
    Requires : username(unique), email(unique), password"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.validated_data['is_active'] = False
            user = serializer.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('registration/acc_active_email_api.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = serializer.validated_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            if user:
                return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmail(APIView):
    """ Confirm user email and activate account """
    def get(self, request, uidb64, token):
        User = get_user_model()
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Account activated'}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(APIView):
    """ Endpoint to change user password

    Patch:
        old_password - user old password
        new_password1 - new user password
        new_password2 - new user password
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # TODO: blacklist and generate new JWT token ?delete token on client side?
        return Response(status=status.HTTP_200_OK)


class ResetPasswordEmail(APIView):
    """ Send password reset email to user """

    def post(self, request):
        """ Send password reset email to user """
        serializer = ResetPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)

                protocol = request.build_absolute_uri().split(':')[0] # TODO
                current_site = get_current_site(request)
                mail_subject = 'Password reset for django blog'
                message = render_to_string('registration/password_reset_email_api.html', {
                    'user': user,
                    'email': email,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': password_reset_token.make_token(user),
                    'protocol': protocol,
                })
                to_email = email
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):
    """ Receive and update user password """

    def patch(self, request, uidb64, token):
        serializer = ResetPasswordSerializer(data=request.data,
                                             context={'request': request, 'token': token, 'uidb64': uidb64})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # TODO: blacklist and generate new JWT token
        return Response(status=status.HTTP_200_OK)


class BlacklistTokenView(APIView):
    """ Blacklist JWT token """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
