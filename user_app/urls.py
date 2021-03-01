"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib.auth.views import PasswordResetView
from django.urls import path, include, reverse_lazy
from . import views
# from django.contrib.auth.views import LoginView, PasswordResetDoneView, auth_logout
from django.contrib.auth import views as auth_views

app_name = 'user_app'
urlpatterns = [
    # path('login/', views.login, name='login'),
    # path('password_reset/',
    #      auth_views.PasswordResetView.as_view(
    #         template_name='registration/password_reset_form.html',
    #         email_template_name='registration/password_reset_email.html',
    #         subject_template_name='registration/password_reset_subject.txt',
    #         success_url=reverse_lazy('user_app:password_reset_done')),
    #         name='password_reset'),
    # path('password-reset/', auth_views.PasswordResetView.as_view(template_name = 'registration/password_reset.html', success_url = reverse_lazy('user_app:password_reset_done')), name = 'password_reset'),
    # path('reset/', PasswordResetView.as_view(
    #     template_name='password_reset.html',
    #     email_template_name='password_reset_email.html',
    #     subject_template_name='password_reset_subject.txt'), name='password_reset_done'),
    # path('', include('django.contrib.auth.urls', namespace='user_app', ), name='account'),

    path('signup/', views.signup_view, name='signup'),
    path('profile/<str:name>/', views.user_detail_view, name='profile'),

    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('user_app:password_change_complete')),
        name='password_change'),

    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_reset_complete.html'),
        name='password_change_complete'),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_email_form.html',
        success_url=reverse_lazy('user_app:password_reset_done')),
        name='password_reset'),

    path('password_reset/done/',auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_done.html'),
        name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('user_app:password_reset_complete'),
        template_name='registration/password_reset_form.html'),
        name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'),

    path('confirm_email/<uidb64>/<token>/', views.activate,
        name='confirm_email'),

    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('login/', auth_views.LoginView.as_view(), name="login"),
]
