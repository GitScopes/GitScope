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
from gitscope.github_search import search_repos
from gitscope.summarize import summarize_repo
from gitscope.clone import RepoManager
from gitscope.installer import generate_install_commands
from gitscope.ai import ChatSession


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

    p_help = sub.add_parser("help", help="Explanations")

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

        # --- Decorated Summary UI ---
        print("\n" + "=" * 60)
        print(f" 🚀 GitScope: Repository Summary")
        print("=" * 60)
        print(f"📦 Repo: {args.repo}")

        print(f"\n📝 Summary:\n{out.get('summary', '')}")

        print(f"\n✨ Features:")
        for feat in out.get("features", []):
            print(f"  • {feat}")

        print(f"\n🛠 Technologies:")
        techs = ", ".join(out.get("technologies", []))
        print(f"  • {techs}")

        print("\n" + "=" * 60)
        print(" 💬 Interactive Session (Type 'exit' or 'quit' to stop)")
        print("=" * 60)

        # --- Interactive Chat Loop ---
        session = ChatSession()

        # Seed the session with the summary context so Gemini knows what we're talking about
        context_seed = (
            f"You just summarized the repository '{args.repo}'. "
            f"Summary: {out.get('summary')}. "
            f"Features: {out.get('features')}. "
            f"Technologies: {out.get('technologies')}. "
            "The user will now ask follow-up questions. Answer them based on this context and your general knowledge."
        )
        session.add_message("model", context_seed)

        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    print("👋 Session ended. History cleared.")
                    break
                if not user_input:
                    continue

                print("🤖 GitScope: ", end="", flush=True)
                response = session.send_message(user_input)
                print(response)
                print("\n" + "─" * 60)

            except KeyboardInterrupt:
                print("\n👋 Session ended. History cleared.")
                break

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
    elif args.command == "help":
        print(
            "The commands that can be used are: \n 1. Search (Search GitHub repositories)\n 2. Summarize (Summarize a Repo's README) \n 3. Clone (Clone a repository) \n 4. Install (Generates installation commands) "
        )


if __name__ == "__main__":
    main()
