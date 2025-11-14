from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
import httpx
import os
import logging
from datetime import datetime

from models import ConditionPreview, Condition, ErrorResponse

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
mock_conditions = [
    ConditionPreview(
        id=1,
        name="Type 2 Diabetes",
        slug="type-2-diabetes",
        subtitle="A chronic condition that affects how your body metabolizes sugar (glucose).",
    ),
    ConditionPreview(
        id=2,
        name="Hypertension",
        slug="hypertension",
        subtitle="High blood pressure is a common condition that affects the body's arteries.",
    ),
    ConditionPreview(
        id=3,
        name="Asthma",
        slug="asthma",
        subtitle="A condition in which your airways narrow and swell and may produce extra mucus.",
    ),
    ConditionPreview(
        id=4,
        name="Migraine",
        slug="migraine",
        subtitle="A headache of varying intensity, often accompanied by nausea and sensitivity to light and sound.",
    ),
]

@router.get("/conditions/index", response_model=List[ConditionPreview])
async def get_conditions_index():
    """
    Retrieve a complete index of all health conditions
    """
    try:
        # Try to fetch from CMS API
        conditions = await fetch_from_cms("api/conditions-index")
        return conditions
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, use mock data
            logger.warning("CMS unavailable, returning mock conditions index")
            return mock_conditions
        raise
    except Exception as exc:
        # For development, return mock data
        if os.getenv("ENV", "development") == "development":
            logger.info("Using mock data for conditions index")
            return mock_conditions
        
        logger.error(f"Error fetching conditions index: {exc}")
        return []

@router.get("/conditions/paths", response_model=List[str])
async def get_condition_paths():
    """
    Get all condition slugs for static path generation
    """
    try:
        # Try to fetch from CMS API
        paths = await fetch_from_cms("conditions/paths")
        return paths
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, log warning and return a few paths
            logger.warning("CMS unavailable, returning limited condition paths")
            return ["type-2-diabetes", "hypertension", "asthma", "migraine"]
        raise
    except Exception as exc:
        # For development, return mock paths
        if os.getenv("ENV", "development") == "development":
            logger.info("Using mock data for condition paths")
            return [condition.slug for condition in mock_conditions]
        
        logger.error(f"Error fetching condition paths: {exc}")
        return []

@router.get("/conditions/{slug}", response_model=Condition)
async def get_condition(slug: str = Path(..., description="The slug of the condition to retrieve")):
    """
    Get a single condition by its slug
    """
    try:
        # Try to fetch from CMS API
        condition = await fetch_from_cms(f"conditions/{slug}")
        return condition
    except HTTPException as exc:
        if exc.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Condition with slug '{slug}' not found")
        elif exc.status_code == 503:
            # If CMS is unavailable, check for mock data
            logger.warning(f"CMS unavailable, trying to serve mock condition {slug}")
            for condition in mock_conditions:
                if condition.slug == slug:
                    # Convert to a full Condition with content
                    return Condition(
                        id=condition.id,
                        name=condition.name,
                        slug=condition.slug,
                        subtitle=condition.subtitle,
                        overview="<p>This is an overview of the condition.</p>",
                        symptoms="<p>Common symptoms include...</p>",
                        causes="<p>This condition is usually caused by...</p>",
                        diagnosis="<p>Diagnosis typically involves...</p>",
                        treatments="<p>Treatment options include...</p>",
                        prevention="<p>To reduce your risk, consider...</p>",
                        complications="<p>If left untreated, complications may include...</p>",
                        image="https://images.unsplash.com/photo-1576091160550-2173dba999ef?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&h=600&q=80",
                        related_conditions=[
                            {"name": rc.name, "slug": rc.slug} 
                            for rc in mock_conditions if rc.id != condition.id
                        ][:2],
                    )
            # If not found, return 404
            raise HTTPException(status_code=404, detail=f"Condition with slug '{slug}' not found")
        raise
    except Exception as exc:
        # For development, return mock data
        if os.getenv("ENV", "development") == "development":
            logger.info(f"Using mock data for condition {slug}")
            for condition in mock_conditions:
                if condition.slug == slug:
                    # Convert to a full Condition with content
                    return Condition(
                        id=condition.id,
                        name=condition.name,
                        slug=condition.slug,
                        subtitle=condition.subtitle,
                        overview="<p>This is an overview of the condition.</p>",
                        symptoms="<p>Common symptoms include...</p>",
                        causes="<p>This condition is usually caused by...</p>",
                        diagnosis="<p>Diagnosis typically involves...</p>",
                        treatments="<p>Treatment options include...</p>",
                        prevention="<p>To reduce your risk, consider...</p>",
                        complications="<p>If left untreated, complications may include...</p>",
                        image="https://images.unsplash.com/photo-1576091160550-2173dba999ef?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&h=600&q=80",
                        related_conditions=[
                            {"name": rc.name, "slug": rc.slug} 
                            for rc in mock_conditions if rc.id != condition.id
                        ][:2],
                    )
            
            raise HTTPException(status_code=404, detail=f"Condition with slug '{slug}' not found")
        
        logger.error(f"Error fetching condition {slug}: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve condition: {str(exc)}")

async def search_conditions(query: str):
    """
    Search conditions by query string
    """
    try:
        # Try to fetch from CMS API
        conditions = await fetch_from_cms("conditions/search", {"q": query})
        return conditions
    except HTTPException as exc:
        if exc.status_code == 503:
            # If CMS is unavailable, use mock data
            logger.warning("CMS unavailable, returning mock search results")
            return [
                condition for condition in mock_conditions
                if query.lower() in condition.name.lower() or 
                  (condition.subtitle and query.lower() in condition.subtitle.lower())
            ]
        raise
    except Exception as exc:
        # For development, return filtered mock data
        if os.getenv("ENV", "development") == "development":
            logger.info(f"Using mock data for condition search: {query}")
            return [
                condition for condition in mock_conditions
                if query.lower() in condition.name.lower() or 
                  (condition.subtitle and query.lower() in condition.subtitle.lower())
            ]
        
        logger.error(f"Error searching conditions: {exc}")
        return []