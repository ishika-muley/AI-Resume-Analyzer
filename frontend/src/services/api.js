// API service layer: all backend calls live here.
async function req(url, opts) {
  let res;
  try { res = await fetch(url, opts); } catch { throw new Error("Cannot reach the server. Is the Flask backend running on port 5000?"); }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}
export const analyzeResume = (file, jd) => {
  const fd = new FormData(); fd.append("resume", file); if (jd?.trim()) fd.append("job_description", jd);
  return req("/api/analyze", { method: "POST", body: fd });
};
export const matchJob = (id, jd) => req(`/api/match/${id}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ job_description: jd }) });
export const getHistory = () => req("/api/history");
export const getAnalysis = (id) => req(`/api/history/${id}`);
export const deleteAnalysis = (id) => req(`/api/history/${id}`, { method: "DELETE" });
export const aiReview = (id, jd) => req(`/api/ai-review/${id}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ job_description: jd }) });
