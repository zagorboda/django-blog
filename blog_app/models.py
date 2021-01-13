from django.db import models
# from django.contrib.auth.models import User
from django.urls import reverse
from hitcount.models import HitCountMixin, HitCount
from django.contrib.contenttypes.fields import GenericRelation
# from django.utils.encoding import python_2_unicode_compatible


STATUS = (
    (0, "Draft"),
    (1, "Publish")
)


class Post(models.Model, HitCountMixin):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey('auth.User', related_name='posts', on_delete=models.CASCADE, default='')
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)

    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')
    likes = models.ManyToManyField('auth.User', blank=True, related_name='post_likes')

    def get_absolute_url(self):
        return reverse("blog_app:post_detail", kwargs={"slug": self.slug})

    def get_like_url(self):
        return reverse("blog_app:post_like", kwargs={"slug": self.slug})

    def get_number_of_likes(self):
        return self.likes.count()

    def current_hit_count(self):
        return self.hit_count.hits

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title


class Tag(models.Model):
    tagline = models.CharField(max_length=200)

    posts = models.ManyToManyField(Post, blank=True, related_name='posts')

    def __str__(self):
        return self.tagline


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('auth.User', related_name='comment_author', on_delete=models.CASCADE, default='')
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {}'.format(self.body)


class ReportPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='report_post')
    reports = models.ManyToManyField('auth.User', blank=True, related_name='post_reports', default=0)
    total_reports = models.IntegerField(default=0)

    def get_number_of_reports(self):
        return self.reports.count()
