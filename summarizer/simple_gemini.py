import google.generativeai as genai
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()



def get_readme(repo_full_name: str) -> str:
    """Fetch README from GitHub"""
    owner, repo = repo_full_name.split("/")
    
    # Try main branch
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
    response = requests.get(url, timeout=10)
    
    if response.status_code != 200:
        # Try master branch
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
        response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        return response.text
    
    raise Exception(f"README not found")


def summarize_with_gemini(readme: str, repo_name: str) -> dict:
    """Use Gemini to summarize"""
    
    # Get API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "summary": "Error: Set GEMINI_API_KEY environment variable",
            "features": [],
            "technologies": []
        }
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Truncate long READMEs
    if len(readme) > 10000:
        readme = readme[:10000] + "\n..."
    
    prompt = f"""Analyze this README and respond with JSON only:

Repository: {repo_name}
README: {readme}

Respond with ONLY this JSON (no markdown, no code blocks):
{{
    "summary": "2-3 sentence description",
    "features": ["feature1", "feature2", "feature3"],
    "technologies": ["tech1", "tech2", "tech3"]
}}"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown if present
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON
        data = json.loads(response_text)
        
        return {
            "summary": data.get("summary", ""),
            "features": data.get("features", []),
            "technologies": data.get("technologies", [])
        }
        
    except Exception as e:
        return {
            "summary": f"Error: {str(e)}",
            "features": [],
            "technologies": []
        }


def summarize_repos(repos: list[dict]) -> list[dict]:
    """
    Add summaries to repos from search_repos()
    
    Input: repos from search_repos() - each has: name, full_name, url, stars
    Output: same repos + summary, features, technologies
    """
    
    for repo in repos:
        try:
            readme = get_readme(repo['full_name'])
            data = summarize_with_gemini(readme, repo['full_name'])
            
            repo['summary'] = data['summary']
            repo['features'] = data['features']
            repo['technologies'] = data['technologies']
            
        except Exception as e:
            repo['summary'] = f"Error: {str(e)}"
            repo['features'] = []
            repo['technologies'] = []
    
    return repos


