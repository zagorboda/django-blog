from rest_framework.views import APIView
from .serializers import PostSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import renderers, viewsets, generics
from rest_framework.decorators import action

from blog_app.models import Post
# from user_app.models import CustomUser
from django.contrib.auth.models import User


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().filter(status=1)
    serializer_class = PostSerializer

    lookup_field = 'slug'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    lookup_field = 'username'


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
