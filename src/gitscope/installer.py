"""Generate environment setup and installation commands using Gemini.


This module will fetch README/requirements.txt and ask Gemini to produce shell commands.
Commands are returned as a list of strings.
"""

import requests
from gitscope.ai import chat


def _fetch_files_from_repo_url(repo_url: str) -> dict:
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1].replace(".git", "")
    base_main = f"https://raw.githubusercontent.com/{owner}/{repo}/main"
    base_master = f"https://raw.githubusercontent.com/{owner}/{repo}/master"

    out = {}
    for path in ["README.md", "requirements.txt"]:
        for base in [base_main, base_master]:
            try:
                r = requests.get(f"{base}/{path}", timeout=10)
                if r.status_code == 200:
                    out[path] = r.text
                    break
            except Exception:
                continue
    return out


def generate_install_commands(repo_url: str) -> list[str]:
    files = _fetch_files_from_repo_url(repo_url)
    if not files:
        return ["echo 'No README or requirements found'"]

    prompt = """
    You are an expert devops engineer. Generate shell commands (zsh on macOS) to:
    1. create a python venv inside the cloned project directory
    2. activate it
    3. install dependencies from requirements.txt if present

    Respond only with plain shell commands, one per line. No explanations or markdown.

    Files:
    """
    if "README.md" in files:
        prompt += f"\nREADME:\n{files['README.md'][:5000]}\n"
    if "requirements.txt" in files:
        prompt += f"\nrequirements.txt:\n{files['requirements.txt']}\n"

    try:
        resp = chat(prompt, model="gemini-2.5-flash")
        lines = [l.strip() for l in resp.splitlines() if l.strip()]
        return lines
    except Exception:
        # Fallback conservative commands
        return [
            "python3 -m venv .venv",
            "source .venv/bin/activate",
            "pip install --upgrade pip",
            "pip install -r requirements.txt || echo 'No requirements.txt'",
        ]
