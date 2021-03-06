# from django.contrib.auth.forms import UserCreationForm
# from django.http import HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
# from django.views.generic.detail import DetailView
# from django.contrib.auth.models import User
# from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, get_user_model, authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string

from blog_app.models import Post, Comment
from .forms import SignUpForm, AuthenticationForm, EditProfileForm
from .tokens import account_activation_token


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'registration/signup_message.html')
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
    User = get_user_model()

    posts_list_page = request.GET.get('post_page', '1')
    comment_list_page = request.GET.get('comment_page', '1')
    tab = request.GET.get('tab', '1')
    if tab != 'post' and tab != 'comment':
        tab = 'post'

    posts_list_page = int(posts_list_page) if posts_list_page.isdigit() else 1
    comment_list_page = int(comment_list_page) if comment_list_page.isdigit() else 1

    user = get_object_or_404(User, username=name)
    context['user_profile'] = user

    user_posts = Post.objects.filter(author=user, status=1)
    paginator = Paginator(user_posts, 15)
    try:
        post_list = paginator.page(posts_list_page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    context['post_list'] = post_list

    user_comments = Comment.objects.filter(author=user, status=1)
    paginator = Paginator(user_comments, 15)
    try:
        comment_list = paginator.page(comment_list_page)
    except PageNotAnInteger:
        comment_list = paginator.page(1)
    except EmptyPage:
        comment_list = paginator.page(paginator.num_pages)
    context['comment_list'] = comment_list

    context['tab'] = tab

    if request.user.id == user.id:
        context['is_owner'] = True

    return render(request, "user_app/user_detail.html", context)


def confirm_email_view(request, uidb64, token):
    User = get_user_model()

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.add_message(request, messages.INFO, 'Thank you for your email confirmation. Now you can login your account.')
        return HttpResponseRedirect(reverse('user_app:login'))
    else:
        messages.add_message(request, messages.INFO, 'Activation link is invalid!')
        return HttpResponseRedirect(reverse('user_app:login'))


@login_required
def edit_profile_view(request):
    user = request.user
    if request.method == 'POST':
        print(request)
        print(request.POST)
        form = EditProfileForm(request.POST)

        if form.is_valid():
            user.bio = form.cleaned_data['bio']
            user.save()

            return HttpResponseRedirect(reverse('user_app:profile', kwargs={'name': user.username}))
    else:
        initial_dict = {
            'bio': user.bio
        }

        form = EditProfileForm(initial=initial_dict)

    context = {
        'form': form,
    }

    return render(request, 'user_app/edit_profile.html', context)
