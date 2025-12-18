"""Search GitHub repositories.


Primary approach: use GitHub REST API (no auth) but will use PyGithub when GITHUB_TOKEN is present.
"""

import os
import requests


from dotenv import load_dotenv

load_dotenv()


GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def search_repos(
    search_input: str, sort_by: str = "stars", order: str = "desc", limit: int = 10
) -> list[dict]:
    """Search GitHub and return list of dicts with name, full_name, url, stars."""
    # Use REST API
    url = f"https://api.github.com/search/repositories?q={search_input}&sort={sort_by}&order={order}&per_page={limit}"
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()

    repos = []
    for item in data.get("items", []):
        repos.append(
            {
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "url": item.get("html_url"),
                "stars": item.get("stargazers_count", 0),
            }
        )

    return repos
