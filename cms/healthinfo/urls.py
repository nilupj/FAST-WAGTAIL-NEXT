from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.contrib.sitemaps.views import sitemap

from . import api
from search import views as search_views

urlpatterns = [
    # Django admin
    path('django-admin/', admin.site.urls),

    # Wagtail admin and documents
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    # Search
    path('search/', search_views.search, name='search'),
    # API search endpoint
    path('api/search/', search_views.api_search, name='api_search'),

    # API endpoints
    path('api/v2/', api.api_router.urls),
    path('api/', include('api.urls')),

    # Sitemap
    path('sitemap.xml', sitemap),

    # Wagtail pages
    path('news/', include(wagtail_urls)),       # Handles /news/ URLs
    path('articles/', include(wagtail_urls)),   # Handles /articles/ URLs (no redirect)

    # Catch-all for homepage and other pages
    path('', include(wagtail_urls)),
]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar (optional)
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass