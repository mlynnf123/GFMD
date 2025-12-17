#!/usr/bin/env python3
"""
MongoDB Vector RAG System for GFMD
True vector database implementation with embeddings and semantic search
"""

import os
import logging
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np

from mongodb_storage import MongoDBStorage

logger = logging.getLogger(__name__)

class VectorRAGSystem:
    """True MongoDB vector database RAG system with embeddings"""
    
    def __init__(self):
        """Initialize the vector RAG system"""
        self.storage = MongoDBStorage()
        
        # Collections for vector storage
        self.knowledge_collection = self.storage.db.knowledge_vectors
        self.embeddings_collection = self.storage.db.document_embeddings
        
        # Initialize embedding model (using a lightweight model)
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Sentence transformer model loaded")
        except ImportError:
            logger.warning("⚠️ sentence-transformers not installed, using fallback")
            self.embedding_model = None
        
        self._ensure_vector_indexes()
    
    def _ensure_vector_indexes(self):
        """Ensure MongoDB vector search indexes exist"""
        try:
            # Create vector search index for embeddings
            # Note: In production, this should be done via MongoDB Atlas UI or API
            self.knowledge_collection.create_index([
                ("title", "text"),
                ("content", "text"),
                ("tags", "text"),
                ("doc_type", 1)
            ])
            logger.debug("Knowledge collection indexes ensured")
            
        except Exception as e:
            logger.debug(f"Index creation: {e}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        if self.embedding_model is None:
            # Fallback: use simple hash-based pseudo-embedding
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            # Convert hash to 384-dimensional vector (matching all-MiniLM-L6-v2)
            hash_int = int(text_hash, 16)
            embedding = [(hash_int >> i) & 1 for i in range(384)]
            return [float(x) for x in embedding]
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []
    
    def add_document(self, title: str, content: str, doc_type: str, 
                    tags: List[str] = None, metadata: Dict = None, 
                    chunk_size: int = 500) -> List[str]:
        """Add document to vector database with chunking"""
        
        # Split content into chunks for better retrieval
        chunks = self._chunk_text(content, chunk_size)
        doc_ids = []
        
        for i, chunk in enumerate(chunks):
            # Create unique ID for chunk
            chunk_hash = hashlib.md5(f"{title}_{chunk}".encode()).hexdigest()
            doc_id = f"{doc_type}_{chunk_hash[:8]}_chunk_{i}"
            
            # Generate embedding
            embedding = self.generate_embedding(chunk)
            
            if not embedding:
                logger.warning(f"Failed to generate embedding for chunk {i}")
                continue
            
            # Document metadata
            document = {
                "_id": doc_id,
                "title": title,
                "content": chunk,
                "full_content": content,  # Keep reference to full document
                "doc_type": doc_type,
                "tags": tags or [],
                "metadata": metadata or {},
                "chunk_index": i,
                "total_chunks": len(chunks),
                "embedding": embedding,
                "embedding_model": "all-MiniLM-L6-v2",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            try:
                self.knowledge_collection.insert_one(document)
                logger.info(f"Added chunk {i+1}/{len(chunks)} for: {title}")
                doc_ids.append(doc_id)
            except Exception as e:
                # Update if exists
                self.knowledge_collection.replace_one(
                    {"_id": doc_id},
                    document,
                    upsert=True
                )
                logger.info(f"Updated chunk {i+1}/{len(chunks)} for: {title}")
                doc_ids.append(doc_id)
        
        return doc_ids
    
    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """Split text into overlapping chunks for better context"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - 50):  # 50-word overlap
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            if len(chunk_words) < chunk_size:
                break
        
        return chunks if chunks else [text]  # Return original if chunking fails
    
    def vector_search(self, query: str, doc_type: str = None, 
                     limit: int = 5, similarity_threshold: float = 0.1) -> List[Dict]:
        """Perform vector similarity search"""
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            logger.warning("Failed to generate query embedding, falling back to text search")
            return self._fallback_text_search(query, doc_type, limit)
        
        # Build aggregation pipeline for vector search
        pipeline = []
        
        # Match stage (filter by doc_type if specified)
        match_stage = {}
        if doc_type:
            match_stage["doc_type"] = doc_type
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        # Add vector similarity calculation
        pipeline.extend([
            {
                "$addFields": {
                    "similarity": {
                        "$let": {
                            "vars": {
                                "dot_product": {
                                    "$reduce": {
                                        "input": {"$range": [0, {"$size": "$embedding"}]},
                                        "initialValue": 0,
                                        "in": {
                                            "$add": [
                                                "$$value",
                                                {
                                                    "$multiply": [
                                                        {"$arrayElemAt": ["$embedding", "$$this"]},
                                                        {"$arrayElemAt": [query_embedding, "$$this"]}
                                                    ]
                                                }
                                            ]
                                        }
                                    }
                                }
                            },
                            "in": "$$dot_product"  # Simplified similarity (dot product)
                        }
                    }
                }
            },
            {"$match": {"similarity": {"$gte": similarity_threshold}}},
            {"$sort": {"similarity": -1}},
            {"$limit": limit}
        ])
        
        try:
            results = list(self.knowledge_collection.aggregate(pipeline))
            logger.debug(f"Vector search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return self._fallback_text_search(query, doc_type, limit)
    
    def _fallback_text_search(self, query: str, doc_type: str = None, limit: int = 5) -> List[Dict]:
        """Fallback text search when vector search fails"""
        search_filter = {"$text": {"$search": query}}
        if doc_type:
            search_filter["doc_type"] = doc_type
        
        results = list(self.knowledge_collection.find(
            search_filter,
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit))
        
        return results
    
    def get_relevant_context(self, query: str, context_types: List[str] = None, 
                           max_context_length: int = 1000) -> str:
        """Get relevant context for RAG email composition"""
        
        context_types = context_types or ["product_info", "pain_points"]
        all_context = []
        
        for doc_type in context_types:
            results = self.vector_search(query, doc_type=doc_type, limit=3)
            
            for result in results:
                content = result.get("content", "")
                if len(content) > 200:  # Use substantial chunks
                    all_context.append(content)
        
        # Combine and truncate context
        combined_context = " ".join(all_context)
        if len(combined_context) > max_context_length:
            combined_context = combined_context[:max_context_length] + "..."
        
        return combined_context
    
    def get_personalized_insights(self, agency_type: str, pain_points: List[str], 
                                 location: str = "") -> Dict[str, str]:
        """Get personalized insights for email composition"""
        
        insights = {}
        
        # Get pain point solutions
        for pain_point in pain_points[:2]:  # Limit to top 2 pain points
            context = self.get_relevant_context(
                f"{pain_point} {agency_type} law enforcement",
                context_types=["pain_points", "product_info"],
                max_context_length=500
            )
            insights[f"{pain_point}_solution"] = context
        
        # Get product benefits relevant to agency type
        product_context = self.get_relevant_context(
            f"{agency_type} benefits advantages cost savings",
            context_types=["product_info"],
            max_context_length=500
        )
        insights["product_benefits"] = product_context
        
        # Get compliance/credibility information
        compliance_context = self.get_relevant_context(
            "DEA approved tested certified compliance",
            context_types=["product_info"],
            max_context_length=300
        )
        insights["credibility"] = compliance_context
        
        return insights
    
    def populate_knowledge_base(self):
        """Populate the vector database with GFMD knowledge"""
        
        print("📚 Populating Vector RAG Database...")
        
        # Knowledge documents to process
        documents = [
            {
                "file": "/Users/merandafreiner/GFMD/GFMD/knowledge_base/gfmd_narc_gone_findings.md",
                "doc_type": "product_info",
                "tags": ["narc_gone", "product_specs", "testing", "compliance", "benefits"]
            },
            {
                "file": "/Users/merandafreiner/GFMD/GFMD/knowledge_base/law_enforcement_pain_points.md",
                "doc_type": "pain_points", 
                "tags": ["law_enforcement", "challenges", "costs", "compliance", "accessibility"]
            }
        ]
        
        total_chunks = 0
        
        for doc_info in documents:
            try:
                with open(doc_info["file"], "r") as f:
                    content = f.read()
                
                # Extract title
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip() if lines else "Unknown Document"
                
                # Add to vector database
                chunk_ids = self.add_document(
                    title=title,
                    content=content,
                    doc_type=doc_info["doc_type"],
                    tags=doc_info["tags"],
                    metadata={"source_file": doc_info["file"]},
                    chunk_size=400  # Optimal for email context
                )
                
                total_chunks += len(chunk_ids)
                print(f"✅ Processed: {title} ({len(chunk_ids)} chunks)")
                
            except Exception as e:
                print(f"❌ Failed to process {doc_info['file']}: {e}")
        
        print(f"\n🎉 Vector database populated with {total_chunks} chunks")
        return total_chunks
    
    def test_rag_retrieval(self):
        """Test RAG retrieval functionality"""
        
        print("\n🔍 Testing RAG Retrieval...")
        
        test_queries = [
            ("cost savings for police departments", ["product_info"]),
            ("storage space evidence room", ["pain_points"]),
            ("DEA compliance testing", ["product_info"]),
            ("small department budget constraints", ["pain_points"])
        ]
        
        for query, doc_types in test_queries:
            print(f"\nQuery: '{query}'")
            
            for doc_type in doc_types:
                results = self.vector_search(query, doc_type=doc_type, limit=2)
                print(f"  {doc_type}: {len(results)} results")
                
                for i, result in enumerate(results):
                    similarity = result.get("similarity", result.get("score", 0))
                    content_preview = result.get("content", "")[:100]
                    print(f"    {i+1}. Score: {similarity:.3f} | {content_preview}...")
        
        # Test personalized insights
        print(f"\n🎯 Testing Personalized Insights...")
        insights = self.get_personalized_insights(
            agency_type="police", 
            pain_points=["cost", "storage"],
            location="Texas"
        )
        
        for key, value in insights.items():
            print(f"  {key}: {len(value)} chars")

def main():
    """Main function for setup and testing"""
    import sys
    
    # Load environment variables
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    value = value.strip('"')
                    os.environ[key] = value
    except FileNotFoundError:
        print("⚠️ .env file not found")
    
    rag_system = VectorRAGSystem()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "populate":
            rag_system.populate_knowledge_base()
        elif sys.argv[1] == "test":
            rag_system.test_rag_retrieval()
        elif sys.argv[1] == "setup":
            rag_system.populate_knowledge_base()
            rag_system.test_rag_retrieval()
    else:
        print("MongoDB Vector RAG System")
        print("Usage:")
        print("  python3 vector_rag_system.py populate  - Populate vector database")
        print("  python3 vector_rag_system.py test      - Test RAG retrieval")
        print("  python3 vector_rag_system.py setup     - Setup and test")

if __name__ == "__main__":
    main()