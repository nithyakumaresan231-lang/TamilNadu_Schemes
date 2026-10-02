"""FastAPI application backend for Tamil Nadu Government Schemes RAG Assistant."""

import logging
import json
import os
import re
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag.generator import generate_answer
from rag.prompt import build_prompt
from rag.retriever import SchemeRetriever

# Configure logger
logger = logging.getLogger("tn_schemes_api")
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI application
app = FastAPI(
    title="Tamil Nadu Government Schemes RAG API",
    description="Backend API for Tamil Nadu Government Schemes RAG Assistant",
    version="1.0.0",
)

# Configure development CORS support
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for context and schemes
GLOBAL_CONTEXT = {
    "last_scheme_name": None
}
SCHEMES_DB: List[Dict[str, Any]] = []
SCHEME_ALIAS_MAP: Dict[str, str] = {}

# Initialize SchemeRetriever and Scheme list once at application startup
try:
    retriever = SchemeRetriever(
        index_path="vectorstore/index.faiss",
        embeddings_path="vectorstore/embeddings.npy",
        chunks_path="data/processed/chunks.json",
        model_name="intfloat/multilingual-e5-small",
    )
    logger.info("SchemeRetriever initialized successfully.")

    schemes_path = os.path.join(os.path.dirname(__file__), "..", "data", "schemes.json")
    with open(schemes_path, "r", encoding="utf-8") as f:
        SCHEMES_DB = json.load(f)
        for s in SCHEMES_DB:
            original = s.get("scheme_name")
            if not original:
                continue
            name = original.lower()

            def add_alias(alias: str):
                if alias:
                    SCHEME_ALIAS_MAP[alias] = original
                    if "-" in alias:
                        SCHEME_ALIAS_MAP[alias.replace("-", "")] = original
                        SCHEME_ALIAS_MAP[alias.replace("-", " ")] = original

            add_alias(name)

            # Smart alias for long names
            if " ninaivu " in name:
                short_name = name.split(" ninaivu ")[1].strip()
                add_alias(short_name)
                add_alias(short_name.replace(" assistance", ""))
                add_alias(short_name.replace(" scheme", ""))
            elif " ammaiyar " in name:
                short_name = name.split(" ammaiyar ")[1].strip()
                add_alias(short_name)

            for alias in s.get("aliases", []):
                add_alias(alias.lower())

    logger.info(f"Loaded {len(SCHEMES_DB)} schemes into memory with {len(SCHEME_ALIAS_MAP)} aliases.")

except Exception as err:
    logger.error(f"Failed to initialize components: {err}")
    retriever = None


# Request / Response Schemas
class AskRequest(BaseModel):
    question: str = Field(..., description="User natural language question about Tamil Nadu Government Schemes")
    language: str = Field("en", description="Language mode: 'en' or 'ta'")


class AskResponse(BaseModel):
    answer: str
    sources: List[str]


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/schemes", status_code=status.HTTP_200_OK)
def get_schemes():
    """Returns the list of schemes from schemes.json."""
    if not SCHEMES_DB:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read scheme data."
        )
    return SCHEMES_DB


def detect_scheme_in_query(query: str) -> str:
    """Finds if a scheme name is explicitly mentioned in the query."""
    q_lower = query.lower()
    # Sort keys by length descending to match longest alias first
    sorted_aliases = sorted(SCHEME_ALIAS_MAP.keys(), key=len, reverse=True)
    for alias in sorted_aliases:
        if alias in q_lower:
            return SCHEME_ALIAS_MAP[alias]
    return None

def rank_and_filter_discovery_schemes(query: str, candidate_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Keywords indicating special conditions
    exclusion_conditions = {
        "widow": ["widow", "widowhood"],
        "orphan": ["orphan", "destitute"],
        "inter-caste": ["inter-caste", "inter caste", "intercaste"],
        "pilgrimage": ["pilgrimage", "jerusalem", "hajj", "christian", "muslim"],
        "weaver": ["weaver", "handloom"],
        "fisher": ["fisher", "fisherman", "fisherwoman", "fishermen", "marine"],
        "differently_abled": ["differently abled", "disabled", "handicapped", "differently-abled"],
        "farmer": ["farmer", "agriculture", "uzhavar", "crop"]
    }

    query_lower = query.lower()

    # Determine which special conditions the user actually mentioned
    mentioned_conditions = set()
    for cond_name, kw_list in exclusion_conditions.items():
        if any(kw in query_lower for kw in kw_list):
            mentioned_conditions.add(cond_name)

    # Group chunks by scheme to evaluate the scheme as a whole
    schemes_dict = {}
    for c in candidate_chunks:
        s_name = c.get("scheme_name", "Unknown")
        if s_name not in schemes_dict:
            schemes_dict[s_name] = []
        schemes_dict[s_name].append(c)

    scored_schemes = []

    for s_name, chunks in schemes_dict.items():
        # Find the full scheme data from SCHEMES_DB
        scheme_data = next((s for s in SCHEMES_DB if s.get("scheme_name") == s_name), None)
        if not scheme_data:
            continue

        # Compile all relevant fields into one text for condition checking and scoring
        fields_text = " ".join([
            str(scheme_data.get("target_beneficiaries", "")),
            str(scheme_data.get("eligibility", "")),
            str(scheme_data.get("category", "")),
            str(scheme_data.get("objective", "")),
            str(scheme_data.get("scheme_name", ""))
        ]).lower()

        # 1. EXCLUSION CHECK
        exclude = False
        for cond_name, kw_list in exclusion_conditions.items():
            if cond_name not in mentioned_conditions:
                if any(kw in fields_text for kw in kw_list):
                    exclude = True
                    break

        if exclude:
            continue

        # 2. SCORING
        score = 0
        # Simple word overlap between query and fields
        query_words = set(re.findall(r'\w+', query_lower))
        stop_words = {"i", "am", "a", "is", "there", "any", "for", "me", "what", "how", "who", "the", "in", "of", "and", "to", "do"}
        query_keywords = query_words - stop_words

        for kw in query_keywords:
            if kw in fields_text:
                score += 1

        # Also include FAISS similarity as a base score
        base_similarity = max((c.get("similarity_score", 0.0) for c in chunks), default=0.0)
        final_score = score + (base_similarity * 2) # give some weight to semantic similarity

        scored_schemes.append({
            "scheme_name": s_name,
            "chunks": chunks,
            "score": final_score
        })

    # Sort by score descending
    scored_schemes.sort(key=lambda x: x["score"], reverse=True)

    # Rebuild final chunks, taking top 2 chunks per top ranked scheme
    final_chunks = []
    # Take top 5 schemes max to avoid overwhelming context
    for s in scored_schemes[:5]:
        final_chunks.extend(s["chunks"][:2])

    return final_chunks

def is_followup_question(query: str, last_scheme_name: str = None) -> bool:
    """Very basic heuristic to check if a query might be a follow-up."""
    q_lower = query.lower()

    # 1. STRONG TOPIC DETECTION
    # If the user introduces a strong domain topic that does NOT belong to the last scheme,
    # it is a new topic, not a follow-up.
    strong_topics = {
        "handloom": ["handloom", "weaver"],
        "widow": ["widow", "remarriage"],
        "fisher": ["fisherman", "fishing", "fisheries", "marine", "fisherwoman", "fishermen"],
        "farmer": ["farmer", "agriculture", "crop", "uzhavar"],
        "construction": ["construction worker"],
        "driver": ["driver"],
        "disability": ["differently abled", "disability", "disabled", "handicapped"],
        "intercaste": ["inter-caste", "inter caste", "intercaste"],
        "girlchild": ["girl child"],
        "pilgrimage": ["pilgrimage", "jerusalem", "hajj", "christian", "muslim"]
    }

    for topic, keywords in strong_topics.items():
        if any(kw in q_lower for kw in keywords):
            if last_scheme_name:
                last_s_lower = last_scheme_name.lower()
                if not any(kw in last_s_lower for kw in keywords):
                    return False
            else:
                return False

    followup_keywords = ["how", "what", "who", "when", "where", "apply", "eligible", "eligibility", "documents", "benefit", "money"]
    words = re.findall(r'\w+', q_lower)

    # If it asks about a "scheme" generically, it's likely a new query
    if "scheme" in q_lower or "thittam" in q_lower or "yojana" in q_lower:
        if "this scheme" not in q_lower:
            return False

    return len(words) <= 7 and any(kw in q_lower for kw in followup_keywords)


@app.post("/api/chat", response_model=AskResponse, status_code=status.HTTP_200_OK)
def ask_question(request: AskRequest):
    """Processes user questions through the existing RAG pipeline."""
    # 1. Validate question
    original_question_text = request.question.strip() if request.question else ""
    if not original_question_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question must not be empty.",
        )

    if retriever is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scheme retriever is not initialized.",
        )

    try:
        # Phase 7A: Tamil Translation Layer (Incoming)
        question_text = original_question_text
        if request.language == "ta":
            from backend.translation import translate_tamil_to_english
            try:
                question_text = translate_tamil_to_english(original_question_text)
                logger.info(f"Translated TA -> EN query: {question_text}")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Translation failed. Please try again. ({str(e)})",
                )

        # CONTEXT RESOLUTION (Step 3 & 5)
        detected_scheme = detect_scheme_in_query(question_text)
        is_single_scheme_query = False
        target_scheme = None
        is_followup = False

        if detected_scheme:
            GLOBAL_CONTEXT["last_scheme_name"] = detected_scheme
            is_single_scheme_query = True
            target_scheme = detected_scheme
            logger.info(f"Detected explicit scheme mention: {detected_scheme}")
        else:
            if GLOBAL_CONTEXT["last_scheme_name"] and is_followup_question(question_text, GLOBAL_CONTEXT["last_scheme_name"]):
                target_scheme = GLOBAL_CONTEXT["last_scheme_name"]
                is_single_scheme_query = True
                is_followup = True
                question_text = f"{question_text} for {target_scheme}"
                logger.info(f"Resolved follow-up context. Modified query: {question_text}")
            else:
                GLOBAL_CONTEXT["last_scheme_name"] = None # Reset if unrelated query
                logger.info("Treating as discovery or multi-scheme query.")

        # 2. Retrieve relevant chunks
        # Increase top_k slightly for multi-scheme to get good diversity before grouping
        chunks = retriever.retrieve(query=question_text, top_k=15)

        # 3. Filter/Group chunks by scheme (Step 2 & 3)
        final_chunks = []
        if is_single_scheme_query and target_scheme:
            # Filter out unrelated schemes to prevent cross-contamination!
            final_chunks = [c for c in chunks if c.get("scheme_name") == target_scheme]
            # If nothing was found after filtering (rare, but possible), just use the top 3 and hope for the best
            if not final_chunks:
                 final_chunks = chunks[:3]
        else:
            # Discovery query (Step 4) - Use ranking layer to filter and score retrieved chunks
            final_chunks = rank_and_filter_discovery_schemes(question_text, chunks)

            # Sort final chunks by scheme name to group them together for the LLM
            final_chunks.sort(key=lambda x: x.get("scheme_name", ""))

        # 4. Extract unique scheme names from final filtered chunks for Sources (Step 8)
        sources: List[str] = []
        for chunk in final_chunks:
            scheme_name = chunk.get("scheme_name")
            if scheme_name and scheme_name not in sources:
                sources.append(scheme_name)

        # Debug logging
        logger.info("================ Debug Retrieval Log ================")
        logger.info(f"Final Query Text: {question_text}")
        logger.info(f"Retrieved {len(final_chunks)} filtered chunk(s):")
        for i, c in enumerate(final_chunks, 1):
            s_name = c.get("scheme_name", "Unknown")
            score = c.get("similarity_score", 0.0)
            text_preview = c.get("text", "").replace("\n", " ")[:100]
            logger.info(f"  [{i}] Scheme: {s_name} | Score: {score:.4f} | Preview: {text_preview}...")
        logger.info("=====================================================")

        # 5. Build existing RAG prompt
        prompt = build_prompt(
            query=question_text,
            context_chunks=final_chunks,
            is_multi_scheme=not is_single_scheme_query,
            is_followup=is_followup
        )

        # 6. Call existing Ollama generator
        answer = generate_answer(prompt)

        # 7. STRICT SOURCE FILTERING
        # Only return sources that the LLM actually mentioned in the generated answer text.
        actual_sources = []
        for s in sources:
            # We do a lowercased check for a significant chunk of the scheme name to ensure we catch variations
            # If the scheme name is short, check it directly.
            # If it is long, check if the first 3 words are in the answer, or if the whole thing is.
            s_lower = s.lower()
            ans_lower = answer.lower()
            if s_lower in ans_lower:
                actual_sources.append(s)
            else:
                words = s_lower.split()
                if len(words) >= 3:
                    # Check if the first 3 words of the scheme name are present in the answer
                    subset = " ".join(words[:3])
                    if subset in ans_lower:
                        actual_sources.append(s)

        # If filtering accidentally stripped everything (due to LLM formatting), fallback to the primary target
        if not actual_sources and sources:
            actual_sources = [sources[0]] if is_single_scheme_query else []

        # Phase 7A: English -> Tamil Translation (Outgoing)
        if request.language == "ta":
            from backend.translation import translate_english_to_tamil
            try:
                answer = translate_english_to_tamil(answer)
            except Exception as e:
                logger.error(f"Translation Error (EN->TA): {e}. Falling back to English.")

        # Return answer + strictly filtered sources
        return AskResponse(answer=answer, sources=actual_sources)

    except ConnectionError as ce:
        logger.error(f"Ollama connection error: {ce}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": "Unable to generate a response. Please make sure Ollama is running."}
        )
    except Exception as err:
        logger.error(f"Unexpected error in /api/chat endpoint: {err}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An internal server error occurred while processing your request."}
        )
