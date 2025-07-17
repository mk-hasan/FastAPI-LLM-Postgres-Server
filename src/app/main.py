from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import llm as llm_endpoints_v1
from app.api.v1.endpoints import data as data_endpoints_v1 # New import
from app.core.exceptions import LLMProviderError, InvalidLLMProviderError, PromptValidationError
from app.core.config import get_settings
from app.utils.logger import setup_logging
from sqlalchemy.exc import SQLAlchemyError # New import
import logging
from fastapi import FastAPI, Request, status # <--- ADD 'status' here

# Setup logging before initializing FastAPI
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LLM API Service with PostgreSQL",
    description="A production-grade FastAPI service for interacting with various Large Language Models, "
                "with PostgreSQL integration for data storage and LLM response caching.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include API routers
app.include_router(llm_endpoints_v1.router, prefix="/api/v1/llm", tags=["LLM Generation"])
app.include_router(data_endpoints_v1.router, prefix="/api/v1/data", tags=["Data Management"]) # New router

# Global Exception Handlers
@app.exception_handler(LLMProviderError)
async def llm_provider_exception_handler(request: Request, exc: LLMProviderError):
    logger.error(f"LLM Provider Error: {exc.detail} for request URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(InvalidLLMProviderError)
async def invalid_llm_provider_exception_handler(request: Request, exc: InvalidLLMProviderError):
    logger.error(f"Invalid LLM Provider Error: {exc.detail} for request URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(PromptValidationError)
async def prompt_validation_exception_handler(request: Request, exc: PromptValidationError):
    logger.error(f"Prompt Validation Error: {exc.detail} for request URL: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handler for SQLAlchemy specific errors."""
    logger.exception(f"Database error: {exc} for request URL: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "A database error occurred. Please try again later."},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc} for request URL: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected server error occurred. Please try again later."},
    )

# Startup event handler
@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    logger.info("FastAPI application starting up.")
    logger.info(f"Connecting to database: {settings.DATABASE_URL.split('@')[1]}") # Log URL without credentials
    # You might want to add a database connection check here
    try:
        from app.db.database import engine
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connection successful.")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        # Depending on criticality, you might want to exit or raise an error here