import numpy as np
import faiss
import pickle
import atexit
from typing import List, Tuple
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from models import ContentItem, SearchResult
from config import Config

# Set torch to use single thread to avoid multiprocessing issues
try:
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
except ImportError:
    pass

class EmbeddingSearchEngine:
    """Semantic search engine using gte-multilingual-base sentence transformer and FAISS"""
    
    def __init__(self, config: Config):
        self.config = config
        self.index = None
        self.content_items = []
        self.embeddings = None
        self.model = None
        
        # Initialize gte-multilingual-base sentence transformer
        print(f"Loading gte-multilingual-base model: {config.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(config.EMBEDDING_MODEL, trust_remote_code=True)
        print("gte-multilingual-base model loaded successfully")
        
        # Register cleanup function
        atexit.register(self.cleanup)
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text using gte-multilingual-base sentence transformer"""
        try:
            # Clean the text
            cleaned_text = text.replace("\n", " ").strip()
            if not cleaned_text:
                return [0.0] * self.config.EMBEDDING_DIMENSION
            
            # Generate embedding using gte-multilingual-base
            embedding = self.model.encode([cleaned_text], normalize_embeddings=True)[0]
            return embedding.tolist()
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return [0.0] * self.config.EMBEDDING_DIMENSION
    
    def build_index(self, content_items: List[ContentItem]):
        """Build FAISS index from content items"""
        self.content_items = content_items
        
        # Create embeddings for all content
        embeddings = []
        for item in content_items:
            # Combine title and content for embedding
            text_to_embed = f"{item.title or ''}"
            embedding = self.get_embedding(text_to_embed)
            embeddings.append(embedding)
        
        if not embeddings:
            raise ValueError("No embeddings created")
            
        # Convert to numpy array
        self.embeddings = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        dimension = self.config.EMBEDDING_DIMENSION
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)
        
        print(f"Built FAISS index with {len(content_items)} items")
    
    def search(self, query: str, k: int = 10) -> List[Tuple[ContentItem, float]]:
        """Search for similar content using semantic similarity"""
        if not self.index:
            return []
        
        # Get query embedding
        query_embedding = np.array([self.get_embedding(query)]).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search FAISS index
        scores, indices = self.index.search(query_embedding, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.content_items) and score > self.config.SIMILARITY_THRESHOLD:
                results.append((self.content_items[idx], float(score)))
        
        return results
    
    def cleanup(self):
        """Clean up resources to prevent semaphore leaks"""
        try:
            if hasattr(self, 'model') and self.model is not None:
                # Clear model from memory
                del self.model
                self.model = None
                
            # Force garbage collection
            import gc
            gc.collect()
            
            # Clear CUDA cache if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except (ImportError, AttributeError):
                pass
                
        except Exception as e:
            # Silently handle cleanup errors to avoid disrupting shutdown
            pass
    
    def save_index(self, path: str):
        """Save FAISS index and metadata to disk"""
        if self.index:
            faiss.write_index(self.index, f"{path}.faiss")
            
            # Save metadata
            with open(f"{path}_metadata.pkl", 'wb') as f:
                pickle.dump({
                    'content_items': self.content_items,
                    'embeddings': self.embeddings
                }, f)
    
    def load_index(self, path: str) -> bool:
        """Load FAISS index and metadata from disk"""
        try:
            self.index = faiss.read_index(f"{path}.faiss")
            
            with open(f"{path}_metadata.pkl", 'rb') as f:
                metadata = pickle.load(f)
                self.content_items = metadata['content_items']
                self.embeddings = metadata['embeddings']
            
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            return False

class KeywordSearchEngine:
    """Keyword search engine using BM25"""
    
    def __init__(self, config: Config):
        self.config = config
        self.bm25 = None
        self.content_items = []
        self.tokenized_docs = []
    
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Convert to lowercase and split on whitespace
        tokens = text.lower().split()
        return tokens
    
    def build_index(self, content_items: List[ContentItem]):
        """Build BM25 index from content items"""
        self.content_items = content_items
        
        # Tokenize all documents
        self.tokenized_docs = []
        for item in content_items:
            # Combine title and content for indexing
            text_to_index = f"{item.title or ''}"
            tokens = self.tokenize(text_to_index)
            self.tokenized_docs.append(tokens)
        
        # Create BM25 index
        self.bm25 = BM25Okapi(self.tokenized_docs)
        print(f"Built BM25 index with {len(content_items)} items")
    
    def search(self, query: str, k: int = 10) -> List[Tuple[ContentItem, float]]:
        """Search using BM25 keyword matching"""
        if not self.bm25:
            return []
        
        # Tokenize query
        query_tokens = self.tokenize(query)
        
        # Get BM25 scores
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top-k results
        top_indices = np.argsort(scores)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if idx < len(self.content_items) and scores[idx] > 0:
                results.append((self.content_items[idx], float(scores[idx])))
        
        return results
    
    def save_index(self, path: str):
        """Save BM25 index and metadata to disk"""
        if self.bm25:
            # Save BM25 index and related data
            with open(f"{path}_keyword.pkl", 'wb') as f:
                pickle.dump({
                    'content_items': self.content_items,
                    'tokenized_docs': self.tokenized_docs,
                    'bm25': self.bm25
                }, f)
    
    def load_index(self, path: str) -> bool:
        """Load BM25 index and metadata from disk"""
        try:
            with open(f"{path}_keyword.pkl", 'rb') as f:
                data = pickle.load(f)
                self.content_items = data['content_items']
                self.tokenized_docs = data['tokenized_docs']
                self.bm25 = data['bm25']
            
            return True
        except Exception as e:
            print(f"Error loading keyword index: {e}")
            return False

class HybridSearchEngine:
    """Combines semantic and keyword search engines"""
    
    def __init__(self, config: Config):
        self.config = config
        self.embedding_engine = EmbeddingSearchEngine(config)
        self.keyword_engine = KeywordSearchEngine(config)
        
        # Register cleanup function
        atexit.register(self.cleanup)
    
    def build_index(self, content_items: List[ContentItem]):
        """Build indices for both search engines"""
        self.embedding_engine.build_index(content_items)
        self.keyword_engine.build_index(content_items)
    
    def search(self, query: str, k: int = 10, 
               semantic_weight: float = 0.7, 
               keyword_weight: float = 0.3,
               search_terms: List[str] = []) -> List[SearchResult]:
        """Hybrid search combining semantic and keyword results"""
        
        # Get semantic results
        semantic_results = self.embedding_engine.search(query, k)
        
        # Get keyword results using reciprocal rank fusion for search terms
        keyword_results = []
        if search_terms:
            # Get results for each search term individually
            term_results = []
            for term in search_terms:
                term_result = self.keyword_engine.search(term, k)
                term_results.append(term_result)
            
            # Apply reciprocal rank fusion to combine results from different terms
            rrf_scores = {}
            for term_result in term_results:
                for rank, (item, _) in enumerate(term_result):
                    if item.id not in rrf_scores:
                        rrf_scores[item.id] = {'item': item, 'rrf_score': 0.0}
                    rrf_scores[item.id]['rrf_score'] += 1.0 / (rank + 1)
            
            # Convert RRF scores to ranked list
            keyword_results = [(data['item'], data['rrf_score']) for data in rrf_scores.values()]
            keyword_results.sort(key=lambda x: x[1], reverse=True)
            keyword_results = keyword_results[:k]
        else:
            # Fall back to original query if no search terms provided
            keyword_results = self.keyword_engine.search(query, k)
        
        # Apply reciprocal rank fusion to combine semantic and keyword results
        final_rrf_scores = {}
        
        # Add semantic results with RRF
        for rank, (item, _) in enumerate(semantic_results):
            if item.id not in final_rrf_scores:
                final_rrf_scores[item.id] = {
                    'item': item,
                    'rrf_score': 0.0,
                    'match_type': 'semantic'
                }
            final_rrf_scores[item.id]['rrf_score'] += semantic_weight * (1.0 / (rank + 1))
        
        # Add keyword results with RRF
        for rank, (item, _) in enumerate(keyword_results):
            if item.id not in final_rrf_scores:
                final_rrf_scores[item.id] = {
                    'item': item,
                    'rrf_score': 0.0,
                    'match_type': 'keyword'
                }
            else:
                final_rrf_scores[item.id]['match_type'] = 'hybrid'
            final_rrf_scores[item.id]['rrf_score'] += keyword_weight * (1.0 / (rank + 1))
        
        # Create search results
        search_results = []
        for data in final_rrf_scores.values():
            if data['rrf_score'] > 0:
                search_results.append(SearchResult(
                    content_item=data['item'],
                    relevance_score=data['rrf_score'],
                    match_type=data['match_type']
                ))
        
        # Sort by RRF score
        search_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return search_results[:k]
    
    def save_indices(self, path: str):
        """Save both indices"""
        self.embedding_engine.save_index(f"{path}_embedding")
        self.keyword_engine.save_index(path)
    
    def load_indices(self, path: str) -> bool:
        """Load both indices"""
        embedding_loaded = self.embedding_engine.load_index(f"{path}_embedding")
        keyword_loaded = self.keyword_engine.load_index(path)
        return embedding_loaded and keyword_loaded
    
    def cleanup(self):
        """Clean up resources from both search engines"""
        try:
            if hasattr(self, 'embedding_engine') and self.embedding_engine is not None:
                self.embedding_engine.cleanup()
            
            # Force garbage collection
            import gc
            gc.collect()
        except Exception as e:
            # Silently handle cleanup errors
            pass
