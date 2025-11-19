from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
client = genai.Client(api_key=GEMINI_API_KEY)


def chat(prompt):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


def main():
    user_prompt = input("Enter your prompt: ")
    response = chat(user_prompt)
    print("Response from Gemini:")
    print(response)


if __name__ == "__main__":
    main()
