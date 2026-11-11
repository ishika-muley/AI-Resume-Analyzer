import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadCloud, FileText } from "lucide-react";
import { analyzeResume } from "../services/api.js";
import { Card, Btn, Alert } from "../components/ui.jsx";
export default function Analyze() {
  const [file, setFile] = useState(null), [jd, setJd] = useState(""), [busy, setBusy] = useState(false), [error, setError] = useState(""), [drag, setDrag] = useState(false);
  const input = useRef(), nav = useNavigate();
  const pick = (f) => {
    setError("");
    if (!f) return;
    if (!/\.(pdf|docx)$/i.test(f.name)) return setError("Only PDF and DOCX files are supported.");
    if (f.size > 5 * 1024 * 1024) return setError("File is larger than 5 MB.");
    setFile(f);
  };
  const submit = async () => {
    setBusy(true); setError("");
    try { const r = await analyzeResume(file, jd); nav(`/results/${r.id}`); } catch (e) { setError(e.message); } finally { setBusy(false); }
  };
  return (<div className="mx-auto max-w-2xl space-y-5"><h2 className="text-2xl font-bold">Analyze a resume</h2>
    <Card><div onClick={() => input.current.click()} onDragOver={(e) => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)}
      onDrop={(e) => { e.preventDefault(); setDrag(false); pick(e.dataTransfer.files[0]); }}
      className={`flex cursor-pointer flex-col items-center rounded-xl border-2 border-dashed p-8 text-center transition ${drag ? "border-brand-500 bg-brand-50" : "border-slate-300 hover:border-brand-500"}`}>
      {file ? <><FileText className="text-brand-600" size={32} /><p className="mt-2 font-medium">{file.name}</p><p className="text-xs text-slate-500">{(file.size / 1024).toFixed(0)} KB</p></>
        : <><UploadCloud className="text-slate-400" size={32} /><p className="mt-2 font-medium">Drop your resume or click to browse</p><p className="text-xs text-slate-500">PDF or DOCX, up to 5 MB</p></>}
      <input ref={input} type="file" accept=".pdf,.docx" hidden onChange={(e) => pick(e.target.files[0])} /></div></Card>
    <Card title="Job description (optional)"><textarea value={jd} onChange={(e) => setJd(e.target.value)} rows={7} placeholder="Paste a job description to get a match score…"
      className="w-full rounded-xl border border-slate-300 p-3 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100" /></Card>
    <Alert>{error}</Alert>
    <Btn onClick={submit} loading={busy} disabled={!file} className="w-full">{busy ? "Analyzing…" : "Analyze resume"}</Btn></div>);
}
