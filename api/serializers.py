from rest_framework import serializers

from blog_app.models import Post, Comment

# from user_app.models import CustomUser
from django.contrib.auth.models import User


class FilteredCommentSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.filter(active=True)
        return super(FilteredCommentSerializer, self).to_representation(data)


class CommentSerializer(serializers.ModelSerializer):
    # author = serializers.ReadOnlyField(source='author.username')
    author = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True, lookup_field='username')

    class Meta:
        list_serializer_class = FilteredCommentSerializer
        model = Comment
        fields = ('author', 'body', 'created_on')


    # def to_representation(self, instance):
    #     qs = Comment.objects.filter(active=True)
    #     print(qs)
    #     serializer = CommentSerializer(instance=qs, many=True)
    #     return qs
        # ret = super().to_representation(instance)
        # print(ret)
        # ret['body'] = 'test change text'
        # return ret

        # data = Comment.objects.all()
        # return super(CommentSerializer, self).to_representation(data)

    # def validate(self, data):
    #     errors = {}
    #     body = data.get('body')
    #     print(body)
    #
    #     if body:
    #         errors['error'] = 'Empty comment'
    #         raise serializers.ValidationError(errors)
    #
    #     return data


class PostSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='post-detail', lookup_field='slug')
    owner = serializers.ReadOnlyField(source='author.username')
    # owner = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    # comments = serializers.HyperlinkedRelatedField(many=True, view_name='', read_only=True, lookup_field='slug')
    # comments = serializers.PrimaryKeyRelatedField(many=True, queryset=Comment.objects.all())
    # comments = serializers.PrimaryKeyRelatedField(many=True, queryset=Comment.objects.filter(id=70))

    # test_variable = serializers.SerializerMethodField()

    comments = CommentSerializer(many=True, read_only=True)
    # comments1 = serializers.SerializerMethodField()
    # print(comments)

    # comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('url', 'id', 'title', 'content', 'slug', 'owner', 'created_on', 'comments')

    # def get_test_variable(self, obj):
    #     return 100

    # def get_comments(self, *args):
    #     print(args)
    #     qs = Comment.objects.filter(active=True)
    #     # print(list(qs))
    #     serializer = CommentSerializer(qs, many=True, read_only=True)
    #     # print(serializer)
    #     # return serializer.data
    #     # return serializer

    # def to_representation(self, instance):
    #     qs = Comment.objects.filter(active=True)
    #     serializer = CommentSerializer(instance=qs, many=True)
    #     print(serializer.data)
    #     return serializer.data

    # def get_comments1(self, instance):
    #     # Filter using the Car model instance and the CarType's related_name
    #     # (which in this case defaults to car_types_set)
    #     comments1_instances = instance.comments1_set.filter(status=1)
    #     return CommentSerializer(comments1_instances, many=True).data


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
