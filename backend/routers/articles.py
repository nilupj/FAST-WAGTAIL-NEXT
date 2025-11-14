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

# Mock data for development (will be replaced with actual CMS API calls)
mock_articles = [
    ArticlePreview(
        id=1,
        title="Effective Ways To Reduce Bloating",
        slug="reduce-bloating",
        summary="The uncomfortable bloating after meals can be caused by food, eating habits, or conditions like IBS. Learn how to reduce bloating and improve your comfort.",
        image="https://images.unsplash.com/photo-1559757175-7b21671c7e96?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=500&q=80",
        category="Digestive Health",
        created_at=datetime.now(),
    ),
    ArticlePreview(
        id=2,
        title="The Key Health Benefits of Pistachios",
        slug="health-benefits-pistachios",
        summary="Discover how these small nuts pack a powerful nutritional punch and contribute to overall health.",
        image="https://images.unsplash.com/photo-1606923829579-0cb981a271d4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=500&q=80",
        category="Nutrition",
        created_at=datetime.now(),
    ),
    ArticlePreview(
        id=3,
        title="How Alcohol Affects Your Skin",
        slug="alcohol-affects-skin",
        summary="Learn about the impact of alcohol consumption on your skin health and appearance.",
        image="https://images.unsplash.com/photo-1590439471364-192aa70c0b53?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=500&q=80",
        category="Skincare",
        created_at=datetime.now(),
    ),
    ArticlePreview(
        id=4,
        title="What Causes Cracked Heels?",
        slug="causes-cracked-heels",
        summary="Understanding the causes, prevention, and treatment options for cracked heels.",
        image="https://images.unsplash.com/photo-1519415943484-9fa1873496d4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=500&q=80",
        category="Foot Health",
        created_at=datetime.now(),
    ),
]

@router.get("/articles/top-stories", response_model=List[ArticlePreview])
async def get_top_stories():
    """
    Retrieve the top stories/featured articles
    """
    try:
        # Try to fetch from CMS API
        articles = await fetch_from_cms("pages/?type=news.NewsPage&fields=title,subtitle,summary,body,publish_date,featured,image,category&order=-first_published_at")
        return articles
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, use mock data for now
            logger.warning("CMS unavailable, returning mock top stories")
            return mock_articles
        raise
    except Exception as exc:
        # For development, return mock data
        if os.getenv("ENV", "development") == "development":
            logger.info("Using mock data for top stories")
            return mock_articles

        logger.error(f"Error fetching top stories: {exc}")
        return []

@router.get("/articles/health-topics", response_model=List[ArticlePreview])
async def get_health_topics():
    """
    Retrieve articles categorized as health topics
    """
    try:
        # Try to fetch from CMS API
        articles = await fetch_from_cms("articles/health-topics")
        return articles
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, use mock data for now
            logger.warning("CMS unavailable, returning mock health topics")
            return mock_articles[:2]
        raise
    except Exception as exc:
        # For development, return mock data
        if os.getenv("ENV", "development") == "development":
            logger.info("Using mock data for health topics")
            return mock_articles[:2]

        logger.error(f"Error fetching health topics: {exc}")
        return []

@router.get("/articles/paths", response_model=List[str])
async def get_article_paths():
    """
    Get all article slugs for static path generation
    """
    try:
        # Try to fetch from CMS API
        paths = await fetch_from_cms("articles/paths")
        return paths
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, log warning and return a few paths
            logger.warning("CMS unavailable, returning limited article paths")
            return ["reduce-bloating", "health-benefits-pistachios", "alcohol-affects-skin"]
        raise
    except Exception as exc:
        # For development, return mock paths
        if os.getenv("ENV", "development") == "development":
            logger.info("Using mock data for article paths")
            return [article.slug for article in mock_articles]

        logger.error(f"Error fetching article paths: {exc}")
        return []

@router.get("/articles/{slug}", response_model=Article)
async def get_article(slug: str = Path(..., description="The slug of the article to retrieve")):
    """
    Get a single article by its slug
    """
    try:
        # Try to fetch from CMS API
        article = await fetch_from_cms(f"articles/{slug}")
        return article
    except HTTPException as exc:
        if exc.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Article with slug '{slug}' not found")
        elif exc.status_code == 503:
            # If CMS is unavailable, check if we have this article in our mock data
            logger.warning(f"CMS unavailable, trying to serve mock article {slug}")
            for article in mock_articles:
                if article.slug == slug:
                    # Convert to a full Article with content
                    return Article(
                        id=article.id,
                        title=article.title,
                        slug=article.slug,
                        summary=article.summary,
                        subtitle=article.summary,
                        image=article.image,
                        content=f"<p>This is the full content of the article about {article.title}.</p><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin euismod, nunc nec aliquam lacinia, nisl nisl aliquam nisl, eget aliquam nisl nisl sit amet nisl.</p>",
                        author={
                            "name": "Dr. Jane Smith",
                            "credentials": "MD, PhD",
                            "bio": "Dr. Smith is a specialist in internal medicine with over 15 years of experience.",
                        },
                        published_date=article.created_at,
                        updated_date=None,
                        tags=["Health", "Wellness"],
                    )

            # If not found in mock data, return 404
            raise HTTPException(status_code=404, detail=f"Article with slug '{slug}' not found")
        raise
    except Exception as exc:
        # For development, return mock data
        if os.getenv("ENV", "development") == "development":
            logger.info(f"Using mock data for article {slug}")
            for article in mock_articles:
                if article.slug == slug:
                    # Convert to a full Article with content
                    return Article(
                        id=article.id,
                        title=article.title,
                        slug=article.slug,
                        summary=article.summary,
                        subtitle=article.summary,
                        image=article.image,
                        content=f"<p>This is the full content of the article about {article.title}.</p><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin euismod, nunc nec aliquam lacinia, nisl nisl aliquam nisl, eget aliquam nisl nisl sit amet nisl.</p>",
                        author={
                            "name": "Dr. Jane Smith",
                            "credentials": "MD, PhD",
                            "bio": "Dr. Smith is a specialist in internal medicine with over 15 years of experience.",
                        },
                        published_date=article.created_at,
                        updated_date=None,
                        tags=["Health", "Wellness"],
                    )

            raise HTTPException(status_code=404, detail=f"Article with slug '{slug}' not found")

        logger.error(f"Error fetching article {slug}: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve article: {str(exc)}")

@router.get("/articles/{slug}/related", response_model=List[ArticlePreview])
async def get_related_articles(slug: str = Path(..., description="The slug of the article")):
    """
    Get articles related to the specified article
    """
    try:
        # Try to fetch from CMS API
        articles = await fetch_from_cms(f"articles/{slug}/related")
        return articles
    except HTTPException as exc:
        if exc.status_code == 404:
            # If the article doesn't exist, return empty list
            return []
        if exc.status_code == 503:
            # If CMS is unavailable, use mock data
            logger.warning("CMS unavailable, returning mock related articles")
            # Exclude the current article
            return [article for article in mock_articles if article.slug != slug][:3]
        raise
    except Exception as exc:
        # For development, return mock data
        if os.getenv("ENV", "development") == "development":
            logger.info(f"Using mock data for related articles to {slug}")
            # Exclude the current article
            return [article for article in mock_articles if article.slug != slug][:3]

        logger.error(f"Error fetching related articles for {slug}: {exc}")
        return []

@router.get("/well-being", response_model=dict)
async def get_well_being_articles():
    """
    Get articles for the well-being section
    """
    try:
        # Try to fetch from CMS API
        data = await fetch_from_cms("well-being")
        return data
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, use mock data for now
            logger.warning("CMS unavailable, returning mock well-being data")
            return {
                "featured": mock_articles[:3],
                "articles": mock_articles
            }
        raise
    except Exception as exc:
        # For development, return mock data
        if os.getenv("ENV", "development") == "development":
            logger.info("Using mock data for well-being section")
            return {
                "featured": mock_articles[:3],
                "articles": mock_articles
            }

        logger.error(f"Error fetching well-being articles: {exc}")
        return {"featured": [], "articles": []}

async def search_articles(query: str):
    """
    Search articles by query string
    """
    try:
        # Try to fetch from CMS API
        articles = await fetch_from_cms("articles/search", {"q": query})
        return articles
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, use mock search results
            logger.warning("CMS unavailable, returning mock search results")
            return [
                article for article in mock_articles 
                if query.lower() in article.title.lower() or 
                   (article.summary and query.lower() in article.summary.lower())
            ]
        raise
    except Exception as exc:
        # For development, return filtered mock data
        if os.getenv("ENV", "development") == "development":
            logger.info(f"Using mock data for article search: {query}")
            return [
                article for article in mock_articles 
                if query.lower() in article.title.lower() or 
                   (article.summary and query.lower() in article.summary.lower())
            ]

        logger.error(f"Error searching articles: {exc}")
        return []