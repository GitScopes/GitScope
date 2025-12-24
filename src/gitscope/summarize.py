"""Fetch README and summarize using Gemini.
Returns a dict: { summary, features, technologies }
"""

import requests
import json
import sys
from dotenv import load_dotenv

from gitscope.ai import generate_json_from_prompt

load_dotenv()


def _fetch_readme(full_name: str) -> str:
    owner, repo = full_name.split("/")
    urls = [
        f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
    ]

    for url in urls:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text

    raise FileNotFoundError("README not found")


def summarize_repo(full_name: str) -> dict:
    readme = _fetch_readme(full_name)

    # Truncate aggressively to avoid model failures
    snippet = readme[:8000] + "\n..." if len(readme) > 8000 else readme

    prompt = f"""
You are a JSON-only API.

Analyze the GitHub repository README below and respond with STRICT JSON ONLY.
No markdown. No commentary. No explanations.

README:
{snippet}

Return exactly this schema:
{{
  "summary": "2–3 sentence summary",
  "features": ["feature1", "feature2"],
  "technologies": ["tech1", "tech2"]
}}
"""

    try:
        raw = generate_json_from_prompt(prompt, model="gemini-1.5-flash")

        # Defensive cleanup
        raw = raw.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(raw)

        return {
            "summary": parsed.get("summary", ""),
            "features": parsed.get("features", []),
            "technologies": parsed.get("technologies", []),
        }

    except Exception as e:
        print(f"[gitscope] summarize error: {e}", file=sys.stderr)
        return {
            "summary": "(failed to generate summary)",
            "features": [],
            "technologies": [],
        }
