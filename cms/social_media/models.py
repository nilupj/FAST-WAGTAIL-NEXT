
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet


@register_snippet
class SocialMediaPlatform(models.Model):
    """Social media platform types (Instagram, YouTube, Facebook, etc.)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=80)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name")
    
    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('icon'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Social Media Platform"
        verbose_name_plural = "Social Media Platforms"


class SocialMediaIndexPage(Page):
    """Landing page for social media content."""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        context['posts'] = SocialMediaPost.objects.descendant_of(self).live().order_by('-publish_date')
        return context
    
    class Meta:
        verbose_name = "Social Media Index Page"


class SocialMediaPost(Page):
    """Individual social media post/content"""
    platform = models.ForeignKey(
        'SocialMediaPlatform',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )
    post_url = models.URLField(blank=True, help_text="Link to original post")
    embed_code = models.TextField(blank=True, help_text="Embed code from platform")
    description = RichTextField(blank=True)
    publish_date = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('description'),
        index.FilterField('platform'),
        index.FilterField('featured'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('platform'),
        FieldPanel('post_url'),
        FieldPanel('embed_code'),
        FieldPanel('description'),
        FieldPanel('thumbnail'),
        FieldPanel('featured'),
    ]
    
    api_fields = [
        APIField('title'),
        APIField('platform'),
        APIField('post_url'),
        APIField('embed_code'),
        APIField('description'),
        APIField('publish_date'),
        APIField('featured'),
        APIField('thumbnail'),
        APIField('view_count'),
    ]
    
    def increase_view_count(self):
        """Increase the view count for this post"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    class Meta:
        verbose_name = "Social Media Post"


class VideoIndexPage(Page):
    """Landing page for video content."""
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]
    
    def get_context(self, request):
        context = super().get_context(request)
        context['videos'] = VideoPage.objects.descendant_of(self).live().order_by('-publish_date')
        return context
    
    class Meta:
        verbose_name = "Video Index Page"


class VideoPage(Page):
    """Individual video content page"""
    video_url = models.URLField(blank=True, help_text="YouTube, Vimeo, or other video URL")
    video_embed_code = models.TextField(blank=True, help_text="Video embed code")
    duration = models.CharField(max_length=20, blank=True, help_text="Video duration (e.g., 10:30)")
    description = RichTextField(blank=True)
    transcript = RichTextField(blank=True, help_text="Video transcript for accessibility")
    publish_date = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('description'),
        index.SearchField('transcript'),
        index.FilterField('featured'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('video_url'),
        FieldPanel('video_embed_code'),
        FieldPanel('duration'),
        FieldPanel('description'),
        FieldPanel('transcript'),
        FieldPanel('thumbnail'),
        FieldPanel('featured'),
    ]
    
    api_fields = [
        APIField('title'),
        APIField('video_url'),
        APIField('video_embed_code'),
        APIField('duration'),
        APIField('description'),
        APIField('transcript'),
        APIField('publish_date'),
        APIField('featured'),
        APIField('thumbnail'),
        APIField('view_count'),
    ]
    
    def increase_view_count(self):
        """Increase the view count for this video"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    class Meta:
        verbose_name = "Video Page"
