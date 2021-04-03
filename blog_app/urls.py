from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

app_name = 'blog_app'
urlpatterns = [
    path('', views.PostList.as_view(), name='home'),
    path('new_post/', views.create_new_post, name='new_post'),

    path('post/<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('post/<slug:slug>/like/', views.PostLikeToggle.as_view(), name='post_like'),
    path('post/<slug:slug>/report/', views.PostReportToggle.as_view(), name='post_report'),
    path('post/<slug:slug>/report/<int:id>/', views.CommentReportToggle.as_view(), name='post_report'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),

    path('hitcount/', include(('hitcount.urls', 'hitcount'), namespace='hitcount')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
