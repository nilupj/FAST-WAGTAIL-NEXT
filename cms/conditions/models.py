from django.db import models
from django import forms

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.search import index
from wagtail.api import APIField


class ConditionCategory(models.Model):
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
        verbose_name = "Condition Category"
        verbose_name_plural = "Condition Categories"


class ConditionIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['conditions'] = ConditionPage.objects.child_of(self).live().order_by('title')
        return context

    class Meta:
        verbose_name = "Condition Index Page"


class ConditionListingPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    class Meta:
        verbose_name = "Condition Listing Page"


class RelatedConditionsOrderable(Orderable):
    page = ParentalKey('ConditionPage', on_delete=models.CASCADE, related_name='related_conditions')
    related_condition = models.ForeignKey(
        'conditions.ConditionPage',
        on_delete=models.CASCADE,
        related_name='+'
    )

    panels = [
        FieldPanel('related_condition'),
    ]


class ConditionPage(Page):
    subtitle = models.CharField(max_length=255, blank=True)
    subtitle_hi = models.CharField(max_length=255, blank=True, verbose_name="Subtitle (Hindi)")
    also_known_as = models.CharField(max_length=255, blank=True)
    also_known_as_hi = models.CharField(max_length=255, blank=True, verbose_name="Also Known As (Hindi)")
    overview = RichTextField()
    overview_hi = RichTextField(blank=True, verbose_name="Overview (Hindi)")
    symptoms = RichTextField()
    symptoms_hi = RichTextField(blank=True, verbose_name="Symptoms (Hindi)")
    causes = RichTextField()
    causes_hi = RichTextField(blank=True, verbose_name="Causes (Hindi)")
    diagnosis = RichTextField()
    diagnosis_hi = RichTextField(blank=True, verbose_name="Diagnosis (Hindi)")
    treatments = RichTextField()
    treatments_hi = RichTextField(blank=True, verbose_name="Treatments (Hindi)")
    prevention = RichTextField()
    prevention_hi = RichTextField(blank=True, verbose_name="Prevention (Hindi)")
    complications = RichTextField(blank=True)
    risk_factors = RichTextField(blank=True)
    specialties = models.CharField(max_length=255, blank=True)
    prevalence = models.CharField(max_length=255, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    
    categories = models.ManyToManyField(
        ConditionCategory,
        blank=True,
        related_name='conditions',
    )
    
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('overview'),
        index.SearchField('symptoms'),
        index.SearchField('causes'),
        index.SearchField('diagnosis'),
        index.SearchField('treatments'),
        index.SearchField('prevention'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('also_known_as'),
        FieldPanel('overview'),
        FieldPanel('symptoms'),
        FieldPanel('causes'),
        FieldPanel('diagnosis'),
        FieldPanel('treatments'),
        FieldPanel('prevention'),
        FieldPanel('complications'),
        FieldPanel('risk_factors'),
        FieldPanel('specialties'),
        FieldPanel('prevalence'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        FieldPanel('image'),
        InlinePanel('related_conditions', label="Related Conditions"),
    ]

    api_fields = [
        APIField('title'),
        APIField('subtitle'),
        APIField('also_known_as'),
        APIField('overview'),
        APIField('symptoms'),
        APIField('causes'),
        APIField('diagnosis'),
        APIField('treatments'),
        APIField('prevention'),
        APIField('complications'),
        APIField('risk_factors'),
        APIField('specialties'),
        APIField('prevalence'),
        APIField('categories'),
        APIField('image'),
        APIField('related_conditions'),
    ]

    class Meta:
        verbose_name = "Condition Page"
class ConditionAZPage(Page):
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        conditions = ConditionPage.objects.live().order_by('title')
        
        # Group conditions alphabetically
        conditions_by_letter = {}
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            conditions_by_letter[letter] = [
                condition for condition in conditions
                if condition.title.upper().startswith(letter)
            ]
            
        context['conditions_by_letter'] = conditions_by_letter
        return context

    class Meta:
        verbose_name = "Condition A-Z Page"
