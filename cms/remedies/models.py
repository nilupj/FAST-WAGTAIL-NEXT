from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index


class RemedyType(models.Model):
    """Type of remedy: Homeopathic, Ayurvedic, Herbal, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Remedy Type"
        verbose_name_plural = "Remedy Types"


class RemedyCategory(models.Model):
    """Categories for remedies like Pain Relief, Digestive Health, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Remedy Category"
        verbose_name_plural = "Remedy Categories"


class RemedyIndexPage(Page):
    """Index page for all remedies"""
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    class Meta:
        verbose_name = "Remedy Index Page"


class RemedyPage(Page):
    """Individual remedy page"""
    subtitle = models.CharField(max_length=255, blank=True)
    also_known_as = models.CharField(max_length=255, blank=True)

    remedy_type = models.ForeignKey(
        RemedyType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='remedies'
    )

    categories = models.ManyToManyField(
        RemedyCategory,
        blank=True,
        related_name='remedies'
    )

    overview = RichTextField()
    uses = RichTextField(blank=True)
    dosage = RichTextField(blank=True)
    benefits = RichTextField(blank=True)
    side_effects = RichTextField(blank=True)
    precautions = RichTextField(blank=True)

    # Homeopathic specific fields
    potency = models.CharField(max_length=100, blank=True, help_text="e.g., 30C, 200C")

    # Ayurvedic specific fields
    dosha_effect = models.CharField(max_length=255, blank=True, help_text="Effect on Vata, Pitta, Kapha")
    ingredients = RichTextField(blank=True)

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    view_count = models.PositiveIntegerField(default=0)

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('subtitle'),
        index.SearchField('also_known_as'),
        index.SearchField('overview'),
        index.SearchField('uses'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('also_known_as'),
        FieldPanel('remedy_type'),
        FieldPanel('categories'),
        FieldPanel('overview'),
        FieldPanel('uses'),
        FieldPanel('dosage'),
        FieldPanel('benefits'),
        FieldPanel('side_effects'),
        FieldPanel('precautions'),
        FieldPanel('potency'),
        FieldPanel('dosha_effect'),
        FieldPanel('ingredients'),
        FieldPanel('image'),
    ]

    class Meta:
        verbose_name = "Remedy Page"