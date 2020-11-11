from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
# from django.http import HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
# from django.views.generic.detail import DetailView
from django.contrib.auth.models import User
# from django.views import generic
from django.contrib.auth import logout

from . import models

from blog_app.models import Post


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_app:login')
    else:
        form = UserCreationForm()
    return render(request, 'user_app/signup.html', {'form': form})


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
    print(name)
    print(request.user)
    try:
        user = User.objects.get(username=name)
        context['user_profile'] = user

        posts_list = Post.objects.filter(author=user)
        context['posts_list'] = posts_list
    except Exception as e:
        print(e)
        context['error'] = 'User not found'
    print(context)
    return render(request, "user_app/user_detail.html", context)


def logout_view(request):
    logout(request)
    return redirect('blog_app:home')


def testing_redirect(request):
    return redirect('user_app:login')
