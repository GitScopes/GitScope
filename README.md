# GitScope

**GitScope** is a developer CLI tool that explores GitHub repositories, analyzes their documentation, and uses Generative AI to produce intelligent summaries, feature extraction, technology detection, and environment setup commands.

GitScope helps developers quickly understand unfamiliar repositories without manually reading long READMEs or codebases.

---

## Features

- Search GitHub repositories from the terminal
- Fetch and analyze repository README files
- Generate concise AI-powered summaries
- Extract key features of a project
- Detect technologies used in a repository
- Generate environment setup and installation commands
- Works as a clean Python CLI tool
- Powered by Gemini (Google Generative AI)

---

## Installation

Clone the repository:

```bash
git clone https://github.com/GitScopes/GitScope.git
cd GitScope
```
Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```
---

## Usage
To use the package, follow these steps:
  Install the cli client by running:
  
  ```bash 
  pip install -e .
  ```

And then,   
  ```bash
  export PYTHONPATH="$PWD/src:$PYTHONPATH"`
  ```
---

## Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
GITHUB_TOKEN=your_github_token_here
```

GitScope uses:

- Gemini API for AI summarization
- GitHub API for repository search

---

## Usage

### Search for repositories

```bash
gitscope search "python requests"
```

### Summarize a repository

```bash
gitscope summarize psf/requests
```

### Generate install commands for a repo

```bash
gitscope install https://github.com/psf/requests
```

---

## Example Output

```
Summary:
Requests is a simple, elegant HTTP library for Python...

Features:
- Simple HTTP requests
- Session management
- Authentication support

Technologies:
- Python
- HTTP
```

---
## Architecture

GitScope follows a modular CLI architecture:

- `github_search.py` → GitHub API interaction
- `summarize.py` → README analysis + AI summary
- `installer.py` → AI-generated setup commands
- `ai.py` → Gemini API wrapper
- `main.py` → CLI entry point

---

## Requirements

- Python 3.10+
- macOS / Linux
- Internet connection
- Gemini API key
- GitHub token

---
