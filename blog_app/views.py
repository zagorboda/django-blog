from django.contrib.auth.decorators import login_required  # permission_required
from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404  # HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.views import generic
from django.views.generic import RedirectView

from hitcount.views import HitCountDetailView

# from django.contrib.postgres.search import SearchVector  # Search
from django.db.models import Q  # Search

from .forms import NewPostForm, CommentForm
from .models import Post, ReportPost, Tag

from datetime import datetime


class BlogPostCounterMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BlogPostCounterMixin, self).get_context_data(**kwargs)
        blog_post_slug = self.kwargs['slug']
        if blog_post_slug not in self.request.session:
            bp = Post.objects.filter(slug=blog_post_slug).update(total_views=+1)
            # Insert the slug into the session as the user has seen it
            self.request.session[blog_post_slug] = blog_post_slug
        return context


class PostList(generic.ListView):
    """ Show list of most recent posts """
    paginate_by = 5
    queryset = Post.objects.filter(status=1).order_by('-created_on')[:10]
    template_name = 'blog_app/index.html'


def search(request):
    if request.method == 'GET':
        if 'q' in request.GET and request.GET.get('q'):
            page = request.GET.get('page', 1)

            query = request.GET.get('q')
            posts = Post.objects.filter(
                Q(title__icontains=query) | Q(tags__tagline__icontains=query), status=1
            ).distinct().order_by('-created_on')
            # posts = Post.objects.filter(
            #     title__icontains=query, tags__tagline__icontains=query, status=1
            # ).order_by('-created_on')
            # posts = Post.objects.annotate(
            #     search=SearchVector('title'),
            # ).filter(search__icontains=query, status=1)
            paginator = Paginator(posts, 10)
            posts = paginator.page(page)

            return render(request, 'blog_app/search.html',
                          {'post_list': posts, 'query': query})
        return render(request, 'blog_app/search.html')


# class PostListSearch(generic.ListView):
#     """ Show list of post that match search query """
#     paginate_by = 5
#     # queryset = Post.objects.filter(status=1).order_by('-created_on')[:10]
#     template_name = 'blog_app/search.html'
#
#     def get_queryset(self, **kwargs):
#         query = self.request.GET.get('q')
#         return Post.objects.filter(
#             title__icontains=query,
#             status=1
#         )
#         # return Post.objects.annotate(
#         #     search=SearchVector('title', ),
#         # ).filter(search=query)


# def post_detail(request, slug):
#     template_name = 'blog_app/post_detail.html'
#     post = get_object_or_404(Post, slug=slug, status=1)
#     comments = post.comments.filter(active=True)
#
#     # Comment posted
#     if request.method == 'POST':
#         print(request.POST)
#         comment_form = CommentForm(data=request.POST)
#         print(comment_form.data)
#         if comment_form.is_valid():
#             # Create Comment object but don't save to database yet
#             new_comment = comment_form.save(commit=False)
#
#             # Assign the current post adn author to the comment
#             new_comment.post = post
#             new_comment.author = request.user
#
#             # Save the comment to the database
#             new_comment.save()
#
#         # request.session['message'] = 'Your previous comment is awaiting moderation'
#
#         return HttpResponseRedirect(reverse('blog_app:post_detail', kwargs={'slug': slug}))
#     else:
#         # if request.COOKIES["postToken"] == 'allow':
#         #     comment_form = CommentForm()
#         # else:
#         #     setting_cookies = 'allow'
#         if request.user.is_authenticated:
#             comment_form = CommentForm()
#         else:
#             comment_form = None
#
#     response = render(request, template_name, {'post': post,
#                                                'comments': comments,
#                                                'comment_form': comment_form})
#
#     # response.set_cookie("postToken", value=setting_cookies)
#
#     return response


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


class PostDetail(HitCountDetailView):
    """ Show single post """
    model = Post
    template_name = 'blog_app/post_detail.html'
    count_hit = True

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status:
            context = self.get_context_data(object=self.object)
            if self.request.user in self.object.likes.all():
                context['is_liked'] = True
            else:
                context['is_liked'] = False
            context['tags'] = self.object.tags.all()
            if self.object.author.id == self.request.user.id:
                context['is_owner'] = True
            else:
                context['is_owner'] = False
            context_object_name = 'post'
            return self.render_to_response(context)
        else:
            raise Http404
            # return HttpResponse(status=404)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = self.object
            new_comment.author = self.request.user
            # Save the comment to the database
            new_comment.save()
        return HttpResponseRedirect(reverse('blog_app:post_detail', kwargs={'slug': kwargs['slug']}))

    # def get_context_data(self, **kwargs):
    #     context = super(PostDetail, self).get_context_data(**kwargs)
    #     blog_post_slug = self.kwargs['slug']
    #     if blog_post_slug not in self.request.session:
    #         # bp = Post.objects.filter(slug=blog_post_slug).update(total_views=+1)
    #         # Insert the slug into the session as the user has seen it
    #         self.request.session[blog_post_slug] = blog_post_slug
    #     return context


@login_required
def create_new_post(request):
    """ Create form to add new post """
    if request.method == 'POST':
        print('Files = ', request.FILES)
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            print(form.cleaned_data)
            new_post = Post()
            new_post.title = form.cleaned_data['title']
            new_post.slug = slugify('{}-{}-{}'.format(form.cleaned_data['title'], request.user.username, str(datetime.now())))
            new_post.content = form.cleaned_data['content']
            new_post.author = request.user
            new_post.created_on = datetime.now()
            new_post.updated_on = datetime.now()
            new_post.status = 0

            new_post.save()

            for tag in form.cleaned_data['tags'].split('#'):
                if tag:
                    new_post.tags.add(
                        Tag.objects.get_or_create(tagline=tag.strip())[0]
                    )

            new_post.image = form.cleaned_data['image']

            new_post.save()

            return HttpResponseRedirect(reverse('blog_app:home'))

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
            print('Files = ', request.FILES)
            form = NewPostForm(request.POST, request.FILES)

            if form.is_valid():
                print(form.cleaned_data)
                old_tags = [str(tag) for tag in old_post.tags.all()]
                new_tags = form.cleaned_data['tags'].strip('#').split(' #')
                delete_tags = list(set(old_tags) - set(new_tags))
                add_tags = list(set(new_tags) - set(old_tags))

                updated_post = Post.objects.get(slug=slug)
                updated_post.title = form.cleaned_data['title']
                updated_post.slug = slugify('{}-{}-{}'.format(form.cleaned_data['title'], request.user.username, old_post.created_on))
                updated_post.content = form.cleaned_data['content']
                updated_post.updated_on = datetime.now()

                updated_post.tags.remove(*[Tag.objects.get(tagline=tag) for tag in delete_tags])
                updated_post.tags.add(*[Tag.objects.get_or_create(tagline=tag)[0] for tag in add_tags])

                updated_post.image = form.cleaned_data['image']

                updated_post.save()

                return HttpResponseRedirect(reverse('blog_app:home'))

        else:
            initial_dict = {
                'title': old_post.title,
                'content': old_post.content,
                'tags': ' '.join(f'#{str(x)}' for x in old_post.tags.all()),
                'image': old_post.image
            }

            form = NewPostForm(initial=initial_dict)

        context = {
            'form': form,
        }

    else:
        context = {'author_error_message': 'You can edit only your posts'}

    return render(request, 'blog_app/edit_post.html', context)
