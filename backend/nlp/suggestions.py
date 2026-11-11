"""Rule-based improvement suggestions (never invents experience)."""
import re
VERBS = ("built","developed","designed","implemented","led","created","improved","reduced","increased","optimized","deployed","automated")
def suggest(analysis: dict, match: dict = None) -> list:
    s = []
    if match and match["missing_skills"]:
        s.append({"type": "skills", "text": "The job description mentions skills not found in your resume: " + ", ".join(match["missing_skills"]) +
                  ". Add them only if you genuinely have this experience; otherwise consider learning them."})
    if match and match["jd_skills"] and match["keywords_missing"]:
        s.append({"type": "keywords", "text": "Relevant keywords absent from your resume: " + ", ".join(match["keywords_missing"][:8]) + ". Include them where truthful."})
    if len(analysis["summary"].split()) < 15:
        s.append({"type": "summary", "text": "Add a 2-3 line professional summary stating your focus, key skills and what you're seeking."})
    proj = " ".join(analysis["projects"] + analysis["experience"])
    if not analysis["projects"]:
        s.append({"type": "projects", "text": "No Projects section detected. Add 2-3 projects with tech stack and outcomes."})
    else:
        if not re.search(r"\d", proj):
            s.append({"type": "projects", "text": "Quantify impact in projects/experience (users, % improvement, dataset size, speed-ups)."})
        if not any(v in proj.lower() for v in VERBS):
            s.append({"type": "projects", "text": "Start bullets with strong action verbs (built, designed, optimized, deployed)."})
    c = analysis["contact"]
    if not c["email"]: s.append({"type": "format", "text": "No email address detected; add clear contact details."})
    if not c["links"]: s.append({"type": "format", "text": "Add GitHub/LinkedIn links to showcase your work."})
    if not analysis["certifications"]: s.append({"type": "format", "text": "No certifications section detected; add relevant ones if you hold any."})
    if analysis["word_count"] > 900: s.append({"type": "format", "text": "Resume is long; aim for 1 page (fresher) or 2 pages max."})
    if analysis["word_count"] < 150: s.append({"type": "format", "text": "Resume looks thin; elaborate on projects, skills and education."})
    if "skills" not in analysis["sections_found"]: s.append({"type": "format", "text": "Add a dedicated Skills section so ATS parsers can find your skills."})
    return s or [{"type": "general", "text": "Resume structure looks solid. Tailor it to each job description."}]
