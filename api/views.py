from rest_framework.reverse import reverse
from rest_framework.views import APIView
from .serializers import UserSerializer, PostSerializer
from rest_framework.response import Response
from rest_framework import renderers, viewsets, generics, status
from rest_framework.decorators import action, api_view
from rest_framework import permissions
from .permissions import IsOwnerOrReadOnly

from blog_app.models import Post
# from user_app.models import CustomUser
from django.contrib.auth.models import User


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user_app-list', request=request, format=format),
        'posts': reverse('post-list', request=request, format=format)
    })


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]

    lookup_field = 'slug'


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    lookup_field = 'username'


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
