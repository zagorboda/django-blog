from rest_framework import serializers

from blog_app.models import Post

# from user_app.models import CustomUser
from django.contrib.auth.models import User


class PostSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='post-detail', lookup_field='slug')
    owner = serializers.ReadOnlyField(source='author.username')
    # owner = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    total_views = serializers.SerializerMethodField('get_hits_count')
    print(total_views)

    class Meta:
        model = Post
        fields = ['url', 'id', 'title', 'content', 'slug', 'owner', 'created_on', 'total_views']

    def get_hits_count(self, obj):
        return obj.hit_count.hits


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='username')
    posts = serializers.HyperlinkedRelatedField(many=True, view_name='post-detail', read_only=True, lookup_field='slug')

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
