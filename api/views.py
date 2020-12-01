from django.http import Http404
from django.utils.text import slugify
from rest_framework.generics import GenericAPIView
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from .serializers import UserSerializer, PostListSerializer, PostDetailSerializer, CommentSerializer
from rest_framework.response import Response
from rest_framework import renderers, viewsets, generics, status, permissions, pagination
from rest_framework.decorators import action, api_view

from rest_framework.settings import api_settings
from rest_framework.authtoken.views import ObtainAuthToken

from blog_app.models import Post, Comment
from django.contrib.auth.models import User

from datetime import datetime


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'blog': reverse('blog_main_page', request=request, format=format)
    })


class PostDetail(GenericAPIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, *args, **kwargs):
        """ Return object or 404 """

        try:
            return Post.objects.get(slug=args[0])
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, slug, format=None):
        """ Return detail post information """

        queryset = self.get_object(slug)
        serializer = PostDetailSerializer(queryset, context={'request': request})

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


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    lookup_field = 'username'


class BlogMainPage(generics.ListAPIView):
    queryset = Post.objects.all().filter(status=1)
    serializer_class = PostListSerializer


class EditPost(APIView):
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
        post = self.get_object(slug)
        if self.request.user.is_authenticated and self.request.user.id == post.author.id:
            request.data['slug'] = slugify('{}-{}-{}'.format(request.data['title'], request.user.username, post.created_on))
            request.data['updated_on'] = datetime.now()
            request.data['status'] = 0
            serializer = PostDetailSerializer(post, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': "You don't have permission to edit this post"}, status=status.HTTP_401_UNAUTHORIZED)


class UserLoginApiView(ObtainAuthToken):
    """ Handle creating user authentication token """
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
