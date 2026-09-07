"""Data preparation pipeline script for Tamil Nadu Government Schemes RAG Assistant.

Executes the pipeline:
1. Load raw scheme dataset from data/schemes.json
2. Validate scheme records
3. Convert valid scheme records into chunks
4. Save generated chunks to data/processed/chunks.json
"""

import json
import sys
from pathlib import Path

from ingestion.chunker import create_scheme_chunks
from ingestion.loader import load_schemes, validate_scheme


def main():
    raw_data_path = Path("data/schemes.json")
    output_dir = Path("data/processed")
    output_file = output_dir / "chunks.json"

    print("=== Starting Tamil Nadu Schemes Data Pipeline ===")

    # Step 1: Load dataset
    try:
        schemes = load_schemes(raw_data_path)
        print(f"Loaded {len(schemes)} schemes from '{raw_data_path}'")
    except Exception as e:
        print(f"Failed to load schemes dataset: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Validate schemes
    valid_schemes = []
    invalid_schemes = []

    for scheme in schemes:
        is_valid, missing_fields = validate_scheme(scheme)
        if is_valid:
            valid_schemes.append(scheme)
        else:
            invalid_schemes.append((scheme, missing_fields))

    print(f"Valid schemes: {len(valid_schemes)}")
    print(f"Invalid schemes: {len(invalid_schemes)}")

    # Step 3: Create chunks
    chunks = create_scheme_chunks(valid_schemes)
    print(f"Created {len(chunks)} chunks")

    # Step 4: Save chunks
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Saved chunks to {output_file}")
    print("=== Data Pipeline Completed Successfully ===")


if __name__ == "__main__":
    main()
