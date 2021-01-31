from django.contrib.auth.models import User
from django.conf.urls import url
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.text import slugify

from rest_framework import generics, status, permissions, pagination, filters, renderers, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
# from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from blog_app.models import Post, Comment, Tag
from .serializers import UserSerializer, PostListSerializer, PostDetailSerializer, CommentSerializer, RegisterSerializer

from datetime import datetime

from django.http import QueryDict
import json
from rest_framework import parsers

from hitcount.views import HitCountDetailView
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

# from .permissions import IsOwnerOrReadOnly
# from django.contrib.auth import logout
# from .filters import DynamicSearchFilter

from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Blog API')


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'blog': reverse('blog_main_page', request=request, format=format)
    })


class CustomPagination(pagination.PageNumberPagination):
    page = 1
    page_size = 10
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
                reverse('user-detail', kwargs={'username': self.request.user})
            )
            response_data['create_new_post_url'] = self.request.build_absolute_uri(
                reverse('new-post')
            )
        else:
            response_data['login_url'] = self.request.build_absolute_uri(reverse('login'))
            response_data['sign_up_url'] = self.request.build_absolute_uri(reverse('signup'))

        response_data['results'] = data

        return Response(response_data)


class PostDetail(GenericAPIView):
    """ Return all information about post """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, *args, **kwargs):
        """ Return object or 404 """

        try:
            return Post.objects.get(slug=args[0], status=1)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        """ Return detail post information """

        queryset = self.get_object(slug)
        serializer = PostDetailSerializer(queryset, context={'request': request})

        hit_count = HitCount.objects.get_for_object(queryset)
        hit_count_response = HitCountMixin.hit_count(request, hit_count)

        return Response(serializer.data)

    def post(self, request, slug, format=None):
        """Add new comment to post"""

        serializer = CommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            post = self.get_object(slug)
            serializer.save(author=self.request.user, created_on=datetime.now(), post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get_serializer_class(self):
        """ Return serializer class for different requests """
        if self.request.method == 'GET':
            return PostDetailSerializer
        if self.request.method == 'POST':
            return CommentSerializer
        return PostDetailSerializer


class PostLikeAPIToggle(APIView):
    """ View to like/unlike post """
    # authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, slug, format=None):
        # slug = self.kwargs.get("slug")
        obj = get_object_or_404(Post, slug=slug)
        # url_ = obj.get_absolute_url()
        user = self.request.user
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


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    """ Return information about user """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    lookup_field = 'username'


class BlogMainPage(generics.ListAPIView):
    """ Return most recent posts """
    queryset = Post.objects.all().filter(status=1)
    serializer_class = PostListSerializer

    pagination_class = CustomPagination

    filter_backends = (filters.SearchFilter,)
    search_fields = ('title', )

    # filter_backends = (DynamicSearchFilter,)


class EditPost(APIView):
    """ Edit existing post """
    # permission_classes = (IsOwnerOrReadOnly, )

    def get_object(self, slug):
        """ Return object or 404 """
        try:
            return Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        """ Return detail post information """

        post = self.get_object(slug)
        if self.request.user.is_authenticated and self.request.user.id == post.author.id:
            serializer = PostDetailSerializer(post, context={'request': request})
            return Response(serializer.data)
        return Response({'detail': "You don't have permission to edit this post"},
                        status=status.HTTP_401_UNAUTHORIZED)

    # Title and content not empty, check this on client side
    def patch(self, request, slug, format=None):
        """ Edit post field """
        post = self.get_object(slug)
        if self.request.user.is_authenticated and self.request.user.id == post.author.id:
            data = request.data.copy()
            if 'title' in data:
                data['slug'] = slugify('{}-{}-{}'.format(
                    request.data['title'],
                    request.user.username,
                    post.created_on.strftime('%Y-%m-%d'))
                )
                while Post.objects.filter(slug=slug).exists():
                    slug = '{}-{}'.format(slug, get_random_string(length=2))
                data['slug'] = slug
            else:
                data['slug'] = post.slug
                data['title'] = post.title
            if 'content' not in request.data:
                data['content'] = post.content
            data['updated_on'] = datetime.now()
            data['status'] = 0

            tags_in_request = False
            if 'tags' in data:
                request_tags = data.getlist('tags')
                del data['tags']
                tags_in_request = True
            if 'image_changed' in data:
                # if 'image' in data:
                if data['image'] == 'deleted':
                    data['image'] = None
            else:
                if post.image:
                    data['image'] = post.image

            serializer = PostDetailSerializer(post, data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                updated_post = self.get_object(slug)

                if tags_in_request:
                    old_tags = [str(tag) for tag in post.tags.all()]
                    new_tags = list(filter(None, request_tags))
                    delete_tags = list(set(old_tags) - set(new_tags))
                    add_tags = list(set(new_tags) - set(old_tags))

                    updated_post.tags.remove(*[Tag.objects.get(tagline=tag) for tag in delete_tags])
                    updated_post.tags.add(*[Tag.objects.get_or_create(tagline=tag)[0] for tag in add_tags])

                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': "You don't have permission to edit this post"}, status=status.HTTP_401_UNAUTHORIZED)


# def gen_MultipartJsonParser(json_fields):
#     print('here get')
#
#     class MultipartJsonParser(parsers.MultiPartParser):
#         print()
#         def parse(self, stream, media_type=None, parser_context=None):
#             result = super().parse(
#                 stream,
#                 media_type=media_type,
#                 parser_context=parser_context
#             )
#             data = {}
#             # find the data field and parse it
#             qdict = QueryDict('', mutable=True)
#             for json_field in json_fields:
#                 json_data = result.data.get(json_field, None)
#                 if not json_data:
#                     continue
#                 data = json.loads(json_data)
#                 if type(data) == list:
#                     for d in data:
#                         qdict.update({json_field: d})
#                 else:
#                     qdict.update({json_field: data})
#
#             return parsers.DataAndFiles(qdict, result.files)
#
#     return MultipartJsonParser


class CreateNewPost(APIView):
    """ Create new post """
    serializer_class = PostDetailSerializer
    # parser_class = (MultiPartParser,)
    # parser_classes = [gen_MultipartJsonParser(['title', 'content'])]
    permission_classes = [IsAuthenticated, ]

    # def dispatch(self, request, *args, **kwargs):
    #     p = request.POST  # Force evaluation of the Django request
    #     return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return Response()
        # return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED) # TODO

    def post(self, request):
        """ Create new object """
        if request.content_type.startswith('multipart/form-data'):
            # as user can upload image, content-type must be multipart/form-data
            # tags must be array of strings
            required_fields = ('title', 'content')
            validation_errors = dict()

            if request.data:
                data = request.data.copy()
            else:
                data = json.loads(request.body)

            for field in required_fields:
                if field not in data:
                    validation_errors[field] = ['This field may not be blank.']
            if validation_errors:
                raise ValidationError(validation_errors)

            slug = slugify('{}-{}-{}'.format(
                data['title'],
                request.user.username,
                datetime.now().strftime('%Y-%m-%d'))
            )
            while Post.objects.filter(slug=slug).exists():
                slug = '{}-{}'.format(slug, get_random_string(length=2))
            data['slug'] = slug

            tags_in_request = False
            if 'tags' in data:
                request_tags = data.getlist('tags')
                del data['tags']
                tags_in_request = True

            serializer = PostDetailSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save(
                    created_on=datetime.now(),
                    status=0,
                    author=self.request.user
                )

                created_post = get_object_or_404(Post, slug=slug)

                if tags_in_request:
                    created_post.tags.add(*[Tag.objects.get_or_create(tagline=tag)[0] for tag in request_tags])

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Incorrect content-type"}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginApiView(ObtainAuthToken):
    """ Handle creating user authentication token """
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# class UserCreateApiView(generics.CreateAPIView):
#     """ Creates the user. """
#     queryset = User.objects.all()
#     permission_classes = (AllowAny,)
#     serializer_class = RegisterSerializer


class UserCreateApiView(APIView):

    def get(self, request):
        return Response()

    def post(self, request, format=None):
        """ Check and save new user """

        serializer = RegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json['token'] = token.key
                return Response(json, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
