import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import logging

from wagtail.models import Page

from articles.models import ArticlePage, ArticleCategory
from conditions.models import ConditionPage, ConditionCategory
from drugs.models import DrugPage
from news.models import NewsPage
from django.core.paginator import Paginator


logger = logging.getLogger(__name__)


@csrf_exempt
def symptom_checker(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            age = data.get('age')
            gender = data.get('gender')
            symptoms = data.get('symptoms', [])

            # Mock response for demonstration
            conditions = [
                {
                    "name": "Common Cold",
                    "description": "A viral infection of the nose and throat",
                    "probability": 75.5,
                    "urgency": 1
                }
            ]

            return JsonResponse({
                "conditions": conditions,
                "disclaimer": "This is for informational purposes only."
            })
        except json.JSONDecodeError as e:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)

def articles_index(request):
    return JsonResponse({"message": "Articles index working", "routes": [
        "/api/articles/top-stories/",
        "/api/articles/paths/",
        "/api/articles/<slug>/"
    ]})


def articles_top_stories(request):
    """Get top stories (featured articles)"""
    try:
        articles = ArticlePage.objects.live().filter(featured=True).order_by('-first_published_at')[:5]

        response = []
        for article in articles:
            article_data = {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'summary': article.summary,
                'body': article.body,
                'image': request.build_absolute_uri(article.image.get_rendition('fill-800x500').url) if article.image else None,
                'author': {
                    'name': article.author.name if hasattr(article, 'author') and hasattr(article.author, 'name') else (article.author if isinstance(getattr(article, 'author', ''), str) else 'Health Expert'),
                    'slug': article.author.slug if hasattr(article, 'author') and hasattr(article.author, 'slug') else '',
                    'image': article.author.image.get_rendition('fill-100x100').url if hasattr(article, 'author') and hasattr(article.author, 'image') and article.author.image else ''
                },
                'category': {
                    'name': article.category.name,
                    'slug': article.category.slug,
                } if article.category else None,
                'created_at': article.first_published_at,
                'tags': [tag.name for tag in article.tags.all()],
            }
            response.append(article_data)

        return JsonResponse(response, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
def news_paths(request):
    """Get all news slugs for static path generation"""
    try:
        news = NewsPage.objects.live().values_list('slug', flat=True)
        return JsonResponse(list(news), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def articles_health_topics(request):
    """Get health topics articles"""
    categories = ArticleCategory.objects.all()
    response = []

    for category in categories:
        articles = category.articles.live().order_by('-first_published_at')[:3]
        if articles:
            category_data = {
                'name': category.name,
                'slug': category.slug,
                'articles': []
            }

            for article in articles:
                article_data = {
                    'id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'summary': article.summary,
                    'image': article.image.get_rendition('fill-800x500').url if article.image else None,
                    'created_at': article.first_published_at,
                }
                category_data['articles'].append(article_data)

            response.append(category_data)

    return JsonResponse(response, safe=False)


def articles_paths(request):
    """Return list of article slugs for static generation"""
    try:
        from articles.models import ArticlePage
        articles = ArticlePage.objects.live().values_list('slug', flat=True)
        return JsonResponse(list(articles), safe=False)
    except Exception as e:
        logger.error(f"Error fetching article paths: {str(e)}")
        return JsonResponse([], safe=False)


from urllib.parse import unquote

def article_detail(request, slug):
    """Get a single article by its slug"""
    try:
        decoded_slug = unquote(slug.strip('/'))
        lang = request.GET.get('lang', 'en')

        # Try to find the article using the appropriate slug field based on language
        if lang == 'hi':
            article = ArticlePage.objects.live().filter(
                Q(slug_hi=decoded_slug) | Q(slug=decoded_slug)
            ).first()
        else:
            article = ArticlePage.objects.live().filter(
                Q(slug=decoded_slug) | Q(slug_hi=decoded_slug)
            ).first()

        if not article:
            return JsonResponse({'message': 'Article not found'}, status=404)

        article_data = {
            'id': article.id,
            'title': article.title_hi if lang == 'hi' and hasattr(article, 'title_hi') and article.title_hi else article.title,
            'slug': article.slug_hi if lang == 'hi' and hasattr(article, 'slug_hi') and article.slug_hi else article.slug,
            'subtitle': article.subtitle_hi if lang == 'hi' and hasattr(article, 'subtitle_hi') and article.subtitle_hi else article.subtitle,
            'summary': article.summary_hi if lang == 'hi' and hasattr(article, 'summary_hi') and article.summary_hi else article.summary,
            'body': article.body_hi if lang == 'hi' and hasattr(article, 'body_hi') and article.body_hi else article.body,
            'image': article.image.get_rendition('fill-800x500').url if article.image else None,
            'author': {
                'name': article.author.name if hasattr(article, 'author') and hasattr(article.author, 'name') else (article.author if isinstance(getattr(article, 'author', ''), str) else 'Health Expert'),
                'credentials': article.author.credentials if hasattr(article, 'author') and hasattr(article.author, 'credentials') else '',
                'bio': article.author.bio if hasattr(article, 'author') and hasattr(article.author, 'bio') else '',
                'image': article.author.image.get_rendition('fill-100x100').url if hasattr(article, 'author') and hasattr(article.author, 'image') and article.author.image else None,
            } if article.author else None,
            'category': {
                'name': article.category.name,
                'slug': article.category.slug,
            } if article.category else None,
            'tags': [tag.name for tag in article.tags.all()],
            'published_date': article.first_published_at,
            'updated_date': article.last_published_at if article.first_published_at != article.last_published_at else None,
        }

        # Update view count
        article.view_count += 1
        article.save()

        return JsonResponse(article_data)
    except ArticlePage.DoesNotExist:
        return JsonResponse({'message': 'Article not found'}, status=404)


def article_related(request, slug):
    """Get articles related to the specified article"""
    try:
        article = ArticlePage.objects.live().get(slug=slug)

        # Get articles with the same category or tags
        related_articles = ArticlePage.objects.live().filter(
            Q(category=article.category) | Q(tags__in=article.tags.all())
        ).exclude(id=article.id).distinct()[:3]

        response = []
        for related in related_articles:
            article_data = {
                'id': related.id,
                'title': related.title,
                'slug': related.slug,
                'summary': related.summary,
                'image': related.image.get_rendition('fill-800x500').url if related.image else None,
                'created_at': related.first_published_at,
            }
            response.append(article_data)

        return JsonResponse(response, safe=False)
    except ArticlePage.DoesNotExist:
        return JsonResponse([], safe=False)


def conditions_index(request):
    """Retrieve a complete index of all health conditions"""
    conditions = ConditionPage.objects.live().order_by('title')

    response = []
    for condition in conditions:
        condition_data = {
            'id': condition.id,
            'name': condition.title,
            'slug': condition.slug,
            'subtitle': condition.subtitle,
        }
        response.append(condition_data)

    return JsonResponse(response, safe=False)


def conditions_paths(request):
    """Get all condition slugs for static path generation"""
    conditions = ConditionPage.objects.live().values_list('slug', flat=True)
    return JsonResponse(list(conditions), safe=False)


def condition_detail(request, slug):
    """Get a single condition by its slug"""
    try:
        condition = ConditionPage.objects.live().get(slug=slug)

        lang = request.GET.get('lang', 'en')

        condition_data = {
            'id': condition.id,
            'name': condition.title,
            'slug': condition.slug,
            'subtitle': condition.subtitle_hi if lang == 'hi' and hasattr(condition, 'subtitle_hi') and condition.subtitle_hi else condition.subtitle,
            'overview': condition.overview_hi if lang == 'hi' and hasattr(condition, 'overview_hi') and condition.overview_hi else condition.overview,
            'symptoms': condition.symptoms_hi if lang == 'hi' and hasattr(condition, 'symptoms_hi') and condition.symptoms_hi else condition.symptoms,
            'causes': condition.causes_hi if lang == 'hi' and hasattr(condition, 'causes_hi') and condition.causes_hi else condition.causes,
            'diagnosis': condition.diagnosis_hi if lang == 'hi' and hasattr(condition, 'diagnosis_hi') and condition.diagnosis_hi else condition.diagnosis,
            'treatments': condition.treatments_hi if lang == 'hi' and hasattr(condition, 'treatments_hi') and condition.treatments_hi else condition.treatments,
            'prevention': condition.prevention_hi if lang == 'hi' and hasattr(condition, 'prevention_hi') and condition.prevention_hi else condition.prevention,
            'complications': condition.complications,
            'also_known_as': condition.also_known_as,
            'specialties': condition.specialties,
            'prevalence': condition.prevalence,
            'risk_factors': condition.risk_factors,
            'image': condition.image.get_rendition('fill-800x500').url if condition.image else None,
            'related_conditions': [
                {
                    'name': rc.related_condition.title,
                    'slug': rc.related_condition.slug,
                }
                for rc in condition.related_conditions.all()
            ],
        }

        # Update view count
        condition.view_count += 1
        condition.save()

        return JsonResponse(condition_data)
    except ConditionPage.DoesNotExist:
        return JsonResponse({'message': 'Condition not found'}, status=404)


def search_articles(request):
    """Search articles by query string"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)

    articles = ArticlePage.objects.live().specific().search(query)

    response = []
    for article in articles:
        article_data = {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.summary,
            'image': article.image.get_rendition('fill-800x500').url if article.image else None,
            'created_at': article.first_published_at,
        }
        response.append(article_data)

    return JsonResponse(response, safe=False)


def search_conditions(request):
    """Search conditions by query string"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)

    conditions = ConditionPage.objects.live().specific().search(query)
    conditions = [result.specific for result in conditions]

    response = []
    for condition in conditions:
        condition_data = {
            'id': condition.id,
            'name': condition.title,
            'slug': condition.slug,
            'subtitle': condition.subtitle,
        }
        response.append(condition_data)

    return JsonResponse(response, safe=False)


def well_being(request):
    """Get articles for the well-being section"""
    categories = ['Nutrition', 'Fitness', 'Mental Health', 'Sleep', 'Stress Management', 'Healthy Aging']
    articles = ArticlePage.objects.live().filter(
        category__name__in=categories
    ).order_by('-first_published_at')

    featured_articles = articles.filter(featured=True)[:3]

    return JsonResponse({
        'featured': [{
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.summary,
            'image': article.image.get_rendition('fill-800x500').url if article.image else None,
            'category': article.category.name if article.category else None,
        } for article in featured_articles],
        'articles': [{
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.summary,
            'image': article.image.get_rendition('fill-800x500').url if article.image else None,
            'category': article.category.name if article.category else None,
        } for article in articles[:12]]
    })
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from pywebpush import webpush, WebPushException
import json

def notification_subscribe(request):
    if request.method == 'POST':
        try:
            subscription_info = json.loads(request.body)
            # Store subscription info in database
            # Send confirmation push notification
            try:
                webpush(
                    subscription_info=subscription_info,
                    data="Thanks for subscribing to notifications!",
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": "mailto:admin@healthinfo.com"}
                )
                return JsonResponse({"status": "success"})
            except WebPushException as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

def newsletter_subscribe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({"status": "error", "message": "Email required"}, status=400)

            # Store email in database
            # Send welcome email
            send_mail(
                'Welcome to Health Info Newsletter',
                'Thank you for subscribing to our newsletter!',
                'noreply@healthinfo.com',
                [email],
                fail_silently=False,
            )
            return JsonResponse({"status": "success"})
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)


def drugs_index(request):
    """Retrieve a listing of all drugs"""
    drugs = DrugPage.objects.live().order_by('title')

    response = []
    for drug in drugs:
        drug_data = {
            'id': drug.id,
            'title': drug.title,
            'slug': drug.slug,
            'generic_name': drug.generic_name,
            'brand_names': drug.brand_names,
            'drug_class': drug.drug_class,
            'meta': {'slug': drug.slug}
        }
        response.append(drug_data)

    return JsonResponse(response, safe=False)


def conditions_index(request):
    """Get all conditions for index page"""
    try:
        conditions = ConditionPage.objects.live().order_by('title')
        data = []
        for condition in conditions:
            data.append({
                'id': condition.id,
                'name': condition.title,
                'slug': condition.slug,
                'subtitle': condition.subtitle,
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def drugs_index(request):
    """Get all drugs for index page"""
    try:
        drugs = DrugPage.objects.live().order_by('title')
        data = []
        for drug in drugs:
            data.append({
                'id': drug.id,
                'title': drug.title,
                'slug': drug.slug,
                'generic_name': drug.generic_name,
                'brand_names': drug.brand_names,
                'drug_class': drug.drug_class,
                'meta': {'slug': drug.slug}
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def drugs_paths(request):
    """Get all drug slugs for static path generation"""
    drugs = DrugPage.objects.live().values_list('slug', flat=True)
    return JsonResponse(list(drugs), safe=False)


def drug_detail(request, slug):
    """Get a single drug by its slug"""
    try:
        drug = DrugPage.objects.live().get(slug=slug)

        drug_data = {
            'id': drug.id,
            'title': drug.title,
            'slug': drug.slug,
            'generic_name': drug.generic_name,
            'brand_names': drug.brand_names,
            'drug_class': drug.drug_class,
            'overview': drug.overview,
            'uses': drug.uses,
            'dosage': drug.dosage,
            'side_effects': drug.side_effects,
            'warnings': drug.warnings,
            'interactions': drug.interactions,
            'storage': drug.storage,
            'pregnancy_category': drug.pregnancy_category,
            'image': drug.image.get_rendition('fill-800x500').url if drug.image else None,
        }

        # Update view count
        drug.view_count += 1
        drug.save()

        return JsonResponse(drug_data)
    except DrugPage.DoesNotExist:
        return JsonResponse({'message': 'Drug not found'}, status=404)


def news_latest(request):
    """Retrieve latest news articles"""
    try:
        limit = int(request.GET.get('limit', 6))
        news = NewsPage.objects.live().order_by('-first_published_at')[:limit]

        response = []
        for article in news:
            article_data = {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'subtitle': article.subtitle,
                'summary': article.summary,
                'image': request.build_absolute_uri(article.image.get_rendition('fill-800x500').url) if article.image else None,
                'category': {
                    'name': article.category.name,
                    'slug': article.category.slug,
                } if article.category else None,
                'publish_date': article.first_published_at.isoformat() if article.first_published_at else None,
                'featured': article.featured,
            }
            response.append(article_data)

        return JsonResponse(response, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e), 'news': []}, status=500)


def news_paths(request):
    """Get all news slugs for static path generation"""
    news = NewsPage.objects.live().values_list('slug', flat=True)
    return JsonResponse(list(news), safe=False)


def news_related(request, slug):
    """Get news articles related to the specified news article"""
    try:
        article = NewsPage.objects.live().get(slug=slug)

        # Get related news with the same category
        related_news = NewsPage.objects.live().exclude(id=article.id)

        if article.category:
            related_news = related_news.filter(category=article.category)

        related_news = related_news.order_by('-first_published_at')[:3]

        response = []
        for related in related_news:
            news_data = {
                'id': related.id,
                'title': related.title,
                'slug': related.slug,
                'summary': related.summary or related.subtitle,
                'image': related.image.get_rendition('fill-800x500').url if related.image else None,
                'category': {
                    'name': related.category.name,
                    'slug': related.category.slug,
                } if related.category else None,
                'created_at': related.first_published_at,
            }
            response.append(news_data)

        return JsonResponse(response, safe=False)
    except NewsPage.DoesNotExist:
        return JsonResponse([], safe=False)


def news_detail(request, slug):
    """Get a single news article by its slug"""
    try:
        article = NewsPage.objects.live().get(slug=slug)

        article_data = {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'subtitle': article.subtitle,
            'summary': article.summary,
            'body': article.body,
            'image': article.image.get_rendition('fill-1200x600').url if article.image else None,
            'category': {
                'name': article.category.name,
                'slug': article.category.slug,
            } if article.category else None,
            'publish_date': article.first_published_at,
            'source': article.source,
            'featured': article.featured,
        }

        # Update view count
        article.view_count += 1
        article.save()

        return JsonResponse(article_data)
    except NewsPage.DoesNotExist:
        return JsonResponse({'message': 'News article not found'}, status=404)


def search_drugs(request):
    """Search drugs by query string"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)

    drugs = DrugPage.objects.live().specific().search(query)

    response = []
    for drug in drugs:
        drug_data = {
            'id': drug.id,
            'title': drug.title,
            'slug': drug.slug,
            'generic_name': drug.generic_name,
            'brand_names': drug.brand_names,
            'drug_class': drug.drug_class,
        }
        response.append(drug_data)

    return JsonResponse(response, safe=False)


def search_news(request):
    """Search news by query string"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse([], safe=False)

    news = NewsPage.objects.live().specific().search(query)

    response = []
    for article in news:
        article_data = {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'subtitle': article.subtitle,
            'summary': article.summary,
            'image': article.image.get_rendition('fill-800x500').url if article.image else None,
            'publish_date': article.first_published_at,
        }
        response.append(article_data)

    return JsonResponse(response, safe=False)


def remedies_latest(request):
    """Get latest remedies"""
    try:
        from remedies.models import RemedyPage

        limit = int(request.GET.get('limit', 20))
        remedy_type = request.GET.get('type', 'all')
        lang = request.GET.get('lang', 'en')

        remedies = RemedyPage.objects.live().order_by('-first_published_at')

        if remedy_type != 'all':
            remedies = remedies.filter(remedy_type__name__iexact=remedy_type)

        remedies = remedies[:limit]

        response = []
        for remedy in remedies:
            remedy_data = {
                'id': remedy.id,
                'title': remedy.title,
                'slug': remedy.slug,
                'subtitle': remedy.subtitle,
                'also_known_as': remedy.also_known_as,
                'overview': remedy.overview,
                'image': remedy.image.get_rendition('fill-800x500').url if remedy.image else None,
                'remedy_type': {
                    'name': remedy.remedy_type.name,
                    'slug': remedy.remedy_type.slug,
                } if remedy.remedy_type else None,
                'categories': [cat.name for cat in remedy.categories.all()],
                'published_date': remedy.first_published_at,
            }
            response.append(remedy_data)

        return JsonResponse(response, safe=False)
    except Exception as e:
        print(f"Error in remedies_latest: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def remedy_detail(request, slug):
    """Get a single remedy by its slug"""
    try:
        from remedies.models import RemedyPage

        remedy = RemedyPage.objects.live().get(slug=slug)
        lang = request.GET.get('lang', 'en')

        remedy_data = {
            'id': remedy.id,
            'title': remedy.title,
            'slug': remedy.slug,
            'subtitle': remedy.subtitle,
            'also_known_as': remedy.also_known_as,
            'overview': remedy.overview,
            'uses': remedy.uses,
            'dosage': remedy.dosage,
            'benefits': remedy.benefits,
            'side_effects': getattr(remedy, 'side_effects', ''),
            'precautions': getattr(remedy, 'precautions', ''),
            'ingredients': getattr(remedy, 'ingredients', ''),
            'potency': getattr(remedy, 'potency', ''),
            'dosha_effect': getattr(remedy, 'dosha_effect', ''),
            'image': remedy.image.get_rendition('fill-800x500').url if remedy.image else None,
            'remedy_type': {
                'name': remedy.remedy_type.name,
                'slug': remedy.remedy_type.slug,
            } if remedy.remedy_type else None,
            'categories': [cat.name for cat in remedy.categories.all()],
            'published_date': remedy.first_published_at,
        }

        return JsonResponse(remedy_data)
    except Exception as e:
        return JsonResponse({'message': 'Remedy not found', 'error': str(e)}, status=404)


def remedies_paths(request):
    """Get all remedy slugs for static path generation"""
    try:
        from remedies.models import RemedyPage

        remedies = RemedyPage.objects.live().values_list('slug', flat=True)
        return JsonResponse(list(remedies), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def articles_list(request):
    articles = ArticlePage.objects.live().order_by('-first_published_at')
    lang = request.GET.get('lang', 'en')

    articles_data = []
    for article in articles:
        articles_data.append({
            'id': article.id,
            'title': article.title_hi if lang == 'hi' and hasattr(article, 'title_hi') and article.title_hi else article.title,
            'slug': article.slug_hi if lang == 'hi' and hasattr(article, 'slug_hi') and article.slug_hi else article.slug,
            'subtitle': article.subtitle_hi if lang == 'hi' and hasattr(article, 'subtitle_hi') and article.subtitle_hi else article.subtitle,
            'image': article.header_image.get_rendition('fill-800x500').url if article.header_image else None,
            'published_date': article.first_published_at.isoformat() if article.first_published_at else None,
            'category': article.category.name if hasattr(article, 'category') and article.category else None,
            'author': article.author if hasattr(article, 'author') else None,
            'author_slug': article.author_slug if hasattr(article, 'author_slug') else None,
            'author_image': article.author_image.url if hasattr(article, 'author_image') and article.author_image else None,
            'medical_reviewer': article.medical_reviewer if hasattr(article, 'medical_reviewer') else None,
            'reviewer_slug': article.reviewer_slug if hasattr(article, 'reviewer_slug') else None,
            'reviewer_credentials': article.reviewer_credentials if hasattr(article, 'reviewer_credentials') else None,
            'reviewer_image': article.reviewer_image.url if hasattr(article, 'reviewer_image') and article.reviewer_image else None,
            'reading_time': article.reading_time if hasattr(article, 'reading_time') else None,
            'last_updated': article.last_published_at.isoformat() if article.last_published_at else None,
        })

    return JsonResponse(articles_data, safe=False)


def doctors_list(request):
    """Return list of all doctors/authors with their profiles"""
    # This is a placeholder - you would create a Doctor model
    # For now, we'll extract unique authors from articles
    authors = {}
    articles = ArticlePage.objects.live().select_related('author')

    for article in articles:
        if hasattr(article, 'author') and article.author:
            author_id = article.author.id if hasattr(article.author, 'id') else article.author.name
            if author_id not in authors:
                authors[author_id] = {
                    'id': author_id,
                    'name': getattr(article.author, 'name', 'Unknown'),
                    'credentials': getattr(article.author, 'credentials', ''),
                    'slug': getattr(article.author, 'slug', str(author_id).lower().replace(' ', '-')),
                    'bio': getattr(article.author, 'bio', ''),
                    'photo': article.author.photo.file.url if hasattr(article.author, 'photo') and article.author.photo else None,
                    'specializations': getattr(article.author, 'specializations', []),
                    'education': getattr(article.author, 'education', ''),
                    'experience': getattr(article.author, 'experience', ''),
                    'articles': []
                }

            authors[author_id]['articles'].append({
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'published_date': article.first_published_at.isoformat() if article.first_published_at else None
            })

    return JsonResponse(list(authors.values()), safe=False)


def doctor_detail(request, slug):
    """Return doctor profile with their articles"""
    # This is a placeholder - you would fetch from Doctor model
    articles = ArticlePage.objects.live().select_related('author')

    doctor_data = None
    doctor_articles = []

    for article in articles:
        if hasattr(article, 'author') and article.author:
            author_slug = getattr(article.author, 'slug', str(article.author.name).lower().replace(' ', '-'))
            if author_slug == slug:
                if not doctor_data:
                    doctor_data = {
                        'id': article.author.id if hasattr(article.author, 'id') else article.author.name,
                        'name': getattr(article.author, 'name', 'Unknown'),
                        'credentials': getattr(article.author, 'credentials', ''),
                        'slug': author_slug,
                        'bio': getattr(article.author, 'bio', ''),
                        'photo': article.author.photo.file.url if hasattr(article.author, 'photo') and article.author.photo else None,
                        'specializations': getattr(article.author, 'specializations', []),
                        'education': getattr(article.author, 'education', ''),
                        'experience': getattr(article.author, 'experience', ''),
                    }

                doctor_articles.append({
                    'id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'published_date': article.first_published_at.isoformat() if article.first_published_at else None
                })

    if doctor_data:
        doctor_data['articles'] = doctor_articles
        return JsonResponse(doctor_data)
    else:
        return JsonResponse({'error': 'Doctor not found'}, status=404)


def videos_latest(request):
    """Get latest videos"""
    try:
        from social_media.models import VideoPage

        limit = int(request.GET.get('limit', 20))
        lang = request.GET.get('lang', 'en')

        videos = VideoPage.objects.live().order_by('-publish_date')[:limit]

        response = []
        for video in videos:
            video_data = {
                'id': video.id,
                'title': video.title,
                'slug': video.slug,
                'video_url': video.video_url,
                'video_embed_code': video.video_embed_code,
                'duration': video.duration,
                'description': video.description,
                'thumbnail': video.thumbnail.get_rendition('fill-800x500').url if video.thumbnail else None,
                'published_date': video.publish_date,
                'featured': video.featured,
                'view_count': video.view_count,
            }
            response.append(video_data)

        return JsonResponse(response, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def video_detail(request, slug):
    """Get a single video by its slug"""
    try:
        from social_media.models import VideoPage

        video = VideoPage.objects.live().get(slug=slug)

        video_data = {
            'id': video.id,
            'title': video.title,
            'slug': video.slug,
            'video_url': video.video_url,
            'video_embed_code': video.video_embed_code,
            'duration': video.duration,
            'description': video.description,
            'transcript': video.transcript,
            'thumbnail': video.thumbnail.get_rendition('fill-800x500').url if video.thumbnail else None,
            'published_date': video.publish_date,
            'featured': video.featured,
            'view_count': video.view_count,
        }

        video.increase_view_count()

        return JsonResponse(video_data)
    except Exception as e:
        return JsonResponse({'message': 'Video not found', 'error': str(e)}, status=404)


def social_posts_latest(request):
    """Get latest social media posts"""
    try:
        from social_media.models import SocialMediaPost

        limit = int(request.GET.get('limit', 20))
        platform = request.GET.get('platform', 'all')

        posts = SocialMediaPost.objects.live().order_by('-publish_date')

        if platform != 'all':
            posts = posts.filter(platform__slug=platform)

        posts = posts[:limit]

        response = []
        for post in posts:
            post_data = {
                'id': post.id,
                'title': post.title,
                'slug': post.slug,
                'post_url': post.post_url,
                'embed_code': post.embed_code,
                'description': post.description,
                'thumbnail': post.thumbnail.get_rendition('fill-800x500').url if post.thumbnail else None,
                'platform': {
                    'name': post.platform.name,
                    'slug': post.platform.slug,
                    'icon': post.platform.icon,
                } if post.platform else None,
                'published_date': post.publish_date,
                'featured': post.featured,
                'view_count': post.view_count,
            }
            response.append(post_data)

        return JsonResponse(response, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def social_post_detail(request, slug):
    """Get a single social media post by its slug"""
    try:
        from social_media.models import SocialMediaPost

        post = SocialMediaPost.objects.live().get(slug=slug)

        post_data = {
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'post_url': post.post_url,
            'embed_code': post.embed_code,
            'description': post.description,
            'thumbnail': post.thumbnail.get_rendition('fill-800x500').url if post.thumbnail else None,
            'platform': {
                'name': post.platform.name,
                'slug': post.platform.slug,
                'icon': post.platform.icon,
            } if post.platform else None,
            'published_date': post.publish_date,
            'featured': post.featured,
            'view_count': post.view_count,
        }

        post.increase_view_count()

        return JsonResponse(post_data)
    except Exception as e:
        return JsonResponse({'message': 'Post not found', 'error': str(e)}, status=404)