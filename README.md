Search GitHub repositories and get AI-powered insights without leaving your terminal.

## What is this?

GitScope combines GitHub's search API with Google's Gemini AI to help you discover and understand repositories faster. Search for projects, get instant summaries, and clone repos you're interested in.

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Set up your API keys in a `.env` file:

```env
GEMINI_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
GOOGLE_API_KEY=your_key_here
```

Run the interactive chat:

```bash
python src/chat_gemini.py
```

## Features

- Search GitHub repositories by keyword, language, or topic
- AI-generated summaries of repository READMEs
- Clone repositories directly to your machine
- Interactive chat interface for project exploration

## Documentation

- [User Guide](docs/user-guide.md) - Detailed usage examples and code snippets
- [Building from Scratch](docs/setup-from-scratch.md) - How this project was built

## Getting API Keys

- **Gemini API**: [Google AI Studio](https://makersuite.google.com/app/apikey)
- **GitHub Token**: [GitHub Settings](https://github.com/settings/tokens)

## Requirements

- Python 3.8+
- Git (for cloning repositories)
- API keys for Gemini and GitHub