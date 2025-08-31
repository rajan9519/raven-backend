import os
from typing import Optional

class Config:
    """Configuration settings for the backend service"""
    
    # Sentence-Transformer settings
    EMBEDDING_MODEL: str = "Alibaba-NLP/gte-multilingual-base"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4.1"
    
    # FAISS settings
    EMBEDDING_DIMENSION: int = 768  # dimension
    
    # Search settings
    MAX_RESULTS: int = 10
    SIMILARITY_THRESHOLD: float = 0.7
    
    # File paths
    MMD_DATA_PATH: str = "mmd_lines_data.json"
    MANUAL_PATH: str = "manual.mmd"
    INDEX_PATH: str = "faiss_index"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
