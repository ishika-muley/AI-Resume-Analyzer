import { NavLink, Link } from "react-router-dom";
import { FileSearch } from "lucide-react";
const cls = ({ isActive }) => `rounded-lg px-3 py-2 text-sm font-medium transition ${isActive ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100"}`;
export default function Navbar() {
  return (<header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur"><div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
    <Link to="/" className="flex items-center gap-2 font-bold text-slate-800"><FileSearch className="text-brand-600" />ResumeAI</Link>
    <nav className="flex gap-1"><NavLink to="/" end className={cls}>Home</NavLink><NavLink to="/analyze" className={cls}>Analyze</NavLink><NavLink to="/history" className={cls}>History</NavLink></nav></div></header>);
}
