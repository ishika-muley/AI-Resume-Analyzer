import io, pytest, docx
from app import create_app
from models import db

RESUME = ["Priya Sharma", "priya@example.com | +91 98765 43210 | github.com/priya", "Summary",
 "Final-year CS student passionate about machine learning and web development.", "Skills",
 "Python, Java, SQL, React, Flask, Docker, Git, scikit-learn, NLP", "Education", "B.Tech Computer Science, 2026",
 "Projects", "Built a resume analyzer using Flask and spaCy for 500 users", "Certifications", "AWS Cloud Practitioner"]
JD = "We need a developer with Python, Flask, React, AWS, Kubernetes and PostgreSQL experience building REST API services."

@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path}/t.db", "UPLOAD_FOLDER": str(tmp_path)})
    return app.test_client()

def make_docx():
    d = docx.Document()
    for l in RESUME: d.add_paragraph(l)
    b = io.BytesIO(); d.save(b); b.seek(0); return b

def make_pdf():
    from reportlab.pdfgen import canvas   # test-only dependency (needs Python 3.10+)
    b = io.BytesIO(); c = canvas.Canvas(b); y = 800
    for l in RESUME: c.drawString(50, y, l); y -= 20
    c.save(); b.seek(0); return b

def up(client, data, name, jd=None):
    form = {"resume": (data, name)}
    if jd: form["job_description"] = jd
    return client.post("/api/analyze", data=form, content_type="multipart/form-data")

def test_docx_upload_and_extraction(client):
    r = up(client, make_docx(), "r.docx"); j = r.get_json()
    assert r.status_code == 201
    a = j["analysis"]
    assert a["name"] == "Priya Sharma" and a["contact"]["email"] == "priya@example.com"
    assert {"python", "react", "docker", "scikit-learn", "nlp"} <= set(a["skills"])
    assert "python" in a["languages"] and a["certifications"] and a["education"] and "metric_hints" in a

def test_pdf_upload(client):
    pytest.importorskip("reportlab", reason="reportlab needs Python 3.10+", exc_type=ImportError)
    r = up(client, make_pdf(), "r.pdf")
    assert r.status_code == 201 and "python" in r.get_json()["analysis"]["skills"]

def test_matching_and_missing_skills(client):
    j = up(client, make_docx(), "r.docx", JD).get_json()
    m = j["match"]
    assert 0 < m["score"] < 100
    assert {"python", "flask", "react", "aws"} <= set(m["matched_skills"])
    assert {"kubernetes", "postgresql"} <= set(m["missing_skills"])
    assert any("kubernetes" in s["text"] for s in j["analysis"]["suggestions"])

def test_match_endpoint_on_saved(client):
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    r = client.post(f"/api/match/{aid}", json={"job_description": JD})
    assert r.status_code == 200 and r.get_json()["match"]["missing_skills"]
    assert client.post(f"/api/match/{aid}", json={"job_description": "x"}).status_code == 400

def test_history_crud(client):
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    assert len(client.get("/api/history").get_json()) == 1
    assert client.get(f"/api/history/{aid}").status_code == 200
    assert client.delete(f"/api/history/{aid}").status_code == 200
    assert client.get("/api/history").get_json() == []
    assert client.delete(f"/api/history/{aid}").status_code == 404

def test_invalid_uploads(client):
    assert up(client, io.BytesIO(b"hello"), "x.txt").status_code == 400
    assert client.post("/api/analyze").status_code == 400
    assert up(client, io.BytesIO(b"not a real pdf"), "bad.pdf").status_code == 422
    assert up(client, io.BytesIO(b"x" * (6 * 1024 * 1024)), "big.pdf").status_code == 413

def test_skills_endpoint(client):
    r = client.post("/api/skills", json={"text": "Experienced in C++, Java and Node.js"})
    assert {"c++", "java", "node.js"} <= set(r.get_json()["skills"])
