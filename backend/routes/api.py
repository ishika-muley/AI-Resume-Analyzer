"""REST API routes."""
import json, os, uuid
from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename
from models import db, Analysis
from parsers.resume_parser import extract_text, extract_links, ParseError
from nlp.extractor import analyze_resume, find_skills
from nlp.matcher import match as run_match
from nlp.suggestions import suggest
from nlp.scoring import quality_score, metric_hints
from nlp.ai_review import review_resume, AIError

api = Blueprint("api", __name__, url_prefix="/api")

def err(msg, code=400):
    return jsonify({"error": msg}), code

def _ext(name):
    return name.rsplit(".", 1)[1].lower() if "." in name else ""

@api.get("/health")
def health():
    return jsonify({"status": "ok"})

@api.post("/analyze")
def analyze():
    """Upload a resume (multipart 'resume'), optional 'job_description'. Extracts, analyzes, saves."""
    f = request.files.get("resume")
    if not f or not f.filename:
        return err("No file uploaded. Attach a PDF or DOCX as 'resume'.")
    ext = _ext(f.filename)
    if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
        return err("Invalid file type. Only PDF and DOCX files are allowed.")
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{uuid.uuid4().hex}.{ext}")
    f.save(path)
    try:
        text = extract_text(path, ext)
        links = extract_links(path, ext)
    except ParseError as e:
        return err(str(e), 422)
    finally:
        if os.path.exists(path): os.remove(path)   # never keep uploaded files
    analysis = analyze_resume(text, links)
    jd = (request.form.get("job_description") or "").strip()
    m = run_match(text, jd, analysis["skills"]) if jd else None
    analysis["suggestions"] = suggest(analysis, m)
    analysis["quality"] = quality_score(analysis)
    analysis["metric_hints"] = metric_hints(analysis)
    rec = Analysis(filename=secure_filename(f.filename), text=text, result_json=json.dumps(analysis),
                   match_json=json.dumps(m) if m else None, match_score=m["score"] if m else None)
    db.session.add(rec); db.session.commit()
    return jsonify(rec.to_dict()), 201

@api.post("/match/<int:aid>")
def match_job(aid):
    """Match a saved resume against a pasted job description."""
    rec = db.session.get(Analysis, aid)
    if not rec: return err("Analysis not found.", 404)
    jd = ((request.get_json(silent=True) or {}).get("job_description") or "").strip()
    if len(jd) < 20: return err("Please paste a job description (at least 20 characters).")
    analysis = json.loads(rec.result_json)
    m = run_match(rec.text, jd, analysis["skills"])
    analysis["suggestions"] = suggest(analysis, m)
    if isinstance(analysis.get("ai_review"), dict):
        analysis["ai_review"]["jd_fit"] = None      # a new job description makes the old "fit" verdict stale
    rec.result_json, rec.match_json, rec.match_score = json.dumps(analysis), json.dumps(m), m["score"]
    db.session.commit()
    return jsonify(rec.to_dict())

@api.post("/skills")
def skills():
    """Extract skills from arbitrary text."""
    t = (request.get_json(silent=True) or {}).get("text", "")
    if not t.strip(): return err("Field 'text' is required.")
    return jsonify({"skills": find_skills(t)})

@api.get("/history")
def history():
    rows = Analysis.query.order_by(Analysis.created_at.desc()).all()
    return jsonify([r.to_dict(full=False) for r in rows])

@api.get("/history/<int:aid>")
def history_item(aid):
    rec = db.session.get(Analysis, aid)
    return jsonify(rec.to_dict()) if rec else err("Analysis not found.", 404)

@api.delete("/history/<int:aid>")
def delete(aid):
    rec = db.session.get(Analysis, aid)
    if not rec: return err("Analysis not found.", 404)
    db.session.delete(rec); db.session.commit()
    return jsonify({"deleted": aid})

@api.post("/ai-review/<int:aid>")
def ai_review(aid):
    """Optional Claude-powered qualitative review. Result is stored inside the analysis JSON."""
    rec = db.session.get(Analysis, aid)
    if not rec: return err("Analysis not found.", 404)
    jd = ((request.get_json(silent=True) or {}).get("job_description") or "").strip()
    if not jd and rec.match_json:   # reuse the job description from the last match
        jd = json.loads(rec.match_json).get("jd_text", "")
    try:
        analysis = json.loads(rec.result_json)
        m = run_match(rec.text, jd, analysis["skills"]) if jd else None   # fresh, deterministic match for the JD being reviewed
        review = review_resume(rec.text, jd, analysis, m)
    except AIError as e:
        return err(str(e), e.code)
    analysis["ai_review"] = review
    rec.result_json = json.dumps(analysis); db.session.commit()
    return jsonify(rec.to_dict())
