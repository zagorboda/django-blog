from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from django import forms

from ckeditor.widgets import CKEditorWidget

from .models import Post, Comment, ReportPost, Tag, ReportComment


class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Post
        fields = '__all__'


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'author', 'slug', 'status', 'created_on', 'formatted_hit_count', 'formatted_likes')
    list_filter = ('status',)
    readonly_fields = ('formatted_hit_count', 'formatted_likes', 'author',)
    search_fields = ('title', 'author__username', 'tags__tagline')
    prepopulated_fields = {'slug': ('title',)}
    # fields = ('title', )
    # fieldsets = None
    exclude = ('likes',)

    filter_horizontal = ('tags',)

    def formatted_likes(self, obj):
        return obj.get_number_of_likes()

    formatted_likes.short_description = 'Likes'

    def formatted_hit_count(self, obj):
        if obj.id:
            hits = obj.current_hit_count()
            return hits if hits > 0 else 0
        return 0

    formatted_hit_count.admin_order_field = 'hit_count_generic__hit_count'
    formatted_hit_count.short_description = 'Hits'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'short_description', 'post_link', 'created_on')
    list_filter = ('status', 'created_on')
    list_display_links = ('author',)
    readonly_fields = ('post_link',)
    search_fields = ('body', 'post__title', 'author__username')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

    def post_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:%s_%s_change' % (obj._meta.app_label, obj.post._meta.model_name), args=[obj.post.id]),
            obj.post))
    post_link.short_description = 'Post'

    def short_description(self, obj):
        return obj.body[:100]


class ReportPostAdmin(admin.ModelAdmin):
    list_display = ('post', 'total_reports',)
    readonly_fields = ('total_reports', 'post_link')
    exclude = ('reports', 'post')

    def total_reports(self, obj):
        return obj.get_number_of_reports()

    total_reports.admin_order_field = 'total_reports'

    def post_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:%s_%s_change' % (obj._meta.app_label, obj.post._meta.model_name), args=[obj.post.id]),
            obj.post))
    post_link.short_description = 'Admin post url'


class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ('get_short_comment', 'total_reports',)
    readonly_fields = ('total_reports', 'get_comment', 'comment_link', 'post_link')
    search_fields = ('comment__body', 'comment__post__content')
    exclude = ('reports', 'comment')

    def get_short_comment(self, obj):
        return obj.comment.body[:100]

    def total_reports(self, obj):
        return obj.get_number_of_reports()

    total_reports.admin_order_field = 'total_reports'

    def post_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:%s_%s_change' % (obj._meta.app_label, obj.comment.post._meta.model_name), args=[obj.comment.post.id]),
            obj.comment.post.title[:100])
        )
    post_link.short_description = 'Post url (admin)'

    def comment_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:%s_%s_change' % (obj._meta.app_label, obj.comment._meta.model_name), args=[obj.comment.id]),
            obj.comment.body[:100])
        )
    comment_link.short_description = 'Comment url (admin)'

    def get_comment(self, obj):
        return obj.comment.body
    get_comment.short_description = 'Comment body'


class TagAdmin(admin.ModelAdmin):
    list_display = ('tagline',)
    search_fields = ('tagline',)


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ReportPost, ReportPostAdmin)
admin.site.register(ReportComment, ReportCommentAdmin)
admin.site.register(Tag, TagAdmin)
