"""Script to build, save, verify, and test FAISS vector index."""

import sys
from pathlib import Path
import faiss
import numpy as np

from ingestion.build_index import build_faiss_index, load_and_verify_index


def main():
    embeddings_path = Path("vectorstore/embeddings.npy")
    index_path = Path("vectorstore/index.faiss")

    print("=== FAISS Index Build ===")

    # 1. Load embeddings.npy
    if not embeddings_path.exists():
        print(f"Error: Embeddings file not found at '{embeddings_path}'. Run generate_embeddings.py first.", file=sys.stderr)
        sys.exit(1)

    embeddings = np.load(embeddings_path)
    if not isinstance(embeddings, np.ndarray):
        print("Error: Loaded embeddings is not a NumPy array.", file=sys.stderr)
        sys.exit(1)

    # 2. Build and save index
    build_faiss_index(embeddings, save_path=index_path)

    # 3. Verify index loading
    index, ntotal, dimension = load_and_verify_index(index_path)
    print("\n=== Verification ===")
    print("Index loaded successfully")
    print(f"Number of vectors: {ntotal}")
    print(f"Vector dimension: {dimension}")

    # 4. Test search using query vector at index 0
    query_idx = 0
    query_vector = embeddings[query_idx:query_idx + 1]  # shape (1, dimension)

    k = 5
    distances, indices = index.search(query_vector, k)

    print(f"\nQuery vector index: {query_idx}")
    print(f"Top {k} results:")
    for rank, (idx, score) in enumerate(zip(indices[0], distances[0]), start=1):
        print(f"{rank}. Index: {idx} | Similarity: {score:.4f}")


if __name__ == "__main__":
    main()
