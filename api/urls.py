from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from rest_framework_simplejwt import views as jwt_views

from . import views

app_name = 'api'

urlpatterns = [

    path('', views.api_root),

    path('blog/', views.BlogMainPage.as_view(), name='blog_main_page'),
    path('blog/new-post/', views.CreateNewPost.as_view(), name='new-post'),
    path('blog/post/<str:slug>/', views.PostDetail.as_view(), name='post-detail'),
    path('blog/post/<str:slug>/edit/', views.EditPost.as_view(), name='edit-post'),
    path('blog/post/<str:slug>/like/', views.PostLikeAPIToggle.as_view(), name='post-like'),
    path('blog/post/<str:slug>/report/', views.PostReportToggle.as_view(), name='report-post'),
    path('blog/post/<str:slug>/report/<int:id>/', views.CommentReportToggle.as_view(), name='report-comment'),

    path('schema/', views.schema_view, name='schema'),
    path('hitcount/', include(('hitcount.urls', 'hitcount'), namespace='hitcount')),

    path('user/edit_profile/', views.EditProfile.as_view(), name='edit_profile'),
    path('user/profile/<str:username>/', views.UserDetail.as_view(), name='user-detail'),
    path('user/signup/', views.UserCreateApiView.as_view(), name='signup'),
    path('user/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/token/blacklist/', views.BlacklistTokenView.as_view(), name='blacklist'),
    path('user/confirm_email/<uidb64>/<token>/', views.ConfirmEmail.as_view(),
         name='confirm_email'),
    path('user/change_password/', views.ChangePassword.as_view(),
         name='change_password'),
    path('user/reset_password/', views.ResetPasswordEmail.as_view(),
         name='email_reset_password'),
    path('user/reset_password/<uidb64>/<token>/', views.ResetPassword.as_view(),
         name='reset_password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
