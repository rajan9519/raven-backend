from openai import OpenAI
import re
import json
from typing import Dict, List
from config import Config
from constants import QUERY_ANALYSIS_SYSTEM_PROMPT, RESULT_SELECTION_SYSTEM_PROMPT, QUERY_ANALYSIS_SCHEMA, RESULT_SELECTION_SCHEMA

class QueryProcessor:
    """Processes natural language queries and determines search intent"""
    
    def __init__(self, config: Config):
        self.config = config
        if config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        else:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    def analyze_query(self, query: str) -> Dict:
        """Analyze query intent and extract key information"""
        
        # Define JSON schema for structured output
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": QUERY_ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Query: {query}"}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "query_analysis",
                        "schema": QUERY_ANALYSIS_SCHEMA,
                        "strict": True
                    }
                }
            )
            
            result_text = response.choices[0].message.content.strip()
            return json.loads(result_text)
                    
        except Exception as e:
            print(f"Error analyzing query with GPT: {e}")
            # Fallback analysis
            return self._fallback_analysis(query)
    
    def _fallback_analysis(self, query: str) -> Dict:
        """Simple fallback analysis if GPT fails"""
        query_lower = query.lower()
        
        # Determine content type
        content_type = "any"
        if any(word in query_lower for word in ["table", "comparison", "factors", "values"]):
            content_type = "table"
        elif any(word in query_lower for word in ["figure", "diagram", "drawing", "shows", "image"]):
            content_type = "figure"
        
        # Extract keywords (simple approach)
        keywords = re.findall(r'\b\w{3,}\b', query_lower)
        keywords = [k for k in keywords if k not in ["the", "and", "for", "can", "you", "show", "need"]]
        
        return {
            "search_terms": keywords[:10],  # Limit keywords
            "content_type": content_type,
            "intent": f"User looking for content related to: {', '.join(keywords[:3])}" if keywords else "General search query",
            "confidence": 0.5
        }
    
    def enhance_query(self, original_query: str, analysis: Dict) -> str:
        """Enhance the original query based on analysis"""
        enhanced_terms = []
        
        # Add original query
        enhanced_terms.append(original_query)
        
        # Add keywords if they're not already in the query
        for keyword in analysis.get("search_terms", []):
            if keyword.lower() not in original_query.lower():
                enhanced_terms.append(keyword)
        
        # Add content type context
        content_type = analysis.get("content_type", "")
        if content_type and content_type != "any":
            enhanced_terms.append(content_type)
        
        return " ".join(enhanced_terms)
    
    def determine_search_strategy(self, analysis: Dict) -> Dict:
        """Determine optimal search strategy based on query analysis"""
        
        confidence = analysis.get("confidence", 0.5)
        content_type = analysis.get("content_type", "any")
        search_terms = analysis.get("search_terms", [])
        intent = analysis.get("intent", "")
        
        # Adjust weights based on analysis
        semantic_weight = 0.5
        keyword_weight = 0.5
        
        # If we have specific search terms, boost keyword search
        if search_terms and len(search_terms) > 0:
            keyword_weight = 0.6
            semantic_weight = 0.4
        else:
            keyword_weight = 0.7
            semantic_weight = 0.3
        
        # If low confidence, rely more on semantic search
        if confidence < 0.6:
            semantic_weight = 0.8
            keyword_weight = 0.2
        return {
            "semantic_weight": semantic_weight,
            "keyword_weight": keyword_weight,
            "max_results": 5,
            "content_type_filter": content_type if content_type != "any" else None,
            "search_terms": search_terms,
            "intent": intent
        }
    
    def select_best_result_with_llm(self, query: str, search_results: List) -> Dict:
        """Use LLM to select the best result from search results based on user query"""
        
        if not search_results:
            return {
                "status": "insufficient_info",
                "selected_index": None,
                "reasoning": "No results to evaluate",
                "confidence": 0.0
            }
        
        # Prepare simple result list for LLM (only essential info)
        results_for_llm = []
        for i, result in enumerate(search_results):
            content_item = result.content_item
            results_for_llm.append({
                "index": i,
                "id": content_item.id,
                "type": content_item.content_type,
                "title": content_item.title or "N/A"
            })
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": RESULT_SELECTION_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Query: {query}\nResults: {json.dumps(results_for_llm)}"}
                ],
                temperature=0.1,
                max_tokens=100,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "result_selection",
                        "schema": RESULT_SELECTION_SCHEMA,
                        "strict": True
                    }
                }
            )
            
            result_text = response.choices[0].message.content.strip()
            llm_result = json.loads(result_text)
            
            # Process LLM response and determine final status
            selected_index = llm_result.get("selected_index")
            confidence = llm_result.get("confidence", 0.5)
            
            if selected_index is None or confidence < 0.4:
                return {
                    "status": "insufficient_info",
                    "selected_index": None,
                    "reasoning": "LLM found no confident match",
                    "confidence": confidence
                }
            elif confidence >= 0.8:
                return {
                    "status": "success", 
                    "selected_index": selected_index,
                    "reasoning": "LLM found a strong match",
                    "confidence": confidence
                }
            else:
                # Medium confidence - check if there are other similar results
                alternatives = [i for i in range(len(search_results)) if i != selected_index and i < 3]
                return {
                    "status": "multiple_candidates" if alternatives else "success",
                    "selected_index": selected_index,
                    "alternative_indices": alternatives,
                    "reasoning": "LLM found a good match with alternatives available" if alternatives else "LLM found a good match",
                    "confidence": confidence
                }
                    
        except Exception as e:
            print(f"Error selecting best result with LLM: {e}")
            # Fallback to simple selection
            return self._fallback_result_selection(search_results)
    
    def _fallback_result_selection(self, search_results: List) -> Dict:
        """Fallback result selection if LLM fails"""
        return {
            "status": "success",
            "selected_index": 0,
            "reasoning": "LLM failed, using top result",
            "confidence": 0.3
        }
