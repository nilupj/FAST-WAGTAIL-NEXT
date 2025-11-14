from django.urls import path
from . import views

urlpatterns = [
    path('latest/', views.news_latest, name='news_latest'),
    path('paths/', views.news_paths, name='news_paths'),
    path('<slug:slug>/', views.news_detail, name='news_detail'),
    path('<slug:slug>/related/', views.news_related, name='news_related'),
]