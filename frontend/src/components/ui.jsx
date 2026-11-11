import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";
export const Card = ({ title, icon: Icon, children, className = "" }) => (
  <div className={`fade-up rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md ${className}`}>
    {title && <h3 className="mb-3 flex items-center gap-2 font-semibold text-slate-800">{Icon && <Icon size={18} className="text-brand-600" />}{title}</h3>}
    {children}
  </div>);
export const Chip = ({ children, tone = "brand" }) => {
  const t = { brand: "bg-brand-50 text-brand-700", green: "bg-emerald-50 text-emerald-700", red: "bg-rose-50 text-rose-700", gray: "bg-slate-100 text-slate-600" }[tone];
  return <span className={`inline-block rounded-full px-2.5 py-1 text-xs font-medium ${t}`}>{children}</span>;
};
export const Chips = ({ items, tone, empty = "None detected" }) =>
  items?.length ? <div className="flex flex-wrap gap-2">{items.map((i) => <Chip key={i} tone={tone}>{i}</Chip>)}</div> : <p className="text-sm text-slate-400">{empty}</p>;
export const Btn = ({ loading, children, className = "", ...p }) => (
  <button {...p} disabled={loading || p.disabled} className={`inline-flex items-center justify-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 font-medium text-white transition hover:bg-brand-700 active:scale-95 disabled:opacity-50 ${className}`}>
    {loading && <Loader2 size={16} className="animate-spin" />}{children}</button>);
export const Alert = ({ type = "error", children }) => children ? (
  <div className={`flex items-start gap-2 rounded-xl p-3 text-sm ${type === "error" ? "bg-rose-50 text-rose-700" : "bg-emerald-50 text-emerald-700"}`}>
    {type === "error" ? <AlertCircle size={18} /> : <CheckCircle2 size={18} />}<span>{children}</span></div>) : null;
export const ScoreRing = ({ value, label }) => {
  const r = 52, c = 2 * Math.PI * r, color = value >= 60 ? "#10b981" : value >= 35 ? "#f59e0b" : "#ef4444";
  return (<div className="relative h-36 w-36">
    <svg viewBox="0 0 120 120" className="-rotate-90"><circle cx="60" cy="60" r={r} stroke="#e2e8f0" strokeWidth="10" fill="none" />
      <circle cx="60" cy="60" r={r} stroke={color} strokeWidth="10" fill="none" strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c * (1 - value / 100)} style={{ transition: "stroke-dashoffset .8s" }} /></svg>
    <div className="absolute inset-0 flex flex-col items-center justify-center"><span className="text-2xl font-bold text-slate-800">{value}%</span><span className="text-xs text-slate-500">{label}</span></div></div>);
};
