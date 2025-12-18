import subprocess
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


def install_repo_dependencies(repo_url: str):
    parts_of_url = repo_url.rstrip("/").split("/")
    owner, repo = parts_of_url[-2], parts_of_url[-1].replace(".git", "")

    githubusercontent_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main"

    readme = requests.get(f"{githubusercontent_url}/README.md")

    if readme.status_code != 200:
        readme = requests.get(
            githubusercontent_url.replace("/main", "/master") + "/README.md", timeout=10
        )

    requirements = requests.get(f"{githubusercontent_url}/requirements.txt", timeout=10)
    if requirements.status_code != 200:
        requirements = requests.get(
            githubusercontent_url.replace("/main", "/master") + "/requirements.txt",
            timeout=10,
        )

    if readme.status_code != 200 and requirements.status_code != 200:
        return "Sorry, no documentation found"

    prompt_content = ""
    if readme.status_code == 200:
        prompt_content += f"README.md:\n{readme.text[:5000]}\n\n"
    if requirements.status_code == 200:
        prompt_content += f"requirements.txt:\n{requirements.text}\n\n"

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # type: ignore
    model = genai.GenerativeModel("gemini-2.5-flash")  # type: ignore

    prompt = f"""Generate shell commands to:
    1. Create Python venv in the cloned directory
    2. Activate venv and install dependencies

    {prompt_content}

    IMPORTANT: Output ONLY plain text shell commands, one per line. 
    NO markdown code blocks, NO ```bash```, NO explanations, NO comments.
    os is macos and shell is zsh"""

    response = model.generate_content(prompt)
    commands = [cmd.strip() for cmd in response.text.strip().split("\n") if cmd.strip()]

    print("\nProposed commands:")
    print("-" * 50)
    for cmd in commands:
        print(f"  {cmd}")
    print("-" * 50)

    approval = input("\nExecute these commands? (y/n): ").lower()

    if approval != "y":
        return "Cancelled by user"

    print("\nExecuting commands...\n")

    for cmd in commands:
        print(f"{cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)

        if result.returncode != 0:
            print(result.stderr)
            print(f"failed at {cmd}")

    return "installation is complete"


if __name__ == "__main__":
    repo_url = input("Enter GitHub repo URL: ")
    result = install_repo_dependencies(repo_url)
    print(result)
