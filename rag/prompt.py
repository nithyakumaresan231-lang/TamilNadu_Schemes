"""Prompt generation module for grounding Llama 3.2 1B with retrieved scheme context."""

from typing import Any, Dict, List


SYSTEM_INSTRUCTIONS = """You are an official AI Assistant for Tamil Nadu Government Schemes.
Your goal is to provide accurate and clear answers to citizens based on official government scheme records.

Guidelines:
1. Always respond in clear English.
2. Answer the question using ONLY the provided Context Information below.
3. Be direct, concise, and well-structured.
4. If the context contains the answer, summarize it clearly.
5. If the provided context does not contain sufficient details, state that the specific details are not specified in the current official records."""


def build_prompt(query: str, context_chunks: List[Dict[str, Any]]) -> str:
    """Builds a grounded RAG prompt containing system instructions, context chunks, and user query.

    Args:
        query: User's natural language question.
        context_chunks: List of retrieved chunk dictionaries from search.

    Returns:
        Formatted prompt string ready for Llama generation.
    """
    if not context_chunks:
        context_str = "No relevant scheme records were found in the database."
    else:
        formatted_blocks = []
        for idx, chunk in enumerate(context_chunks, start=1):
            scheme_name = chunk.get("scheme_name", "Unknown Scheme")
            chunk_type = chunk.get("chunk_type", "general").upper()
            dept = chunk.get("department", "Government of Tamil Nadu")
            text = chunk.get("text", "").strip()

            block = (
                f"[Document {idx} - {scheme_name} ({chunk_type})]\n"
                f"Department: {dept}\n"
                f"Content:\n{text}"
            )
            formatted_blocks.append(block)

        context_str = "\n\n".join(formatted_blocks)

    prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"--- CONTEXT ---\n"
        f"{context_str}\n"
        f"---------------\n\n"
        f"User Question: {query}\n\n"
        f"Answer:"
    )

    return prompt
