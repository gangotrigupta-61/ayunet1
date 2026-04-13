import { useState } from "react";
import { Search, AlertTriangle } from "lucide-react";
import { api } from "../lib/api";
import GraphView from "./GraphView";

const COMMON_DRUGS = [
  "Metformin", "Warfarin", "Paracetamol", "Aspirin", "Ibuprofen",
  "Amoxicillin", "Omeprazole", "Amlodipine", "Simvastatin", "Clopidogrel",
  "Fluoxetine", "Sertraline", "Rifampicin", "Lisinopril", "Phenytoin",
  "Isoniazid", "Prednisolone", "Atenolol", "Losartan", "Diclofenac",
];

export default function DrugCheckTab() {
  const [selected, setSelected] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  function toggleDrug(drug: string) {
    setSelected((prev) =>
      prev.includes(drug) ? prev.filter((d) => d !== drug) : [...prev, drug]
    );
  }

  async function handleCheck() {
    if (selected.length < 2) return;
    setLoading(true);
    try {
      const data = await api.drugCheck(selected);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const filtered = COMMON_DRUGS.filter((d) =>
    d.toLowerCase().includes(search.toLowerCase())
  );

  const graphNodes = result ? buildDrugGraphNodes(result) : [];
  const graphEdges = result ? buildDrugGraphEdges(result) : [];

  return (
    <div className="h-full flex gap-6">
      {/* Left Panel */}
      <div className="w-[380px] shrink-0 flex flex-col gap-4">
        <div className="bg-white dark:bg-slate-900/60 backdrop-blur border border-slate-200 dark:border-white/10 rounded-2xl p-5 shadow-sm dark:shadow-none">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-4">
            Select Drugs to Check
          </h3>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search drugs..."
            className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-white/10 rounded-xl p-2.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 mb-3 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
          />
          <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
            {filtered.map((drug) => (
              <button
                key={drug}
                onClick={() => toggleDrug(drug)}
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                  selected.includes(drug)
                    ? "bg-emerald-50 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500"
                    : "bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-white/10 hover:border-emerald-500/50"
                }`}
              >
                {drug}
              </button>
            ))}
          </div>
          <button
            onClick={handleCheck}
            disabled={loading || selected.length < 2}
            className="w-full mt-4 bg-green-600 hover:bg-green-500 text-white py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50 transition-colors"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            Check Interactions ({selected.length} drugs)
          </button>
        </div>

        {/* Interaction results */}
        {result?.interactions?.interactions && (
          <div className="flex-1 overflow-y-auto space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">
              Interactions Found
            </h4>
            {result.interactions.interactions.map((ix: any, i: number) => (
              <div
                key={i}
                className={`rounded-xl p-4 border transition-colors shadow-sm dark:shadow-none ${
                  ix.severity === "severe"
                    ? "bg-red-50 dark:bg-red-500/10 border-red-300 dark:border-red-500/50"
                    : ix.severity === "moderate"
                    ? "bg-yellow-50 dark:bg-yellow-500/10 border-yellow-300 dark:border-yellow-500/50"
                    : "bg-green-50 dark:bg-green-500/10 border-green-300 dark:border-green-500/50"
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle
                    className={`w-4 h-4 ${
                      ix.severity === "severe"
                        ? "text-red-500 dark:text-red-400"
                        : ix.severity === "moderate"
                        ? "text-yellow-500 dark:text-yellow-400"
                        : "text-green-500 dark:text-green-400"
                    }`}
                  />
                  <span className="font-bold text-slate-900 dark:text-white text-sm">
                    {ix.drug1} + {ix.drug2}
                  </span>
                  <span
                    className={`ml-auto text-xs font-bold px-2 py-0.5 rounded-full ${
                      ix.severity === "severe"
                        ? "bg-red-100 dark:bg-red-500/30 text-red-600 dark:text-red-300"
                        : ix.severity === "moderate"
                        ? "bg-yellow-100 dark:bg-yellow-500/30 text-yellow-700 dark:text-yellow-300"
                        : "bg-green-100 dark:bg-green-500/30 text-green-700 dark:text-green-300"
                    }`}
                  >
                    {ix.severity}
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400">{ix.mechanism}</p>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{ix.clinical_note}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right: Graph */}
      <div className="flex-1 min-h-[500px]">
        {graphNodes.length > 0 ? (
          <GraphView nodes={graphNodes} edges={graphEdges} layout="cola" />
        ) : (
          <div className="h-full flex items-center justify-center bg-slate-50 dark:bg-slate-950/50 rounded-2xl border border-slate-200 dark:border-white/10">
            <p className="text-slate-400 dark:text-slate-500 text-sm">
              Select 2+ drugs to visualize interactions
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function buildDrugGraphNodes(result: any) {
  const nodes: any[] = [];
  const drugs = result.drugs || [];
  drugs.forEach((d: string) => {
    nodes.push({ id: d, label: d, type: "Drug", hop: 1 });
  });
  return nodes;
}

function buildDrugGraphEdges(result: any) {
  const edges: any[] = [];
  result.interactions?.interactions?.forEach((ix: any) => {
    edges.push({
      source: ix.drug1,
      target: ix.drug2,
      label: ix.severity,
      severity: ix.severity,
      weight: ix.severity === "severe" ? 1 : ix.severity === "moderate" ? 0.6 : 0.3,
    });
  });
  return edges;
}
