from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

class ContentType(str, Enum):
    TABLE = "table"
    FIGURE = "figure"
    TEXT = "text"

class BoundingBox(BaseModel):
    top_left_x: int
    top_left_y: int  
    width: int
    height: int

class Citation(BaseModel):
    page_no: int
    bounding_box: BoundingBox
    confidence: Optional[float] = None

class ContentItem(BaseModel):
    id: str
    content_type: ContentType
    title: Optional[str] = None
    content: str
    citation: Citation
    metadata: Dict[str, Any] = {}
    image_url: Optional[str] = None

class SearchQuery(BaseModel):
    query: str = Field(..., description="Natural language query from operator")
    max_results: Optional[int] = Field(10, description="Maximum number of results to return")

class SearchResult(BaseModel):
    content_item: ContentItem
    relevance_score: float
    match_type: str = Field(description="semantic, keyword, or hybrid")

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult] = []
    status: str = Field(default="success", description="success, no_matches, or insufficient_info")
    message: Optional[str] = None
    total_found: int = 0

class LLMSearchQuery(BaseModel):
    query: str = Field(..., description="Natural language query from operator for LLM-enhanced search")
    max_results: Optional[int] = Field(10, description="Maximum number of results to consider for LLM selection")

class LLMSearchResponse(BaseModel):
    query: str
    selected_result: Optional[SearchResult] = None
    alternative_candidates: List[SearchResult] = []
    status: str = Field(default="success", description="success, insufficient_info, or multiple_candidates")
    message: Optional[str] = None
    llm_reasoning: Optional[str] = None
    confidence_score: Optional[float] = None
