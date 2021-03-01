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
from .forms import SignUpForm, AuthenticationForm


def signup_view(request):
    if request.method == 'POST':
        print(request.POST)
        form = SignUpForm(request.POST)
        if form.is_valid():
            print('form is valid')
            print(form.cleaned_data)
            form.save()
            return redirect('user_app:login')
    else:
        form = SignUpForm()
    return render(request, 'user_app/signup.html', {'form': form})


def login_view(request):

    context = {}

    # user = request.user
    # if user.is_authenticated:
    #     return redirect("blog_app:home")

    if request.POST:
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()

    context['form'] = form
    return render(request, 'registration/login.html', context)


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


def logout_view(request):
    logout(request)
    return redirect('blog_app:home')


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

