"""Prompt generation module for grounded Llama 3.2 1B responses with multilingual support."""

from typing import Any, Dict, List


def build_prompt(query: str, context_chunks: List[Dict[str, Any]], is_multi_scheme: bool = False, is_followup: bool = False) -> str:
    """Build a grounded prompt using retrieved scheme chunks."""

    if not context_chunks:
        context_str = "No relevant scheme records were found."
    else:
        # Group chunks by scheme_name
        grouped_schemes = {}
        for chunk in context_chunks:
            scheme_name = chunk.get("scheme_name", "Unknown Scheme")
            if scheme_name not in grouped_schemes:
                grouped_schemes[scheme_name] = {
                    "scheme_id": chunk.get("scheme_id", "Unknown"),
                    "department": chunk.get("department", "Government of Tamil Nadu"),
                    "chunks": []
                }
            
            chunk_type = chunk.get("chunk_type", "general").upper()
            text = chunk.get("text", "").strip()
            grouped_schemes[scheme_name]["chunks"].append(f"Section: {chunk_type}\n{text}")

        formatted_blocks = []
        for idx, (scheme_name, data) in enumerate(grouped_schemes.items(), start=1):
            chunks_str = "\n".join([f"- {c}" for c in data["chunks"]])
            block = (
                f"====================================================\n"
                f"SCHEME NAME: {scheme_name}\n"
                f"DEPARTMENT: {data['department']}\n"
                f"FACTS:\n{chunks_str}\n"
                f"===================================================="
            )
            formatted_blocks.append(block)

        context_str = "\n\n".join(formatted_blocks)

    if is_followup:
        system_rules = """You are the official Tamil Nadu Government Schemes Assistant.
Answer the user's question directly using ONLY the factual information provided in the CONTEXT.

CRITICAL RULES:
1. STRICT TARGETING: The user is asking a follow-up question. Answer ONLY the specific field/information requested (e.g., application process, documents, eligibility). 
2. DO NOT generate the full scheme overview, target, or benefits unless explicitly asked.
3. If the requested information is missing, state exactly: "The available official record does not specify this information for this scheme." Do not compensate by generating unrelated fields.
4. DO NOT invent rural-area requirements, generic financial assistance, portals, forms, or deadlines unless explicitly in the text.
5. Keep the output clean and concise.

OUTPUT FORMAT:
Provide a concise answer with just the requested information. For example:
**How to apply:** [Application steps]"""
    elif is_multi_scheme:
        system_rules = """You are the official Tamil Nadu Government Schemes Assistant.
Answer the user's question directly using ONLY the factual information provided in the CONTEXT.

CRITICAL RULES:
1. Ground your answer strictly in CONTEXT facts. Do not invent facts, URLs, documents, application processes, or eligibility.
2. If the user asks to verify a claim (e.g. "Does the government provide 50000?"), answer DIRECTLY based on context. If the records do not support the claim, clearly state: "The available official records do not support this claim."
3. List all the relevant schemes provided in the context. Do not invent unrelated schemes.
4. Keep the output clean. Do not output internal brackets or template instructions.

OUTPUT FORMAT:
Use a clean markdown list for the schemes. For each scheme, briefly state who it is for and what the benefit is, ONLY if the information is present in the context."""
    else:
        system_rules = """You are the official Tamil Nadu Government Schemes Assistant.
Answer the user's question directly using ONLY the factual information provided in the CONTEXT.

CRITICAL RULES:
1. Ground your answer strictly in CONTEXT facts. Do not invent facts, URLs, documents, or procedures.
2. If the user asks to verify a claim (e.g. "Does the government provide 50000?"), answer DIRECTLY based on context. If the records do not support the claim, state: "The available official records do not support this claim."
3. IMPLEMENTATION IS NOT APPLICATION: If a scheme is implemented through schools or departments, do NOT invent an application process.
4. If requested information is missing, do not generate a section for it. Just omit it.
5. Keep the output clean. Do not output internal brackets or template instructions.

OUTPUT FORMAT:
Use a clean markdown structure. Include the Scheme Name as a heading. Use bold labels like Overview, Target, Benefit, Eligibility, and How to apply. ONLY include a label if you have actual facts from the context. If a detail is missing, skip the label entirely."""

    prompt = f"""{system_rules}

CONTEXT (OFFICIAL GOVERNMENT RECORDS):
{context_str}

USER QUESTION:
{query}

ANSWER:
"""

    return prompt