from datetime import datetime

from django.contrib.auth import get_user_model, password_validation
from django.core import exceptions
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.validators import validate_email
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.text import slugify

from rest_framework import serializers
from rest_framework.reverse import reverse

from blog_app.models import Post, Comment, Tag

from .tokens import password_reset_token
from scripts import filter_html


class CommentSerializer(serializers.ModelSerializer):
    """ Serialize comments """
    url = serializers.SerializerMethodField('get_url')
    author = serializers.HyperlinkedRelatedField(view_name='api:user-detail', read_only=True, lookup_field='username')
    author_username = serializers.ReadOnlyField(source='author.username')
    status = serializers.ReadOnlyField()
    report_url = serializers.SerializerMethodField('get_report_url')
    child_comments_url = serializers.SerializerMethodField('get_child_comments_url')
    post_url = serializers.SerializerMethodField('get_post_url')

    def validate_parent(self, parent):
        # Allow user to reply only to top-level comments
        if parent.is_parent:
            return parent
        raise serializers.ValidationError('Incorrect parent id. Replies allowed only to top-level comments')

    def get_url(self, obj):
        request = self.context['request']
        return reverse('api:comment-detail', kwargs={'slug': obj.post.slug, 'id': obj.id}, request=request)

    def get_post_url(self, obj):
        request = self.context['request']
        return reverse('api:post-detail', kwargs={'slug': obj.post.slug}, request=request)

    def get_report_url(self, obj):
        request = self.context['request']
        return reverse('api:report-comment', kwargs={'slug': obj.post.slug, 'id': obj.id}, request=request)

    def get_child_comments_url(self, obj):
        if obj.children() and obj.is_parent:
            request = self.context['request']
            return reverse('api:comment-detail', kwargs={'slug': obj.post.slug, 'id': obj.id}, request=request)

    class Meta:
        model = Comment
        fields = ('id', 'url', 'author', 'author_username', 'body', 'parent', 'created_on', 'status', 'report_url',
                  'parent_id', 'parent', 'post_url', 'child_comments_url')
        extra_kwargs = {
            'parent': {'write_only': True},
        }


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('tagline',)


class PostDetailSerializer(serializers.HyperlinkedModelSerializer):
    """ Serialize post, return list of comments """
    url = serializers.HyperlinkedIdentityField(view_name='api:post-detail', lookup_field='slug')
    author_username = serializers.ReadOnlyField(source='author.username')
    author = serializers.HyperlinkedRelatedField(view_name='api:user-detail', read_only=True, lookup_field='username')

    comments_url = serializers.SerializerMethodField('get_comments_url')

    total_views = serializers.SerializerMethodField('get_hits_count')
    total_likes = serializers.SerializerMethodField('get_likes')
    like_url = serializers.SerializerMethodField('get_like_url')
    report_url = serializers.SerializerMethodField('get_report_url')

    tags = TagSerializer(many=True, required=False, validators=[])

    class Meta:
        model = Post
        fields = ('url', 'id', 'status', 'title', 'content', 'slug', 'author_username', 'author', 'created_on',
                  'updated_on', 'total_views', 'total_likes', 'like_url', 'report_url', 'tags', 'comments_url')
        extra_kwargs = {
            'tags': {'validators': []},
            'slug': {'read_only': True},
            'status': {'read_only': True},
        }

    def get_comments_url(self, obj):
        """ Return url to resource with list of related comments """
        return reverse('api:post-comments', kwargs={'slug': obj.slug}, request=self.context['request'])

    def get_hits_count(self, obj):
        return obj.hit_count.hits

    def get_likes(self, obj):
        return obj.get_number_of_likes()

    def get_like_url(self, obj):
        return reverse('api:post-like', kwargs={'slug': obj.slug}, request=self.context['request'])

    def get_report_url(self, obj):
        return reverse('api:report-post', kwargs={'slug': obj.slug}, request=self.context['request'])

    def create(self, validated_data):
        tags = validated_data.pop('tags') if 'tags' in validated_data else None

        title = validated_data['title']
        content = validated_data['content']
        author = self.context['request'].user

        content = filter_html.filter_html_input(content)

        #  generate slug from user data
        slug = slugify('{}-{}-{}'.format(
            validated_data['title'],
            self.context['request'].user.username,
            datetime.now().strftime('%Y-%m-%d'))
        )
        while Post.objects.filter(slug=slug).exists():
            slug = '{}-{}'.format(slug, get_random_string(length=2))

        post = Post.objects.create(
            title=title,
            content=content,
            slug=slug,
            author=author,
            created_on=datetime.now(),
            updated_on=datetime.now(),
            status=1
        )

        if tags:
            list_of_tags = [list(tag.values())[0] for tag in tags]

            post.tags.add(*[Tag.objects.get_or_create(tagline=tag)[0] for tag in list_of_tags])

        return post

    def update(self, post, validated_data):
        post.title = validated_data.get('title', post.title)
        content = validated_data.get('content', post.content)
        content = filter_html.filter_html_input(content)
        post.content = content

        tags = validated_data.pop('tags') if 'tags' in validated_data else None

        post.save()

        if tags:
            list_of_tags = [list(tag.values())[0] for tag in tags]

            post.tags.set([Tag.objects.get_or_create(tagline=tag)[0] for tag in list_of_tags])

        return post


class PostListSerializer(serializers.HyperlinkedModelSerializer):
    """ Serialize posts; content length is 200 chars, don't return comments and edit_url"""
    url = serializers.HyperlinkedIdentityField(view_name='api:post-detail', lookup_field='slug')
    author_username = serializers.ReadOnlyField(source='author.username')
    author = serializers.HyperlinkedRelatedField(view_name='api:user-detail', read_only=True, lookup_field='username')

    total_views = serializers.SerializerMethodField('get_hits_count')
    content = serializers.SerializerMethodField('get_short_content')

    class Meta:
        model = Post
        fields = ('url', 'id', 'status', 'title', 'content', 'slug', 'author_username', 'author', 'created_on',
                  'total_views')

    def get_short_content(self, obj):
        return obj.content[:200]

    def get_hits_count(self, obj):
        return obj.hit_count.hits


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """ Serialize user information """
    url = serializers.HyperlinkedIdentityField(view_name='api:user-detail', lookup_field='username')
    posts = serializers.SerializerMethodField('get_user_posts', read_only=True)
    comments = serializers.SerializerMethodField('get_comments', read_only=True)

    def get_user_posts(self, user):
        """ Return url to user posts endpoint """
        request = self.context['request']
        return reverse('api:user-objects', kwargs={'username': self.context['kwargs']['username'],
                                                   'object_type': 'posts'}, request=request)

    def get_comments(self, user):
        """ Return url to user comments endpoint """
        request = self.context['request']
        return reverse('api:user-objects', kwargs={'username': self.context['kwargs']['username'],
                                                   'object_type': 'comments'}, request=request)

    class Meta:
        User = get_user_model()
        model = User
        fields = ('url', 'id', 'username', 'bio', 'posts', 'comments')


class RegisterUserSerializer(serializers.ModelSerializer):
    """ Serializer for user signup """

    class Meta:
        User = get_user_model()
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        password = validated_data.get('password', None)
        username = validated_data.get('username', None)
        email = validated_data.get('email', None)

        errors = dict()
        try:
            password_validation.validate_password(password, self.context['request'].user)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)

        try:
            validate_email(email)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({'message': "Email is incorrect"})

        if password is None:
            raise serializers.ValidationError({'message': "Password can't be empty"})
        instance = self.Meta.model.objects.create_user(**validated_data)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """ Serializer for password change endpoint """
    old_password = serializers.CharField(write_only=True, required=True)
    new_password1 = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Your old password was entered incorrectly. Please enter it again.')
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': "The two password fields didn't match."})
        password_validation.validate_password(data['new_password1'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class ResetPasswordEmailSerializer(serializers.Serializer):
    """ Serializer for email input for password reset endpoint """

    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """ Serializer for password reset """

    new_password = serializers.CharField(write_only=True, required=True)

    def save(self, **kwargs):
        User = get_user_model()
        try:
            uid = force_text(urlsafe_base64_decode(self.context['uidb64']))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None:
            if password_reset_token.check_token(user, self.context['token']):
                password = self.validated_data['new_password']
                user.set_password(password)
                user.save()
            else:
                raise


class EditProfileSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    class Meta:
        User = get_user_model()
        model = User
        fields = ('username', 'bio', 'email')
        extra_kwargs = {
            'username': {'read_only': True},
            'email': {'read_only': True},
        }
