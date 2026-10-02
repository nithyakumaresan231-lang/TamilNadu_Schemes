import json
import os
import re

from deep_translator import MyMemoryTranslator


# ============================================================
# LOAD SCHEME DATABASE
# ============================================================

SCHEMES_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "schemes.json",
)

try:
    with open(SCHEMES_PATH, "r", encoding="utf-8") as f:
        SCHEMES_DB = json.load(f)

    print(
        f"[TRANSLATION] Loaded {len(SCHEMES_DB)} schemes "
        f"from schemes.json"
    )

except Exception as e:
    SCHEMES_DB = []

    print(
        f"[TRANSLATION] Failed to load schemes.json: {e}"
    )


# ============================================================
# BASIC TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize ordinary English text for comparison.
    """

    if not text:
        return ""

    text = text.lower().strip()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def normalize_latin(text: str) -> str:
    """
    Normalize transliterated Latin text.

    This is used only for scheme detection.
    It does NOT modify the user's actual query.
    """

    if not text:
        return ""

    text = text.lower()

    replacements = {
        "è": "e",
        "é": "e",
        "ē": "e",
        "ā": "a",
        "ī": "i",
        "ū": "u",
        "ò": "o",
        "ō": "o",
        "dh": "th",
        "gh": "g",
        "bh": "b",
        "zh": "z",
        "rr": "r",
        "~n": "n",
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new,
        )

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# TAMIL TRANSLITERATION
# ============================================================

def transliterate_tamil(text: str) -> str:
    """
    Convert Tamil script into Latin transliteration.

    Used only for detecting known scheme names.
    """

    if not text:
        return ""

    try:
        from indic_transliteration import sanscript

        result = sanscript.transliterate(
            text,
            sanscript.TAMIL,
            sanscript.ITRANS,
        )

        return normalize_latin(result)

    except Exception as e:
        print(
            f"[TRANSLATION] Tamil transliteration failed: {e}"
        )

        return ""


# ============================================================
# SCHEME DATABASE HELPERS
# ============================================================

def get_scheme_records():
    """
    Return normalized scheme records from schemes.json.
    """

    records = []

    for scheme in SCHEMES_DB:

        scheme_id = str(
            scheme.get(
                "scheme_id",
                "",
            )
        ).strip()

        scheme_name = str(
            scheme.get(
                "scheme_name",
                "",
            )
        ).strip()

        aliases = scheme.get(
            "aliases",
            [],
        )

        if not isinstance(
            aliases,
            list,
        ):
            aliases = []

        aliases = [
            str(alias).strip()
            for alias in aliases
            if str(alias).strip()
        ]

        if scheme_name:

            records.append(
                {
                    "scheme_id": scheme_id,
                    "scheme_name": scheme_name,
                    "aliases": aliases,
                }
            )

    return records


# ============================================================
# DETECT SCHEME FROM TAMIL
# ============================================================
def detect_scheme_from_tamil(text):
    """
    Detect a government scheme directly from Tamil text.

    Conservative strategy:
    - Prefer distinctive Tamil keywords from the scheme name/aliases.
    - Require multiple meaningful matches.
    - Avoid selecting a scheme from generic words such as
      "திட்டம்", "உதவி", "யார்", etc.
    """

    normalized_query = normalize_text(text)

    # Generic Tamil words that are not useful for scheme identification
    generic_words = {
        "திட்டம்",
        "திட்டத்தின்",
        "திட்டத்திற்கு",
        "திட்டத்தில்",
        "உதவி",
        "உதவித்",
        "உதவிக்கு",
        "நன்மை",
        "நன்மைகள்",
        "வழங்கப்படுகின்றன",
        "யார்",
        "என்ன",
        "எப்படி",
        "எவ்வாறு",
        "எந்த",
        "தகுதி",
        "தகுதியானவர்கள்",
        "பெற",
        "பெறலாம்",
        "வழங்கப்படும்",
    }

    query_words = set(normalized_query.split())

    meaningful_query_words = {
        word for word in query_words
        if len(word) >= 3 and word not in generic_words
    }

    best_record = None
    best_score = 0.0

    for record in get_scheme_records():
        scheme_id = record.get("scheme_id") or record.get("id")
        scheme_name = record.get("scheme_name", "")
        aliases = record.get("aliases", [])

        if isinstance(aliases, str):
            aliases = [aliases]

        candidate_text = " ".join(
            [scheme_name] + aliases
        )

        candidate_normalized = normalize_text(candidate_text)
        candidate_words = set(candidate_normalized.split())

        meaningful_candidate_words = {
            word for word in candidate_words
            if len(word) >= 3 and word not in generic_words
        }

        if not meaningful_candidate_words:
            continue

        # Exact meaningful-word overlap
        overlap = meaningful_query_words & meaningful_candidate_words

        if not overlap:
            continue

        # Basic overlap score
        overlap_score = (
            len(overlap) / min(
                len(meaningful_query_words),
                len(meaningful_candidate_words)
            )
        ) * 100

        # Strong bonus when multiple distinctive concepts match
        score = overlap_score

        if len(overlap) >= 2:
            score += 20

        if len(overlap) >= 3:
            score += 15

        if score > best_score:
            best_score = score
            best_record = record

    # Conservative threshold
    if best_record is not None and best_score >= 70:
        print(
            f"[TRANSLATION DEBUG] Tamil scheme detected: "
            f"{best_record.get('scheme_id') or best_record.get('id')} "
            f"- {best_record.get('scheme_name')} "
            f"(score: {best_score:.1f})"
        )
        return best_record

    print(
        f"[TRANSLATION DEBUG] No confident Tamil scheme detected. "
        f"Best score: {best_score:.1f}"
    )

    return None


# ============================================================
# DETECT SCHEME FROM TRANSLATED ENGLISH
# ============================================================
def detect_scheme_from_english(english_text: str):
    """
    Detect a government scheme from translated English text.

    Uses the scheme name plus existing descriptive fields from
    schemes.json. Matching is conservative and requires distinctive
    evidence rather than generic words such as "assistance" or
    "scheme".
    """

    if not english_text:
        return None
        
    normalized_query = normalize_text(english_text)

    # Known machine-translation phrase for TN071 and TN002.
    if (
        "success entrepreneurship programme"
        in normalized_query
        or
        "success entrepreneurship program"
        in normalized_query
    ):
        for scheme in SCHEMES_DB:
            if scheme.get("scheme_id") == "TN071":
                print(
                    "[TRANSLATION DEBUG] "
                    "English scheme detected: "
                    "TN071 - "
                    f"{scheme.get('scheme_name')} "
                    "(known translation phrase)"
                )
                return scheme

    if (
        "tamil muttalavan" in normalized_query
        or "tamil muttavan" in normalized_query
        or "tamil puthalavan" in normalized_query
        or "tamil pudalvan" in normalized_query
    ):
        for scheme in SCHEMES_DB:
            if scheme.get("scheme_id") == "TN002":
                print(
                    "[TRANSLATION DEBUG] "
                    "English scheme detected: "
                    "TN002 - "
                    f"{scheme.get('scheme_name')} "
                    "(known translation phrase)"
                )
                return scheme

    try:
        from thefuzz import fuzz

        query = normalize_text(english_text)

        generic_words = {
            "scheme",
            "schemes",
            "assistance",
            "financial",
            "benefit",
            "benefits",
            "provided",
            "provide",
            "provides",
            "what",
            "who",
            "how",
            "is",
            "are",
            "the",
            "for",
            "to",
            "of",
            "under",
            "from",
            "with",
            "eligible",
            "eligibility",
            "available",
            "given",
            "offered",
            "get",
            "gets",
            "can",
            "may",
            "support",
            "programme",
            "program",
        }

        query_words = set(
            re.findall(r"[a-z]+", query)
        )

        meaningful_query_words = (
            query_words - generic_words
        )

        if not meaningful_query_words:
            print(
                "[TRANSLATION DEBUG] "
                "No meaningful English scheme keywords found."
            )
            return None

        best_scheme = None
        best_score = 0.0

        for raw_scheme in SCHEMES_DB:

            scheme_id = str(
                raw_scheme.get("scheme_id", "")
            ).strip()

            scheme_name = str(
                raw_scheme.get("scheme_name", "")
            ).strip()

            aliases = raw_scheme.get("aliases", [])

            if isinstance(aliases, str):
                aliases = [aliases]

            # Use existing descriptive fields from the dataset.
            searchable_fields = [
                scheme_name,
                *aliases,
                str(raw_scheme.get("category", "")),
                str(raw_scheme.get("target_beneficiaries", "")),
                str(raw_scheme.get("benefits", "")),
                str(raw_scheme.get("objective", "")),
            ]

            candidate_text = " ".join(
                x for x in searchable_fields if x
            )

            candidate_normalized = normalize_text(
                candidate_text
            )

            candidate_words = set(
                re.findall(
                    r"[a-z]+",
                    candidate_normalized
                )
            )

            meaningful_candidate_words = (
                candidate_words - generic_words
            )

            matched_words = (
                meaningful_query_words
                & meaningful_candidate_words
            )

            overlap_count = len(matched_words)

            if overlap_count == 0:
                continue

            # ----------------------------------------------------
            # Base score from distinctive word overlap.
            # ----------------------------------------------------

            overlap_score = (
                overlap_count
                / max(
                    len(meaningful_query_words),
                    1
                )
            ) * 100

            score = overlap_score

            # ----------------------------------------------------
            # Strong bonus for multiple distinctive matches.
            # ----------------------------------------------------

            if overlap_count >= 2:
                score += 20

            if overlap_count >= 3:
                score += 15

            # ----------------------------------------------------
            # Extra confidence when the words occur together in
            # the scheme's descriptive information.
            # ----------------------------------------------------

            if (
                "widow" in meaningful_query_words
                and "remarriage" in meaningful_query_words
            ):
                if (
                    "widow" in candidate_normalized
                    and "remarriage" in candidate_normalized
                ):
                    score += 25

            # ----------------------------------------------------
            # Phrase similarity is only supporting evidence.
            # ----------------------------------------------------

            phrase_score = fuzz.partial_ratio(
                query,
                candidate_normalized
            )

            # Do not allow generic phrase similarity alone
            # to identify a scheme.
            if overlap_count >= 2:
                score = max(
                    score,
                    min(phrase_score, score + 10)
                )

            if score > best_score:
                best_score = score
                best_scheme = raw_scheme

        # --------------------------------------------------------
        # Conservative threshold.
        # --------------------------------------------------------

        if (
            best_scheme
            and best_score >= 70
        ):
            print(
                "[TRANSLATION DEBUG] "
                f"English scheme detection score: "
                f"{best_score:.1f}"
            )

            print(
                "[TRANSLATION DEBUG] "
                f"English detected scheme: "
                f"{best_scheme['scheme_id']} - "
                f"{best_scheme['scheme_name']}"
            )

            return best_scheme

        print(
            "[TRANSLATION DEBUG] "
            f"No confident English scheme detected. "
            f"Best score: {best_score:.1f}"
        )

        return None

    except Exception as e:

        print(
            "[TRANSLATION DEBUG] "
            f"English scheme detection failed: {e}"
        )

        return None


# ============================================================
# RESTORE CANONICAL SCHEME NAME
# ============================================================

def restore_canonical_scheme_name(
    translated_text: str,
    detected_scheme,
):
    """
    Ensure that the final English query contains the
    official scheme name from schemes.json.

    We never delete question words.
    """

    if (
        not translated_text
        or not detected_scheme
    ):
        return translated_text

    canonical = detected_scheme[
        "scheme_name"
    ]

    result = translated_text

    # --------------------------------------------------------
    # If the canonical name is already present, do nothing.
    # --------------------------------------------------------

    if normalize_text(
        canonical
    ) in normalize_text(
        result
    ):

        return result

    # --------------------------------------------------------
    # Replace known generic machine translations.
    # --------------------------------------------------------

    generic_patterns = [
        r"success entrepreneurship programme",
        r"success entrepreneurship program",
        r"successful entrepreneur scheme",
        r"successful entrepreneurship scheme",
        r"tamil muttalavan",
        r"tamil muttavan",
        r"tamil puthalavan",
        r"tamil pudalvan",
    ]

    replaced = False

    for pattern in generic_patterns:

        new_result = re.sub(
            pattern,
            canonical,
            result,
            flags=re.IGNORECASE,
        )

        if new_result != result:

            result = new_result
            replaced = True

            break

    if replaced:
        return result

    # --------------------------------------------------------
    # If no generic phrase was safely replaceable,
    # append the canonical scheme name.
    #
    # This preserves the entire translated question.
    # --------------------------------------------------------

    return (
        f"{result} "
        f"[{canonical}]"
    )


# ============================================================
# TAMIL → ENGLISH
# ============================================================

def translate_tamil_to_english(
    text: str,
) -> str:
    """
    Translate Tamil input to English.

    Pipeline:

        Tamil
          ↓
        MyMemory translation
          ↓
        Scheme detection
          ↓
        Canonical scheme restoration
          ↓
        English RAG query

    IMPORTANT:
    The original Tamil sentence is NEVER modified
    before translation.
    """

    if not text or not text.strip():
        return text

    original_text = text.strip()

    try:

        translator = MyMemoryTranslator(
            source="ta-IN",
            target="en-GB",
            email="tester_phase7@example.com",
        )

        # ----------------------------------------------------
        # 1. Translate COMPLETE Tamil question.
        # ----------------------------------------------------

        translated = translator.translate(
            original_text
        )

        if not translated:
            raise ValueError(
                "Tamil-to-English translation returned empty text."
            )

        print()
        print("[TRANSLATION DEBUG]")
        print(
            "Original Tamil :",
            original_text,
        )
        print(
            "Raw English    :",
            translated,
        )

        # ----------------------------------------------------
        # 2. First try Tamil-based scheme detection.
        # ----------------------------------------------------

        detected_scheme = detect_scheme_from_tamil(
            original_text
        )

        # ----------------------------------------------------
        # 3. If Tamil detection fails, try the translated
        #    English question.
        # ----------------------------------------------------

        if not detected_scheme:

            detected_scheme = detect_scheme_from_english(
                translated
            )

        # ----------------------------------------------------
        # 4. Restore canonical dataset scheme name.
        # ----------------------------------------------------

        translated = restore_canonical_scheme_name(
            translated,
            detected_scheme,
        )

        print(
            "Final English  :",
            translated,
        )

        print(
            "[END TRANSLATION DEBUG]"
        )
        print()

        return translated

    except Exception as e:

        print(
            "[TRANSLATION ERROR - TA→EN]",
            repr(e),
        )

        raise ValueError(
            "Failed to translate Tamil input "
            f"to English: {repr(e)}"
        )


# ============================================================
# ENGLISH → TAMIL
# ============================================================

def translate_english_to_tamil(
    text: str,
) -> str:
    """
    Translate English RAG answer to Tamil.
    """

    if not text or not text.strip():
        return text

    try:

        translator = MyMemoryTranslator(
            source="en-GB",
            target="ta-IN",
            email="tester_phase7@example.com",
        )

        # ----------------------------------------------------
        # Avoid Unicode encoding issues with ₹ in the
        # external translation service.
        # ----------------------------------------------------

        text = text.replace(
            "₹",
            "Rs.",
        )

        lines = text.split(
            "\n"
        )

        translated_lines = []

        for line in lines:

            # Preserve blank lines.
            if not line.strip():

                translated_lines.append(
                    ""
                )

                continue

            # ------------------------------------------------
            # MyMemory has a practical character limit.
            # ------------------------------------------------

            if len(line) > 499:

                sub_chunks = [
                    line[i:i + 499]
                    for i in range(
                        0,
                        len(line),
                        499,
                    )
                ]

                translated_sub = []

                for chunk in sub_chunks:

                    translated_sub.append(
                        translator.translate(
                            chunk
                        )
                    )

                translated_lines.append(
                    "".join(
                        translated_sub
                    )
                )

            else:

                translated_lines.append(
                    translator.translate(
                        line
                    )
                )

        return "\n".join(
            translated_lines
        )

    except Exception as e:

        print(
            "[TRANSLATION ERROR - EN→TA] "
            "Failed to translate:",
            repr(e),
        )

        # Safe fallback:
        # never fabricate a Tamil answer.
        return text