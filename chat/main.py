from dotenv import load_dotenv
import os
from google import genai

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
openai = openai.OpenAI(api_key=OPENAI_API_KEY)


def chat(prompt):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def main():
    user_prompt = input("Enter your prompt: ")
    response = chat(user_prompt)
    print("Response from OpenAI:")
    print(response)


if __name__ == "__main__":
    main()
