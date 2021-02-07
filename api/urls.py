from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from rest_framework_simplejwt import views as jwt_views

from . import views


urlpatterns = [

    path('blog/', views.BlogMainPage.as_view(), name='blog_main_page'),
    path('blog/new-post/', views.CreateNewPost.as_view(), name='new-post'),
    path('blog/post/<str:slug>/', views.PostDetail.as_view(), name='post-detail'),
    path('blog/post/<str:slug>/edit/', views.EditPost.as_view(), name='edit-post'),
    path('blog/post/<str:slug>/like/', views.PostLikeAPIToggle.as_view(), name='post-like'),

    path('schema/', views.schema_view, name='schema'),

    # path('user/', views.UserList.as_view(), name='user-list'),
    path('user/profile/<str:username>/', views.UserDetail.as_view(), name='user-detail'),

    path('api-auth/', include('rest_framework.urls')),
    # path('login/', views.UserLoginApiView.as_view(), name='login'),
    path('signup/', views.UserCreateApiView.as_view(), name='signup'),
    path('', views.api_root),

    path('hitcount/', include(('hitcount.urls', 'hitcount'), namespace='hitcount')),

    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/blacklist/', views.BlacklistTokenView.as_view(), name='blacklist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
