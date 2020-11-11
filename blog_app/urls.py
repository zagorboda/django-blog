from . import views
from django.urls import path, include


app_name = 'blog_app'
urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('post/<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('new_post/', views.create_new_post, name='new_post'),
]
