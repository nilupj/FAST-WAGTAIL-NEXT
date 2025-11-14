from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import os
from fastapi import APIRouter
import logging
from fastapi_socketio import SocketManager
from typing import Dict, Any
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from routers import articles, conditions, symptoms, drugs, news  # Make sure to import news router
from models import ErrorResponse

router = APIRouter()

@router.get("/articles/{slug}")
async def redirect_article(slug: str):
    """Redirect /articles requests to /news"""
    return RedirectResponse(url=f"/news/{slug}", status_code=301)
# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(),
    ],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HealthInfo API",
    description="API for the HealthInfo medical information website",
    version="1.0.0",
)

# Add CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Use the configured origins instead of "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Socket.IO
socket_manager = SocketManager(app=app, cors_allowed_origins="*")

@socket_manager.on('message')
async def handle_message(sid: str, message: Dict[str, Any]):
    await socket_manager.emit('message', message)



# Include routers
app.include_router(articles.router, prefix="/api", tags=["Articles"])
app.include_router(news.router, prefix="/api", tags=["News"])  # Make sure news router is included
app.include_router(conditions.router, prefix="/api", tags=["Conditions"])
app.include_router(symptoms.router, prefix="/api", tags=["Symptoms"])
app.include_router(drugs.router, prefix="/api", tags=["Drugs"])

# Exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="An unexpected error occurred. Please try again later.",
            details=str(exc) if os.getenv("ENV", "production") != "production" else None
        ).dict(),
    )

@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for the API
    """
    return {"status": "healthy"}

@app.get("/api/search", tags=["Search"])
async def search(q: str = ""):
    """
    Search articles, conditions, and drugs
    """
    if not q or len(q.strip()) < 2:
        return {
            "articles": [],
            "conditions": [],
            "drugs": [],
            "news": []  # Add news to search results
        }
    
    # Call individual search endpoints
    articles_results = await articles.search_articles(q)
    conditions_results = await conditions.search_conditions(q)
    news_results = await news.search_news(q)  # Add news search
    
    return {
        "articles": articles_results,
        "conditions": conditions_results,
        "drugs": [],  # Keep as empty array until implemented
        "news": news_results
    }

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENV", "production") != "production",
        log_level="info"
    )