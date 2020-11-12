from django.urls import include, path
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register(r'posts', views.PostViewSet, 'posts')
# router.register(r'users', views.UserViewSet, 'user-detail')

# user_detail = views.UserViewSet.as_view({
#     'get': 'retrieve',
# })

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path('users/<str:username>/', user_detail, name='user-detail'),
    # path('', include(router.urls)),
    # path('users/', views.UserList.as_view()),
    # path('users/<str:name>/', views.UserDetail.as_view()),

    path('posts/', views.PostList.as_view(), name='post-list'),
    path('posts/<str:slug>/', views.PostDetail.as_view(), name='post-detail'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<str:username>/', views.UserDetail.as_view(), name='user-detail'),
    path('api-auth/', include('rest_framework.urls')),
    path('', views.api_root),
]