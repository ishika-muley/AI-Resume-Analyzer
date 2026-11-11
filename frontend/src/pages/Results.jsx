import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Sparkles, CheckCircle2, XCircle, User, Code2, GraduationCap, FolderGit2, Award, Lightbulb, Target, FileText, Tags } from "lucide-react";
import { getAnalysis, matchJob, aiReview } from "../services/api.js";
import { Card, Chips, Btn, Alert, ScoreRing } from "../components/ui.jsx";
const List = ({ items }) => items?.length ? <ul className="list-disc space-y-1 pl-5 text-sm text-slate-700">{items.map((i, k) => <li key={k}>{i}</li>)}</ul> : <p className="text-sm text-slate-400">Not detected</p>;
export default function Results() {
  const { id } = useParams();
  const [d, setD] = useState(null), [jd, setJd] = useState(""), [busy, setBusy] = useState(false), [error, setError] = useState(""), [ok, setOk] = useState(""), [aiBusy, setAiBusy] = useState(false), [aiErr, setAiErr] = useState("");
  useEffect(() => { getAnalysis(id).then(setD).catch((e) => setError(e.message)); }, [id]);
  const rematch = async () => {
    setBusy(true); setError(""); setOk("");
    try { setD(await matchJob(id, jd)); setOk("Job match updated."); } catch (e) { setError(e.message); } finally { setBusy(false); }
  };
  const runAi = async () => {
    setAiBusy(true); setAiErr("");
    try { setD(await aiReview(id, jd.trim().length >= 20 ? jd : "")); } catch (e) { setAiErr(e.message); } finally { setAiBusy(false); }
  };
  if (!d) return error ? <Alert>{error}</Alert> : <p className="text-slate-500">Loading…</p>;
  const a = d.analysis, m = d.match;
  return (<div className="space-y-5"><div><h2 className="text-2xl font-bold">{a.name || "Resume analysis"}</h2><p className="text-sm text-slate-500">{d.filename}</p></div>
    <div className="grid gap-5 lg:grid-cols-3">
      <Card title="Summary" icon={User}><div className="space-y-1 text-sm text-slate-700"><p>Email: {a.contact.email || "—"}</p><p>Phone: {a.contact.phone || "—"}</p>
        <p>Links: {a.contact.links.join(", ") || "—"}</p><p>Words: {a.word_count}</p><p>Skills found: {a.skills.length}</p></div></Card>
      <Card title="Job match" icon={Target} className="flex flex-col items-center">{m ? <>{m.score != null ? <ScoreRing value={m.score} label="match" /> : <p className="text-center text-sm text-slate-500">Score not calculated: no recognisable skills in this job description.</p>}
        <div className="mt-2 space-y-0.5 text-center text-sm text-slate-600">{m.skill_coverage != null && <p>Skill coverage: <b>{m.skill_coverage}%</b></p>}{m.keyword_coverage != null && <p>Keyword coverage: <b>{m.keyword_coverage}%</b></p>}<p>Text similarity: <b>{m.text_similarity}%</b></p></div>
        <p className="mt-2 text-center text-xs text-slate-500">{m.note}</p></> : <p className="text-sm text-slate-400">Paste a job description below to see your match.</p>}</Card>
      <Card title="Programming languages" icon={Code2}><Chips items={a.languages} /></Card></div>
    <div className="grid gap-5 md:grid-cols-2">
      {a.quality && <Card title={`Resume quality: ${a.quality.score}/100`} icon={Lightbulb} className="md:col-span-2"><div className="grid gap-2 sm:grid-cols-2">{a.quality.checks.map((c) => <div key={c.label} className="flex items-start gap-2 text-sm">{c.passed ? <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-emerald-600" /> : <XCircle size={16} className="mt-0.5 shrink-0 text-rose-500" />}<span className={c.passed ? "text-slate-700" : "text-slate-500"}><b>{c.label}</b> ({c.earned}/{c.points}){!c.passed && <> — {c.tip}</>}</span></div>)}</div></Card>}
      {a.metric_hints?.length > 0 && <Card title="Add numbers to these bullets" icon={Lightbulb} className="md:col-span-2"><ul className="space-y-2 text-sm">{a.metric_hints.map((h, k) => <li key={k} className="rounded-lg bg-slate-50 p-3"><p className="text-slate-700">{h.bullet}</p><p className="mt-1 text-xs text-brand-700">Add: {h.hint}. Only use figures that are true.</p></li>)}</ul></Card>}
      <Card title="All technical skills" icon={Code2}><Chips items={a.skills} /></Card>
      <Card title="Important keywords" icon={Tags}><Chips items={a.keywords} tone="gray" /></Card>
      <Card title="Education" icon={GraduationCap}><List items={a.education} /></Card>
      <Card title="Certifications" icon={Award}><List items={a.certifications} /></Card>
      <Card title="Projects" icon={FolderGit2}><List items={a.projects} /></Card>
      <Card title="Experience" icon={FolderGit2}><List items={a.experience} /></Card></div>
    <Card title="Job description matching" icon={Target}>
      <textarea value={jd} onChange={(e) => setJd(e.target.value)} rows={5} placeholder="Paste a job description…" className="w-full rounded-xl border border-slate-300 p-3 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100" />
      <div className="mt-3 space-y-3"><Btn onClick={rematch} loading={busy} disabled={jd.trim().length < 20}>{busy ? "Matching…" : "Match against this job"}</Btn><Alert>{error}</Alert><Alert type="ok">{ok}</Alert></div>
      {m && m.jd_skills.length === 0 && <div className="mt-5"><Alert>No known technical skills were found in this job description, so skill matching is empty. Paste the actual requirements/responsibilities section.</Alert></div>}
      {m && m.jd_skills.length > 0 && <div className="mt-5 grid gap-4 md:grid-cols-2"><div><h4 className="mb-2 text-sm font-semibold text-emerald-700">Matched skills</h4><Chips items={m.matched_skills} tone="green" empty="No overlap" /></div>
        <div><h4 className="mb-2 text-sm font-semibold text-rose-700">Missing skills</h4><Chips items={m.missing_skills} tone="red" empty="None missing" /></div>
        <div><h4 className="mb-2 text-sm font-semibold">Keywords found</h4><Chips items={m.keywords_found} tone="green" /></div>
        <div><h4 className="mb-2 text-sm font-semibold">Keywords missing</h4><Chips items={m.keywords_missing} tone="red" /></div></div>}</Card>
    <Card title="AI review" icon={Sparkles}>
      <p className="mb-3 text-xs text-slate-500">Qualitative review of your resume (and the job description above, if pasted). Uses Claude if ANTHROPIC_API_KEY is set on the backend, otherwise a free local Ollama model.</p>
      <Btn onClick={runAi} loading={aiBusy}>{aiBusy ? "Reviewing…" : a.ai_review ? "Re-run AI review" : "Get AI review"}</Btn>
      <div className="mt-3"><Alert>{aiErr}</Alert></div>
      {a.ai_review && <div className="mt-4 space-y-4 text-sm text-slate-700">
        <p className="text-xs text-slate-400">Reviewed by: {a.ai_review.provider}</p>
        <p>{a.ai_review.overall_impression}</p>
        <div className="grid gap-4 md:grid-cols-2"><div><h4 className="mb-1 font-semibold text-emerald-700">Strengths</h4><List items={a.ai_review.strengths} /></div>
          <div><h4 className="mb-1 font-semibold text-rose-700">Weaknesses</h4><List items={a.ai_review.weaknesses} /></div></div>
        {a.ai_review.bullet_rewrites.length > 0 && <div><h4 className="mb-2 font-semibold">AI rewrite ideas (may be imperfect){a.ai_review.bullet_rewrites.some((b) => b.suggested.includes("[")) && " (fill in the [placeholders] with your real numbers)"}</h4>
          <p className="mb-2 text-xs text-slate-500">Keep only claims you can back up; delete any result you did not actually achieve.</p><div className="space-y-2">{a.ai_review.bullet_rewrites.map((b, k) => <div key={k} className="rounded-lg bg-slate-50 p-3"><p className="text-slate-500 line-through">{b.original}</p><p className="font-medium">{b.suggested}</p><p className="text-xs text-slate-500">{b.why}</p></div>)}</div></div>}
        {a.ai_review.jd_fit && <div><h4 className="mb-1 font-semibold">Fit for this job</h4><p>{a.ai_review.jd_fit.verdict}</p>
          <div className="mt-2 grid gap-4 md:grid-cols-2"><div><h5 className="mb-1 text-emerald-700">Strong matches</h5><List items={a.ai_review.jd_fit.strong_matches} /></div><div><h5 className="mb-1 text-rose-700">Gaps</h5><List items={a.ai_review.jd_fit.gaps} /></div></div></div>}
      </div>}
    </Card>
    <Card title="Improvement suggestions" icon={Lightbulb}><ul className="space-y-2">{a.suggestions.map((s, k) => <li key={k} className="rounded-lg bg-slate-50 p-3 text-sm text-slate-700"><span className="mr-2 rounded bg-brand-100 px-1.5 py-0.5 text-xs font-semibold uppercase text-brand-700">{s.type}</span>{s.text}</li>)}</ul></Card>
    <Card title="Extracted text preview" icon={FileText}><pre className="max-h-60 overflow-auto whitespace-pre-wrap text-xs text-slate-600">{d.text_preview}</pre></Card></div>);
}
