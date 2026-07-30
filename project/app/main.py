"""
Main FastAPI Application
Document Understanding API with OCR, Indexing, and RAG capabilities.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings, setup_directories
from app.models import HealthResponse
from app.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    setup_directories()
    logger.success("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    Document Understanding API with AI-powered OCR, indexing, and question answering.
    
    ## Features
    
    * **Extract**: OCR processing for PDF and images (DeepSeek-OCR)
    * **Index**: Document chunking and vector database indexing (ChromaDB)
    * **Chat**: AI-powered question answering with RAG (Qwen/Gemini)
    
    ## Workflow
    
    1. **Extract** documents using `/api/v1/extract` endpoint
    2. **Index** documents into vector database using `/api/v1/index` endpoint
    3. **Chat** to ask questions about your documents using `/api/v1/chat` endpoint
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root() -> HealthResponse:
    """Root endpoint - API health check."""
    return HealthResponse(status="healthy", version=settings.APP_VERSION, message=f"{settings.APP_NAME} is running")


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version=settings.APP_VERSION, message="API is operational")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=1201,
        reload=settings.DEBUG,
    )
