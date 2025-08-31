# Table & Image Search Backend Service

A sophisticated backend service that locates and extracts tables/images from technical manuals based on natural language queries. Features dual search modes: basic hybrid search and LLM-enhanced intelligent selection. Built with FastAPI, GPT-4, transformer embeddings, FAISS vector search, and BM25 keyword matching.

## Features

- 🔍 **Natural Language Search**: Query using operator-style requests like "Show me the actuator types comparison"
- 🧠 **Dual Search Modes**: 
  - **Basic Hybrid Search**: Combines semantic understanding (transformer embeddings) with keyword matching (BM25)
  - **LLM-Enhanced Search**: Uses GPT-4 to intelligently analyze queries and select the most relevant result
- 📊 **Multi-Content Support**: Searches tables, figures, and text blocks from technical documents
- 📍 **Precise Citations**: Returns page numbers and bounding box coordinates for all results
- ⚡ **Fast Performance**: Sub-second search responses with persistent FAISS indexing
- 🧩 **Intelligent Result Selection**: LLM analyzes search candidates and provides reasoning for selections
- 🔄 **Smart Ambiguity Handling**: Returns single best match, multiple candidates, or "insufficient_info" based on confidence

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Initial setup (creates virtual environment)**:
   ```bash
   ./setup.sh
   ```

2. **Set your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

3. **Start the server**:
   ```bash
   ./start_server.sh
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Running Sample Queries

```bash
# Option 1: Using the wrapper script (recommended)
./run_samples_venv.sh

# Option 2: Manual activation
source venv/bin/activate
python run_samples.py
```

This will execute the example queries from the assignment and save results to `sample_query_results.json`.

### Manual Virtual Environment Management

If you prefer to manage the virtual environment manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run the service
python main.py

# Deactivate when done
deactivate
```

## API Endpoints

### `POST /search`
Basic hybrid search for tables and images with natural language queries.

**Request**:
```json
{
  "query": "Can you pull up the comparison of actuator types?",
  "max_results": 5
}
```

**Response**:
```json
{
  "query": "Can you pull up the comparison of actuator types?",
  "results": [
    {
      "content_item": {
        "id": "table_1",
        "content_type": "table",
        "title": "Table 2-1. Actuator Selection Criteria",
        "content": "...",
        "citation": {
          "page_no": 23,
          "bounding_box": {
            "top_left_x": 350,
            "top_left_y": 450,
            "width": 800,
            "height": 300
          }
        }
      },
      "relevance_score": 0.892,
      "match_type": "hybrid"
    }
  ],
  "status": "success",
  "total_found": 1
}
```

### `POST /llm-search` ⭐ **Recommended**
LLM-enhanced search with intelligent result selection. Uses GPT-4 to analyze query intent and select the most appropriate result from search candidates.

**Request**:
```json
{
  "query": "Show me the sizing factors for liquids",
  "max_results": 10
}
```

**Response Types**:

**1. Single Best Match (`success`):**
```json
{
  "query": "Show me the sizing factors for liquids",
  "selected_result": {
    "content_item": {
      "id": "table_5",
      "content_type": "table",
      "title": "Table 4-2. Liquid Sizing Factors",
      "content": "...",
      "citation": {
        "page_no": 45,
        "bounding_box": {
          "top_left_x": 200,
          "top_left_y": 300,
          "width": 600,
          "height": 400
        }
      }
    },
    "relevance_score": 0.945,
    "match_type": "hybrid"
  },
  "alternative_candidates": [],
  "status": "success",
  "message": "Found match",
  "llm_reasoning": "This table specifically covers liquid sizing factors which directly matches the user's request.",
  "confidence_score": 0.92
}
```

**2. Multiple Candidates (`multiple_candidates`):**
```json
{
  "query": "cavitation information",
  "selected_result": {
    "content_item": {
      "id": "figure_8",
      "content_type": "figure", 
      "title": "Figure 3-5. Cavitation Process Diagram",
      "content": "...",
      "citation": {...}
    },
    "relevance_score": 0.834,
    "match_type": "semantic"
  },
  "alternative_candidates": [
    {
      "content_item": {
        "id": "table_12",
        "content_type": "table",
        "title": "Table 3-2. Cavitation Index Values", 
        "content": "...",
        "citation": {...}
      },
      "relevance_score": 0.821,
      "match_type": "hybrid"
    }
  ],
  "status": "multiple_candidates",
  "message": "Found 2 candidates",
  "llm_reasoning": "The figure provides a visual explanation which seems most helpful for understanding cavitation, though the table with index values is also relevant.",
  "confidence_score": 0.75
}
```

**3. Insufficient Information (`insufficient_info`):**
```json
{
  "query": "quantum mechanics equations",
  "selected_result": null,
  "alternative_candidates": [],
  "status": "insufficient_info",
  "message": "No confident match found",
  "llm_reasoning": "The query asks for quantum mechanics content, but this manual focuses on control valves and oil & gas applications. No relevant matches found.",
  "confidence_score": 0.0
}
```

### `GET /statistics`
Get statistics about indexed content.

**Response**:
```json
{
  "content_statistics": {
    "total_items": 45,
    "figures": 23,
    "tables": 22,
    "text_blocks": 0,
    "initialized": true
  },
  "service_status": "initialized"
}
```

### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service_initialized": "True",
  "openai_configured": "yes"
}
```

## Architecture

### Core Components

- **Data Parser**: Extracts structured content from `mmd_lines_data.json` with LaTeX table/figure detection
- **Hybrid Search Engine**: Combines transformer embeddings (FAISS) with BM25 keyword search using Reciprocal Rank Fusion
- **Query Processor**: 
  - GPT-4 powered query analysis and intent classification
  - LLM-based intelligent result selection with confidence scoring
  - Dynamic search strategy optimization
- **FastAPI Service**: RESTful API with dual search modes and comprehensive error handling

### Search Flow

1. **Basic Search (`/search`)**:
   - Query analysis → Strategy determination → Hybrid search → Result filtering → Response

2. **LLM-Enhanced Search (`/llm-search`)** ⭐:
   - Query analysis → Hybrid search → **LLM result selection** → Confidence evaluation → Smart response

### Key Features

- **Semantic Understanding**: `gte-multilingual-base` embeddings for content similarity
- **Keyword Precision**: BM25Okapi for exact term matching
- **Intelligent Selection**: GPT-4 analyzes candidates and provides reasoning
- **Persistent Indexing**: FAISS indices saved to disk for fast startup
- **Citation Accuracy**: Precise page numbers and bounding box coordinates

## Sample Queries

### Basic Search Examples (`/search`)
Returns all relevant matches with relevance scores:
- "Can you pull up the comparison of actuator types?"
- "Show me the sizing factors for liquids."
- "I need the noise level reference values."

### LLM-Enhanced Search Examples (`/llm-search`) ⭐ **Recommended**
Returns the single best match with reasoning:
- **Visual Content**: "Do we have a figure that explains cavitation?"  
  → Returns best diagram with explanation of why it was selected
- **Specific Data**: "Show me the overall oil & gas value chain diagram"  
  → Identifies and returns the exact process flow diagram
- **Comparison Tables**: "Compare different actuator types"  
  → Finds and returns the most comprehensive comparison table
- **Technical Values**: "What are the standard noise level limits?"  
  → Returns specific reference table with LLM reasoning

### Complex Query Handling
- **Ambiguous queries**: Returns `multiple_candidates` with primary selection + alternatives
- **Out-of-scope queries**: Returns `insufficient_info` with clear explanation
- **Partial matches**: LLM determines if results meet user intent threshold

## Input Files

- `mmd_lines_data.json`: Layout metadata with pages, blocks, and coordinates
- `manual.mmd`: Markdown manual with tables and image references

## Output Format

All results include:
- Content type (table/figure/text)
- Title and content
- Page number
- Bounding box coordinates (top_left_x, top_left_y, width, height)
- Relevance score and match type

## Response Types & Error Handling

### LLM-Enhanced Search Response Types
- **`success`**: Single confident match found with high confidence score
- **`multiple_candidates`**: Multiple relevant results found; LLM selects primary + alternatives
- **`insufficient_info`**: No confident matches found; LLM explains why query can't be satisfied

### Basic Search Response Types  
- **`success`**: One or more relevant results found
- **`insufficient_info`**: No relevant content found matching query terms

### Error Handling
- **LLM Fallback**: If GPT-4 API fails, system falls back to rule-based analysis
- **API Resilience**: Graceful degradation when OpenAI API is unavailable
- **Input Validation**: Proper HTTP status codes and error messages for malformed requests
- **Confidence Thresholding**: Results below confidence threshold trigger `insufficient_info`

## Performance

- **Initialization**: ~30-60 seconds (one-time indexing)
- **Search**: <1 second response time
- **Memory**: Optimized in-memory indices with disk persistence

## Project Structure

```
backend-assignment/
├── main.py                           # FastAPI application with dual endpoints
├── service.py                        # Main service orchestration (basic + LLM search)
├── search_engines.py                 # Hybrid search implementation (FAISS + BM25)
├── query_processor.py                # GPT-powered query analysis & LLM result selection
├── data_parser.py                    # Content extraction & LaTeX parsing
├── models.py                         # Pydantic data models (SearchQuery, LLMSearchResponse, etc.)
├── config.py                         # Configuration settings
├── constants.py                      # Application constants
├── requirements.txt                  # Dependencies
├── DESIGN.md                         # Architecture documentation
├── README.md                         # Usage instructions (this file)
├── sample_output.json               # Example basic search results
├── sample_query_results.json        # Example LLM search results  
├── setup.sh                         # Initial setup with virtual environment
├── start_server.sh                  # Server startup script (uses venv)
├── run_samples.py                   # Demo script with sample queries
├── run_samples_venv.sh              # Demo script wrapper (uses venv)
├── .gitignore                       # Git ignore file
├── mmd_lines_data.json              # Input: Layout metadata with coordinates
├── manual.mmd                       # Input: Markdown manual content
├── faiss_index_embedding.faiss      # Persistent FAISS semantic index
├── faiss_index_keyword.pkl          # Persistent BM25 keyword index
├── faiss_index_embedding_metadata.pkl # Index metadata
└── venv/                            # Virtual environment (created by setup)
```

See `DESIGN.md` for detailed architecture information.
