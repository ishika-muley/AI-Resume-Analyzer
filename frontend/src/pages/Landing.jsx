import { Link } from "react-router-dom";
import { Upload, Target, Lightbulb, History as H } from "lucide-react";
const F = [[Upload, "Upload & Parse", "PDF or DOCX resumes parsed locally."], [Target, "Job Matching", "TF-IDF cosine similarity with matched and missing skills."],
  [Lightbulb, "Smart Suggestions", "Honest, rule-based tips. Never invents experience."], [H, "Analysis History", "Revisit or delete past analyses anytime."]];
export default function Landing() {
  return (<div className="space-y-12"><section className="fade-up py-10 text-center">
    <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">Understand your resume <span className="text-brand-600">before recruiters do</span></h1>
    <p className="mx-auto mt-4 max-w-2xl text-slate-600">An NLP-powered analyzer that runs fully on your machine. No API keys, no data leaving your computer.</p>
    <Link to="/analyze" className="mt-8 inline-block rounded-xl bg-brand-600 px-6 py-3 font-medium text-white transition hover:bg-brand-700">Analyze my resume</Link></section>
    <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{F.map(([I, t, d]) => (
      <div key={t} className="rounded-2xl border border-slate-200 bg-white p-5 transition hover:-translate-y-1 hover:shadow-md"><I className="mb-3 text-brand-600" /><h3 className="font-semibold">{t}</h3><p className="mt-1 text-sm text-slate-500">{d}</p></div>))}</section></div>);
}
