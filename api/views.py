from django.http import Http404
from django.utils.text import slugify
from rest_framework.generics import GenericAPIView
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from .serializers import UserSerializer, PostListSerializer, PostDetailSerializer, CommentSerializer
from rest_framework.response import Response
from rest_framework import renderers, viewsets, generics, status, permissions, pagination
from rest_framework.decorators import action, api_view
from .permissions import IsOwnerOrReadOnly
from django.contrib.auth import logout
from django.shortcuts import redirect

from blog_app.models import Post, Comment
from blog_app.forms import CommentForm
from django.contrib.auth.models import User

from itertools import chain
from datetime import datetime

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        # 'user': reverse('user-list', request=request, format=format),
        # 'posts': reverse('post-list', request=request, format=format),
        'blog': reverse('blog_main_page', request=request, format=format)
    })


# class PostList(generics.ListAPIView):
#     queryset = Post.objects.all().filter(status=1)
#     serializer_class = PostListSerializer
#
#     # def perform_create(self, serializer):
#     #     serializer.save(author=self.request.user)
#
#     # permission_classes = [permissions.IsAuthenticatedOrReadOnly,
#     #                       IsOwnerOrReadOnly]


class PostDetail(GenericAPIView):

    # serializer_class = PostDetailSerializer

    # permission_classes = [permissions.IsAuthenticatedOrReadOnly,
    #                       IsOwnerOrReadOnly]

    # lookup_field = 'slug'

    # page_size = 2

    def get(self, request, slug, format=None):
        # serializer_class = PostDetailSerializer
        try:
            queryset = Post.objects.get(slug=slug)
            serializer = PostDetailSerializer(queryset, context={'request': request})

            return Response(serializer.data)
        except Post.DoesNotExist:
            # return Response(status=status.HTTP_404_NOT_FOUND)
            raise Http404

    def post(self, request, slug, format=None):
        """Add new comment to post"""

        # serializer_class = CommentSerializer
        print('data = ', request.data)
        serializer = CommentSerializer(data=request.data, context={'request': request})
        print(serializer)
        if request.user.is_authenticated:
            if serializer.is_valid():
                print(serializer.validated_data)
                post = Post.objects.get(slug=slug)
                serializer.save(author=self.request.user, created_on=datetime.now(), post=post)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Credential was not provided'}, status=status.HTTP_401_UNAUTHORIZED)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostDetailSerializer
        if self.request.method == 'POST':
            return CommentSerializer
        # return PostDetailSerializer

# class PostDetail(generics.ModelViewSet):
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly,
#                           IsOwnerOrReadOnly]
#     queryset = Post.objects.all().filter(status=1)
#     serializer_class = PostSerializer
#
#     def retrieve(self, request, *args, **kwargs):
#         # ret = super(StoryViewSet, self).retrieve(request)
#         return Response({'key': 'single value'})


    # def create(self, request):
    #     model_form = CommentForm.BuildingForm(request.data)
    #     if model_form.is_valid():
    #         data = serializers.BuildingSerializer(obj).data
    #         return Response(data, status=201)
    #     else:
    #         return Response({'errors': model_form.errors}, status=400)


# class UserList(generics.ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    lookup_field = 'username'


class BlogMainPage(generics.ListAPIView):
    queryset = Post.objects.all().filter(status=1)
    serializer_class = PostListSerializer


class EditPost(APIView):

    def get_object(self, slug):
        try:
            return Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            raise Http404

    def get(self, *args, **kwargs):
        post = self.get_object(kwargs['slug'])
        # print(self.request.user.id)
        # print(post.author.id)
        if self.request.user.is_authenticated and self.request.user.id == post.author.id:
            serializer = PostDetailSerializer(post, context={'request': self.request})
            return Response(serializer.data)
        return Response({'detail': "You don't have permission to edit this post"}, status=status.HTTP_401_UNAUTHORIZED)

    # def put(self, request, *args, **kwargs):
    #     return self.update(request, *args, **kwargs)

    # Title and content not empty, check this on client side
    def patch(self, request, slug, format=None):
        post = self.get_object(slug)
        if self.request.user.is_authenticated and self.request.user.id == post.author.id:
            request.data['slug'] = slugify('{}-{}-{}'.format(request.data['title'], request.user.username, post.created_on))
            request.data['updated_on'] = datetime.now()
            request.data['status'] = 0
            serializer = PostDetailSerializer(post, data=request.data, context={'request': self.request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': "You don't have permission to edit this post"}, status=status.HTTP_401_UNAUTHORIZED)


def logout_view(request):
    logout(request)
    return redirect('blog_main_page')

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

    # permission_classes = [permissions.IsAuthenticatedOrReadOnly,
    #                       IsOwnerOrReadOnly]


# class PostViewSet(viewsets.ModelViewSet):
#     queryset = Post.objects.all().filter(status=1)
#     serializer_class = PostSerializer
#
#     lookup_field = 'slug'


# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#     lookup_field = 'username'


# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     This viewset automatically provides `list` and `retrieve` actions.
#     """
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#     lookup_field = 'id'


# class UserList(APIView):
#
#     def get(self, request):
#         users = User.objects.all()
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)  # Return JSON
#
#
# class UserDetail(APIView):
#
#     def get(self, request, name):
#         users = User.objects.get(username=name)
#         serializer1 = UserSerializer(users)
#         print(serializer1)
#         print(serializer1.data)
#         # users2 = User.objects.get(username='admin')
#         # serializer2 = UserSerializer(users2)
#         return Response(serializer1.data)  # Return JSON


# @api_view(['GET'])
# def get_configuration(request):
#     m = Post.objects.all()
#     serializer = PostSerializer(m)
#     return Response(serializer.data, status=status.HTTP_200_OK)



# class PostDetail(APIView):
#     # model = Post
#     # serializer_class = PostSerializer
#     def get(self, request):
#         posts = Post.objects.all()
#         serializer = PostSerializer(posts, many=True)
#         return Response(serializer.data)
#
#
# class PostList(viewsets.ModelViewSet):
#     queryset = Post.objects.filter(status=1).order_by('-created_on')
#     serializer_class = PostSerializer


# class UserDetail(generics.RetrieveAPIView):
#     model = User
#     serializer_class = UserSerializer

    # @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    # def highlight(self, request, *args, **kwargs):
    #     snippet = self.get_object()
    #     return Response(snippet.highlighted)

# class SnippetList(APIView):
#     """
#     List all code snippets, or create a new snippet.
#     """
#     def get(self, request, format=None):
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return Response(serializer.data)
