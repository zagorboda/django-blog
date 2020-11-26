from django.core.paginator import Paginator
from rest_framework import serializers, pagination

from blog_app.models import Post, Comment

# from user_app.models import CustomUser
from django.contrib.auth.models import User


class FilteredCommentSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        print(data)
        data = data.filter(active=True)
        print(data)
        return super(FilteredCommentSerializer, self).to_representation(data)


class CommentSerializer(serializers.ModelSerializer):
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


class PostDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='post-detail', lookup_field='slug')
    author_username = serializers.ReadOnlyField(source='author.username')
    author = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True, lookup_field='username')
    # owner = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    # comments = serializers.HyperlinkedRelatedField(many=True, view_name='', read_only=True, lookup_field='slug')
    # comments = serializers.PrimaryKeyRelatedField(many=True, queryset=Comment.objects.all())
    # comments = serializers.PrimaryKeyRelatedField(many=True, queryset=Comment.objects.filter(id=70))

    test_variable = serializers.SerializerMethodField()

    comments = CommentSerializer(many=True, read_only=True)
    # comments1 = serializers.SerializerMethodField()
    # print(comments)

    # comments = serializers.SerializerMethodField('paginated_comments')

    class Meta:
        model = Post
        fields = ('url', 'id', 'title', 'content', 'slug', 'author_username', 'author', 'created_on', 'comments', 'test_variable')

    # def paginated_comments(self, obj):
    #     page_size = 10
    #     paginator = Paginator(obj.comments.all(), page_size)
    #     # print(paginator)
    #     books = paginator.page(1)
    #     serializer = CommentSerializer(books, many=True)
    #     return serializer.data

    # def paginated_comment(self, obj):
    #     comments = Comment.objects.filter(active=True)
    #     paginator = pagination.PageNumberPagination()
    #     page = paginator.paginate_queryset(comments, self.context['request'])
    #     serializer = CommentSerializer(page, many=True, context={'request': self.context['request']})
    #     print(serializer)
    #     # return serializer.data

    # def paginated_comment(self, obj):
    #     # page_size = self.context['request'].query_params.get('size') or 2
    #     page_size = 2
    #     paginator = Paginator(obj.comments.all(), page_size)
    #     print(paginator)
    #     page = self.context['request'].query_params.get('page') or 1
    #     print(page)
    #
    #     comment = paginator.page(page)
    #     print(comment)
    #     serializer = CommentSerializer(comment, many=True)
    #     print(serializer.data)
    #     # return serializer.data

    def get_test_variable(self, obj):
        return 100

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
    #     comments1_instances = instance.comments1_set.filter(status=1)
    #     return CommentSerializer(comments1_instances, many=True).data


class PostListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='post-detail', lookup_field='slug')
    author_username = serializers.ReadOnlyField(source='author.username')
    author = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True, lookup_field='username')

    class Meta:
        model = Post
        fields = ('url', 'id', 'title', 'content', 'slug', 'author_username', 'author', 'created_on')


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
