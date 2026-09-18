"""End-to-end test script for Tamil Nadu Government Schemes RAG Assistant."""

import sys
import time

# Reconfigure stdout to support UTF-8 characters on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from rag.generator import generate_answer
from rag.prompt import build_prompt
from rag.retriever import SchemeRetriever


def main():
    print("=== Initializing Tamil Nadu Schemes RAG Assistant ===")

    # Initialize retriever
    retriever = SchemeRetriever(
        index_path="vectorstore/index.faiss",
        embeddings_path="vectorstore/embeddings.npy",
        chunks_path="data/processed/chunks.json",
        model_name="all-MiniLM-L6-v2",
    )

    test_queries = [
        "What is the Pudhumai Penn scheme and who is eligible for it?",
        "What is the objective of the Naan Mudhalvan scheme?",
        "How does the Chief Minister's Breakfast Scheme work in schools?",
    ]

    for query in test_queries:
        print("\n" + "=" * 70)
        print(f"USER QUERY: {query}")
        print("=" * 70)

        start_time = time.time()

        # Step 1: Retrieve relevant scheme chunks
        retrieved_chunks = retriever.retrieve(query=query, top_k=3)
        retrieval_time = time.time() - start_time

        print(f"\n[Retrieved {len(retrieved_chunks)} relevant chunk(s) in {retrieval_time:.3f}s]:")
        for chunk in retrieved_chunks:
            print(
                f" - {chunk.get('scheme_name')} ({chunk.get('chunk_type')}) | "
                f"Similarity: {chunk.get('similarity_score'):.4f}"
            )

        # Step 2: Build grounded RAG prompt
        prompt = build_prompt(query=query, context_chunks=retrieved_chunks)

        # Step 3: Generate response via local Ollama (Llama 3.2 1B)
        gen_start = time.time()
        answer = generate_answer(prompt)
        gen_time = time.time() - gen_start

        print(f"\n[AI ASSISTANT RESPONSE (Generated in {gen_time:.2f}s)]:")
        print(answer)
        print("-" * 70)


if __name__ == "__main__":
    main()
