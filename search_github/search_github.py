import requests


def search_repos(search_input):
    url = f"https://api.github.com/search/repositories?q={search_input}"
    response = requests.get(url)
    response_in_dictionary = response.json()

    repos = []

    for item in response_in_dictionary["items"][:10]:
        repos.append(
            {
                "name": item["name"],
                "full_name": item["full_name"],
                "url": item["html_url"],
                "stars": item["stargazers_count"],
            }
        )
    return repos


print(search_repos("kitty"))
