from dotenv import load_dotenv
import os
from google import genai
from github import Github
import logging
import requests 
from urllib.parse import urlparse
from git import Repo, exc 
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GEMINI_API_KEY:
    print("Please add GEMINI_API_KEY to your .env file")
    exit(1)

if not GITHUB_TOKEN:
    print("Please add GITHUB_TOKEN to your .env file")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_REPO_DIR = os.path.join(os.getcwd(), "downloaded_repos")
os.makedirs(DEFAULT_REPO_DIR, exist_ok=True)

# ======================== GITHUB SEARCH ========================

def search_repos(query: str, limit: int = 5):
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

    response = requests.get(url, headers=headers, timeout=15)
    data = response.json()

    repos = []
    for item in data.get("items", [])[:limit]:
        repos.append({
            "name": item["name"],
            "full_name": item["full_name"],
            "url": item["html_url"],
            "stars": item["stargazers_count"],
            "clone_url": item["clone_url"]
        })

    return repos

# ======================== REPO MANAGER ========================

def _get_repo_name_from_url(url):
    parsed = urlparse(url)
    name = parsed.path.split("/")[-1].replace(".git", "")
    return name or "repo"

def clone_repo(repo_url, local_path=None):

    repo_name = _get_repo_name_from_url(repo_url)

    if local_path:
        destination = os.path.join(local_path, repo_name)
    else:
        destination = os.path.join(DEFAULT_REPO_DIR, repo_name)

    if os.path.exists(destination):
        raise FileExistsError(f"Folder '{destination}' already exists")

    try:
        logger.info(f"Cloning into {destination} ...")
        Repo.clone_from(repo_url, destination)
        return destination

    except exc.GitCommandError as e:
        raise Exception(f"Git clone failed: {e}")

def download_zip_fallback(repo_url):

    repo_name = _get_repo_name_from_url(repo_url)
    zip_path = os.path.join(DEFAULT_REPO_DIR, f"{repo_name}.zip")

    clean_url = repo_url.replace(".git", "")
    zip_url = f"{clean_url}/archive/refs/heads/main.zip"

    r = requests.get(zip_url, stream=True)

    if r.status_code == 404:
        zip_url = f"{clean_url}/archive/refs/heads/master.zip"
        r = requests.get(zip_url, stream=True)

    r.raise_for_status()

    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    return zip_path

# ======================== README FETCH ========================

def get_readme(repo_full_name: str) -> str:

    owner, repo = repo_full_name.split("/")

    urls = [
        f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
    ]

    for url in urls:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.text

    raise Exception("README not found")

# ======================== GEMINI SUMMARY ========================

def summarize_with_gemini(readme: str, repo_name: str):

    if len(readme) > 10000:
        readme = readme[:10000] + "\n..."

    prompt = f"""
Analyze this README and respond with JSON ONLY.

Repository: {repo_name}

README:
{readme}

Format:
{{
  "summary": "2-3 sentence description",
  "features": ["feature1", "feature2"],
  "technologies": ["tech1", "tech2"]
}}
"""

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Clean if Gemini wrapped JSON
    text = text.replace("```json", "").replace("```", "").strip()

    return json.loads(text)


def chat_with_gemini(prompt: str):
    response = model.generate_content(prompt)
    return response.text


# ======================== CLI INTERFACE ========================

def show_repos(repos):
    print("\n🔍 Top GitHub Results:\n")

    for i, repo in enumerate(repos, 1):
        print(f"{i}. {repo['full_name']} ⭐ {repo['stars']}")
        print(f"   {repo['url']}\n")


def menu():
    print("\nChoose an option:")
    print("1. Clone repository")
    print("2. Download as ZIP")
    print("3. Summarize README with Gemini")
    print("4. Chat about repository")
    print("0. Exit")

    return input("\nEnter choice: ")


# ======================== MAIN ========================

def main():

    print("\n🚀 GitHub AI Explorer (CLI)")
    query = input("\nEnter search term: ").strip()

    repos = search_repos(query)

    if not repos:
        print("❌ No results found")
        return

    show_repos(repos)

    selection = int(input("Choose a repo number: "))

    if selection < 1 or selection > len(repos):
        print("❌ Invalid selection")
        return

    selected = repos[selection - 1]

    while True:
        choice = menu()

        if choice == "1":
            try:
                path = clone_repo(selected["clone_url"])
                print(f"\n✅ Cloned to: {path}")
            except Exception as e:
                print(f"❌ {e}")

        elif choice == "2":
            try:
                path = download_zip_fallback(selected["clone_url"])
                print(f"\n✅ ZIP saved to: {path}")
            except Exception as e:
                print(f"❌ {e}")

        elif choice == "3":
            try:
                print("\nFetching README...")
                readme = get_readme(selected["full_name"])

                print("Sending to Gemini...\n")
                result = summarize_with_gemini(readme, selected["full_name"])

                print("\n📌 SUMMARY\n", result["summary"])
                print("\n🚀 FEATURES:")
                for f in result["features"]:
                    print(" -", f)

                print("\n💻 TECHNOLOGIES:")
                for t in result["technologies"]:
                    print(" -", t)

            except Exception as e:
                print(f"❌ {e}")

        elif choice == "4":
            prompt = input("\nAsk about this repo: ")

            full_prompt = f"Repository: {selected['full_name']}\n\nUser: {prompt}"
            print("\nGemini Response:\n")
            print(chat_with_gemini(full_prompt))

        elif choice == "0":
            print("\n👋 Exiting...")
            break

        else:
            print("\n❌ Invalid option")


if __name__ == "__main__":
    main()