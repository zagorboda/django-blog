from django.urls import include, path
from . import views


urlpatterns = [

    path('blog/', views.BlogMainPage.as_view(), name='blog_main_page'),
    path('blog/new-post/', views.CreateNewPost.as_view(), name='new-post'),
    path('blog/post/<str:slug>/', views.PostDetail.as_view(), name='post-detail'),
    path('blog/post/<str:slug>/edit/', views.EditPost.as_view(), name='edit-post'),

    # path('user/', views.UserList.as_view(), name='user-list'),
    path('user/profile/<str:username>/', views.UserDetail.as_view(), name='user-detail'),

    path('api-auth/', include('rest_framework.urls')),
    path('login/', views.UserLoginApiView.as_view()),
    path('', views.api_root),
]
