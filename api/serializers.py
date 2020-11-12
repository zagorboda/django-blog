from rest_framework import serializers

from blog_app.models import Post

# from user_app.models import CustomUser
from django.contrib.auth.models import User


class PostSerializer(serializers.HyperlinkedModelSerializer):
    # author = UserSerializer()
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'slug', 'author', 'created_on']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    # snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)
    posts = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'posts']

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
