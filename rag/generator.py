"""Generator module for communicating with local Llama 3.2 1B model via Ollama HTTP API."""

import os
from pathlib import Path
from typing import Optional
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")


def generate_answer(
    prompt: str,
    base_url: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.2,
    stream: bool = False,
) -> str:
    """Sends a grounded prompt to Ollama and returns the generated text response.

    Args:
        prompt: Formatted RAG prompt string.
        base_url: Base URL for Ollama service (defaults to OLLAMA_BASE_URL env var).
        model_name: Target model name in Ollama (defaults to OLLAMA_MODEL env var).
        temperature: Generation sampling temperature.
        stream: Whether to stream the HTTP response (default: False).

    Returns:
        Generated text string from Llama.

    Raises:
        ConnectionError: If unable to reach local Ollama service.
        RuntimeError: If Ollama returns a non-200 HTTP status or error.
    """
    url = f"{(base_url or OLLAMA_BASE_URL).rstrip('/')}/api/generate"
    model = model_name or OLLAMA_MODEL

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": temperature,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
    except requests.exceptions.RequestException as err:
        raise ConnectionError(
            f"Failed to connect to local Ollama service at '{url}'. "
            f"Ensure Ollama is running (`ollama serve`). Error: {err}"
        ) from err

    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama API request failed with status code {response.status_code}: {response.text}"
        )

    result = response.json()
    return result.get("response", "").strip()
