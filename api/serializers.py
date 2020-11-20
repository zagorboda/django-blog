from rest_framework import serializers

from blog_app.models import Post, Comment

# from user_app.models import CustomUser
from django.contrib.auth.models import User


class CommentSerializer(serializers.ModelSerializer):
    # author = serializers.ReadOnlyField(source='author.username')
    author = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True, lookup_field='username')

    class Meta:
        model = Comment
        fields = ('author', 'body', 'created_on')


class PostSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='post-detail', lookup_field='slug')
    owner = serializers.ReadOnlyField(source='author.username')
    # owner = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    # comments = serializers.HyperlinkedRelatedField(many=True, view_name='', read_only=True, lookup_field='slug')
    # comments = serializers.PrimaryKeyRelatedField(many=True, queryset=Comment.objects.all())

    comments = CommentSerializer(many=True)

    class Meta:
        model = Post
        fields = ['url', 'id', 'title', 'content', 'slug', 'owner', 'created_on', 'comments']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='username')
    posts = serializers.HyperlinkedRelatedField(many=True, view_name='post-detail', read_only=True, lookup_field='slug')
    # posts = serializers.SerializerMethodField('get_published_posts')

    # TODO : if other user make request, return only published posts, if owner make request return
    #  all posts, marked as draft/posted(return status)
    # def get_published_posts(self, user):
    #     posts = Post.objects.filter(status=1)
    #     serializer = PostSerializer(instance=posts, many=True)
    #     return serializer.data

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'posts']


# class PostSerializer(serializers.HyperlinkedModelSerializer):
#     # author = UserSerializer()
#     author = serializers.ReadOnlyField(source='author.username')
#
#     class Meta:
#         model = Post
#         fields = ['url', 'id', 'title', 'content', 'slug', 'author', 'created_on']
#
#
# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     posts = serializers.HyperlinkedRelatedField(many=True, view_name='post-detail', read_only=True)
#
#     class Meta:
#         model = User
#         fields = ['url', 'id', 'username', 'posts']

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     print(instance.username)
    #     # print(UserSerializer(instance.author).data)
    #     representation["posts"] = PostSerializer(instance).data
    #     # representation["author_id"] = UserSerializer(instance.author).data['id']
    #     return representation


    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     print(UserSerializer(instance.author).data)
    #     representation["author"] = UserSerializer(instance.author).data
    #     representation["author_id"] = UserSerializer(instance.author).data['id']
       #     return representation



# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username', 'id']
#
#
# class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ['bio', 'location']
