import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Landing from "./pages/Landing.jsx";
import Analyze from "./pages/Analyze.jsx";
import Results from "./pages/Results.jsx";
import History from "./pages/History.jsx";
export default function App() {
  return (<><Navbar /><main className="mx-auto max-w-6xl px-4 py-8"><Routes>
    <Route path="/" element={<Landing />} /><Route path="/analyze" element={<Analyze />} />
    <Route path="/results/:id" element={<Results />} /><Route path="/history" element={<History />} /></Routes></main></>);
}
