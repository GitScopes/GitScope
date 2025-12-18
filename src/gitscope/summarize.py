"""Fetch README and summarize using Gemini.
Returns a dict: { summary, features, technologies }
"""

import requests
import json
from gitscope.ai import generate_json_from_prompt


def _fetch_readme(full_name: str) -> str:
    owner, repo = full_name.split("/")
    urls = [
        f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
    ]

    for u in urls:
        r = requests.get(u, timeout=10)
        if r.status_code == 200:
            return r.text

    raise FileNotFoundError("README not found")


def summarize_repo(full_name: str) -> dict:
    readme = _fetch_readme(full_name)

    # Truncate to keep prompt size reasonable
    if len(readme) > 10000:
        snippet = readme[:10000] + "\n..."
    else:
        snippet = readme

    prompt = f"""
    Analyze this README and respond with JSON only:
    Repository: {full_name}
    README:
    {snippet}


    Return only JSON with keys: summary, features (list), technologies (list)
    """

    try:
        raw = generate_json_from_prompt(prompt, model="gemini-1.5-flash")
        # Clean code fences
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        return {
            "summary": parsed.get("summary", ""),
            "features": parsed.get("features", []),
            "technologies": parsed.get("technologies", []),
        }
    except Exception:
        # Best-effort fallback
        return {
            "summary": "(failed to generate summary)",
            "features": [],
            "technologies": [],
        }
