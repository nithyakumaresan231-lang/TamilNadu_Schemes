"""Test script for semantic scheme retrieval."""

from rag.retriever import SchemeRetriever


def main():
    print("=== Initializing Scheme Retriever ===")
    retriever = SchemeRetriever(
        index_path="vectorstore/index.faiss",
        chunks_path="data/processed/chunks.json",
        model_name="all-MiniLM-L6-v2",
    )

    test_questions = [
        "What schemes are available for students?",
        "What benefits are available for women?",
        "How can I apply for a government scheme?",
    ]

    for question in test_questions:
        print("\n" + "=" * 60)
        print(f"Question: {question}")
        print("=" * 60)

        chunks = retriever.retrieve(query=question, top_k=5)
        print(f"Top {len(chunks)} retrieved chunks:")

        for i, chunk in enumerate(chunks, start=1):
            print(f"\n{i}.")
            print(f"Scheme: {chunk.get('scheme_name', 'N/A')}")
            print(f"Chunk type: {chunk.get('chunk_type', 'N/A')}")
            print(f"Similarity: {chunk.get('similarity_score', 0.0):.4f}")
            print("Text:")
            # Indent text slightly for readability
            text_lines = chunk.get("text", "").split("\n")
            for line in text_lines:
                print(f"  {line}")


if __name__ == "__main__":
    main()
