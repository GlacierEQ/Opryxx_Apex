"""Main FastAPI application factory."""
import os
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

# Import routers
from .health import router as health_router
from .middleware.security import setup_security_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup code
    logger.info("Starting OPRYXX AI Workbench API...")
    
    # TODO: Initialize database connections, AI models, etc.
    
    yield  # The application runs here
    
    # Shutdown code
    logger.info("Shutting down OPRYXX AI Workbench API...")
    # TODO: Clean up resources

def create_app(
    config: Optional[Dict[str, Any]] = None,
    test_config: Optional[Dict[str, Any]] = None,
) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        config: Application configuration
        test_config: Test-specific configuration (overrides config)
        
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # Merge configs with test_config taking precedence
    app_config = {**(config or {}), **(test_config or {})}
    
    # Create FastAPI app with metadata
    app = FastAPI(
        title="OPRYXX AI Workbench API",
        description="High-performance AI model serving and management platform",
        version=os.getenv("APP_VERSION", "0.1.0"),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # Setup security middleware
    setup_security_middleware(app)
    
    # Add exception handlers
    add_exception_handlers(app)
    
    # Include routers
    app.include_router(health_router, prefix="/api")
    
    # Add a simple root endpoint
    @app.get("/")
    async def root() -> Dict[str, str]:
        return {
            "name": "OPRYXX AI Workbench",
            "version": app.version,
            "status": "operational",
            "docs": "/docs",
        }
    
    return app

def add_exception_handlers(app: FastAPI) -> None:
    """Add global exception handlers to the FastAPI app."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exc.errors(),
                "body": exc.body,
            },
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle all other exceptions."""
        logger.error(
            f"Unhandled exception: {str(exc)}",
            exc_info=True,
            extra={"path": request.url.path, "method": request.method},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

# For development with uvicorn
if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
    )
