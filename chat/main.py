from dotenv import load_dotenv
import os
from google import genai
from github import Github


load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
client = genai.Client(api_key=GEMINI_API_KEY)

""" This needs to be worked upon and refined """
# This is to just test how it would function


def search_projects(query):
    g = Github(GITHUB_TOKEN)
    repositories = g.search_repositories(query=query)
    return [repo.full_name for repo in repositories[:5]]


def chat(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


def main():
    user_prompt = input("Enter your prompt: ")
    projects = search_projects(user_prompt)
    num = 1
    for project in projects:
        print("Entered GitHub Projects:", num, project)
        num += 1
    print("Choose the project number you want to explore further or 0 to skip:")
    choice = int(input())
    if choice != 0 and 1 <= choice <= len(projects):
        selected_project = projects[choice - 1]
        user_prompt += (
            f"\n\nPlease provide insights on the GitHub project: {selected_project}"
        )
        response = chat(user_prompt)
        print("Response from Gemini:")


if __name__ == "__main__":
    main()
