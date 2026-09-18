"""Semantic Scheme Retriever module using FAISS / NumPy vector search and Sentence Transformers."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer

# Try importing FAISS; fall back gracefully if blocked by system DLL security policy
try:
    import faiss
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False


class SchemeRetriever:
    """Retriever class to find the most relevant scheme chunks for a natural language query."""

    def __init__(
        self,
        index_path: Union[str, Path] = "vectorstore/index.faiss",
        embeddings_path: Union[str, Path] = "vectorstore/embeddings.npy",
        chunks_path: Union[str, Path] = "data/processed/chunks.json",
        model_name: str = "all-MiniLM-L6-v2",
        model: Optional[SentenceTransformer] = None,
    ):
        """Initializes the retriever by loading index/embeddings, chunk data, and model."""
        self.index_path = Path(index_path)
        self.embeddings_path = Path(embeddings_path)
        self.chunks_path = Path(chunks_path)
        self.model_name = model_name

        if not self.chunks_path.exists():
            raise FileNotFoundError(f"Processed chunks file not found at '{self.chunks_path}'.")

        # Load chunk JSON records
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            self.chunks: List[Dict[str, Any]] = json.load(f)

        # Initialize vector index / embeddings matrix
        self.use_faiss = False
        self.index = None
        self.embeddings = None

        if FAISS_AVAILABLE and self.index_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                self.use_faiss = True
            except Exception:
                self.use_faiss = False

        if not self.use_faiss:
            if not self.embeddings_path.exists():
                raise FileNotFoundError(f"Embeddings file not found at '{self.embeddings_path}'.")
            self.embeddings = np.load(self.embeddings_path)

        total_vectors = self.index.ntotal if self.use_faiss else len(self.embeddings)
        if len(self.chunks) != total_vectors:
            print(
                f"Warning: Number of chunks ({len(self.chunks)}) does not match "
                f"vector count ({total_vectors})."
            )

        # Load SentenceTransformer model once
        if model is None:
            self.model = SentenceTransformer(self.model_name)
        else:
            self.model = model

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant scheme chunks for a given query."""
        if not query or not query.strip():
            return []

        total_chunks = len(self.chunks)
        if total_chunks == 0:
            return []

        effective_k = min(max(1, top_k), total_chunks)

        # Encode and normalize query vector (384 dimensions)
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)

        indices = []
        distances = []

        if self.use_faiss:
            dists, idxs = self.index.search(query_embedding, effective_k)
            indices = idxs[0]
            distances = dists[0]
        else:
            # Cosine similarity search via dot product on normalized vectors
            scores = np.dot(self.embeddings, query_embedding[0])
            top_indices = np.argsort(scores)[::-1][:effective_k]
            indices = top_indices
            distances = scores[top_indices]

        results: List[Dict[str, Any]] = []

        for idx, score in zip(indices, distances):
            if 0 <= idx < len(self.chunks):
                chunk_record = dict(self.chunks[idx])
                chunk_record["similarity_score"] = float(score)
                results.append(chunk_record)

        return results


def retrieve(
    query: str,
    top_k: int = 5,
    index_path: Union[str, Path] = "vectorstore/index.faiss",
    embeddings_path: Union[str, Path] = "vectorstore/embeddings.npy",
    chunks_path: Union[str, Path] = "data/processed/chunks.json",
    model_name: str = "all-MiniLM-L6-v2",
) -> List[Dict[str, Any]]:
    """Standalone helper function to perform retrieval."""
    retriever = SchemeRetriever(
        index_path=index_path,
        embeddings_path=embeddings_path,
        chunks_path=chunks_path,
        model_name=model_name,
    )
    return retriever.retrieve(query=query, top_k=top_k)
