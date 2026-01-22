"""
Thin wrapper around Google Gemini (google-generativeai).

Provides:
- chat(prompt, model)
- generate_json_from_prompt(prompt, model)
"""

import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)

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


class ChatSession:
    """
    Manages a chat session with history saved to a local file.
    The file is cleared on initialization to ensure session-only memory.
    """
    def __init__(self, history_file: str = "history.json"):
        self.history_file = history_file
        self.history: List[Dict] = []
        self._clear_history()

    def _clear_history(self):
        with open(self.history_file, "w") as f:
            json.dump([], f)
        self.history = []

    def _save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def add_message(self, role: str, text: str):
        # Gemini roles are 'user' and 'model'
        gemini_role = "user" if role.lower() == "user" else "model"
        self.history.append({"role": gemini_role, "parts": [{"text": text}]})
        self._save_history()

    @retry(
        retry=retry_if_exception_type(errors.ClientError),
        wait=wait_random_exponential(multiplier=1, max=60),
        stop=stop_after_attempt(5),
    )
    def send_message(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        client = _get_client()
        
        # Add user message to local history first
        self.add_message("user", prompt)

        # Send the entire history to Gemini
        try:
            response = client.models.generate_content(
                model=model,
                contents=self.history
            )
            response_text = response.text
            # Add model response to history
            self.add_message("model", response_text)
            return response_text
            
        except errors.ClientError as e:
            if e.code == 429:
                print("(Rate limit hit, retrying...)", end=" ", flush=True)
            raise e


@retry(
    retry=retry_if_exception_type(errors.ClientError),
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def chat(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Generate a plain-text response from Gemini.
    """
    client = _get_client()

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except errors.ClientError as e:
         if e.code == 429:
            print("(Rate limit hit, retrying...)", end=" ", flush=True)
         raise e


@retry(
    retry=retry_if_exception_type(errors.ClientError),
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
)
def generate_json_from_prompt(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Generate structured (usually JSON) text from a prompt.
    Caller is responsible for parsing/validating JSON.
    """
    client = _get_client()

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except errors.ClientError as e:
         if e.code == 429:
            print("(Rate limit hit, retrying...)", end=" ", flush=True)
         raise e