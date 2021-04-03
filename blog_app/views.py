from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404

from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views import generic
from django.views.generic import RedirectView

from hitcount.views import HitCountDetailView

from .forms import NewPostForm, CommentForm
from .models import Post, ReportPost, Tag, Comment, ReportComment

from datetime import datetime


class PostList(generic.ListView):
    """ Show list of most recent posts """
    paginate_by = 15
    template_name = 'blog_app/index.html'

    def get_queryset(self, **kwargs):
        query_list = self.request.GET.getlist('q', [])
        if query_list:
            qs = [Q(title__icontains=keyword) | Q(tags__tagline__icontains=keyword) for keyword in query_list]
            query = qs.pop()

            for q in qs:
                query |= q
            posts = Post.objects.filter(query, status=1)
        else:
            posts = Post.objects.filter(status=1)
        return posts


class PostDetail(HitCountDetailView):
    """ Show single post """
    template_name = 'blog_app/post_detail.html'
    count_hit = True
    context_object_name = 'post'

    def get_object(self, slug):
        if Post.objects.filter(slug=slug, status=1).exists():
            return Post.objects.get(slug=slug)
        raise Http404

    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_object(slug)

        if self.object:
            context = self.get_context_data()

            if self.request.user in self.object.likes.all():
                context['is_liked'] = True
            else:
                context['is_liked'] = False

            context['tags'] = self.object.tags.all()

            if self.object.author.id == self.request.user.id:
                context['is_owner'] = True
            else:
                context['is_owner'] = False

            context['parent_comments'] = self.object.get_parent_comments()

            return self.render_to_response(context)
        else:
            raise Http404

    def post(self, request, *args, **kwargs):
        comment_form = CommentForm(data=request.POST)
        slug = kwargs['slug']
        self.object = self.get_object(slug)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)

            new_comment.post = self.object
            new_comment.author = self.request.user
            new_comment.active = True
            parent_obj = None
            try:
                parent_id = int(request.POST.get('parent_id'))
            except (ValueError, TypeError):
                parent_id = None

            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    parent_obj = parent_qs.first()

            new_comment.parent = parent_obj

            new_comment.save()
        return HttpResponseRedirect(reverse('blog_app:post_detail', kwargs={'slug': kwargs['slug']}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
def create_new_post(request):
    """ Create form to add new post """
    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = Post()

            new_post.title = form.cleaned_data['title']

            new_post.slug = slugify('{}-{}-{}'.format(
                form.cleaned_data['title'],
                request.user.username,
                datetime.now().strftime('%Y-%m-%d'))
            )
            slug = new_post.slug
            while Post.objects.filter(slug=slug).exists():
                slug = '{}-{}'.format(slug, get_random_string(length=2))
            new_post.slug = slug

            new_post.content = form.cleaned_data['content']
            new_post.author = request.user
            new_post.created_on = datetime.now()

            new_post.save()

            for tag in form.cleaned_data['tags'].split('#'):
                if tag:
                    new_post.tags.add(
                        Tag.objects.get_or_create(tagline=tag.strip())[0]
                    )

            return HttpResponseRedirect(reverse('blog_app:home'))
        context = {
            'form': form,
        }

        return render(request, 'blog_app/new_post.html', context)

    # If this is a GET (or any other method) create the default form.

    else:
        form = NewPostForm()

    context = {
        'form': form,
    }

    return render(request, 'blog_app/new_post.html', context)


@login_required
def edit_post(request, slug):
    """ View to edit created post """
    old_post = get_object_or_404(Post, slug=slug)

    if request.user.id == old_post.author.id:
        if request.method == 'POST':
            form = NewPostForm(request.POST, request.FILES)

            if form.is_valid():
                # set new data
                updated_post = Post.objects.get(slug=slug)
                updated_post.title = form.cleaned_data['title']

                updated_post.slug = slugify('{}-{}-{}'.format(
                    form.cleaned_data['title'],
                    request.user.username,
                    old_post.created_on.strftime('%Y-%m-%d'))
                )
                while Post.objects.filter(slug=slug).exists():
                    slug = '{}-{}'.format(slug, get_random_string(length=2))
                updated_post.slug = slug

                updated_post.content = form.cleaned_data['content']
                updated_post.updated_on = datetime.now()

                # check what tags to add and delete
                old_tags = [str(tag) for tag in old_post.tags.all()]
                new_tags = list(filter(None, form.cleaned_data['tags'].strip('#').split(' #')))
                delete_tags = list(set(old_tags) - set(new_tags))
                add_tags = list(set(new_tags) - set(old_tags))

                updated_post.tags.remove(*[Tag.objects.get(tagline=tag) for tag in delete_tags])
                updated_post.tags.add(*[Tag.objects.get_or_create(tagline=tag)[0] for tag in add_tags])

                updated_post.save()

                return HttpResponseRedirect(reverse('blog_app:home'))
            else:
                context = {
                    'form': form,
                }

                return render(request, 'blog_app/new_post.html', context)

        else:
            initial_dict = {
                'title': old_post.title,
                'content': old_post.content,
                'tags': ' '.join(f'#{str(x)}' for x in old_post.tags.all()),
            }

            form = NewPostForm(initial=initial_dict)

        context = {
            'form': form,
        }

    else:
        context = {'author_error_message': 'You can edit only your posts'}

    return render(request, 'blog_app/edit_post.html', context)


class PostLikeToggle(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        obj = get_object_or_404(Post, slug=slug)
        url_ = obj.get_absolute_url()
        user = self.request.user
        if user.is_authenticated:
            if user in obj.likes.all():
                obj.likes.remove(user)
            else:
                obj.likes.add(user)
        return url_


class PostReportToggle(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        slug = self.kwargs.get("slug")
        post = get_object_or_404(Post, slug=slug)
        url_ = post.get_absolute_url()
        user = self.request.user
        if user.is_authenticated:
            if ReportPost.objects.filter(post=post).exists():
                report = ReportPost.objects.get(post=post)
                if not report.reports.filter(username=user.username).exists():
                    report.total_reports += 1
                    report.reports.add(user)
                    report.save()
            else:
                report = ReportPost.objects.create(post=post)
                report.total_reports += 1
                report.reports.add(user)
                report.save()
        return url_


class CommentReportToggle(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        id = self.kwargs.get("id")
        comment = Comment.objects.get(id=id)

        slug = self.kwargs.get("slug")
        post = Post.objects.get(slug=slug)
        url_ = post.get_absolute_url()

        user = self.request.user
        if user.is_authenticated:
            if ReportComment.objects.filter(comment=comment).exists():
                report = ReportComment.objects.get(comment=comment)
                if not report.reports.filter(username=user.username).exists():
                    report.total_reports += 1
                    report.reports.add(user)
                    report.save()
            else:
                report = ReportComment.objects.create(comment=comment)
                report.total_reports += 1
                report.reports.add(user)
                report.save()
        return url_
