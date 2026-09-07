"""Script to generate, save, and verify Sentence Transformer embeddings for scheme chunks."""

import json
import sys
from pathlib import Path
import numpy as np

from ingestion.embedder import generate_embeddings


def main():
    chunks_path = Path("data/processed/chunks.json")
    vectorstore_dir = Path("vectorstore")
    embeddings_path = vectorstore_dir / "embeddings.npy"

    print("=== Starting Embedding Generation Pipeline ===")

    # 1. Load chunks
    if not chunks_path.exists():
        print(f"Error: Chunks file not found at '{chunks_path}'. Run prepare_data.py first.", file=sys.stderr)
        sys.exit(1)

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks from '{chunks_path}'")

    # 2. Generate embeddings
    embeddings = generate_embeddings(chunks, model_name="all-MiniLM-L6-v2")

    print("Generated embeddings")
    print(f"Embedding shape: {embeddings.shape}")
    print(f"Embedding dimension: {embeddings.shape[1]}")

    # 3. Save embeddings
    vectorstore_dir.mkdir(parents=True, exist_ok=True)
    np.save(embeddings_path, embeddings)
    print(f"Saved embeddings to '{embeddings_path}'")

    # 4. Verify embeddings file
    print("=== Verifying Saved Embeddings File ===")
    loaded_embeddings = np.load(embeddings_path)
    print(f"Successfully loaded '{embeddings_path}'")
    print(f"Loaded embedding shape: {loaded_embeddings.shape}")
    print("=== Embedding Pipeline Completed Successfully ===")


if __name__ == "__main__":
    main()
