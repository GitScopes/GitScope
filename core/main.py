"""


Usage:
python main.py <command> [args...]


Commands:
search Search GitHub repositories
summarize Summarize a repo README using Gemini
clone Clone a repository (git or ZIP fallback)
install Generate venv + install commands (Gemini-assisted)
"""

import argparse
from core.github_search import search_repos
from core.summarize import summarize_repo
from core.clone import RepoManager
from core.installer import generate_install_commands


def main():
    parser = argparse.ArgumentParser(prog="gitscope", description="GitScope CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = sub.add_parser("search", help="Search GitHub repositories")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, default=10)

    # summarize
    p_sum = sub.add_parser("summarize", help="Summarize a repo README")
    p_sum.add_argument("repo", help="Repo full name (owner/repo)")

    # clone
    p_clone = sub.add_parser("clone", help="Clone a repository")
    p_clone.add_argument("repo_url", help="HTTP(S) URL to repo")
    p_clone.add_argument("--dest", help="Destination folder", default=None)

    # install
    p_inst = sub.add_parser("install", help="Generate install commands")
    p_inst.add_argument("repo_url", help="HTTP(S) URL to repo")

    args = parser.parse_args()

    if args.command == "search":
        repos = search_repos(args.query, limit=args.limit)
        if not repos:
            print("No repositories found.")
            return
        for r in repos:
            print(f"{r['full_name']} — {r['stars']} stars — {r['url']}")

    elif args.command == "summarize":
        out = summarize_repo(args.repo)
        print("Summary:\n", out.get("summary", ""))
        print("Features:", out.get("features", []))
        print("Technologies:", out.get("technologies", []))

    elif args.command == "clone":
        manager = RepoManager()
        try:
            path = manager.clone_repo(args.repo_url, local_path=args.dest)
            print("Cloned to:", path)
        except Exception as e:
            print("Clone failed:", e)
            print("Attempting ZIP fallback...")
            try:
                zip_path = manager.download_zip(args.repo_url, save_path=args.dest)
                print("Downloaded ZIP to:", zip_path)
            except Exception as e2:
                print("ZIP fallback failed:", e2)

    elif args.command == "install":
        cmds = generate_install_commands(args.repo_url)
        print("Generated commands:")
        for c in cmds:
            print(c)


if __name__ == "__main__":
    main()
