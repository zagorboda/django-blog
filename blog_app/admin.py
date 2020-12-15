from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Post, Comment, ReportPost


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'slug', 'status', 'created_on', 'formatted_hit_count')
    list_filter = ('status',)
    readonly_fields = ('formatted_hit_count',)
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}

    def formatted_hit_count(self, obj):
        return obj.hit_count.hits if obj.hit_count.hits > 0 else 0

    formatted_hit_count.admin_order_field = 'hit_count_generic__hit_count'
    formatted_hit_count.short_description = 'Hits'


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


class ReportAdmin(admin.ModelAdmin):
    list_display = ('post', 'total_reports', 'post_link')
    readonly_fields = ('total_reports',)

    def total_reports(self, obj):
        return obj.get_number_of_reports()

    total_reports.admin_order_field = 'total_reports'


    def post_link(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse('admin:%s_%s_change' % (obj._meta.app_label, obj.post._meta.model_name), args=[obj.post.id]),
            obj.post))
    post_link.short_description = 'Admin post url'


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ReportPost, ReportAdmin)
