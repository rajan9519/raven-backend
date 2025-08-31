#!/usr/bin/env python3
"""
Sample script to demonstrate the table/image search service functionality
"""

import os
import json
import atexit
from models import SearchQuery
from service import TableImageSearchService  
from config import Config

# Set environment variables to reduce multiprocessing issues
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1" 
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def run_sample_queries():
    """Run sample queries and generate output for demonstration"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: Please set OPENAI_API_KEY environment variable")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Initialize service
    print("Initializing Table & Image Search Service...")
    config = Config()
    service = TableImageSearchService(config)
    
    try:
        try:
            service.initialize()
            print("✅ Service initialized successfully\n")
        except Exception as e:
            print(f"❌ Failed to initialize service: {e}")
            return
    
        # Sample queries from the assignment
        sample_queries = [
            "Can you pull up the comparison of actuator types?",
            "Show me the sizing factors for liquids.",
            "I need the noise level reference values.", 
            "Do we have a figure that explains cavitation?",
            "Show me the overall oil & gas value chain diagram."
        ]
        
        print("=" * 80)
        print("SAMPLE QUERY RESULTS")
        print("=" * 80)
        
        all_results = {}
        
        for i, query_text in enumerate(sample_queries, 1):
            print(f"\n🔍 QUERY {i}: {query_text}")
            print("-" * 60)
            
            try:
                # Create search query
                query = SearchQuery(query=query_text, max_results=3)
                
                # Execute search
                result = service.search(query)
                
                # Display results
                print(f"Status: {result.status}")
                print(f"Total Found: {result.total_found}")
                if result.message:
                    print(f"Message: {result.message}")
                
                print(f"\nTop Results:")
                
                if result.results:
                    for j, search_result in enumerate(result.results, 1):
                        item = search_result.content_item
                        print(f"\n  {j}. {item.content_type.upper()}: {item.title or item.id}")
                        print(f"     Page: {item.citation.page_no}")
                        print(f"     Relevance Score: {search_result.relevance_score:.3f}")
                        print(f"     Match Type: {search_result.match_type}")
                        print(f"     Bounding Box: ({item.citation.bounding_box.top_left_x}, {item.citation.bounding_box.top_left_y}) "
                            f"{item.citation.bounding_box.width}x{item.citation.bounding_box.height}")
                        
                        # Show snippet of content
                        content_snippet = item.content[:200] + "..." if len(item.content) > 200 else item.content
                        print(f"     Content: {content_snippet}")
                else:
                    print("     No results found")
                
                # Store results for JSON output
                all_results[query_text] = {
                    "status": result.status,
                    "message": result.message,
                    "total_found": result.total_found,
                    "results": [
                        {
                            "id": r.content_item.id,
                            "content_type": r.content_item.content_type,
                            "title": r.content_item.title,
                            "page_no": r.content_item.citation.page_no,
                            "bounding_box": {
                                "top_left_x": r.content_item.citation.bounding_box.top_left_x,
                                "top_left_y": r.content_item.citation.bounding_box.top_left_y,
                                "width": r.content_item.citation.bounding_box.width,
                                "height": r.content_item.citation.bounding_box.height
                            },
                            "relevance_score": r.relevance_score,
                            "match_type": r.match_type,
                            "content_snippet": r.content_item.content[:200] + "..." if len(r.content_item.content) > 200 else r.content_item.content
                        }
                        for r in result.results
                    ]
                }
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                all_results[query_text] = {"error": str(e)}
        
            # Save results to JSON file
            output_file = "sample_query_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Results saved to: {output_file}")
            
            # Display service statistics
            stats = service.get_content_statistics()
            print(f"\n📊 SERVICE STATISTICS")
            print("-" * 30)
            print(f"Total Content Items: {stats['total_items']}")
            print(f"Figures: {stats['figures']}")  
            print(f"Tables: {stats['tables']}")
            print(f"Text Blocks: {stats['text_blocks']}")
            print(f"Service Initialized: {stats['initialized']}")
            
            print("\n✅ Sample query execution completed!")

    
    finally:
        # Explicit cleanup
        print("\n🧹 Cleaning up resources...")
        try:
            service.cleanup()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
        
        # Force garbage collection
        import gc
        gc.collect()
        
        print("Cleanup completed.")

if __name__ == "__main__":
    run_sample_queries()
