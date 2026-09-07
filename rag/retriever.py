"""Semantic Scheme Retriever module using FAISS and Sentence Transformers."""

json_import = True
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class SchemeRetriever:
    """Retriever class to find the most relevant scheme chunks for a natural language query."""

    def __init__(
        self,
        index_path: Union[str, Path] = "vectorstore/index.faiss",
        chunks_path: Union[str, Path] = "data/processed/chunks.json",
        model_name: str = "all-MiniLM-L6-v2",
        model: Optional[SentenceTransformer] = None,
    ):
        """Initializes the retriever by loading the FAISS index, chunk data, and model.

        Args:
            index_path: Path to the vectorstore index.faiss file.
            chunks_path: Path to the processed chunks.json file.
            model_name: SentenceTransformer model name.
            model: Optional pre-loaded SentenceTransformer instance.
        """
        self.index_path = Path(index_path)
        self.chunks_path = Path(chunks_path)
        self.model_name = model_name

        if not self.index_path.exists():
            raise FileNotFoundError(f"FAISS index file not found at '{self.index_path}'.")

        if not self.chunks_path.exists():
            raise FileNotFoundError(f"Processed chunks file not found at '{self.chunks_path}'.")

        # Load FAISS index
        self.index = faiss.read_index(str(self.index_path))

        # Load chunk JSON records
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            self.chunks: List[Dict[str, Any]] = json.load(f)

        if len(self.chunks) != self.index.ntotal:
            print(
                f"Warning: Number of chunks ({len(self.chunks)}) does not match "
                f"FAISS index count ({self.index.ntotal})."
            )

        # Load SentenceTransformer model once
        if model is None:
            self.model = SentenceTransformer(self.model_name)
        else:
            self.model = model

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieves the top_k most relevant scheme chunks for a given user query.

        Args:
            query: Natural language query string.
            top_k: Number of relevant chunks to retrieve.

        Returns:
            List of chunk dictionaries augmented with 'similarity_score'.
        """
        if not query or not query.strip():
            return []

        total_chunks = self.index.ntotal
        if total_chunks == 0:
            return []

        # Handle top_k safely
        effective_k = min(max(1, top_k), total_chunks)

        # Encode and normalize query vector (384 dimensions for all-MiniLM-L6-v2)
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)

        # FAISS search
        distances, indices = self.index.search(query_embedding, effective_k)

        results: List[Dict[str, Any]] = []

        # Retrieve chunks maintaining exact FAISS ranking
        for idx, score in zip(indices[0], distances[0]):
            if 0 <= idx < len(self.chunks):
                chunk_record = dict(self.chunks[idx])
                chunk_record["similarity_score"] = float(score)
                results.append(chunk_record)

        return results


def retrieve(
    query: str,
    top_k: int = 5,
    index_path: Union[str, Path] = "vectorstore/index.faiss",
    chunks_path: Union[str, Path] = "data/processed/chunks.json",
    model_name: str = "all-MiniLM-L6-v2",
) -> List[Dict[str, Any]]:
    """Standalone helper function to perform retrieval."""
    retriever = SchemeRetriever(
        index_path=index_path,
        chunks_path=chunks_path,
        model_name=model_name,
    )
    return retriever.retrieve(query=query, top_k=top_k)
