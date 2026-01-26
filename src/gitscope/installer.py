"""Generate environment setup and installation commands using Gemini.


This module will fetch README/requirements.txt and ask Gemini to produce shell commands.
Commands are returned as a list of strings.
"""

from urllib.parse import urlparse
import requests
from gitscope.ai import chat


def _extract_owner_repo(repo_url: str) -> tuple[str, str]:
    """Handle https, ssh, trailing slashes, .git, etc."""
    if repo_url.startswith("git@github.com:"):
        repo_url = repo_url.replace("git@github.com:", "https://github.com/")

    parsed = urlparse(repo_url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")

    owner = parts[0]
    repo = parts[1].replace(".git", "")
    return owner, repo


def _fetch_file(owner: str, repo: str, path: str) -> str | None:
    """Try main then master."""
    bases = [
        f"https://raw.githubusercontent.com/{owner}/{repo}/main",
        f"https://raw.githubusercontent.com/{owner}/{repo}/master",
    ]
    for base in bases:
        try:
            r = requests.get(f"{base}/{path}", timeout=10)
            if r.status_code == 200:
                return r.text
        except Exception:
            pass
    return None


def generate_install_commands(repo_url: str) -> list[str]:
    owner, repo = _extract_owner_repo(repo_url)

    readme = _fetch_file(owner, repo, "README.md")
    requirements = _fetch_file(owner, repo, "requirements.txt")
    pyproject = _fetch_file(owner, repo, "pyproject.toml")
    setup_py = _fetch_file(owner, repo, "setup.py")

    # CASE 1 — requirements.txt exists

    if requirements:
        return [
            "python3 -m venv .venv",
            "source .venv/bin/activate",
            "pip install --upgrade pip",
            "pip install -r requirements.txt",
        ]

    # Now since it is without requirements, it checks for pyproject.toml or setup.py
    if pyproject or setup_py:
        return [
            "python3 -m venv .venv",
            "source .venv/bin/activate",
            "pip install --upgrade pip",
            "pip install .",
        ]

    #It uses Gemini now
    if not readme:
        return ["echo 'No README or dependency file found'"]

    prompt = f"""
You are an expert DevOps engineer.

A repository has no requirements.txt, no pyproject.toml, and no setup.py.

Based ONLY on the README below, infer the correct shell commands (zsh on macOS) to:
1. create a python venv
2. activate it
3. install dependencies

Output ONLY plain shell commands, one per line.
No markdown. No comments. No explanations.

README:
{readme[:6000]}
"""

    try:
        resp = chat(prompt)
        resp = resp.replace("```bash", "").replace("```", "")
        lines = [l.strip() for l in resp.splitlines() if l.strip()]
        return lines
    except Exception:
        return [
            "python3 -m venv .venv",
            "source .venv/bin/activate",
            "pip install --upgrade pip",
        ]