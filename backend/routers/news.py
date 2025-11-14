from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
import httpx
import os
import logging
from datetime import datetime

from models import ArticlePreview, Article, ErrorResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Set the CMS API URL from environment variable with a fallback
CMS_API_URL = os.getenv("CMS_API_URL", "http://localhost:8001/api")

# Utility function to make requests to the CMS API
async def fetch_from_cms(endpoint: str, params=None):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CMS_API_URL}/{endpoint}", params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            logger.error(f"Error fetching {endpoint}: {exc}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: Unable to connect to CMS API."
            )
        except httpx.HTTPStatusError as exc:
            logger.error(f"Error response {exc.response.status_code} from CMS: {exc}")
            status_code = exc.response.status_code
            try:
                detail = exc.response.json()
            except:
                detail = str(exc)
            raise HTTPException(status_code=status_code, detail=detail)
        except Exception as exc:
            logger.error(f"Unexpected error fetching {endpoint}: {exc}")
            raise HTTPException(status_code=500, detail=str(exc))

# Mock news data for development
mock_news = [
    ArticlePreview(
        id=1,
        title="New AI Tools Send Lifesaving Alerts on Sepsis",
        slug="new-ai-tools-send-lifesaving-alerts-on-sepsis",
        summary="Artificial intelligence systems are being deployed in hospitals to help detect sepsis earlier and save more lives.",
        image="https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=500&q=80",
        category="Medical Technology",
        created_at=datetime.now(),
    ),
    ArticlePreview(
        id=2,
        title="Breakthrough in Cancer Treatment Shows Promise",
        slug="breakthrough-cancer-treatment-shows-promise",
        summary="Researchers have developed a new immunotherapy approach that shows remarkable results in clinical trials.",
        image="https://images.unsplash.com/photo-1559757148-5c350d0d3c56?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=500&q=80",
        category="Cancer Research",
        created_at=datetime.now(),
    ),
    ArticlePreview(
        id=3,
        title="Mental Health Apps Gain Popularity During Pandemic",
        slug="mental-health-apps-gain-popularity-pandemic",
        summary="Digital mental health solutions have seen unprecedented growth as people seek accessible mental health support.",
        image="https://images.unsplash.com/photo-1512438248247-f0f2a5a8b7f0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=500&q=80",
        category="Mental Health",
        created_at=datetime.now(),
    ),
    ArticlePreview(
        id=4,
        title="Study Links Exercise to Better Brain Health",
        slug="study-links-exercise-better-brain-health",
        summary="New research demonstrates the powerful connection between physical activity and cognitive function.",
        image="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=500&q=80",
        category="Research",
        created_at=datetime.now(),
    ),
]

@router.get("/news/latest", response_model=List[ArticlePreview])
async def get_latest_news():
    """
    Retrieve the latest news articles
    """
    try:
        # Try to fetch from CMS API
        news = await fetch_from_cms("pages/?type=news.NewsPage&fields=title, subtitle, summary, body, publish_date, featured, image, category&order=-first_published_at")
        return news
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, use mock data for now
            logger.warning("CMS unavailable, returning mock latest news")
            return mock_news
        raise
    except Exception as exc:
        # For development, return mock data
        if os.getenv("ENV", "development") == "development":
            logger.info("Using mock data for latest news")
            return mock_news

        logger.error(f"Error fetching latest news: {exc}")
        return []

@router.get("/news/paths", response_model=List[str])
async def get_news_paths():
    """
    Get all news slugs for static path generation
    """
    try:
        # Try to fetch from CMS API
        paths = await fetch_from_cms("news/paths")
        return paths
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, log warning and return a few paths
            logger.warning("CMS unavailable, returning limited news paths")
            return [news.slug for news in mock_news]
        raise
    except Exception as exc:
        # For development, return mock paths
        if os.getenv("ENV", "development") == "development":
            logger.info("Using mock data for news paths")
            return [news.slug for news in mock_news]

        logger.error(f"Error fetching news paths: {exc}")
        return []

@router.get("/news/{slug}", response_model=Article)
async def get_news_article(slug: str = Path(..., description="The slug of the news article to retrieve")):
    """
    Get a single news article by its slug
    """
    try:
        # Decode the slug if it's URL-encoded
        from urllib.parse import unquote
        decoded_slug = unquote(slug)
        
        # Try to fetch from CMS API
        article = await fetch_from_cms(f"news/{decoded_slug}")
        return article
    except HTTPException as exc:
        if exc.status_code == 404:
            raise HTTPException(status_code=404, detail=f"News article with slug '{slug}' not found")
        elif exc.status_code == 503:
            # If CMS is unavailable, check if we have this article in our mock data
            logger.warning(f"CMS unavailable, trying to serve mock news article {slug}")
            for news in mock_news:
                if news.slug == slug:
                    # Convert to a full Article with content
                    return Article(
                        id=news.id,
                        title=news.title,
                        slug=news.slug,
                        summary=news.summary,
                        subtitle=news.summary,
                        image=news.image,
                        content=f"<p>This is the full content of the news article about {news.title}.</p><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin euismod, nunc nec aliquam lacinia, nisl nisl aliquam nisl, eget aliquam nisl nisl sit amet nisl.</p>",
                        author={
                            "name": "Health News Team",
                            "credentials": "Editorial Staff",
                            "bio": "Our editorial team provides the latest health news and updates.",
                        },
                        published_date=news.created_at,
                        updated_date=None,
                        tags=["Health News", "Breaking"],
                    )

            # If not found in mock data, return 404
            raise HTTPException(status_code=404, detail=f"News article with slug '{slug}' not found")
        raise
    except Exception as exc:
        # For development, return mock data
        if os.getenv("ENV", "development") == "development":
            logger.info(f"Using mock data for news article {slug}")
            for news in mock_news:
                if news.slug == slug:
                    # Convert to a full Article with content
                    return Article(
                        id=news.id,
                        title=news.title,
                        slug=news.slug,
                        summary=news.summary,
                        subtitle=news.summary,
                        image=news.image,
                        content=f"<p>This is the full content of the news article about {news.title}.</p><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin euismod, nunc nec aliquam lacinia, nisl nisl aliquam nisl, eget aliquam nisl nisl sit amet nisl.</p>",
                        author={
                            "name": "Health News Team",
                            "credentials": "Editorial Staff",
                            "bio": "Our editorial team provides the latest health news and updates.",
                        },
                        published_date=news.created_at,
                        updated_date=None,
                        tags=["Health News", "Breaking"],
                    )

            raise HTTPException(status_code=404, detail=f"News article with slug '{slug}' not found")

        logger.error(f"Error fetching news article {slug}: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve news article: {str(exc)}")
@router.get("/news/{slug}/related", response_model=List[ArticlePreview])
async def get_related_news(slug: str = Path(..., description="The slug of the article")):
    """
    Get articles related to the specified article
    """
    try:
        # Try to fetch from CMS API
        news = await fetch_from_cms(f"news/{slug}/related")
        return news
    except HTTPException as exc:
        if exc.status_code == 404:
            # If the article doesn't exist, return empty list
            return []
        if exc.status_code == 503:
            # If CMS is unavailable, use mock data
            logger.warning("CMS unavailable, returning mock related articles")
            # Exclude the current article
            return [news.slug for news in mock_news if news.slug != slug][:3]
        raise
    except Exception as exc:
        # For development, return mock data
        if os.getenv("ENV", "development") == "development":
            logger.info(f"Using mock data for related articles to {slug}")
            # Exclude the current article
            return [news.slug for news in mock_news if news.slug != slug][:3]

        logger.error(f"Error fetching related articles for {slug}: {exc}")
        return []

async def search_news(query: str):
    """
    Search news articles by query string
    """
    try:
        # Try to fetch from CMS API
        news = await fetch_from_cms("news/search", {"q": query})
        return news
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, use mock search results
            logger.warning("CMS unavailable, returning mock news search results")
            return [
                news for news in mock_news 
                if query.lower() in news.title.lower() or 
                   (news.summary and query.lower() in news.summary.lower())
            ]
        raise
    except Exception as exc:
        # For development, return filtered mock data
        if os.getenv("ENV", "development") == "development":
            logger.info(f"Using mock data for news search: {query}")
            return [
                news for news in mock_news 
                if query.lower() in news.title.lower() or 
                   (news.summary and query.lower() in news.summary.lower())
            ]

        logger.error(f"Error searching news: {exc}")
        return []
