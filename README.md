# AI Resume Analyzer

A full-stack web app that parses PDF/DOCX resumes, extracts skills and qualifications, matches them against a job description with TF-IDF + cosine similarity, and suggests honest improvements. Runs fully locally: no paid APIs or keys.

## Features
- PDF/DOCX upload with type and size (5 MB) validation and readable error messages
- Extraction: name, contact, skills, programming languages, education, projects, experience, certifications, keywords
- Job matching: similarity %, matched/missing skills, keywords found/missing (indicative score, **not** a hiring probability)
- Rule-based suggestions that never invent experience
- Dashboard with score ring, chips and cards; SQLite history with view and delete

## Tech stack
React (Vite), Tailwind CSS, lucide-react · Flask, SQLAlchemy, SQLite · spaCy, scikit-learn (TF-IDF), pdfplumber, python-docx

## Installation
```bash
cd backend
pip install -r requirements.txt          # for tests: pip install -r requirements-dev.txt
python -m spacy download en_core_web_sm
cd ../frontend && npm install
```

## Run
```bash
# terminal 1
cd backend && python app.py          # http://localhost:5001 (5000 is used by AirPlay on macOS)
# terminal 2
cd frontend && npm run dev           # http://localhost:5173 (proxies /api to Flask)
```
Tests: `cd backend && python -m pytest tests -q`

## API
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/analyze` | multipart: `resume` (file), optional `job_description`; parses, analyzes, saves |
| POST | `/api/match/<id>` | JSON `{job_description}`; match a saved resume |
| POST | `/api/skills` | JSON `{text}`; extract skills |
| GET | `/api/history` | List analyses |
| GET | `/api/history/<id>` | Full analysis |
| DELETE | `/api/history/<id>` | Delete analysis |

Errors return `{"error": "..."}` with 400 (bad input), 404, 413 (too large) or 422 (unreadable file).

## Windows
Use `python -m venv venv`, `venv\\Scripts\\activate`, then the same `pip install` / `python app.py` / `npm install` / `npm run dev` steps. Ollama and Node.js have Windows installers.

## Notes
- Uploaded resumes are analysed locally and the text is stored in `backend/analyzer.db` (git-ignored). Delete the file to clear history; do not share it.
- Rule-based extraction works best on text-based PDFs/DOCX with standard section headings. Scanned/image resumes are not supported.
- The match score is indicative, not a hiring probability. `debug=True` in `app.py` is for local use only.

## Structure
`backend/{routes,parsers,nlp,models.py,config.py,tests}` · `frontend/src/{pages,components,services}`

## Screenshots
_Add screenshots here after running the app._

## Optional AI review
**Free, local (Ollama):** install Ollama (ollama.com), run `ollama pull llama3.2`, keep it running, start the backend normally.
**Claude API (paid, more accurate):** `export ANTHROPIC_API_KEY="your-key"` before `python app.py` (optional `ANTHROPIC_MODEL`).
If a key is set Claude is used, otherwise Ollama. Force one with `AI_PROVIDER=ollama|anthropic`; Ollama options: `OLLAMA_MODEL`, `OLLAMA_HOST`.
`POST /api/ai-review/<id>` with optional `{job_description}`. Never commit API keys. Without either option the rest of the app works unchanged.
