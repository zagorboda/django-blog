from rest_framework import serializers

from blog_app.models import Post
# from user_app.models import CustomUser
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'id']


class PostSerializer(serializers.ModelSerializer):
    # author = UserSerializer()

    class Meta:
        model = Post
        fields = ['title', 'content', 'slug', 'author', 'created_on']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        print(UserSerializer(instance.author).data)
        representation["author"] = UserSerializer(instance.author).data
        representation["author_id"] = UserSerializer(instance.author).data['id']
        return representation



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
