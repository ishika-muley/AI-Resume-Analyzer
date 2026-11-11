"""Transparent 100-point resume quality checklist (no JD needed). Every point is explained."""
import re
VERBS = set("""developed built designed implemented led created improved reduced increased optimized deployed automated integrated collaborated contributed
generated managed analyzed engineered launched migrated configured maintained tested wrote delivered established coordinated trained architected refactored
resolved streamlined translated organized presented researched mentored achieved secured""".split())
NUM = re.compile(r"\d+(?:\.\d+)?\s?%|\b\d+\s?\+|\b\d+\s+(?:users|clients|customers|records|requests|endpoints|models|members|teams|hours|ms|rows)\b", re.I)

def quality_score(a: dict) -> dict:
    items = a["projects"] + a["experience"]
    body = " ".join(items)
    verbs = sum(1 for i in items if i.split()[:1] and i.split()[0].lower() in VERBS)
    c = a["contact"]
    spec = [
     ("Email address", 5, bool(c["email"]), "Add a professional email address."),
     ("Phone number", 5, bool(c["phone"]), "Add a phone number."),
     ("Profile links (GitHub/LinkedIn)", 5, bool(c["links"]), "Add GitHub/LinkedIn links."),
     ("Professional summary", 10, len(a["summary"].split()) >= 15, "Add a 2-3 line summary of your focus and strengths."),
     ("Education section", 10, "education" in a["sections_found"], "Add an Education section."),
     ("Skills section", 10, "skills" in a["sections_found"], "Add a dedicated Skills section for ATS parsers."),
     ("Projects or experience", 10, bool(items), "Add projects or work/internship experience."),
     ("Certifications", 5, bool(a["certifications"]), "Add certifications if you hold any."),
     ("Quantified impact (numbers, %)", 10, bool(NUM.search(body)), "Add measurable results, e.g. 'served 200 users' or 'cut load time 30%'."),
     ("Action verbs in bullets (3+)", 10, verbs >= 3, "Start bullets with verbs like Built, Designed, Optimized."),
     ("Length (250-900 words)", 10, 250 <= a["word_count"] <= 900, "Aim for roughly 1 page (fresher) to 2 pages."),
     ("Enough skills listed (8+)", 10, len(a["skills"]) >= 8, "List more relevant technical skills you genuinely have."),
    ]
    checks = [{"label": l, "points": p, "earned": p if ok else 0, "passed": ok, "tip": t} for l, p, ok, t in spec]
    return {"score": sum(c["earned"] for c in checks), "checks": checks}


_HINTS = [(r"recogni|classif|detect|predict|model|accuracy|train", "accuracy or error rate (e.g. 92%) and dataset size"),
          (r"analy|extract|automat|process|generat|pars", "time saved or number of items processed (e.g. 200 resumes, 40% faster)"),
          (r"web|app|application|platform|tracker|portal|website|system|api", "number of users, records or requests handled"),
          (r"team|collaborat|hackathon", "team size, your role and the result (rank, users reached)")]

def metric_hints(a: dict, limit: int = 4) -> list:
    """Rule-based: for action-verb bullets without numbers, say WHAT could be measured (never invents a figure)."""
    out = []
    for b in a["projects"] + a["experience"]:
        if "|" in b or " — " in b or NUM.search(b) or re.search(r"\d", b) or b.split()[0].lower() not in VERBS:
            continue
        hint = next((h for pat, h in _HINTS if re.search(pat, b, re.I)), "a measurable result (users, accuracy, time saved, size of data)")
        out.append({"bullet": b, "hint": hint})
        if len(out) >= limit: break
    return out
