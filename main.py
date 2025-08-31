from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict, Any
from contextlib import asynccontextmanager

from models import SearchQuery, SearchResponse, LLMSearchQuery, LLMSearchResponse
from service import TableImageSearchService
from config import Config

# Initialize configuration
config = Config()

# Initialize service
service = TableImageSearchService(config)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        print("Starting up Table & Image Search API...")
        service.initialize()
        print("Service initialization completed successfully")
    except Exception as e:
        print(f"Failed to initialize service: {e}")
        raise e
    
    yield
    
    # Shutdown (if needed)
    print("Shutting down Table & Image Search API...")

# Initialize FastAPI app
app = FastAPI(
    title="Table & Image Search API",
    description="Backend service for locating and extracting tables/images from technical manuals",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with basic API information"""
    return {
        "message": "Table & Image Search API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "search": "/search",
            "llm_search": "/llm-search",
            "statistics": "/statistics",
            "health": "/health"
        }
    }

@app.post("/search", response_model=SearchResponse)
async def search(query: SearchQuery) -> SearchResponse:
    """
    Search for tables and images based on natural language query
    
    - **query**: Natural language query (e.g., "Show me the actuator types comparison")
    - **max_results**: Maximum number of results to return (optional, default: 10)
    
    Returns search results with content items and citation information.
    """
    try:
        if not query.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        result = service.search(query)
        return result
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/llm-search", response_model=LLMSearchResponse)
async def llm_search(query: LLMSearchQuery) -> LLMSearchResponse:
    """
    LLM-enhanced search for tables and images with intelligent result selection
    
    This endpoint first searches for relevant content, then uses an LLM to intelligently
    select the most appropriate result based on the user's specific query.
    
    - **query**: Natural language query (e.g., "Show me the actuator types comparison")
    - **max_results**: Maximum number of initial results to consider for LLM selection (default: 10)
    
    Returns:
    - **selected_result**: The best match as determined by the LLM
    - **alternative_candidates**: Other potentially relevant results (for multiple_candidates status)
    - **status**: "success", "multiple_candidates", or "insufficient_info"
    - **llm_reasoning**: Explanation of why the LLM selected this result
    - **confidence_score**: LLM's confidence in the selection (0.0-1.0)
    """
    try:
        if not query.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        result = service.llm_search(query)
        return result
        
    except Exception as e:
        print(f"LLM Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/statistics")
async def get_statistics() -> Dict[str, Any]:
    """
    Get statistics about the indexed content
    
    Returns information about available tables, figures, and text blocks.
    """
    try:
        stats = service.get_content_statistics()
        return {
            "content_statistics": stats,
            "service_status": "initialized" if service.initialized else "not_initialized"
        }
    except Exception as e:
        print(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service_initialized": str(service.initialized),
        "openai_configured": "yes" if config.OPENAI_API_KEY else "no"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    # Check for required environment variables
    if not config.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is required")
        exit(1)
    
    print(f"Starting server on {config.HOST}:{config.PORT}")
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )
