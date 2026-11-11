import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Trash2, Eye } from "lucide-react";
import { getHistory, deleteAnalysis } from "../services/api.js";
import { Card, Alert, Chip } from "../components/ui.jsx";
export default function History() {
  const [rows, setRows] = useState(null), [error, setError] = useState(""), [ok, setOk] = useState("");
  const load = () => getHistory().then(setRows).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);
  const del = async (id) => {
    if (!confirm("Delete this analysis?")) return;
    try { await deleteAnalysis(id); setOk("Analysis deleted."); setRows((r) => r.filter((x) => x.id !== id)); } catch (e) { setError(e.message); }
  };
  return (<div className="space-y-4"><h2 className="text-2xl font-bold">Analysis history</h2><Alert>{error}</Alert><Alert type="ok">{ok}</Alert>
    {rows && !rows.length && <Card><p className="text-slate-500">No analyses yet. <Link to="/analyze" className="text-brand-600 underline">Analyze a resume</Link></p></Card>}
    <div className="grid gap-3">{rows?.map((r) => (<Card key={r.id} className="flex items-center justify-between !p-4"><div><p className="font-medium">{r.filename}</p>
      <p className="text-xs text-slate-500">{new Date(r.created_at).toLocaleString()}</p><div className="mt-2 flex gap-2"><Chip tone="gray">{r.skill_count} skills</Chip>{r.match_score != null && <Chip>{r.match_score}% match</Chip>}</div></div>
      <div className="flex gap-2"><Link to={`/results/${r.id}`} className="rounded-lg p-2 text-brand-600 hover:bg-brand-50" title="View"><Eye size={18} /></Link>
        <button onClick={() => del(r.id)} className="rounded-lg p-2 text-rose-600 hover:bg-rose-50" title="Delete"><Trash2 size={18} /></button></div></Card>))}</div></div>);
}
