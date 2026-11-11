import json
from tests.test_api import client, make_docx, up   # noqa: F401  (reuse fixtures/helpers)
from nlp import ai_review

GOOD = {"overall_impression": "Solid fresher resume.", "strengths": ["Clear projects"], "weaknesses": ["No metrics"],
        "bullet_rewrites": [{"original": "Built a resume analyzer using Flask and spaCy for 500 users", "suggested": "Built a resume analyzer using Flask and spaCy for 500 users, cutting review time by [X%]", "why": "Adds impact"}], "jd_fit": None}

class Resp:
    def __init__(self, status=200, text=None): self.status_code = status; self._t = text if text is not None else json.dumps(GOOD)
    def json(self): return {"content": [{"type": "text", "text": self._t}]}

def test_not_configured(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False); monkeypatch.delenv("AI_PROVIDER", raising=False)
    def down(*a, **k): raise ai_review.requests.ConnectionError()
    monkeypatch.setattr(ai_review.requests, "post", down)
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    r = client.post(f"/api/ai-review/{aid}", json={})
    assert r.status_code == 503 and "ANTHROPIC_API_KEY" in r.get_json()["error"]

def test_success_saved_and_payload(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    seen = {}
    def fake(url, headers, json, timeout): seen.update(h=headers, b=json); return Resp(text="```json\n" + __import__("json").dumps(GOOD) + "\n```")
    monkeypatch.setattr(ai_review.requests, "post", fake)
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    r = client.post(f"/api/ai-review/{aid}", json={"job_description": "Need Python and Flask developer " * 3})
    assert r.status_code == 200 and r.get_json()["analysis"]["ai_review"]["strengths"] == ["Clear projects"]
    assert seen["h"]["x-api-key"] == "sk-test" and "<resume>" in seen["b"]["messages"][0]["content"] and "<job_description>" in seen["b"]["messages"][0]["content"]
    assert client.get(f"/api/history/{aid}").get_json()["analysis"]["ai_review"]["overall_impression"] == "Solid fresher resume."

def test_bad_json_and_auth_errors(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    monkeypatch.setattr(ai_review.requests, "post", lambda *a, **k: Resp(text="sorry, no json"))
    assert client.post(f"/api/ai-review/{aid}", json={}).status_code == 502
    monkeypatch.setattr(ai_review.requests, "post", lambda *a, **k: Resp(status=401))
    r = client.post(f"/api/ai-review/{aid}", json={})
    assert r.status_code == 502 and "rejected" in r.get_json()["error"]
    assert client.post("/api/ai-review/9999", json={}).status_code == 404


import pytest
FAKE = dict(GOOD, bullet_rewrites=GOOD["bullet_rewrites"] + [{"original": "Led a team of 50 engineers at Google", "suggested": "x", "why": "y"}])

def test_fabricated_rewrite_is_dropped(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setattr(ai_review.requests, "post", lambda *a, **k: Resp(text=json.dumps(FAKE)))
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    rw = client.post(f"/api/ai-review/{aid}", json={}).get_json()["analysis"]["ai_review"]["bullet_rewrites"]
    assert len(rw) == 1 and "Google" not in rw[0]["original"]

class OResp:
    def __init__(self, status=200): self.status_code = status
    def json(self): return {"message": {"content": json.dumps(GOOD)}}

def test_ollama_used_without_key(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False); monkeypatch.delenv("AI_PROVIDER", raising=False)
    seen = {}
    def fake(url, json, timeout): seen.update(u=url, b=json); return OResp()
    monkeypatch.setattr(ai_review.requests, "post", fake)
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    r = client.post(f"/api/ai-review/{aid}", json={}).get_json()["analysis"]["ai_review"]
    assert "11434/api/chat" in seen["u"] and seen["b"]["format"] == "json" and seen["b"]["stream"] is False
    assert r["provider"].startswith("Ollama") and r["strengths"] == ["Clear projects"]

def test_ollama_model_missing(client, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False); monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.setattr(ai_review.requests, "post", lambda *a, **k: OResp(404))
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    r = client.post(f"/api/ai-review/{aid}", json={})
    assert r.status_code == 503 and "ollama pull" in r.get_json()["error"]


BAD = dict(GOOD, weaknesses=["No mention of relevant projects or achievements", "Lack of quantified results in projects", "Needs a clearer summary"],
  bullet_rewrites=GOOD["bullet_rewrites"] + [
    {"original": "Built a resume analyzer using Flask and spaCy for 500 users", "suggested": "[N users] can analyze resumes", "why": "meaning changed"},
    {"original": "Built a resume analyzer using Flask and spaCy for 500 users", "suggested": "Built a resume analyzer using Flask and spaCy for 500 users", "why": "This bullet point is already clear, no rewrite needed"}])

def test_grounding_and_quality_filters(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    seen = {}
    def fake(url, headers, json, timeout): seen["c"] = json["messages"][0]["content"]; return Resp(text=__import__("json").dumps(BAD))
    monkeypatch.setattr(ai_review.requests, "post", fake)
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    rv = client.post(f"/api/ai-review/{aid}", json={}).get_json()["analysis"]["ai_review"]
    assert "<detected_facts>" in seen["c"] and "projects listed: 1" in seen["c"]
    assert "No mention of relevant projects or achievements" not in rv["weaknesses"]       # contradicts parser facts
    assert "Lack of quantified results in projects" in rv["weaknesses"] and "Needs a clearer summary" in rv["weaknesses"]
    assert len(rv["bullet_rewrites"]) == 1 and "[X%]" in rv["bullet_rewrites"][0]["suggested"]  # mangled + unchanged rewrites dropped


def test_ai_review_reuses_saved_job_description(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test"); seen = {}
    def fake(url, headers, json, timeout): seen["c"] = json["messages"][0]["content"]; return Resp()
    monkeypatch.setattr(ai_review.requests, "post", fake)
    aid = up(client, make_docx(), "r.docx", "Need a Python developer with Docker and Kubernetes experience for backend services.").get_json()["id"]
    client.post(f"/api/ai-review/{aid}", json={})                       # no JD sent: falls back to the saved one
    assert "<job_description>" in seen["c"] and "Kubernetes" in seen["c"]


def test_new_match_clears_stale_jd_fit(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    fit = dict(GOOD, jd_fit={"verdict": "v", "strong_matches": ["a"], "gaps": ["b"]})
    monkeypatch.setattr(ai_review.requests, "post", lambda *a, **k: Resp(text=json.dumps(fit)))
    aid = up(client, make_docx(), "r.docx", "Need a Python developer with Docker and Kubernetes experience for backend services.").get_json()["id"]
    assert client.post(f"/api/ai-review/{aid}", json={}).get_json()["analysis"]["ai_review"]["jd_fit"]["verdict"].startswith("Your resume contains")
    r = client.post(f"/api/match/{aid}", json={"job_description": "Java developer with Spring Boot and MySQL experience for backend work."}).get_json()
    assert r["analysis"]["ai_review"]["jd_fit"] is None and r["analysis"]["ai_review"]["strengths"] == ["Clear projects"]


HALLU = dict(GOOD, strengths=["Experience with Agile methodology and team collaboration", "Strong Python skills"],
  weaknesses=["Limited experience with Docker, AWS", "Lack of specific numbers and metrics", "No clear indication of proficiency in NLP"],
  jd_fit={"verdict": "Good fit", "strong_matches": ["Kubernetes"], "gaps": ["AWS"]})

def test_ai_fit_is_grounded_in_matcher(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test"); seen = {}
    def fake(url, headers, json, timeout): seen["c"] = json["messages"][0]["content"]; return Resp(text=__import__("json").dumps(HALLU))
    monkeypatch.setattr(ai_review.requests, "post", fake)
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    rv = client.post(f"/api/ai-review/{aid}", json={"job_description": "Need Python, Docker, Agile, Kubernetes and AWS experience for backend services."}).get_json()["analysis"]["ai_review"]
    assert "<job_match_facts>" in seen["c"] and "resume does NOT have: agile, kubernetes" in seen["c"]
    assert rv["strengths"] == ["Strong Python skills"]                                       # Agile claim removed (resume lacks it)
    assert rv["weaknesses"][0] == "Lack of specific numbers and metrics" and "agile, kubernetes" in rv["weaknesses"][1]   # false 'limited Docker/AWS/NLP' removed; real gap added
    assert rv["jd_fit"]["gaps"] == ["agile", "kubernetes"] and rv["jd_fit"]["strong_matches"] == ["aws", "docker", "python"]
    assert "3 of the 5" in rv["jd_fit"]["verdict"] and "Good fit" not in rv["jd_fit"]["verdict"]


IMP = dict(GOOD, weaknesses=["May need to improve their skills in areas like NLP", "Could improve project descriptions with metrics"],
  bullet_rewrites=[dict(GOOD["bullet_rewrites"][0], why="This is a key requirement for the job")])

def test_improve_claims_filtered_and_why_is_fixed(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setattr(ai_review.requests, "post", lambda *a, **k: Resp(text=json.dumps(IMP)))
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    rv = client.post(f"/api/ai-review/{aid}", json={"job_description": "Need Python and Docker experience for backend services."}).get_json()["analysis"]["ai_review"]
    assert rv["weaknesses"] == ["Could improve project descriptions with metrics"]      # 'improve ... NLP' contradicts the resume
    assert "key requirement" not in rv["bullet_rewrites"][0]["why"] and "measurable result" in rv["bullet_rewrites"][0]["why"]


SUMM = dict(GOOD, bullet_rewrites=GOOD["bullet_rewrites"] + [{"original": "Final-year CS student passionate about machine learning and web development.",
  "suggested": "Final-year CS student passionate about machine learning and web development, serving [N users].", "why": "x"}])

def test_rewrites_limited_to_project_and_experience_bullets(client, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setattr(ai_review.requests, "post", lambda *a, **k: Resp(text=json.dumps(SUMM)))
    aid = up(client, make_docx(), "r.docx").get_json()["id"]
    rw = client.post(f"/api/ai-review/{aid}", json={}).get_json()["analysis"]["ai_review"]["bullet_rewrites"]
    assert len(rw) == 1 and rw[0]["original"].startswith("Built a resume analyzer")      # the summary-line rewrite is dropped


def test_known_gaps_added_and_student_status_fixed():
    q = {"checks": [{"label": "Quantified impact (numbers, %)", "passed": False}]}
    w = ai_review._add_known_gaps([], {"quality": q}, {"missing_skills": ["docker", "agile"]})
    assert any("measurable" in x for x in w) and any("docker, agile" in x for x in w)
    assert ai_review._add_known_gaps(["Needs numbers and metrics"], {"quality": q}, None) == ["Needs numbers and metrics"]   # no duplicate
    assert ai_review._fix_student_status("A recent computer science graduate with skills.", {"education": ["B.Tech 2024-2099"]}) == "A computer science student with skills."
    assert ai_review._fix_student_status("A graduate.", {"education": ["B.Tech 2018-2022"]}) == "A graduate."


def test_recent_certification_weakness_dropped():
    out = ai_review._drop_false_claims(["Certifications are recent, with AWS Cloud Practitioner in 2025", "Recent certifications may be less relevant", "Real weakness"], None)
    assert out == ["Real weakness"]
