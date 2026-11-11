"""Job matching: skill coverage + keyword coverage (explainable), TF-IDF cosine shown separately."""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .extractor import find_skills, top_keywords

def match(resume_text: str, jd_text: str, resume_skills: list) -> dict:
    m = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True).fit_transform([resume_text, jd_text])
    sim = float(cosine_similarity(m[0], m[1])[0][0]) * 100
    jd_skills = find_skills(jd_text)
    rs = set(resume_skills)
    matched = [s for s in jd_skills if s in rs]
    missing = [s for s in jd_skills if s not in rs]
    rl = resume_text.lower()
    jd_kw = top_keywords(jd_text, 20, drop_orgs=True)
    sw = {w.rstrip("s") for s in jd_skills for w in re.findall(r"[a-z]+", s)}
    jd_kw = [k for k in jd_kw if k.rstrip("s") not in sw]   # skip words already counted as skills (e.g. "rest" from "REST API")
    if not jd_skills:
        jd_kw = []   # JD with no technical content (e.g. only a disclaimer): keyword lists would just be noise
    found = [k for k in jd_kw if k in rl]
    skill_cov = 100 * len(matched) / len(jd_skills) if jd_skills else None
    kw_cov = 100 * len(found) / len(jd_kw) if jd_kw else None
    # No recognisable skills in the JD => no honest score (better than a fake number)
    score = round(0.7 * skill_cov + 0.3 * (kw_cov if kw_cov is not None and len(jd_kw) >= 5 else skill_cov), 1) if skill_cov is not None else None
    return {"score": score, "skill_coverage": None if skill_cov is None else round(skill_cov, 1),
            "keyword_coverage": None if kw_cov is None or len(jd_kw) < 5 else round(kw_cov, 1), "text_similarity": round(sim, 1),
            "matched_skills": matched, "missing_skills": missing, "jd_skills": jd_skills,
            "keywords_found": found, "keywords_missing": [k for k in jd_kw if k not in rl],
            "jd_text": jd_text[:6000],
            "note": "Score = 70% skill coverage + 30% keyword coverage (skill coverage alone when the job description has fewer than 5 usable keywords). Indicative only; it is NOT a hiring probability."}
