"""Retrieval test script for the new 50-scheme dataset across 5 target categories."""

import sys
from rag.retriever import SchemeRetriever

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    retriever = SchemeRetriever(
        index_path="vectorstore/index.faiss",
        embeddings_path="vectorstore/embeddings.npy",
        chunks_path="data/processed/chunks.json",
        model_name="all-MiniLM-L6-v2",
    )

    queries = [
        ("Student Schemes", "What education scholarships and higher education schemes are available for students?"),
        ("Women Schemes", "What financial and welfare schemes are available for women and mothers?"),
        ("Agriculture Schemes", "What schemes provide subsidies, equipment, and support for farmers in agriculture?"),
        ("Health Schemes", "What medical insurance, emergency care, and healthcare schemes are available?"),
        ("Welfare / Financial Assistance", "What pension, assistance, and social security schemes provide monthly financial support?"),
    ]

    print("=== NEW DATASET RETRIEVAL VERIFICATION (50 SCHEMES / 200 CHUNKS) ===")

    for category, query in queries:
        print("\n" + "=" * 75)
        print(f"CATEGORY: {category}")
        print(f"QUERY: {query}")
        print("=" * 75)

        results = retriever.retrieve(query=query, top_k=4)
        for rank, item in enumerate(results, start=1):
            print(
                f"  {rank}. Scheme: {item.get('scheme_name')} | "
                f"Chunk Type: {item.get('chunk_type')} | "
                f"Similarity Score: {item.get('similarity_score'):.4f}"
            )


if __name__ == "__main__":
    main()
