
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from news.models import NewsPage

class HomePage(Page):
    """Home page model."""
    intro = RichTextField(blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
    ]

    def get_featured_news(self):
        """Get the latest featured news articles"""
        return NewsPage.objects.live().filter(featured=True).order_by('-publish_date')[:3]

    def get_latest_news(self):
        """Get the latest news articles"""
        return NewsPage.objects.live().order_by('-publish_date')[:3]
