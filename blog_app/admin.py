from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'slug', 'status', 'created_on')
    list_filter = ('status',)
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'short_description', 'post_link', 'created_on')
    list_filter = ('active', 'created_on')
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


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)