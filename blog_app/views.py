from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse
# from django.contrib import messages
from django.template.defaultfilters import slugify

from .forms import NewPostForm, CommentForm
from .models import Post

from datetime import datetime


class PostList(generic.ListView):
    """ Show list of most recent posts """
    paginate_by = 5
    queryset = Post.objects.filter(status=1).order_by('-created_on')[:10]
    template_name = 'blog_app/index.html'


# TODO: return object only if it status==1, else 404
def post_detail(request, slug):
    template_name = 'blog_app/post_detail.html'
    post = get_object_or_404(Post, slug=slug, status=1)
    comments = post.comments.filter(active=True)

    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        print(comment_form.data)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)

            # Assign the current post adn author to the comment
            new_comment.post = post
            new_comment.author = request.user

            # Save the comment to the database
            new_comment.save()

        # request.session['message'] = 'Your previous comment is awaiting moderation'

        return HttpResponseRedirect(reverse('blog_app:post_detail', kwargs={'slug': slug}))
    else:
        # if request.COOKIES["postToken"] == 'allow':
        #     comment_form = CommentForm()
        # else:
        #     setting_cookies = 'allow'
        if request.user.is_authenticated:
            comment_form = CommentForm()
        else:
            comment_form = None

    response = render(request, template_name, {'post': post,
                                               'comments': comments,
                                               'comment_form': comment_form})

    # response.set_cookie("postToken", value=setting_cookies)

    return response


# class PostDetail(generic.DetailView):
#     """ Show single post """
#     model = Post
#     template_name = 'blog_app/post_detail.html'
#
#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         if self.object.status:
#             context = self.get_context_data(object=self.object)
#             return self.render_to_response(context)
#         else:
#             raise Http404
#             # return HttpResponse(status=404)

    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     comment_form = CommentForm(data=request.POST)
    #     if comment_form.is_valid():
    #         # Create Comment object but don't save to database yet
    #         new_comment = comment_form.save(commit=False)
    #         # Assign the current post to the comment
    #         new_comment.post = self.object
    #         # Save the comment to the database
    #         new_comment.save()


@login_required
def create_new_post(request):
    """ Create form to add new post """
    if request.method == 'POST':

        form = NewPostForm(request.POST)
        if form.is_valid():
            new_post = Post()
            new_post.title = form.cleaned_data['title']
            new_post.slug = slugify('{}-{}-{}'.format(form.cleaned_data['title'], request.user.username, str(datetime.now())))
            new_post.content = form.cleaned_data['content']
            new_post.author = request.user
            new_post.created_on = datetime.now()
            new_post.updated_on = datetime.now()
            new_post.status = 0

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

    if request.user == old_post.author:
        if request.method == 'POST':
            form = NewPostForm(request.POST)

            if form.is_valid():
                Post.objects.filter(slug=slug).update(
                    title=form.cleaned_data['title'],
                    slug=slugify('{}-{}-{}'.format(form.cleaned_data['title'], request.user.username, old_post.created_on)),
                    content=form.cleaned_data['content'],
                    updated_on=datetime.now()
                )

                return HttpResponseRedirect(reverse('blog_app:home'))

        else:
            initial_dict = {
                'title': old_post.title,
                'content': old_post.content
            }

            form = NewPostForm(initial=initial_dict)

        context = {
            'form': form,
        }

    else:
        context = {'author_error_message': 'You can edit only your posts'}

    return render(request, 'blog_app/edit_post.html', context)
