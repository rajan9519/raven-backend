# Design Document: Table & Image Search Backend Service

## Architecture Overview

The system implements a **hybrid search architecture** with intelligent LLM-enhanced result selection to locate tables and images from technical manuals based on natural language queries.

## Document Processing & Indexing Pipeline

### 1. Document Parsing (`data_parser.py`)
- **Input Sources**: Processes `mmd_lines_data.json`
- **Content Extraction**: 
  - Identifies LaTeX table/figure blocks using regex patterns (`\begin{table}`, `\begin{figure}`)
  - Extracts captions and tabular content from LaTeX markup
  - Groups text lines into logical blocks based on spatial proximity and font consistency
- **Citation Generation**: Creates precise citation metadata with page numbers and bounding box coordinates
- **Output**: Structured `ContentItem` objects with standardized metadata

### 2. Index Building (`search_engines.py`)
- **Semantic Indexing**: 
  - Uses `gte-multilingual-base` transformer model (768-dim embeddings)
  - FAISS IndexFlatIP for efficient cosine similarity search
  - Embeddings generated from content titles for semantic understanding
- **Keyword Indexing**: 
  - BM25Okapi algorithm for exact term matching
  - Tokenized document corpus for traditional IR approaches
- **Persistence**: Both indices saved to disk for fast startup (`faiss_index.faiss`, `faiss_index_keyword.pkl`)

## Query Processing & Search Flow

### 3. Query Analysis (`query_processor.py`)
- **LLM Analysis**: GPT-4.1 with structured JSON schema analyzes:
  - Search terms extraction
  - Content type preference (table/figure/any)
  - Query intent classification
  - Confidence scoring
- **Fallback**: Rule-based analysis if LLM fails
- **Strategy Determination**: Dynamically adjusts semantic/keyword weights based on analysis

### 4. Hybrid Search Execution
- **Dual Search**: Parallel execution of semantic and keyword searches
- **Reciprocal Rank Fusion**: Combines results using weighted RRF algorithm
- **Content Filtering**: Applies content type filters based on query analysis
- **Ranking**: Final relevance scoring considers both semantic similarity and keyword matches

### 5. LLM Result Selection (`query_processor.py`)
- **Candidate Evaluation**: GPT-4.1 analyzes search results against user query
- **Selection Logic**: Returns structured response with confidence scores
- **Response Types**:
  - `success`: Single confident match
  - `multiple_candidates`: Primary selection + alternatives
  - `insufficient_info`: No confident matches found

## Service Architecture

### 6. API Layer (`main.py`, `service.py`)
- **Endpoints**:
  - `/search`: Basic hybrid search
  - `/llm-search`: LLM-enhanced intelligent selection
  - `/statistics`: Content metadata
- **Initialization**: Lazy loading with index persistence
- **Error Handling**: Graceful degradation with fallback mechanisms

## Key Design Decisions

- **Modular Pipeline**: Clear separation of parsing → indexing → querying → selection
- **Dual Search Strategy**: Semantic understanding + keyword precision
- **LLM Integration**: Intelligent query analysis and result selection rather than generation
- **Citation-First**: All results include precise page/coordinate citations