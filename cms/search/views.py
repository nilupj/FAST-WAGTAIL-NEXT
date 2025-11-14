import os
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Meilisearch removed - using Wagtail's built-in search

def search(request):
    from articles.models import ArticlePage
    from conditions.models import ConditionPage
    from drugs.models import DrugPage
    
    search_query = request.GET.get('q', '').strip()

    if not search_query:
        return JsonResponse({
            'articles': [],
            'conditions': [],
            'drugs': []
        })

    try:
        # Search using Wagtail's built-in search
        articles_results = ArticlePage.objects.live().search(search_query)[:20]
        conditions_results = ConditionPage.objects.live().search(search_query)[:20]
        drugs_results = DrugPage.objects.live().search(search_query)[:20]

        # Format articles
        articles = [{
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.subtitle if hasattr(article, 'subtitle') else '',
            'category': article.category.name if hasattr(article, 'category') and article.category else '',
            'image': article.image.file.url if hasattr(article, 'image') and article.image else '',
            'created_at': article.first_published_at.isoformat() if article.first_published_at else '',
        } for article in articles_results]

        # Format conditions
        conditions = [{
            'id': condition.id,
            'name': condition.title,
            'slug': condition.slug,
            'subtitle': condition.subtitle if hasattr(condition, 'subtitle') else '',
        } for condition in conditions_results]

        # Format drugs
        drugs = [{
            'id': drug.id,
            'name': drug.title,
            'slug': drug.slug,
            'type': drug.drug_class if hasattr(drug, 'drug_class') else '',
        } for drug in drugs_results]

        return JsonResponse({
            'articles': articles,
            'conditions': conditions,
            'drugs': drugs
        })
    except Exception as e:
        logger.error(f'Search error in search view: {str(e)}')
        # Fallback to empty results
        return JsonResponse({
            'error': str(e),
            'articles': [],
            'conditions': [],
            'drugs': []
        }, status=500)

def api_search(request):
    """API endpoint for Wagtail search"""
    from articles.models import ArticlePage
    from conditions.models import ConditionPage
    from drugs.models import DrugPage
    from news.models import NewsPage
    
    query = request.GET.get('q', '').strip()
    lang = request.GET.get('lang', 'en')

    if not query:
        return JsonResponse({
            'articles': [],
            'conditions': [],
            'drugs': [],
            'news': []
        })

    try:
        results = {
            'articles': [],
            'conditions': [],
            'drugs': [],
            'news': []
        }

        # Search articles
        try:
            articles_results = ArticlePage.objects.live().search(query)[:10]
            results['articles'] = [{
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'subtitle': article.subtitle if hasattr(article, 'subtitle') else '',
                'summary': article.summary if hasattr(article, 'summary') else '',
                'image': article.image.file.url if hasattr(article, 'image') and article.image else '',
                'publish_date': article.first_published_at.isoformat() if article.first_published_at else '',
            } for article in articles_results]
        except Exception as e:
            logger.error(f"Error searching articles: {e}")

        # Search conditions
        try:
            conditions_results = ConditionPage.objects.live().search(query)[:10]
            results['conditions'] = [{
                'id': condition.id,
                'name': condition.title,
                'slug': condition.slug,
                'subtitle': condition.subtitle if hasattr(condition, 'subtitle') else '',
            } for condition in conditions_results]
        except Exception as e:
            logger.error(f"Error searching conditions: {e}")

        # Search drugs
        try:
            drugs_results = DrugPage.objects.live().search(query)[:10]
            results['drugs'] = [{
                'id': drug.id,
                'title': drug.title,
                'slug': drug.slug,
            } for drug in drugs_results]
        except Exception as e:
            logger.error(f"Error searching drugs: {e}")

        # Search news
        try:
            news_results = NewsPage.objects.live().search(query)[:10]
            results['news'] = [{
                'id': news.id,
                'title': news.title,
                'slug': news.slug,
                'subtitle': news.subtitle if hasattr(news, 'subtitle') else '',
            } for news in news_results]
        except Exception as e:
            logger.error(f"Error searching news: {e}")

        return JsonResponse(results)

    except Exception as e:
        logger.error(f"API search error: {e}")
        return JsonResponse({
            'articles': [],
            'conditions': [],
            'drugs': [],
            'news': [],
            'error': str(e)
        }, status=500)