from django.contrib.auth import get_user_model
from django.core import exceptions
from django.core.validators import validate_email
# from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from blog_app.models import Post, Comment, Tag
from rest_framework.reverse import reverse


# class FieldMixin(object):
#     def get_field_names(self, *args, **kwargs):
#         field_names = self.context.get('fields', None)
#         if field_names:
#             return field_names
#
#         return super(FieldMixin, self).get_field_names(*args, **kwargs)


class CommentSerializer(serializers.ModelSerializer):
    """ Serialize comments """
    author = serializers.HyperlinkedRelatedField(view_name='api:user-detail', read_only=True, lookup_field='username')
    author_username = serializers.ReadOnlyField(source='author.username')
    status = serializers.ReadOnlyField()

    class Meta:
        # list_serializer_class = FilteredCommentSerializer
        model = Comment
        fields = ('id', 'author', 'author_username', 'body', 'created_on', 'status')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('tagline',)
        extra_kwargs = {
            'tagline': {'validators': []},
        }

    def create(self, validated_data):
        pass # get_or_create

    # def get_unique_validators(self):
    #     """Overriding method to disable unique checks"""
    #     return []


class PostDetailSerializer(serializers.HyperlinkedModelSerializer):
    """ Serialize post, return list of comments """
    url = serializers.HyperlinkedIdentityField(view_name='api:post-detail', lookup_field='slug')
    author_username = serializers.ReadOnlyField(source='author.username')
    author = serializers.HyperlinkedRelatedField(view_name='api:user-detail', read_only=True, lookup_field='username')

    # comments = CommentSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField('get_active_comments')
    # edit_url = serializers.HyperlinkedRelatedField(view_name='edit-post', read_only=True, lookup_field='slug')
    edit_url = serializers.SerializerMethodField('get_edit_url')

    total_views = serializers.SerializerMethodField('get_hits_count')
    total_likes = serializers.SerializerMethodField('get_likes')
    like_url = serializers.SerializerMethodField('get_like_url')
    report_url = serializers.SerializerMethodField('get_report_url')

    # tags = serializers.SerializerMethodField('get_tags')
    tags = TagSerializer(many=True, read_only=False, required=False)
    image = serializers.ImageField(max_length=None, allow_empty_file=True, allow_null=True, required=False)
    # image_url = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Post
        fields = ('url', 'edit_url', 'id', 'status', 'title', 'content', 'slug', 'author_username', 'author',
                  'created_on', 'total_views', 'total_likes', 'like_url', 'report_url', 'image', 'tags',
                  'comments')
        extra_kwargs = {
            'tags': {'validators': []},
        }

    def get_active_comments(self, obj):
        """ Return only active comments (active=True) """
        posts = Comment.objects.all().filter(status=1, post=obj)
        serializer = CommentSerializer(posts, many=True, context={'request': self.context['request']})
        return serializer.data

    def get_edit_url(self, obj):
        """ Return url to edit-post view """
        request = self.context['request']
        if request and request.user.id == obj.author.id:
            return reverse('edit-post', kwargs={'slug': obj.slug}, request=request)
        return None

    def get_hits_count(self, obj):
        return obj.hit_count.hits

    def get_likes(self, obj):
        return obj.get_number_of_likes()

    def get_like_url(self, obj):
        request = self.context['request']
        return reverse('api:post-like', kwargs={'slug': obj.slug}, request=request)

    def get_report_url(self, obj):
        request = self.context['request']
        return reverse('api:report-post', kwargs={'slug': obj.slug}, request=request)

    def get_tags(self, obj):
        """ Return tags """
        tags = Tag.objects.all().filter(post=obj)
        tag_list = [tag.tagline for tag in tags]
        return tag_list

    def get_image_url(self, obj):
        """ Return url to image """
        if obj.image != '':
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image.url)
        return None

    # def update(self, instance, validated_data):
    #     print(validated_data)
    #     # tags = validated_data.pop('tags', None)
    #     Post.objects.filter(pk=instance.id).update(**validated_data)
    #     post = Post.objects.get(pk=instance.id)
    #     return post
    #     # print(validated_data)
    #     # print(obj)
    #
    #     # obj.update(**validated_data)
    #
    #     # return obj
    #
    #     # post = Post.objects.get(data)
    #     # for track_data in tracks_data:
    #     #     Track.objects.create(album=album, **track_data)

    # def create(self, validated_data):
    #     tags = validated_data.pop('tags')
    #     post = Post.objects.create(**validated_data)
    #     return post
    #
    # def validate(self, data):
    #     # for tag in data['tags']:
    #     #     print(tag)
    #     return data

    # def get_attr_or_default(self, attr, attrs, default=''):
    #     """Return the value of key ``attr`` in the dict ``attrs``; if that is
    #     not present, return the value of the attribute ``attr`` in
    #     ``self.instance``; otherwise return ``default``.
    #     """
    #     return attrs.get(attr, getattr(self.instance, attr, ''))

    # def get_field_names(self, *args, **kwargs):
    #     field_names = self.context.get('fields', None)
    #     if field_names:
    #         return field_names
    #
    #     return super(PostDetailSerializer, self).get_field_names(*args, **kwargs)


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

    def get_likes(self, obj):
        return obj.get_number_of_likes()

    def get_like_url(self, obj):
        request = self.context['request']
        return reverse('post-like', kwargs={'slug': obj.slug}, request=request)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """ Serialize user information """
    url = serializers.HyperlinkedIdentityField(view_name='api:user-detail', lookup_field='username')
    # posts = serializers.HyperlinkedRelatedField(many=True, view_name='post-detail', read_only=True,
    #                                             lookup_field='slug')
    posts = serializers.SerializerMethodField('get_user_posts')
    comments = serializers.SerializerMethodField('get_comments')

    def get_user_posts(self, user):
        """ Return all user posts if owner makes request, for other users return only published posts """
        if self.context['request'].user == user:
            posts = Post.objects.all().filter(author=user)
        else:
            posts = Post.objects.all().filter(author=user, status=1)
        serializer = PostListSerializer(posts, many=True, context={'request': self.context['request']})
        return serializer.data

    def get_comments(self, user):
        """ Return comments only if owner makes request """
        if self.context['request'].user == user:
            comments = Comment.objects.all().filter(author=user)
        else:
            comments = []
        serializer = CommentSerializer(comments, many=True, context={'request': self.context['request']})
        return serializer.data

    class Meta:
        User = get_user_model()
        model = User
        fields = ('url', 'id', 'username', 'posts', 'comments')


# class CreateUserSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(
#             validators=[UniqueValidator(queryset=User.objects.all())]
#             )
#     password = serializers.CharField(min_length=8)
#
#     def create(self, validated_data):
#         user = User.objects.create_user(validated_data['username'], '', validated_data['password'])
#         return user
#
#     class Meta:
#         model = User
#         fields = ('id', 'password', 'username')
#         extra_kwargs = {'password': {'write_only': True}}


# class RegisterSerializer(serializers.ModelSerializer):
#
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#
#     class Meta:
#         User = get_user_model()
#         model = User
#         fields = ('username', 'password')
#
#     def create(self, validated_data):
#         User = get_user_model()
#         user = User.objects.create_user(username=validated_data['username'])
#
#         user.set_password(validated_data['password'])
#         user.save()
#
#         return user


class RegisterUserSerializer(serializers.ModelSerializer):

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
            validate_password(password=password)
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


# class FilteredCommentSerializer(serializers.ListSerializer):
#     """ ListSerializer used to filter active comments """
#     def to_representation(self, data):
#         data = data.filter(active=True)
#         return super(FilteredCommentSerializer, self).to_representation(data)
