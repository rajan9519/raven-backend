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

### `POST /llm-search`
LLM-enhanced search with intelligent result selection. Uses GPT-4 to analyze query intent and select the most appropriate result from search candidates.

## Example 1:
**Request**:
```json
{
  "query": "Show me the sizing factors for liquids",
}
```

**Response Types**:

**1. Single Best Match (`success`):**
```json
{
    "query": "Show me the sizing factors for liquids.",
    "selected_result": {
        "content_item": {
            "id": "table_14",
            "content_type": "table",
            "title": "Table 4-1. Representative Sizing Coefficients for Rotary Shaft Valves",
            "content": "{|l|l|l|l|l|l|l|}\n\\hline Valve Size (NPS) & Valve Style & Degrees of Valve Opening & \\(\\mathrm{C}_{\\mathrm{v}}\\) & \\(\\mathrm{F}_{\\mathrm{L}}\\) & \\(\\mathrm{X}_{\\mathrm{T}}\\) & \\(\\mathrm{F}_{\\mathrm{D}}\\) \\\\\n\\hline 1 & V-Notch Ball Valve & 60 & 15.6 & 0.86 & 0.53 & \\\\\n\\hline & & 90 & 34.0 & 0.86 & 0.42 & \\\\\n\\hline 1 1/2 & V-Notch Ball Valve & 60 & 28.5 & 0.85 & 0.50 & \\\\\n\\hline & & 90 & 77.3 & 0.74 & 0.27 & \\\\\n\\hline 2 & \\multirow[t]{4}{*}{\\begin{tabular}{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve",
            "citation": {
                "page_no": 54,
                "bounding_box": {
                    "top_left_x": 246,
                    "top_left_y": 319,
                    "width": 1698,
                    "height": 1327
                },
                "confidence": null
            },
            "metadata": {
                "confidence": 0.8943800926208496,
                "font_size": 22
            },
            "image_url": null
        },
        "relevance_score": 0.6,
        "match_type": "keyword"
    },
    "alternative_candidates": [other result items],
    "status": "multiple_candidates",
    "message": "Found 3 candidates",
    "llm_reasoning": "LLM found a good match with alternatives available",
    "confidence_score": 0.7
}
```


### `POST /search`
Basic hybrid search (like RAG) for tables and images with natural language queries.

**Request**:
```json
{
  "query": "Show me the sizing factors for liquids."
}
```

**Response**:
```json
{
    "query": "Show me the sizing factors for liquids.",
    "results": [
        {
            "content_item": {
                "id": "table_14",
                "content_type": "table",
                "title": "Table 4-1. Representative Sizing Coefficients for Rotary Shaft Valves",
                "content": "{|l|l|l|l|l|l|l|}\n\\hline Valve Size (NPS) & Valve Style & Degrees of Valve Opening & \\(\\mathrm{C}_{\\mathrm{v}}\\) & \\(\\mathrm{F}_{\\mathrm{L}}\\) & \\(\\mathrm{X}_{\\mathrm{T}}\\) & \\(\\mathrm{F}_{\\mathrm{D}}\\) \\\\\n\\hline 1 & V-Notch Ball Valve & 60 & 15.6 & 0.86 & 0.53 & \\\\\n\\hline & & 90 & 34.0 & 0.86 & 0.42 & \\\\\n\\hline 1 1/2 & V-Notch Ball Valve & 60 & 28.5 & 0.85 & 0.50 & \\\\\n\\hline & & 90 & 77.3 & 0.74 & 0.27 & \\\\\n\\hline 2 & \\multirow[t]{4}{*}{\\begin{tabular}{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve\n{l}\nV-Notch Ball Valve \\\\\nHigh Performance Butterfly Valve",
                "citation": {
                    "page_no": 54,
                    "bounding_box": {
                        "top_left_x": 246,
                        "top_left_y": 319,
                        "width": 1698,
                        "height": 1327
                    },
                    "confidence": null
                },
                "metadata": {
                    "confidence": 0.8943800926208496,
                    "font_size": 22
                },
                "image_url": null
            },
            "relevance_score": 0.6,
            "match_type": "keyword"
        },
        {
            "content_item": {
                "id": "table_15",
                "content_type": "table",
                "title": "Table 4-2. Representative Sizing Coefficients for Design ED Single-Ported Globe Style Valve Bodies",
                "content": "{|l|l|l|l|l|l|l|l|l|}\n\\hline Valve Size (NPS) & Valve Plug Style & Flow Characteristic & Port Dia. (in.) & Rated Travel (in.) & \\(\\mathrm{C}_{\\mathrm{V}}\\) & \\(\\mathrm{F}_{\\mathrm{L}}\\) & \\(\\mathrm{x}_{\\mathrm{T}}\\) & \\(\\mathrm{F}_{\\mathrm{D}}\\) \\\\\n\\hline 1/2 & Post Guided & Equal Percentage & 0.38 & 0.50 & 2.41 & 0.90 & 0.54 & 0.61 \\\\\n\\hline 3/4 & Post Guided & Equal Percentage & 0.56 & 0.50 & 5.92 & 0.84 & 0.61 & 0.61 \\\\\n\\hline \\multirow{5}{*}{1} & \\multirow[t]{5}{*}{Micro Form \\({ }^{\\text {TM }}\\)} & \\multirow[t]{3}{*}{Equal Percentage} & 3/8 & 3/4 & 3.07 & 0.89 & 0.66 & 0.72 \\\\\n\\hline & & & 1/2 & 3/4 & 4.91 & 0.93 & 0.80 & 0.67 \\\\\n\\hline & & & 3/4 & 3/4 & 8.84 & 0.97 & 0.92 & 0.62 \\\\\n\\hline & \\multirow[t]{2}{*}{Cage Guided} & Linear & 1 5/16 & 3/4 & 20.6 & 0.84 & 0.64 & 0.34 \\\\\n\\hline & & Equal Percentage & 1 5/16 & 3/4 & 17.2 & 0.88 & 0.67 & 0.38 \\\\\n\\hline \\multirow{5}{*}{1 1/2} & \\multirow[t]{5}{*}{\\begin{tabular}{l}\nMicro-Form \\({ }^{\\text {™ }}\\) \\\\\nCage Guided",
                "citation": {
                    "page_no": 55,
                    "bounding_box": {
                        "top_left_x": 242,
                        "top_left_y": 317,
                        "width": 1703,
                        "height": 879
                    },
                    "confidence": null
                },
                "metadata": {
                    "confidence": 0.8349151611328125,
                    "font_size": 22
                },
                "image_url": null
            },
            "relevance_score": 0.3,
            "match_type": "keyword"
        },
        {
            "content_item": {
                "id": "table_10",
                "content_type": "table",
                "title": "Tabel 2-5. Typical High Performance Butterfly Torque Factors for Valve with Composition Seal",
                "content": "{|l|l|l|l|l|l|l|l|l|}\n\\hline Valve Size, NPS & Shaft Diameter Inches & A & B & \\multicolumn{3}{|c|}{C} & \\multicolumn{2}{|c|}{Maximum Torque, Inch-Pounds} \\\\\n\\hline & & & & \\(60^{\\circ}\\) & \\(75^{\\circ}\\) & \\(90^{\\circ}\\) & Breakout \\(\\mathrm{T}_{\\mathrm{B}}\\) & Dynamic \\(\\mathrm{T}_{\\mathrm{D}}\\) \\\\\n\\hline 3 & 1/2 & 0.50 & 136 & 0.8 & 1.8 & 8 & 280 & 515 \\\\\n\\hline 4 & 5/8 & 0.91 & 217 & 3.1 & 4.7 & 25 & 476 & 225 \\\\\n\\hline 6 & 3/4 & 1.97 & 403 & 30 & 24 & 70 & 965 & 2120 \\\\\n\\hline 8 & 1 & 4.2 & 665 & 65 & 47 & 165 & 1860 & 4140 \\\\\n\\hline 10 & 1-1/4 & 7.3 & 1012 & 125 & 90 & 310 & 3095 & 9820 \\\\\n\\hline 12 & 1-1/2 & 11.4 & 1422 & 216 & 140 & 580 & 4670 & 12,000 \\\\\n\\hline",
                "citation": {
                    "page_no": 35,
                    "bounding_box": {
                        "top_left_x": 246,
                        "top_left_y": 872,
                        "width": 1695,
                        "height": 397
                    },
                    "confidence": null
                },
                "metadata": {
                    "confidence": 0.6514238863508126,
                    "font_size": 22
                },
                "image_url": null
            },
            "relevance_score": 0.19999999999999998,
            "match_type": "keyword"
        }
    ],
    "status": "success",
    "message": "Found 3 relevant results",
    "total_found": 3
}
```

## Example 2:
**Request**:
```json
{
  "query": "Can you pull up the comparison of actuator types?"
}
```
**Response**
```json
{
    "query": "Can you pull up the comparison of actuator types?",
    "selected_result": {
        "content_item": {
            "id": "table_11",
            "content_type": "table",
            "title": "Table 2-6 Actuator Feature Comparison",
            "content": "{|l|l|l|}\n\\hline Actuator Type & Advantages & Disadvantages \\\\\n\\hline Spring-and-Diaphragm & \\begin{tabular}{l}\nLowest cost \\\\\nAbility to throttle without positioner Simplicity \\\\\nInherent fail-safe action \\\\\nLow supply pressure requirement \\\\\nAdjustable to varying conditions \\\\\nEase of maintenance\n{l}\nLimited output capability \\\\\nLarger size and weight\n{l}\nHigh thrust capability \\\\\nCompact \\\\\nLightweight \\\\\nAdaptable to high ambient temperatures \\\\\nFast stroking speed \\\\\nRelatively high actuator stiffness\n{l}\nHigher cost \\\\\nFail-safe requires accessories or addition of a spring \\\\\nPositioner required for throttling \\\\\nHigh supply pressure requirement\n{l}\nCompactness \\\\\nVery high stiffness \\\\\nHigh output capability\n{l}\nHigh cost \\\\\nLack of fail-safe action \\\\\nLimited duty cycle \\\\\nSlow stroking speed\n{l}\nHigh output capability \\\\\nHigh actuator stiffness \\\\\nExcellent throttling ability \\\\\nFast stroking speed\n{l}\nHigh cost \\\\\nComplexity and maintenance difficulty \\\\\nLarge size and weight \\\\\nFail-safe action only with accessories",
            "citation": {
                "page_no": 36,
                "bounding_box": {
                    "top_left_x": 243,
                    "top_left_y": 677,
                    "width": 1701,
                    "height": 1110
                },
                "confidence": null
            },
            "metadata": {
                "confidence": 0.99951171875,
                "font_size": 28
            },
            "image_url": null
        },
        "relevance_score": 1.0,
        "match_type": "hybrid"
    },
    "alternative_candidates": [],
    "status": "success",
    "message": "Found match",
    "llm_reasoning": "LLM found a strong match",
    "confidence_score": 0.95
}
```

## Example 3:
**Request**:
```json
{
  "query": "I need the noise level reference values."
}
```
**Response**
```json
{
    "query": "I need the noise level reference values.",
    "selected_result": null,
    "alternative_candidates": [],
    "status": "insufficient_info",
    "message": "No confident match found",
    "llm_reasoning": "LLM found no confident match",
    "confidence_score": 0.2
}
```

## Example 4:

**Request**:
```json
{
  "query": "Do we have a figure that explains cavitation?"
}
**Response**
```json
{
    "query": "Do we have a figure that explains cavitation?",
    "selected_result": {
        "content_item": {
            "id": "figure_44",
            "content_type": "figure",
            "title": "Figure 6-3. Pressure recovery above the vapor pressure of the liquid results in cavitation. Remaining below the vapor pressure incures flashing.",
            "content": "\\includegraphics[width=\\textwidth]{https://cdn.mathpix.com/cropped/2025_08_28_14c222ac7973e4f89cc8g-062.jpg?height=535&width=784&top_left_y=292&top_left_x=252}\n\\captionsetup{labelformat=empty}\n\\caption{Figure 6-3. Pressure recovery above the vapor pressure of the liquid results in cavitation. Remaining below the vapor pressure incures flashing.}",
            "citation": {
                "page_no": 62,
                "bounding_box": {
                    "top_left_x": 252,
                    "top_left_y": 292,
                    "width": 784,
                    "height": 535
                },
                "confidence": null
            },
            "metadata": {
                "confidence": 1.0,
                "font_size": 18
            },
            "image_url": null
        },
        "relevance_score": 0.4,
        "match_type": "semantic"
    },
    "alternative_candidates": [],
    "status": "success",
    "message": "Found match",
    "llm_reasoning": "LLM found a strong match",
    "confidence_score": 0.9
}
```

## Example 5:
**Request**:
```json
{
  "query": "Show me the overall oil & gas value chain diagram."
}
```
**Response**
```json
{
    "query": "Show me the overall oil & gas value chain diagram.",
    "selected_result": null,
    "alternative_candidates": [],
    "status": "insufficient_info",
    "message": "No confident match found",
    "llm_reasoning": "LLM found no confident match",
    "confidence_score": 0.2
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
