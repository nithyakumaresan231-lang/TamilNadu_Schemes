"""FAISS vector index builder module for scheme chunk embeddings."""

from pathlib import Path
from typing import Tuple, Union
import faiss
import numpy as np


def build_faiss_index(
    embeddings: np.ndarray,
    save_path: Union[str, Path] = "vectorstore/index.faiss",
) -> faiss.IndexFlatIP:
    """Builds and saves an IndexFlatIP FAISS index from normalized embeddings.

    Args:
        embeddings: 2D NumPy array of shape (number_of_chunks, dimension).
        save_path: File path to save the FAISS index to.

    Returns:
        The constructed FAISS index.
    """
    if not isinstance(embeddings, np.ndarray):
        raise TypeError(f"Expected embeddings to be a NumPy array, got {type(embeddings).__name__}.")

    if embeddings.ndim != 2:
        raise ValueError(f"Expected 2D array of shape (N, dim), got shape {embeddings.shape}.")

    num_vectors, dimension = embeddings.shape
    print(f"Loaded embeddings: ({num_vectors}, {dimension})")

    # FAISS requires float32 format
    if embeddings.dtype != np.float32:
        embeddings = embeddings.astype(np.float32)

    print("Creating IndexFlatIP...")
    index = faiss.IndexFlatIP(dimension)

    # Add embeddings maintaining strict row-index alignment
    index.add(embeddings)
    print(f"Added {index.ntotal} vectors")

    save_file = Path(save_path)
    save_file.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(save_file))
    print(f"Saved index to {save_file}")

    return index


def load_and_verify_index(index_path: Union[str, Path] = "vectorstore/index.faiss") -> Tuple[faiss.Index, int, int]:
    """Loads a FAISS index from disk and returns (index, total_vectors, dimension).

    Args:
        index_path: Path to the FAISS index file.

    Returns:
        Tuple of (index, ntotal, d).
    """
    path = Path(index_path)
    if not path.exists():
        raise FileNotFoundError(f"FAISS index file not found at '{path}'.")

    index = faiss.read_index(str(path))
    return index, index.ntotal, index.d
