QUERY_ANALYSIS_SYSTEM_PROMPT="""You are an expert at extracting search terms from technical queries for a control valve manual search system.

Your task is to analyze the user's natural language query and extract the most relevant keywords and phrases that would help find matching figures and tables in a BM25 keyword search engine. The search engine will match these terms against figure captions, table titles, and content descriptions.

Return a JSON response with:
- search_terms: list of specific keywords and phrases optimized for BM25 search
- content_type: "table", "figure", or "any" based on what the user is looking for
- intent: brief description of what user wants
- confidence: 0-1 score for how clear the query is

Focus on technical terms, specific concepts, and descriptive phrases that would appear in captions or titles. Include variations and synonyms when relevant.

Examples:

Query: "What are the different valve body materials?"
Response: {"search_terms": ["valve body materials", "body material", "cast iron", "carbon steel", "stainless steel", "material selection", "material properties"], "content_type": "table", "intent": "information about valve body material options", "confidence": 0.8}

Query: "Show me the flow characteristics diagram"
Response: {"search_terms": ["flow characteristics", "flow curve", "equal percentage", "linear flow", "quick opening", "flow diagram", "characteristic curve"], "content_type": "figure", "intent": "diagram showing valve flow characteristics", "confidence": 0.9}

Query: "I need pressure drop calculations"
Response: {"search_terms": ["pressure drop", "pressure loss", "delta P", "flow calculation", "pressure differential", "hydraulic calculation", "flow resistance"], "content_type": "any", "intent": "information about pressure drop calculations", "confidence": 0.7}

Query: "Find the temperature rating chart"
Response: {"search_terms": ["temperature rating", "temperature limits", "operating temperature", "temperature chart", "thermal rating", "temperature range", "service temperature"], "content_type": "table", "intent": "chart showing temperature ratings or limits", "confidence": 0.9}

Return only valid JSON."""

RESULT_SELECTION_SYSTEM_PROMPT="""You are an expert at selecting the most relevant result for technical queries about control valves.

Given a user query and a list of search results (with ID, type, and title), select the best match.

Return ONLY a JSON with:
- selected_index: index of best result (number) or null if none are good
- confidence: 0.0-1.0 confidence score

Rules:
- High confidence (0.8+): Exact or very close match
- Medium confidence (0.5-0.7): Good but not perfect match  
- Low confidence (0.0-0.4): Poor matches, return null for selected_index

Example: {"selected_index": 2, "confidence": 0.9}"""

QUERY_ANALYSIS_SCHEMA = {
            "type": "object",
            "properties": {
                "search_terms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of specific keywords and phrases optimized for BM25 search"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["table", "figure", "any"],
                    "description": "Type of content the user is looking for"
                },
                "intent": {
                    "type": "string",
                    "description": "Brief description of what user wants"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "description": "Confidence score for how clear the query is"
                }
            },
            "required": ["search_terms", "content_type", "intent", "confidence"],
            "additionalProperties": False
        }

RESULT_SELECTION_SCHEMA = {
            "type": "object",
            "properties": {
                "selected_index": {
                    "type": ["integer", "null"],
                    "description": "Index of best result (number) or null if none are good",
                    "minimum": 0
                },
                "confidence": {
                    "type": "number",
                    "description": "Confidence score from 0.0 to 1.0",
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "required": ["selected_index", "confidence"],
            "additionalProperties": False
        }
