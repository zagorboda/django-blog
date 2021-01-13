from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Post, Comment, ReportPost, Tag


class PostAdminForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
          verbose_name='Tags',
          is_stacked=False
        )
    )

    class Meta:
        fields = "__all__"
        model = Post

    def __init__(self, *args, **kwargs):
        super(PostAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['tags'].initial = self.instance.posts.all()

    def save(self, commit=True):
        post = super(PostAdminForm, self).save(commit=False)

        if commit:
            post.save()

        if post.pk:
            print(self.cleaned_data)
            print(post.posts.set(self.cleaned_data['tags']))
        self.save_m2m()

        return post


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'slug', 'status', 'created_on', 'formatted_hit_count', 'formatted_likes')
    list_filter = ('status',)
    readonly_fields = ('formatted_hit_count', 'formatted_likes')
    search_fields = ('title', 'content', 'author__username', 'tags__tagline')
    prepopulated_fields = {'slug': ('title',)}
    # fields = ('title', )
    # fieldsets = None
    exclude = ('likes',)

    filter_horizontal = ('posts',)
    form = PostAdminForm


    # def get_all_tags(self, obj):
    #     return obj.tag_set.all()

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


class TagAdmin(admin.ModelAdmin):
    list_display = ('tagline',)
    search_fields = ('tagline',)
    
    filter_horizontal = ('posts',)


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ReportPost, ReportAdmin)
admin.site.register(Tag, TagAdmin)
