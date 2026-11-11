from nlp.extractor import analyze_resume
T = """Test User
test@mail.com
GitHub | LinkedIn
Projects
Built a tracker with Flask for 100 users
HACKATHON EXPERIENCE
Smart India Hackathon 2025 finalist
ACHIEVEMENTS
Won a coding contest
Education
B.Tech CSE
HSC - 77.67% 2023
SSC - 88.8% 2021
"""
def test_sections_and_links():
    a = analyze_resume(T)
    assert not any("Hackathon" in x for x in a["projects"])
    assert any("Hackathon" in x for x in a["experience"])
    assert not any("contest" in x for x in a["experience"])
    assert len(a["education"]) == 3          # digit lines must not end the section
    assert a["contact"]["links"] == ["GitHub", "LinkedIn"]
def test_url_links():
    assert analyze_resume(T, ["https://github.com/x", "mailto:a@b.c"])["contact"]["links"] == ["https://github.com/x"]

from nlp.extractor import find_skills, split_sections
from nlp.matcher import match
from nlp.scoring import quality_score

def test_ambiguous_skills_case_sensitive():
    assert "go" not in find_skills("We go to market and excel in sales; R&D team")
    assert {"go", "r", "c"} <= set(find_skills("Skills: Go, R, C, Java"))
    assert "c" not in find_skills("C++ developer") and "c++" in find_skills("C++ developer")

def test_wrapped_bullets_merged():
    t = "Experience\n● Collaborated with a team to design a digital solution for streamlining\npatient management and therapy scheduling.\n● Built a tool.\n"
    e = split_sections(t)["experience"]
    assert len(e) == 2 and e[0].startswith("Collaborated") and e[0].endswith("scheduling.")

def test_no_fake_score_without_jd_skills():
    m = match("Python Flask developer with SQL", "Disclaimer: this position is open only for citizens. No guarantee of offer.", ["python"])
    assert m["score"] is None and m["skill_coverage"] is None
    assert m["keyword_coverage"] is None and m["keywords_missing"] == [] and m["keywords_found"] == []

def test_score_formula_and_quality():
    m = match("Python Flask SQL developer", "Need Python, Flask and Docker experience", ["python", "flask", "sql"])
    assert round(m["skill_coverage"]) == 67 and 0 < m["score"] <= 100
    q = quality_score(analyze_resume(T))
    assert 0 <= q["score"] <= 100 and sum(c["points"] for c in q["checks"]) == 100


A = """RAHUL KUMAR SHARMA
rahul@gmail.com | +91-98765-43210 | Pune
PROFESSIONAL SUMMARY
Final year B.E. student seeking a backend developer role, with experience in Java and Spring Boot.
KEY SKILLS
Java, Spring Boot, MySQL
ACADEMIC PROJECTS
Library System
- Developed REST APIs using Spring Boot for 300 students
INTERNSHIP EXPERIENCE
Software Intern, TechSoft (Jun 2025 - Aug 2025)
- Fixed 25+ bugs in a Java microservice
EDUCATIONAL QUALIFICATIONS
B.E. Computer Engineering, Pune University, 2026
CERTIFICATIONS & ACHIEVEMENTS
Oracle Certified Java Associate
"""
def test_heading_variants_and_phone():
    a = analyze_resume(A)
    assert set(a["sections_found"]) == {"summary", "skills", "projects", "experience", "education", "certifications"}
    assert a["contact"]["phone"] == "+91-98765-43210" and a["projects"][0] == "Library System" and len(a["experience"]) == 2
    b = analyze_resume("Skills & Tools\nPython, SQL\nTechnical Proficiency\nGit\nAcademic Projects\nTracker app built in Flask\nProject Tracker\nBuilt it")
    assert "skills" in b["sections_found"] and "projects" in b["sections_found"]
    assert any("Project Tracker" in x for x in b["projects"])      # a project title is not a heading

def test_phone_formats():
    from nlp.extractor import find_phone
    assert find_phone("Amit\namit@mail.com 9123456780") == "9123456780"
    assert find_phone("Priya | (555) 123-4567 | x") == "(555) 123-4567"
    assert find_phone("B.Tech 2019-2023 2024 CGPA 8.92/10") is None


def test_jd_keywords_exclude_skill_words_and_filler():
    m = match("Python Flask developer", "Software Engineer Trainee. Required skills: Python, REST APIs. Good to have: Docker, Agile methodology. Develop and test backend services.", ["python", "flask"])
    for bad in ("rest", "agile", "required", "trainee", "methodology", "test"):
        assert bad not in m["keywords_found"] + m["keywords_missing"]
    assert "rest api" in m["missing_skills"] and "jd_text" in m


def test_few_keywords_do_not_distort_score():
    m = match("Python Flask developer", "Need Python, Flask, Docker and Git. Backend services.", ["python", "flask"])
    assert m["skill_coverage"] == 50.0 and m["score"] == 50.0 and m["keyword_coverage"] is None     # 1 keyword must not swing the score


def test_resume_keywords_exclude_skills():
    assert "java" not in analyze_resume(A)["keywords"] and "spring" not in analyze_resume(A)["keywords"]


def test_single_word_noise_lines_dropped():
    a = analyze_resume("Experience\nSoftware\nBuilt a tool for 10 users in Python\n")
    assert a["experience"] == ["Built a tool for 10 users in Python"]


from nlp.scoring import metric_hints
M = """Projects
Sign Tracker | Python, OpenCV
- Developed a real-time gesture recognition system using MediaPipe to detect hand movements.
- Built a web application to manage 200 job applications and track status.
- Generated resume insights to evaluate skill relevance.
"""
def test_metric_hints_and_phrase_keywords():
    a = analyze_resume(M)
    h = metric_hints(a)
    assert len(h) == 2 and "accuracy" in h[0]["hint"] and "time saved" in h[1]["hint"]     # numbered bullet and title skipped
    kw = a["keywords"]
    assert any("gesture" in k for k in kw) and "python" not in kw and "opencv" not in kw


def test_hint_order_and_university_keywords():
    a = {"projects": ["Built an AI-powered application using NLP to analyze resumes and extract relevant skills."], "experience": []}
    assert "time saved" in metric_hints(a)[0]["hint"]            # 'analyze/extract' beats the generic 'application' rule
    from nlp.extractor import phrase_keywords
    kw = phrase_keywords("B.Tech student at Ramdeobaba University with an interest in building practical solutions. Developed a web application.", [])
    assert not any("university" in k or k == "interest" for k in kw)
