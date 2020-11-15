from django.shortcuts import render
from django.views import generic
from .models import Post

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse

from django.template.defaultfilters import slugify

from .forms import NewPostForm
from .models import Post

from datetime import datetime


class PostList(generic.ListView):
    """ Show list of most recent posts """
    paginate_by = 5
    queryset = Post.objects.filter(status=1).order_by('-created_on')[:10]
    template_name = 'blog_app/index.html'


# TODO: return object only if it status==1, else 404
class PostDetail(generic.DetailView):
    """ Show single post """
    model = Post
    template_name = 'blog_app/post_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        else:
            raise Http404
            # return HttpResponse(status=404)


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
        form = NewPostForm()  # initial={'renewal_date': proposed_renewal_date}

    context = {
        'form': form,
    }

    return render(request, 'blog_app/new_post.html', context)
