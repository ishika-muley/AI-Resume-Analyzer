# AI Resume Analyzer

A full-stack web app that analyzes a resume, scores it, matches it against a job description, and gives actionable suggestions. An optional local LLM (via Ollama) adds a written AI review, so no resume data leaves your machine.

## Features

- **Resume parsing**: upload a PDF or DOCX and extract the text.
- **Information extraction**: pulls out skills, contact details, education, and experience sections.
- **Job description matching**: compares resume skills against a job description and shows matched and missing skills.
- **Resume scoring**: an overall score with a quality checklist (structure, keywords, completeness).
- **Improvement suggestions**: specific tips on what to add or fix.
- **AI review (optional)**: a written review generated locally with Ollama (`llama3.1:8b`).
- **History**: past analyses are stored in a local SQLite database and can be revisited.

## Tech Stack

| Layer    | Technology                                   |
|----------|----------------------------------------------|
| Backend  | Python, Flask, SQLite                        |
| NLP      | Rule-based extraction and skill matching     |
| AI review| Ollama with `llama3.1:8b` (runs locally)     |
| Frontend | React, Vite, Tailwind CSS                    |
| Tests    | pytest                                       |

## Project Structure

```
AI-Resume-Analyzer/
├── backend/
│   ├── app.py              # App entry point
│   ├── config.py           # Configuration
│   ├── models.py           # Database models
│   ├── routes/api.py       # API endpoints
│   ├── parsers/            # PDF/DOCX resume parsing
│   ├── nlp/                # Extraction, matching, scoring, suggestions, AI review
│   ├── tests/              # pytest tests
│   ├── requirements.txt
│   └── requirements-dev.txt
└── frontend/
    ├── src/
    │   ├── pages/          # Landing, Analyze, Results, History
    │   ├── components/
    │   └── services/api.js
    └── package.json
```

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- [Ollama](https://ollama.com) (only needed for the AI review feature)

## Setup

### 1. Clone

```bash
git clone https://github.com/<your-username>/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Backend

macOS / Linux:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows (PowerShell):

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 3. Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL that Vite prints (usually `http://localhost:5173`).

### 4. AI review (optional)

```bash
ollama pull llama3.1:8b
ollama serve
```

Without Ollama the app still works; only the AI review section is unavailable.

## Running Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest tests -q
```

## Limitations

- Skill extraction is keyword based, so uncommon or newly coined skills may be missed.
- Scanned (image-only) PDFs are not supported unless they contain selectable text.
- The AI review depends on a local model, so quality and speed depend on your hardware.
- Scores are a guide, not a substitute for human feedback.

## Privacy

Resumes are processed locally. Nothing is sent to an external service. Do not commit real resumes or screenshots containing personal details (phone, email, address) to this repository.

## Author

Your Name: [GitHub profile](https://github.com/your-username)

## License

Add a license of your choice (for example MIT) before sharing publicly.
