"""
CareMatrix Backend - Predictive Hospital Flow & Patient Optimization System
FastAPI Application Entry Point

This is a production-ready backend for managing hospital patient flows,
resource allocation, and predictive analytics.

Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Import database and routers
from database import init_db
from routers import patients_router, admissions_router, hospitals_router, analytics_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for application startup and shutdown
    """
    # ==================== STARTUP ====================
    logger.info("🚀 Starting CareMatrix Backend Server...")
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # ==================== SHUTDOWN ====================
    logger.info("🛑 Shutting down CareMatrix Backend Server...")


# Create FastAPI application
app = FastAPI(
    title="CareMatrix API",
    description="Predictive Hospital Flow & Patient Optimization System Backend",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# ==================== CORS CONFIGURATION ====================
# Allow requests from frontend applications
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"✅ CORS enabled for origins: {allowed_origins}")


# ==================== INCLUDE ROUTERS ====================
app.include_router(patients_router, prefix="/api/v1")
app.include_router(admissions_router, prefix="/api/v1")
app.include_router(hospitals_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")

logger.info("✅ All routers registered")


# ==================== HEALTH CHECK ENDPOINTS ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "CareMatrix API",
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Welcome to CareMatrix API",
        "description": "Predictive Hospital Flow & Patient Optimization System",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "api_base": "/api/v1"
    }


# ==================== ERROR HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return {
        "detail": "Internal server error",
        "status_code": 500
    }


# ==================== EVENT LOGGING ====================

@app.middleware("http")
async def log_requests(request, call_next):
    """
    Middleware to log all requests
    """
    logger.info(f"📨 {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"📤 Response: {response.status_code}")
    return response


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    logger.info(f"🌐 Starting server on {HOST}:{PORT}")
    
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info"
    )
