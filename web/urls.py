# web/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.video_search, name='video_search'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video/<int:pk>/like/', views.like_video, name='like_video'),
    path('video/<int:pk>/watchlist/', views.toggle_watchlist, name='toggle_watchlist'),
    path('video/<int:video_id>/progress/', views.update_playback_progress, name='update_playback_progress'),
]