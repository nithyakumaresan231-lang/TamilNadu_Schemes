"""Interactive CLI Assistant for Tamil Nadu Government Schemes RAG."""

import sys
from rag.generator import generate_answer
from rag.prompt import build_prompt
from rag.retriever import SchemeRetriever

# Reconfigure stdout to support UTF-8 on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    print("===============================================================")
    print("  Tamil Nadu Government Schemes — RAG AI Assistant (50 Schemes)")
    print("===============================================================")
    print("Initializing retriever and connecting to local Llama 3.2 1B...\n")

    retriever = SchemeRetriever(
        index_path="vectorstore/index.faiss",
        embeddings_path="vectorstore/embeddings.npy",
        chunks_path="data/processed/chunks.json",
        model_name="all-MiniLM-L6-v2",
    )

    print("System Ready! Type your question below (or type 'exit' to quit).\n")

    while True:
        try:
            query = input("Ask a question about TN Schemes: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                break

            print("\nSearching scheme knowledge base...")
            chunks = retriever.retrieve(query=query, top_k=3)

            print(f"Retrieved {len(chunks)} relevant scheme record(s):")
            for c in chunks:
                print(
                    f" - {c.get('scheme_name')} ({c.get('chunk_type')}) "
                    f"[Score: {c.get('similarity_score'):.4f}]"
                )

            print("\nGenerating AI response from Llama 3.2 1B...")
            prompt = build_prompt(query=query, context_chunks=chunks)
            answer = generate_answer(prompt)

            print("\n" + "=" * 60)
            print("AI ASSISTANT RESPONSE:")
            print("=" * 60)
            print(answer)
            print("=" * 60 + "\n")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError processing query: {e}\n")


if __name__ == "__main__":
    main()
