"""Chunking module for Tamil Nadu Government Schemes dataset.

Converts structured scheme records into independent text chunks for vector embedding.
"""

from typing import Any, Dict, List


def create_scheme_chunks(schemes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Converts a list of scheme dictionaries into meaningful chunks.

    For each scheme, up to 4 chunk types are generated (where information exists):
    1. overview
    2. eligibility
    3. benefits
    4. application

    Args:
        schemes: List of validated scheme dictionaries.

    Returns:
        List of chunk dictionaries with standardized schema.
    """
    chunks: List[Dict[str, Any]] = []

    for scheme in schemes:
        scheme_id = scheme.get("scheme_id", "")
        scheme_name = scheme.get("scheme_name", "")
        department = scheme.get("department", "")
        category = scheme.get("category", "")
        source_doc = scheme.get("source_document", "")
        source_pg = scheme.get("source_page", "")
        source_url = scheme.get("official_source_url", "")

        # Common metadata dictionary for chunks
        base_metadata = {
            "scheme_id": scheme_id,
            "scheme_name": scheme_name,
            "department": department,
            "category": category,
            "source_document": source_doc,
            "source_page": source_pg,
            "source_url": source_url,
        }

        # 1. Overview Chunk
        objective = scheme.get("objective", "").strip()
        target_beneficiaries = scheme.get("target_beneficiaries", "").strip()
        if objective or target_beneficiaries:
            overview_text_parts = [f"Scheme: {scheme_name}"]
            if department:
                overview_text_parts.append(f"Department: {department}")
            if category:
                overview_text_parts.append(f"Category: {category}")
            if objective:
                overview_text_parts.append(f"Objective: {objective}")
            if target_beneficiaries:
                overview_text_parts.append(f"Target Beneficiaries: {target_beneficiaries}")

            chunks.append({
                "chunk_id": f"{scheme_id}_overview",
                "chunk_type": "overview",
                "text": "\n".join(overview_text_parts),
                **base_metadata,
            })

        # 2. Eligibility Chunk
        eligibility = scheme.get("eligibility", "").strip()
        important_conditions = scheme.get("important_conditions", "").strip()
        if eligibility or important_conditions:
            eligibility_text_parts = [f"Scheme: {scheme_name}"]
            if eligibility:
                eligibility_text_parts.append(f"Eligibility Criteria: {eligibility}")
            if important_conditions:
                eligibility_text_parts.append(f"Important Conditions: {important_conditions}")

            chunks.append({
                "chunk_id": f"{scheme_id}_eligibility",
                "chunk_type": "eligibility",
                "text": "\n".join(eligibility_text_parts),
                **base_metadata,
            })

        # 3. Benefits Chunk
        benefits = scheme.get("benefits", "").strip()
        benefit_amount = scheme.get("benefit_amount", "").strip()
        if benefits or benefit_amount:
            benefits_text_parts = [f"Scheme: {scheme_name}"]
            if benefits:
                benefits_text_parts.append(f"Benefits: {benefits}")
            if benefit_amount:
                benefits_text_parts.append(f"Benefit Amount: {benefit_amount}")

            chunks.append({
                "chunk_id": f"{scheme_id}_benefits",
                "chunk_type": "benefits",
                "text": "\n".join(benefits_text_parts),
                **base_metadata,
            })

        # 4. Application Chunk
        app_process = scheme.get("application_process", "").strip()
        app_mode = scheme.get("application_mode", "").strip()
        docs_required = scheme.get("documents_required", "").strip()
        app_url = scheme.get("official_application_url", "").strip()

        if app_process or app_mode or docs_required or app_url:
            app_text_parts = [f"Scheme: {scheme_name}"]
            if app_process:
                app_text_parts.append(f"Application Process: {app_process}")
            if app_mode:
                app_text_parts.append(f"Application Mode: {app_mode}")
            if docs_required:
                app_text_parts.append(f"Documents Required: {docs_required}")
            if app_url:
                app_text_parts.append(f"Official Application URL: {app_url}")

            chunks.append({
                "chunk_id": f"{scheme_id}_application",
                "chunk_type": "application",
                "text": "\n".join(app_text_parts),
                **base_metadata,
            })

    return chunks
