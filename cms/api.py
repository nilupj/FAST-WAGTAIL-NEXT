from django.urls import path
from django.http import JsonResponse, Http404
from wagtail.models import Page
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.images.api.v2.views import ImagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from articles.models import ArticlePage, ArticleCategory, ArticleAuthor
from conditions.models import ConditionPage, ConditionCategory
from drugs.models import DrugPage
from news.models import NewsPage
from django.urls import path
from .views import news_latest, news_detail  # Import your view functions


api_router = WagtailAPIRouter('wagtailapi')

def drug_index(request):
    """Retrieve a listing of all drugs"""
    drugs = DrugPage.objects.live().order_by('title')
    data = [{
        'id': drug.id,
        'title': drug.title,
        'slug': drug.slug,
        'generic_name': drug.generic_name,
        'brand_names': drug.brand_names,
        'drug_class': drug.drug_class
    } for drug in drugs]
    return JsonResponse(data, safe=False)

def drug_paths(request):
    """Get all drug slug for path generation"""
    slugs = [drug.slug for drug in DrugPage.objects.live()]
    return JsonResponse(slugs, safe=False)

def drug_detail(request, slug):
    """Retrieve details for a specific drug"""
    try:
        drug = DrugPage.objects.live().get(slug=slug)
        data = {
            'id': drug.id,
            'title': drug.title,
            'slug': drug.slug,
            'generic_name': drug.generic_name,
            'brand_names': drug.brand_names,
            'drug_class': drug.drug_class,
            'overview': str(drug.overview),
            'uses': str(drug.uses),
            'dosage': str(drug.dosage),
            'side_effects': str(drug.side_effects),
            'warnings': str(drug.warnings),
            'interactions': str(drug.interactions),
            'storage': str(drug.storage),
            'pregnancy_category': drug.pregnancy_category,
        }
        return JsonResponse(data)
    except DrugPage.DoesNotExist:
        return JsonResponse({'error': 'Drug not found'}, status=404)

def news_latest(request):
    """Retrieve latest news articles"""
    news = NewsPage.objects.live().order_by('-first_published_at')[:3]
    data = [{
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'summary': article.subtitle or article.summary,
        'image': article.image.get_rendition('fill-800x500').url if article.image else None,
        'category': {'name': article.category.name} if article.category else None,
        'created_at': article.first_published_at,
    } for article in news]
    return JsonResponse(data, safe=False)

def news_paths(request):
    """Get all news slugs for static path generation"""
    slugs = [news.slug for news in NewsPage.objects.live()]
    return JsonResponse(slugs, safe=False)

def news_detail(request, slug):
    """Retrieve a specific news article"""
    try:
        article = NewsPage.objects.live().get(slug=slug)
        data = {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'subtitle': article.subtitle,
            'content': str(article.body),
            'image': article.image.get_rendition('fill-800x500').url if article.image else None,
            'published_date': article.first_published_at,
            'author': {
                'name': article.author.name if article.author else None,
                'bio': article.author.bio if article.author else None,
            } if article.author else None,
        }
        return JsonResponse(data)
    except NewsPage.DoesNotExist:
        return JsonResponse({'error': 'News article not found'}, status=404)

api_router.register_endpoint('pages', PagesAPIViewSet)
api_router.register_endpoint('images', ImagesAPIViewSet)
api_router.register_endpoint('documents', DocumentsAPIViewSet)

def articles_top_stories(request):
    """Get top stories (featured articles)"""
    articles = ArticlePage.objects.live().filter(featured=True).order_by('-first_published_at')[:5]
    return JsonResponse([{
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'summary': article.subtitle,
        'image': article.image.get_rendition('fill-800x450').url if article.image else None,
        'category': article.categories.first().name if article.categories.exists() else None,
        'created_at': article.first_published_at,
    } for article in articles], safe=False)

def articles_health_topics(request):
    """Get health topics articles"""
    try:
        health_category = ArticleCategory.objects.get(slug='health-topics')
        articles = ArticlePage.objects.live().filter(categories=health_category).order_by('-first_published_at')[:4]
    except ArticleCategory.DoesNotExist:
        articles = ArticlePage.objects.live().order_by('-first_published_at')[:4]
    
    return JsonResponse([{
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'summary': article.subtitle,
        'image': article.image.get_rendition('fill-800x450').url if article.image else None,
        'category': article.categories.first().name if article.categories.exists() else None,
        'created_at': article.first_published_at,
    } for article in articles], safe=False)

def articles_paths(request):
    """Get all article slugs for static path generation"""
    slugs = [
        article.slug for article in ArticlePage.objects.live()
    ]
    return JsonResponse(slugs, safe=False)

def article_detail(request, slug):
    """Get a single article by its slug"""
    try:
        article = ArticlePage.objects.live().get(slug=slug)
    except ArticlePage.DoesNotExist:
        raise Http404("Article not found")
    
    # Record the view
    article.increase_view_count()
    
    # Prepare the response
    data = {
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'subtitle': article.subtitle,
        'content': article.body,
        'image': article.image.get_rendition('fill-1200x600').url if article.image else None,
        'published_date': article.first_published_at,
        'updated_date': article.last_published_at if article.first_published_at != article.last_published_at else None,
        'tags': [tag.name for tag in article.tags.all()],
    }
    
    # Add category information if available
    if article.categories.exists():
        category = article.categories.first()
        data['category'] = {
            'name': category.name,
            'slug': category.slug,
        }
    
    # Add author information if available
    if article.author:
        data['author'] = {
            'name': article.author.name,
            'credentials': article.author.credentials,
            'bio': article.author.bio,
            'image': article.author.image.get_rendition('fill-100x100').url if article.author.image else None,
        }
    
    return JsonResponse(data)

def article_related(request, slug):
    """Get articles related to the specified article"""
    try:
        article = ArticlePage.objects.live().get(slug=slug)
    except ArticlePage.DoesNotExist:
        return JsonResponse([], safe=False)
    
    related_articles = ArticlePage.objects.live().exclude(id=article.id)
    
    # First try to get articles in the same categories
    if article.categories.exists():
        category_articles = related_articles.filter(categories__in=article.categories.all()).distinct()
        if category_articles.count() >= 3:
            related_articles = category_articles
    
    # Then try with tags if not enough related by category
    if article.tags.exists() and related_articles.count() < 3:
        tag_articles = related_articles.filter(tags__name__in=article.tags.names()).distinct()
        related_articles = (related_articles | tag_articles).distinct()
    
    related_articles = related_articles.order_by('-first_published_at')[:3]
    
    return JsonResponse([{
        'id': related.id,
        'title': related.title,
        'slug': related.slug,
        'summary': related.subtitle,
        'image': related.image.get_rendition('fill-800x450').url if related.image else None,
        'category': related.categories.first().name if related.categories.exists() else None,
        'created_at': related.first_published_at,
    } for related in related_articles], safe=False)

def conditions_index(request):
    """Retrieve a complete index of all health conditions"""
    conditions = ConditionPage.objects.live().order_by('title')
    
    return JsonResponse([{
        'id': condition.id,
        'name': condition.title,
        'slug': condition.slug,
        'subtitle': condition.subtitle,
    } for condition in conditions], safe=False)

def conditions_paths(request):
    """Get all condition slugs for static path generation"""
    slugs = [
        condition.slug for condition in ConditionPage.objects.live()
    ]
    return JsonResponse(slugs, safe=False)

def condition_detail(request, slug):
    """Get a single condition by its slug"""
    try:
        condition = ConditionPage.objects.live().get(slug=slug)
    except ConditionPage.DoesNotExist:
        raise Http404("Condition not found")
    
    # Record the view
    condition.increase_view_count()
    
    # Prepare the response
    data = {
        'id': condition.id,
        'name': condition.title,
        'slug': condition.slug,
        'subtitle': condition.subtitle,
        'image': condition.image.get_rendition('fill-1200x600').url if condition.image else None,
        'also_known_as': condition.also_known_as,
        'overview': condition.overview,
        'symptoms': condition.symptoms,
        'causes': condition.causes,
        'diagnosis': condition.diagnosis,
        'treatments': condition.treatments,
        'prevention': condition.prevention,
        'complications': condition.complications,
        'specialties': condition.specialties,
        'prevalence': condition.prevalence,
        'risk_factors': condition.risk_factors,
    }
    
    # Add related conditions
    if condition.related_conditions.exists():
        data['related_conditions'] = [{
            'name': related.related_condition.title,
            'slug': related.related_condition.slug,
        } for related in condition.related_conditions.all()]
    
    return JsonResponse(data)

def search_articles(request):
    """Search articles by query string"""
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse([], safe=False)
    
    # Perform the search
    articles = ArticlePage.objects.live().search(query)
    
    # Record the search query
    Page.objects.live().search(query)
    
    return JsonResponse([{
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'summary': article.subtitle,
        'image': article.image.get_rendition('fill-800x450').url if article.image else None,
        'category': article.categories.first().name if article.categories.exists() else None,
        'created_at': article.first_published_at,
    } for article in articles], safe=False)

def search_conditions(request):
    """Search conditions by query string"""
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse([], safe=False)
    
    # Perform the search
    conditions = ConditionPage.objects.live().search(query)
    
    # Record the search query
    Page.objects.live().search(query)
    
    return JsonResponse([{
        'id': condition.id,
        'name': condition.title,
        'slug': condition.slug,
        'subtitle': condition.subtitle,
    } for condition in conditions], safe=False)
def search_drugs(request):
    """search conditions by query string"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)
    # perform the search
    drugs = DrugPage.objects.live().search(query)
    #record the search query
    Page.objects.live().search(query)
    return JsonResponse([{
        'id': drug.id,
        'name': drug.title,
        'slug': drug.slug,
        'subtitle': drug.subtitle,
    } for drug in drugs], safe=False)
    

def well_being(request):
    """Get articles for the well-being section"""
    try:
        wellbeing_category = ArticleCategory.objects.get(slug='well-being')
        articles = ArticlePage.objects.live().filter(categories=wellbeing_category).order_by('-first_published_at')
    except ArticleCategory.DoesNotExist:
        articles = ArticlePage.objects.live().order_by('-first_published_at')
    
    # Featured well-being articles (latest 3)
    featured = articles[:3]
    
    return JsonResponse({
        'featured': [{
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.subtitle,
            'image': article.image.get_rendition('fill-800x450').url if article.image else None,
            'category': article.categories.first().name if article.categories.exists() else None,
            'created_at': article.first_published_at,
        } for article in featured],
        'articles': [{
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.subtitle,
            'image': article.image.get_rendition('fill-800x450').url if article.image else None,
            'category': article.categories.first().name if article.categories.exists() else None,
            'created_at': article.first_published_at,
        } for article in articles],
    })

# URLs for our custom API endpoints
urlpatterns = [
    path('drugs/index', drug_index, name='drugs_index'),
    path('drugs/paths', drug_paths, name='drug_paths'),
    path('drugs/<slug:slug>', drug_detail, name='drug_detail'),
    path('news/paths', news_paths, name='news_paths'),
    path('news/latest', news_latest, name='news_latest'),
    path('news/<slug:slug>', news_detail, name='news_detail'),
    # Article endpoints
    path('articles/top-stories', articles_top_stories, name='articles_top_stories'),
    path('articles/health-topics', articles_health_topics, name='articles_health_topics'),
    path('articles/paths', articles_paths, name='articles_paths'),
    path('articles/<slug:slug>', article_detail, name='article_detail'),
    path('articles/<slug:slug>/related', article_related, name='article_related'),
    path('articles/search', search_articles, name='search_articles'),
    
    # Condition endpoints
    path('conditions/index', conditions_index, name='conditions_index'),
    path('conditions/paths', conditions_paths, name='conditions_paths'),
    path('conditions/<slug:slug>', condition_detail, name='condition_detail'),
    path('conditions/search', search_conditions, name='search_conditions'),
    
    # Well-being endpoint
    path('well-being', well_being, name='well_being'),
    # Latest news (3 most recent articles)
    
    # Individual news article detail
    
    # ... your other URL patterns ...
    # New articles endpoints (duplicate functionality)
    
    # Or if you want separate logic:

    path('drugs/<slug:slug>', drug_detail, name='drug_detail'),
    path('drugs/search', search_drugs, name='search_drugs')
]