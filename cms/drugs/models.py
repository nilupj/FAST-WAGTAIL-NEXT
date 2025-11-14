
from django.db import models
from django import forms

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from wagtail.api import APIField

class DrugCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Drug Category"
        verbose_name_plural = "Drug Categories"

class DrugIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]
    
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['drugs'] = DrugPage.objects.child_of(self).live().order_by('title')
        return context

    def get_context(self, request):
        context = super().get_context(request)
        context['drugs'] = DrugPage.objects.child_of(self).live().order_by('title')
        return context

    class Meta:
        verbose_name = "Drug Index Page"

class DrugAZPage(Page):
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        drugs = DrugPage.objects.live().order_by('title')
        
        drugs_by_letter = {}
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drugs_by_letter[letter] = [
                drug for drug in drugs
                if drug.title.upper().startswith(letter)
            ]
            
        context['drugs_by_letter'] = drugs_by_letter
        return context

    class Meta:
        verbose_name = "Drug A-Z Page"

class DrugListingPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    class Meta:
        verbose_name = "Drug Listing Page"


class DrugPage(Page):
    generic_name = models.CharField(max_length=255, blank=True)
    brand_names = models.CharField(max_length=255, blank=True)
    drug_class = models.CharField(max_length=255, blank=True)
    overview = RichTextField()
    uses = RichTextField()
    dosage = RichTextField()
    side_effects = RichTextField()
    warnings = RichTextField()
    interactions = RichTextField(blank=True)
    storage = RichTextField(blank=True)
    pregnancy_category = models.CharField(max_length=255, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    
    categories = models.ManyToManyField(
        DrugCategory,
        blank=True,
        related_name='drugs'
    )
    
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('title', boost=10),
        index.SearchField('generic_name', boost=8),
        index.SearchField('brand_names', boost=8),
        index.SearchField('drug_class', boost=5),
        index.SearchField('overview'),
        index.SearchField('uses'),
        index.SearchField('dosage'),
        index.SearchField('side_effects'),
        index.FilterField('drug_class'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('generic_name'),
        FieldPanel('brand_names'),
        FieldPanel('drug_class'),
        FieldPanel('overview'),
        FieldPanel('uses'),
        FieldPanel('dosage'),
        FieldPanel('side_effects'),
        FieldPanel('warnings'),
        FieldPanel('interactions'),
        FieldPanel('storage'),
        FieldPanel('pregnancy_category'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        FieldPanel('image'),
    ]

    api_fields = [
        APIField('title'),
        APIField('generic_name'),
        APIField('brand_names'),
        APIField('drug_class'),
        APIField('overview'),
        APIField('uses'),
        APIField('dosage'),
        APIField('side_effects'),
        APIField('warnings'),
        APIField('interactions'),
        APIField('storage'),
        APIField('pregnancy_category'),
        APIField('categories'),
        APIField('image'),
        APIField('view_count'),
    ]

    class Meta:
        verbose_name = "Drug Page"
