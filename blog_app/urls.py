from . import views
from django.urls import path, include


app_name = 'blog_app'
urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('search/', views.search, name='search'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('new_post/', views.create_new_post, name='new_post'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),
]
