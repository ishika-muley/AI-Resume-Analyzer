"""Rule-based + spaCy resume information extraction."""
import re, spacy
from collections import Counter
from .skills import ALL_SKILLS, LANGUAGES, ALIASES, AMBIG

_nlp = spacy.load("en_core_web_sm", disable=["lemmatizer"])
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3,5}\)?[\s-]?)\d{3,5}[\s-]?\d{3,5}")
LINK = re.compile(r"(?:https?://)?(?:www\.)?(?:linkedin\.com|github\.com)/[\w\-./]+", re.I)
SECTIONS = {"education":["education","academic","qualification"], "projects":["projects","project work"],
 "experience":["experience","employment","internship","work history","hackathon experience","hackathon","work experience","professional experience"], "certifications":["certification","certificate","courses","licenses"],
 "skills":["skills","technical skills","technologies"], "summary":["summary","objective","profile","about me"],
 "other":["achievements","leadership","positions of responsibility","extracurricular","hobbies","interests","languages","references","awards"]}

def _skill_pattern(s):
    if s in AMBIG:  # case-sensitive, exact capitalised form
        return re.compile(r"(?<![\w+#.])" + re.escape(AMBIG[s]) + r"(?![\w+#&]|\.\w)")
    return re.compile(r"(?<![\w+#.])" + re.escape(s) + r"(?![\w+#]|\.\w)", re.I)
_PATTERNS = {s: _skill_pattern(s) for s in list(ALL_SKILLS) + list(ALIASES)}

def find_skills(text: str) -> list:
    """Return canonical skills found in text."""
    found = set()
    for key, pat in _PATTERNS.items():
        if pat.search(text):
            found.add(ALIASES.get(key, key))
    return sorted(found)

BULLET = re.compile(r"^[●•▪◦■\-\*–]\s*")

# A line is a section heading only if EVERY word is heading vocabulary (so "Project Tracker" or "Experience with Python" are not headings)
_KEYS = [("projects", "project projects"), ("experience", "experience employment internship internships history"),
 ("certifications", "certification certifications certificate certificates courses licenses licences training"),
 ("skills", "skills skill proficiency competencies technologies tools expertise"), ("summary", "summary objective profile about"),
 ("education", "education educational qualification qualifications academics"),
 ("other", "achievements achievement awards honors leadership responsibility responsibilities extracurricular activities hobbies interests languages references declaration publications volunteering")]
_KEYMAP = {w: k for k, ws in _KEYS for w in ws.split()}
_MODS = set("key core technical professional academic career work relevant additional personal and of the other hackathon major mini me details positions".split())

def _heading(raw):
    if BULLET.match(raw) or len(raw) > 50 or raw.endswith((".", ",", ";")): return None
    words = re.findall(r"[a-z]+", raw.lower())
    if not words or len(words) > 6 or any(w not in _KEYMAP and w not in _MODS for w in words): return None
    return next((_KEYMAP[w] for w in words if w in _KEYMAP), None)

def split_sections(text: str) -> dict:
    """Split resume into sections by heading; merge wrapped lines; strip bullet glyphs."""
    out, cur, prev_bullet = {k: [] for k in SECTIONS}, None, False
    for line in text.splitlines():
        raw = line.strip()
        if not raw: continue
        hit = _heading(raw)
        if hit:
            cur, prev_bullet = hit, False; continue
        if cur and re.fullmatch(r"[A-Z &/]{4,40}", raw):  # unknown ALL-CAPS heading ends the section
            cur = "other"; continue
        if not cur: continue
        is_bullet = bool(BULLET.match(raw)); t = BULLET.sub("", raw); items = out[cur]
        if items and not is_bullet and (t[:1].islower() or items[-1].endswith(("–", "-", ","))
                or (prev_bullet and not items[-1].endswith((".", ":", ";")) and "|" not in t and "—" not in t)):
            items[-1] += " " + t          # wrapped continuation line
        else:
            items.append(t); prev_bullet = is_bullet
    return out

def extract_name(text: str):
    for l in [l.strip() for l in text.splitlines() if l.strip()][:5]:
        if EMAIL.search(l) or any(c.isdigit() for c in l) or len(l.split()) > 4:
            continue
        if l.replace(" ", "").replace(".", "").isalpha() and 1 < len(l.split()) <= 4:
            return l.title() if l.isupper() else l
    for e in _nlp(text[:300]).ents:
        if e.label_ == "PERSON":
            return e.text
    return None

GENERIC = {"resume","way","number","value","sign","recognition","application","development","management","science","computer","software",
 "language","stack","data","fundamentals","technology","business","career","initiative","organizations","role","platforms","generation",
 "world","process","solutions","work","job","skills","engineering","experience","knowledge","team","position","company"}
LABELS = {"github": "GitHub", "linkedin": "LinkedIn", "leetcode": "LeetCode"}

GENERIC |= {"requirements","customer","partners","collaboration","innovation","programs","end","capabilities","expertise","recruitment","description",
 "student","interest","concepts","academic","hands","education","linkedin","leetcode","required","good","trainee","test","code","clean","write","develop","methodology","engineer","have","need","looking","candidate","preferred","plus","strong","excellent","candidates","account","summary","objective","professional","technical","proficiency","final","year","key","portfolio","essentials","solution","solutions","projects","smart","system","skill","technologies","opportunity","responsibilities","ability","years","team","teams","clients","services"}

def top_keywords(text: str, n=15, drop_orgs=False) -> list:
    """Frequent nouns, excluding places/people/dates (and company names when drop_orgs) and generic words."""
    doc = _nlp(text[:20000])
    bad = {"GPE", "PERSON", "LOC", "NORP", "DATE"} | ({"ORG"} if drop_orgs else set())
    words = [t.text.lower() for t in doc if t.pos_ in ("NOUN", "PROPN") and not t.is_stop and len(t.text) > 2 and t.text.isalpha()
             and t.ent_type_ not in bad and t.text.lower() not in GENERIC]
    return [w for w, _ in Counter(words).most_common(n)]

PHONE2 = re.compile(r"\+?\(?\d[\d \t().-]{8,16}\d")

def find_phone(text: str):
    """First 10-13 digit number (spaces, dashes, brackets allowed); ignores year ranges. Top of resume is searched first."""
    for chunk in (text[:800], text):
        for m in PHONE2.finditer(chunk):
            c = m.group().strip(); d = re.sub(r"\D", "", c)
            if 10 <= len(d) <= 13 and not re.fullmatch(r"(?:\D*(?:19|20)\d{2}\D*)+", c):
                return c
    return None

def phrase_keywords(body: str, skills: list, n: int = 12) -> list:
    """Domain noun phrases from summary/projects/experience text (skills, places, names and generic words excluded)."""
    sw = {w.rstrip("s") for s in skills for w in re.findall(r"[a-z]+", s)}
    cnt = Counter()
    for ch in _nlp(body[:20000]).noun_chunks:
        words = [t.text.lower() for t in ch if t.is_alpha and not t.is_stop and t.ent_type_ not in {"GPE", "PERSON", "DATE", "NORP"}][-3:]
        if not words or any(w in {"university", "college", "institute", "school"} for w in words) or all(w.rstrip("s") in sw or w in GENERIC or len(w) < 3 for w in words):
            continue
        cnt[" ".join(words)] += 1
    return [p for p, _ in cnt.most_common(n)]

def analyze_resume(text: str, extra_links=None) -> dict:
    sec = split_sections(text)
    skills = find_skills(text)
    name = extract_name(text); nm = set((name or '').lower().split())
    em = EMAIL.search(text)
    urls = set(m.group() for m in LINK.finditer(text)) | {l for l in (extra_links or []) if l.startswith("http")}
    # Hyperlinked words like "GitHub | LinkedIn" carry no URL in the text; fall back to the labels
    links = sorted(urls) or [v for k, v in LABELS.items() if k in text.lower()]
    phone = find_phone(text)
    return {
        "name": name,
        "contact": {"email": em.group() if em else None, "phone": phone,
                    "links": links},
        "skills": skills,
        "languages": [s for s in skills if s in LANGUAGES],
        "education": sec["education"][:8], "projects": [x for x in sec["projects"] if len(x.split()) > 1][:12],
        "experience": [x for x in sec["experience"] if len(x.split()) > 1][:12], "certifications": sec["certifications"][:8],
        "summary": " ".join(sec["summary"][:3]), "keywords": phrase_keywords(" ".join(x for x in sec["summary"][:3] + sec["projects"][:12] + sec["experience"][:12] if "|" not in x), skills) or [k for k in top_keywords(text, 25) if k not in nm][:15],
        "word_count": len(text.split()), "sections_found": [k for k, v in sec.items() if v and k != "other"],
    }
