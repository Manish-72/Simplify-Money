from sentence_transformers import SentenceTransformer
from transformers import pipeline
import numpy as np
from typing import List, Dict
import logging

class RAGSystem:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.qa_model = pipeline(
            "text-generation",
            model="google/flan-t5-base",
            device="cpu"
        )
        self.index = {}  # In-memory index (replace with FAISS/Pinecone in production)

    def generate_embeddings(self, text: str) -> List[float]:
        return self.embedding_model.encode(text).tolist()

    def index_document(self, file_id: str, rows: List[Dict]):
        """Index CSV rows with vector embeddings"""
        self.index[file_id] = []
        for row in rows:
            text = " ".join(f"{k}:{v}" for k, v in row.items())
            embedding = self.generate_embeddings(text)
            self.index[file_id].append({
                "text": text,
                "embedding": embedding,
                "row": row
            })

    def query(self, file_id: str, query: str, top_k: int = 3) -> Dict:
        """RAG-based query processing"""
        if file_id not in self.index:
            raise ValueError("File not indexed")
        
        query_embedding = self.generate_embeddings(query)
        similarities = []
        
        for item in self.index[file_id]:
            sim = np.dot(query_embedding, item["embedding"])
            similarities.append((sim, item))
        
        # Get top-k most relevant rows
        similarities.sort(reverse=True, key=lambda x: x[0])
        context = "\n".join([item["text"] for (_, item) in similarities[:top_k]])
        
        # Generate response
        prompt = f"""Context from CSV data:
{context}

Question: {query}
Answer:"""
        
        result = self.qa_model(prompt, max_length=200)
        return {
            "response": result[0]['generated_text'],
            "relevant_rows": [item["row"] for (_, item) in similarities[:top_k]]
        }

rag = RAGSystem()