from django.shortcuts import render
from django.views import generic
from .models import Post


class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')[:10]
    template_name = 'blog_app/index.html'


class PostDetail(generic.DetailView):
    model = Post
    template_name = 'blog_app/post_detail.html'
