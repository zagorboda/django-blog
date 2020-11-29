# from django.core.paginator import Paginator
from rest_framework import serializers, pagination
from django.contrib.auth.models import User

from blog_app.models import Post, Comment
from rest_framework.reverse import reverse


class FilteredCommentSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.filter(active=True)
        return super(FilteredCommentSerializer, self).to_representation(data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True, lookup_field='username')
    author_username = serializers.ReadOnlyField(source='author.username')
    active = serializers.ReadOnlyField()

    class Meta:
        # list_serializer_class = FilteredCommentSerializer
        model = Comment
        fields = ('author', 'author_username', 'body', 'created_on', 'active')


class PostDetailSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='post-detail', lookup_field='slug')
    author_username = serializers.ReadOnlyField(source='author.username')
    author = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True, lookup_field='username')

    # comments = CommentSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField('get_active_comments')
    # edit_url = serializers.HyperlinkedRelatedField(view_name='edit-post', read_only=True, lookup_field='slug')
    edit_url = serializers.SerializerMethodField('get_edit_url')

    class Meta:
        model = Post
        fields = ('url', 'edit_url', 'id', 'status', 'title', 'content', 'slug', 'author_username', 'author', 'created_on', 'comments')

    def get_active_comments(self, obj):
        posts = Comment.objects.all().filter(active=1, post=obj)
        serializer = CommentSerializer(posts, many=True, context={'request': self.context['request']})
        return serializer.data

    def get_edit_url(self, obj):
        request = self.context['request']
        return reverse('edit-post', kwargs={'slug': obj.slug}, request=request)


class PostListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='post-detail', lookup_field='slug')
    author_username = serializers.ReadOnlyField(source='author.username')
    author = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True, lookup_field='username')

    content = serializers.SerializerMethodField('get_short_content')

    class Meta:
        model = Post
        fields = ('url', 'id', 'status', 'title', 'content', 'slug', 'author_username', 'author', 'created_on')

    def get_short_content(self, obj):
        return obj.content[:200]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='username')
    # posts = serializers.HyperlinkedRelatedField(many=True, view_name='post-detail', read_only=True,
    #                                             lookup_field='slug')
    posts = serializers.SerializerMethodField('get_published_posts')
    comments = serializers.SerializerMethodField('get_comments')

    def get_published_posts(self, user):
        if self.context['request'].user == user:
            posts = Post.objects.all().filter(author=user)
        else:
            posts = Post.objects.all().filter(author=user, status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': self.context['request']})
        return serializer.data

    def get_comments(self, user):
        if self.context['request'].user == user:
            comments = Comment.objects.all().filter(author=user)
        else:
            comments = []
        serializer = CommentSerializer(comments, many=True, context={'request': self.context['request']})
        return serializer.data

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'posts', 'comments')
