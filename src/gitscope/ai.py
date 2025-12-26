"""
Thin wrapper around Google Gemini (google-generativeai).

Provides:
- chat(prompt, model)
- generate_json_from_prompt(prompt, model)
"""

import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def _ensure_api_key():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured")


def _get_client() -> genai.Client:
    """
    Create and return a GenAI client instance.
    """
    _ensure_api_key()
    return genai.Client(api_key=GEMINI_API_KEY)


def chat(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Generate a plain-text response from Gemini.
    """
    client = _get_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return response.text


def generate_json_from_prompt(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Generate structured (usually JSON) text from a prompt.
    Caller is responsible for parsing/validating JSON.
    """
    client = _get_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return response.text
