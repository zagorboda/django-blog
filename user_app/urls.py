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
from django.contrib import admin
from django.urls import path, include
from . import views
# from django.contrib.auth.views import LoginView, PasswordResetDoneView

app_name = 'user_app'
urlpatterns = [
    path('test_redirect/', views.testing_redirect, name='test_red'),
    path('', include('django.contrib.auth.urls'), name='account'),
    path('signup/', views.signup_view, name='signup'),
    # path('pass/', views.signup_view, name='signup'),
    path('profile/<str:name>/', views.user_detail_view, name='profile'),
]
