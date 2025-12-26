"""
Thin wrapper around Google Gemini (google-generativeai).

Provides:
- chat(prompt, model)
- generate_json_from_prompt(prompt, model)
"""

import os
from dotenv import load_dotenv

import google.genai as genai


# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def _ensure_api_key():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured")


def chat(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Generate a plain-text response from Gemini.
    """
    _ensure_api_key()
    model_obj = genai.GenerativeModel(model)
    response = model_obj.generate_content(prompt)
    return response.text


def generate_json_from_prompt(prompt: str, model: str = "gemini-1.5-flash") -> str:
    """
    Generate structured (usually JSON) text from a prompt.
    Caller is responsible for parsing/validating JSON.
    """
    _ensure_api_key()
    model_obj = genai.GenerativeModel(model)
    response = model_obj.generate_content(prompt)
    return response.text
