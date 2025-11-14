from django.urls import path, include
from . import views
from search.views import search
from news.views import news_latest, news_detail, articles_top_stories
from drugs.views import drugs_index, drug_detail, drugs_search, drug_categories

urlpatterns = [
    path('search/', search, name='api_search'),
    # Articles
    path('articles/', views.articles_index, name='articles_index'),

    path('articles/top-stories/', articles_top_stories, name='articles_top_stories'),
    path('articles/top-stories', articles_top_stories, name='articles_top_stories_no_slash'),
    path('articles/health-topics/', views.articles_health_topics, name='articles_health_topics'),
    path('articles/health-topics', views.articles_health_topics, name='articles_health_topics_no_slash'),
    path('articles/paths/', views.articles_paths, name='articles_paths'),
    path('articles/paths', views.articles_paths, name='articles_paths_no_slash'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('articles/<slug:slug>', views.article_detail, name='article_detail_no_slash'),
    path('articles/<slug:slug>/related', views.article_related, name='article_related'),
    path('articles/hi/<slug:slug>', views.article_detail, name='article_detail_hi'), #Added Hindi slug for articles

    # Conditions
    path('conditions-index/', views.conditions_index, name='conditions_index'),
    path('conditions/paths/', views.conditions_paths, name='conditions_paths'),
    path('conditions/<slug:slug>/', views.condition_detail, name='condition_detail'),
    path('conditions/hi/<slug:slug>/', views.condition_detail, name='condition_detail_hi'), #Added Hindi slug for conditions

    # Search
    path('search/articles', views.search_articles, name='search_articles'),
    path('search/conditions', views.search_conditions, name='search_conditions'),

    # Well-being
    path('well-being', views.well_being, name='well_being'),
    #Symptom Checker
    path('symptom-checker/', views.symptom_checker, name='symptom_checker'),
    path('notifications/subscribe', views.notification_subscribe, name='notification_subscribe'),
    path('newsletter/subscribe', views.newsletter_subscribe, name='newsletter_subscribe'),
    # News endpoints
    path('news/latest/', news_latest, name='news_latest'),
    path('news/paths', views.news_paths, name='news_paths'),
    path('news/<slug:slug>', views.news_detail, name='news_detail'),
    path('news/search', views.search_news, name='search_news'),
    path('news/<slug:slug>/related/', views.news_related, name='news_related'),

    # Drugs endpoints
    path('drugs/index/', drugs_index, name='drugs_index'),
    path('drugs/paths', views.drugs_paths, name='drugs_paths'),
    path('drugs/search/', drugs_search, name='drugs_search'),
    path('drugs/categories/', drug_categories, name='drug_categories'),
    path('drugs/<slug:slug>/', drug_detail, name='drug_detail'),

    # Doctors endpoints
    path('doctors/', views.doctors_list, name='api_doctors'),
    path('doctors/<slug:slug>/', views.doctor_detail, name='api_doctor_detail'),

    # Remedies endpoints
    path('remedies/latest/', views.remedies_latest, name='remedies_latest'),
    path('remedies/paths/', views.remedies_paths, name='remedies_paths'),
    path('remedies/<slug:slug>/', views.remedy_detail, name='remedy_detail'),

    # Social Media endpoints
    path('videos/latest/', views.videos_latest, name='videos_latest'),
    path('videos/<slug:slug>/', views.video_detail, name='video_detail'),
    path('social-posts/latest/', views.social_posts_latest, name='social_posts_latest'),
    path('social-posts/<slug:slug>/', views.social_post_detail, name='social_post_detail'),
    # Frontend convenience endpoints
    path('articles/', views.articles_index, name='articles_index'),
    path('wellness/', views.well_being, name='wellness'),
    path('topics/', views.articles_health_topics, name='topics'),


]