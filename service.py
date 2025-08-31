import os
import atexit
from typing import List
from models import ContentItem, SearchQuery, SearchResponse, ContentType, LLMSearchQuery, LLMSearchResponse
from data_parser import DataParser
from search_engines import HybridSearchEngine
from query_processor import QueryProcessor
from config import Config

class TableImageSearchService:
    """Main service class for table and image search"""
    
    def __init__(self, config: Config):
        self.config = config
        self.data_parser = DataParser(config)
        self.search_engine = HybridSearchEngine(config)
        self.query_processor = QueryProcessor(config)
        
        self.all_content_items: List[ContentItem] = []
        self.figures: List[ContentItem] = []
        self.tables: List[ContentItem] = []
        self.text_blocks: List[ContentItem] = []
        
        self.initialized = False
        
        # Register cleanup function
        atexit.register(self.cleanup)
    
    def initialize(self):
        """Initialize the service by parsing data and building indices"""
        print("Initializing TableImageSearchService...")
        
        # Check if we can load existing indices
        embedding_exists = os.path.exists(f"{self.config.INDEX_PATH}_embedding.faiss")
        keyword_exists = os.path.exists(f"{self.config.INDEX_PATH}_keyword.pkl")
        
        if embedding_exists and keyword_exists:
            print("Loading existing indices...")
            if self.search_engine.load_indices(self.config.INDEX_PATH):
                # Still need to parse content for filtering
                self._parse_content()
                self.initialized = True
                print("Successfully loaded existing indices")
                return
        
        print("Parsing content and building indices...")
        
        # Parse all content
        self._parse_content()
        
        # Build search indices
        if self.all_content_items:
            self.search_engine.build_index(self.all_content_items)
            
            # Save indices for future use
            self.search_engine.save_indices(self.config.INDEX_PATH)
            print(f"Saved indices to {self.config.INDEX_PATH}")
        else:
            raise ValueError("No content items found during parsing")
        
        self.initialized = True
        print("Service initialization completed")
    
    def _parse_content(self):
        """Parse content from input files"""
        self.figures, self.tables, self.text_blocks = self.data_parser.parse_all_content()
        
        # Combine all content items
        self.all_content_items = self.figures + self.tables
        
        print(f"Parsed content: {len(self.figures)} figures, {len(self.tables)} tables, {len(self.text_blocks)} text blocks")
    
    def search(self, query: SearchQuery) -> SearchResponse:
        """Process search query and return results"""
        if not self.initialized:
            return SearchResponse(
                query=query.query,
                status="error",
                message="Service not initialized"
            )
        
        try:
            # Analyze the query
            analysis = self.query_processor.analyze_query(query.query)
            print(f"Query analysis: {analysis}")
            
            # Determine search strategy
            strategy = self.query_processor.determine_search_strategy(analysis)
            print(f"Search strategy: {strategy}")
            
            # Enhance query for better search
            # enhanced_query = self.query_processor.enhance_query(query.query, analysis)
            
            # Perform hybrid search
            search_results = self.search_engine.search(
                query.query,
                k=min(query.max_results or self.config.MAX_RESULTS, strategy["max_results"]),
                semantic_weight=strategy["semantic_weight"],
                keyword_weight=strategy["keyword_weight"],
                search_terms=strategy["search_terms"]
            )
            
            # Apply content type filtering if specified
            if strategy.get("content_type_filter"):
                content_type = ContentType(strategy["content_type_filter"])
                search_results = [r for r in search_results if r.content_item.content_type == content_type]
            
            # Determine response status
            status = "success"
            message = None
            
            if not search_results:
                status = "insufficient_info"
                message = "No relevant tables or images found for your query"
            elif len(search_results) == 1:
                message = "Found a matching result"
            else:
                message = f"Found {len(search_results)} relevant results"
            
            return SearchResponse(
                query=query.query,
                results=search_results,
                status=status,
                message=message,
                total_found=len(search_results)
            )
            
        except Exception as e:
            print(f"Error processing search: {e}")
            return SearchResponse(
                query=query.query,
                status="error",
                message=f"An error occurred while processing your query: {str(e)}"
            )
    
    def llm_search(self, query: LLMSearchQuery) -> LLMSearchResponse:
        """LLM-enhanced search that finds candidates then uses LLM to select the best one"""
        if not self.initialized:
            return LLMSearchResponse(query=query.query, status="error", message="Service not initialized")
        
        try:
            # Get search results
            search_query = SearchQuery(query=query.query, max_results=query.max_results or 10)
            results = self.search(search_query)
            
            # Return insufficient_info if no results
            if not results.results:
                return LLMSearchResponse(
                    query=query.query,
                    status="insufficient_info", 
                    message="No relevant content found",
                    confidence_score=0.0
                )
            
            # Use LLM to select best result
            llm_result = self.query_processor.select_best_result_with_llm(query.query, results.results)
            
            status = llm_result["status"]
            selected_index = llm_result.get("selected_index")
            confidence = llm_result["confidence"]
            reasoning = llm_result["reasoning"]
            
            # Handle insufficient_info
            if status == "insufficient_info":
                return LLMSearchResponse(
                    query=query.query,
                    status="insufficient_info",
                    message="No confident match found",
                    llm_reasoning=reasoning,
                    confidence_score=confidence
                )
            
            # Get selected result and alternatives
            selected_result = results.results[selected_index] if selected_index is not None else None
            alternatives = []
            
            if status == "multiple_candidates":
                # Add top 2 alternatives (excluding selected)
                for i, result in enumerate(results.results[:3]):
                    if i != selected_index:
                        alternatives.append(result)
            
            return LLMSearchResponse(
                query=query.query,
                selected_result=selected_result,
                alternative_candidates=alternatives,
                status=status,
                message="Found match" if status == "success" else f"Found {len(alternatives)+1} candidates",
                llm_reasoning=reasoning,
                confidence_score=confidence
            )
                
        except Exception as e:
            print(f"LLM search error: {e}")
            return LLMSearchResponse(query=query.query, status="error", message=str(e))

    def get_content_statistics(self) -> dict:
        """Get statistics about available content"""
        return {
            "total_items": len(self.all_content_items),
            "figures": len(self.figures),
            "tables": len(self.tables),
            "text_blocks": len(self.text_blocks),
            "initialized": self.initialized
        }
    
    def cleanup(self):
        """Clean up service resources"""
        try:
            if hasattr(self, 'search_engine') and self.search_engine is not None:
                self.search_engine.cleanup()
                
            # Force garbage collection
            import gc
            gc.collect()
        except Exception as e:
            # Silently handle cleanup errors
            pass
