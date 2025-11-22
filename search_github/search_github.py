import requests


def search_repos(
    search_input: str, sort_by: str = "stars", order: str = "desc", limit: int = 10
) -> list[dict]:
    """
    Search for GitHub repositories.

    search_input: what to search for (e.g., "python", "react")
    sort_by: how to sort results
        - "stars" (most starred)
        - "forks" (most forked)
        - "updated" (recently updated)
        - "help-wanted-issues" (most help-wanted issues)
    order: sort direction
        - "desc" (high to low)
        - "asc" (low to high)
    limit: how many results to return (default: 10)

    Returns a list of repositories with name, url, and star count.
    """
    url = f"https://api.github.com/search/repositories?q={search_input}&sort={sort_by}&order={order}"
    response = requests.get(url)
    response_in_dictionary = response.json()

    repos = []

    for item in response_in_dictionary["items"]:
        repos.append(
            {
                "name": item["name"],
                "full_name": item["full_name"],
                "url": item["html_url"],
                "stars": item["stargazers_count"],
            }
        )
    return repos[:limit]


query = input("search repos: ")
results = search_repos(query)

for repo in results:
    print(f"{repo['full_name']} - ⭐ {repo['stars']}")
    print(f"  {repo['url']}\n")
