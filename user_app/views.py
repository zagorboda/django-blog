from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.forms import UserCreationForm
# from django.http import HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
# from django.views.generic.detail import DetailView
# from django.contrib.auth.models import User
# from django.views import generic
from django.contrib.auth import logout, get_user_model, authenticate, login

from blog_app.models import Post, Comment
from .forms import SignUpForm, LoginForm


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_app:login')
    else:
        form = SignUpForm()
    return render(request, 'user_app/signup.html', {'form': form})


# def login(request):
#     print('here')
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         print(form)
#         if form.is_valid():
#             print(form.cleaned_data)
#             # login(request, request.user)
#
#     # context = LoginForm(request, {
#     #     'state': state,
#     #     'email': email,
#     #     'form': form, # pass form to the front-end / template
#     # })
#     else:
#         form = LoginForm()
#     return render(request, 'registration/login.html', {'form': form})


# @login_required
# user_profile = request.userprofile.get_profile()
# url = user_profile.url
# class UserView(DetailView):
#     model = User
#     template_name = 'user_app/user_detail.html'
#
#     def get_object(self, **kwargs):
#         print(self.kwargs)
#         return get_object_or_404(User, username=self.kwargs['name'])


def user_detail_view(request, name):
    context = dict()
    try:
        User = get_user_model()
        user = User.objects.get(username=name)
        context['user_profile'] = user
        posts_list = Post.objects.filter(author=user, status=1)
        context['posts_list'] = posts_list
        if request.user.id == user.id:
            comment_list = Comment.objects.filter(author=user)
            context['comment_list'] = comment_list
            context['is_owner'] = True
        return render(request, "user_app/user_detail.html", context)
    except Exception as e:
        raise Http404
        # context['error'] = 'User not found'

