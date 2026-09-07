"""Embedding generation module using Sentence Transformers."""

from typing import Any, Dict, List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer


def generate_embeddings(
    chunks: List[Dict[str, Any]],
    model_name: str = "all-MiniLM-L6-v2",
    model: Optional[SentenceTransformer] = None,
) -> np.ndarray:
    """Generates normalized vector embeddings for text chunks.

    Args:
        chunks: List of chunk dictionaries, each containing a 'text' key.
        model_name: Name of the SentenceTransformer model to use.
        model: Optional pre-loaded SentenceTransformer instance.

    Returns:
        NumPy float32 array of shape (number_of_chunks, embedding_dimension).
    """
    if not chunks:
        print("Warning: Received empty list of chunks.")
        return np.empty((0, 384), dtype=np.float32)

    if model is None:
        print(f"Loading SentenceTransformer model '{model_name}'...")
        model = SentenceTransformer(model_name)

    texts = [chunk["text"] for chunk in chunks]

    if not texts:
        raise ValueError("Error: None of the provided chunks contain a 'text' field.")

    print(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.astype(np.float32)
