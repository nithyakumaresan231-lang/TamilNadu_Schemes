import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    "scheme_id",
    "scheme_name",
    "department",
    "category",
    "objective",
    "target_beneficiaries",
    "eligibility",
    "benefits",
    "documents_required",
    "application_process",
    "official_source_url",
]


def load_schemes(filepath: str | Path = "data/schemes.json") -> List[Dict[str, Any]]:
    """Loads and safely parses scheme records from a JSON file using pathlib.

    Args:
        filepath: Relative or pathlib Path to the schemes JSON file.

    Returns:
        List of scheme dictionary records.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file content is not valid JSON or not a JSON list.
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Error: Scheme dataset file not found at path '{path}'.")

    if not path.is_file():
        raise FileNotFoundError(f"Error: Path '{path}' is not a file.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        raise ValueError(f"Error: Failed to parse JSON in '{path}': {err}") from err

    if not isinstance(data, list):
        raise ValueError(f"Error: Expected JSON array in '{path}', but found {type(data).__name__}.")

    return data


def validate_scheme(scheme: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates that a scheme dictionary contains all required fields.

    Args:
        scheme: Dictionary representing a single scheme record.

    Returns:
        Tuple of (is_valid: bool, missing_fields: List[str]).
    """
    missing_fields = []
    scheme_id = scheme.get("scheme_id", "<MISSING_ID>")
    scheme_name = scheme.get("scheme_name", "<MISSING_NAME>")

    for field in REQUIRED_FIELDS:
        if field not in scheme or scheme[field] is None:
            missing_fields.append(field)

    if missing_fields:
        print(f"[VALIDATION FAILED] Scheme '{scheme_id}' ({scheme_name}) missing required field(s): {', '.join(missing_fields)}")
        return False, missing_fields

    return True, []
