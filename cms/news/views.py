from django.http import JsonResponse
from django.db.models import Q
from .models import NewsPage
from articles.models import ArticlePage

def news_latest(request):
    """Get latest news articles"""
    try:
        limit = int(request.GET.get('limit', 6))
        news = NewsPage.objects.live().order_by('-first_published_at')[:limit]
        data = []

        for article in news:
            article_data = {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'subtitle': article.subtitle or '',
                'summary': article.summary or '',
                'image': request.build_absolute_uri(article.image.get_rendition('fill-800x500').url) if article.image else None,
                'category': {
                    'name': article.category.name,
                    'slug': article.category.slug,
                } if article.category else None,
                'source': article.source or '',
                'publish_date': article.first_published_at.isoformat() if article.first_published_at else None,
                'featured': article.featured,
            }
            data.append(article_data)

        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"Error in news_latest: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

def news_detail(request, slug):
    """Get a single news article by slug"""
    try:
        from urllib.parse import unquote
        decoded_slug = unquote(slug)

        # Try to find the news article
        article = NewsPage.objects.live().filter(slug=decoded_slug).first()

        if not article:
            # Log available slugs for debugging
            available_slugs = list(NewsPage.objects.live().values_list('slug', flat=True)[:10])
            print(f"News article not found with slug: '{decoded_slug}'")
            print(f"Available news slugs: {available_slugs}")
            return JsonResponse({
                'message': 'News article not found',
                'requested_slug': decoded_slug,
                'available_slugs': available_slugs
            }, status=404)

        # Build article data
        article_data = {
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'subtitle': article.subtitle or '',
            'summary': article.summary or article.subtitle or '',
            'body': article.body,
            'image': request.build_absolute_uri(article.image.get_rendition('fill-800x500').url) if article.image else None,
            'author': {
                'name': article.author_name or 'Health News Team',
                'credentials': article.author_credentials or '',
                'bio': article.author_bio or '',
            },
            'publish_date': article.first_published_at.isoformat() if article.first_published_at else None,
            'category': {
                'name': article.category.name if article.category else 'Health News',
                'slug': article.category.slug if article.category else 'health-news',
            } if hasattr(article, 'category') and article.category else None,
        }

        # Increment view count
        article.view_count += 1
        article.save(update_fields=['view_count'])

        return JsonResponse(article_data)
    except Exception as e:
        print(f"Error in news_detail: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

def news_paths(request):
    """Get all news slugs for static generation"""
    try:
        news = NewsPage.objects.live().values_list('slug', flat=True)
        return JsonResponse(list(news), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def news_related(request, slug):
    """Get related news articles"""
    try:
        article = NewsPage.objects.live().get(slug=slug)

        # Get related articles from the same category
        related = NewsPage.objects.live().filter(
            category=article.category
        ).exclude(id=article.id).order_by('-first_published_at')[:3]

        data = []
        for related_article in related:
            article_data = {
                'id': related_article.id,
                'title': related_article.title,
                'slug': related_article.slug,
                'summary': related_article.summary,
                'publish_date': related_article.first_published_at,
                'category': {
                    'name': related_article.category.name,
                    'slug': related_article.category.slug,
                } if related_article.category else None,
            }
            data.append(article_data)

        return JsonResponse(data, safe=False)
    except NewsPage.DoesNotExist:
        return JsonResponse({'message': 'News article not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def articles_top_stories(request):
    """Get top stories (featured articles)"""
    try:
        articles = ArticlePage.objects.live().filter(featured=True).order_by('-first_published_at')[:6]

        data = []
        for article in articles:
            # Handle author safely
            author_data = None
            if hasattr(article, 'author_obj') and article.author_obj:
                author_data = {
                    'name': article.author_obj.name,
                    'credentials': getattr(article.author_obj, 'credentials', ''),
                }
            elif hasattr(article, 'author') and article.author:
                author_data = {
                    'name': article.author if isinstance(article.author, str) else str(article.author),
                    'credentials': '',
                }

            article_data = {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'summary': article.summary or '',
                'body': article.body or '',
                'image': request.build_absolute_uri(article.image.get_rendition('fill-800x500').url) if article.image else None,
                'author': author_data,
                'category': {
                    'name': article.category.name,
                    'slug': article.category.slug,
                } if article.category else None,
                'created_at': article.first_published_at,
                'tags': [tag.name for tag in article.tags.all()] if hasattr(article, 'tags') else [],
                'featured': article.featured,
            }
            data.append(article_data)

        return JsonResponse(data, safe=False)
    except Exception as e:
        import traceback
        print(f"Error in articles_top_stories: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)