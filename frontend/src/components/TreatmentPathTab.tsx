import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { api } from "../lib/api";
import GraphView from "./GraphView";

const DISEASES = [
  "Dengue Fever", "Type 2 Diabetes", "Hypertension", "Malaria",
  "Tuberculosis", "Pneumonia", "Asthma", "Coronary Artery Disease",
  "Chronic Kidney Disease", "Rheumatoid Arthritis", "Depression",
  "Anemia", "Gastritis", "Hepatitis B",
];

export default function TreatmentPathTab() {
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  async function handleFind() {
    if (!selected) return;
    setLoading(true);
    try {
      const data = await api.treatmentPath(selected);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const graphNodes = result ? buildPathNodes(result) : [];
  const graphEdges = result ? buildPathEdges(result) : [];
  const animSeq = result ? buildPathAnimation(result) : [];

  return (
    <div className="h-full flex gap-6">
      {/* Left Panel */}
      <div className="w-[380px] shrink-0 flex flex-col gap-4">
        <div className="bg-white dark:bg-slate-900/60 backdrop-blur border border-slate-200 dark:border-white/10 rounded-2xl p-5 shadow-sm dark:shadow-none">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-4">
            Select Disease
          </h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {DISEASES.map((d) => (
              <button
                key={d}
                onClick={() => setSelected(d)}
                className={`w-full text-left px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  selected === d
                    ? "bg-orange-50 dark:bg-orange-500/20 text-orange-700 dark:text-orange-300 border border-orange-400 dark:border-orange-500"
                    : "bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-white/10 hover:border-orange-500/50"
                }`}
              >
                {d}
              </button>
            ))}
          </div>
          <button
            onClick={handleFind}
            disabled={loading || !selected}
            className="w-full mt-4 bg-orange-600 hover:bg-orange-500 text-white py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50 transition-colors"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <ArrowRight className="w-4 h-4" />
            )}
            Find Treatment Path
          </button>
        </div>

        {/* Pathway results */}
        {result?.pathway?.pathways && (
          <div className="flex-1 overflow-y-auto space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">
              Treatment Pathways
            </h4>
            {result.pathway.pathways.map((p: any, i: number) => (
              <div
                key={i}
                className="bg-white dark:bg-slate-900/60 backdrop-blur border border-slate-200 dark:border-white/10 rounded-xl p-4 shadow-sm dark:shadow-none"
              >
                <div className="flex items-center gap-2 text-xs mb-3 flex-wrap">
                  <span className="px-2 py-0.5 rounded bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-300 font-bold">
                    {result.disease}
                  </span>
                  <ArrowRight className="w-3 h-3 text-slate-400 dark:text-slate-500" />
                  <span className="px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-500/20 text-purple-600 dark:text-purple-300 font-bold">
                    {p.specialist_name}
                  </span>
                  <ArrowRight className="w-3 h-3 text-slate-400 dark:text-slate-500" />
                  <span className="px-2 py-0.5 rounded bg-orange-100 dark:bg-orange-500/20 text-orange-600 dark:text-orange-300 font-bold">
                    {p.treatment_name}
                  </span>
                  <ArrowRight className="w-3 h-3 text-slate-400 dark:text-slate-500" />
                  <span className="px-2 py-0.5 rounded bg-green-100 dark:bg-green-500/20 text-green-600 dark:text-green-300 font-bold">
                    {p.drug_name}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="text-slate-400 dark:text-slate-500">Success:</span>
                    <span className="text-green-600 dark:text-green-400 font-bold ml-1">
                      {(p.success_rate * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 dark:text-slate-500">Cost:</span>
                    <span className="text-amber-600 dark:text-amber-400 font-bold ml-1">{p.cost_tier}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 dark:text-slate-500">Duration:</span>
                    <span className="text-slate-700 dark:text-slate-300 font-bold ml-1">{p.duration}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right: Graph */}
      <div className="flex-1 min-h-[500px]">
        {graphNodes.length > 0 ? (
          <GraphView
            nodes={graphNodes}
            edges={graphEdges}
            animationSequence={animSeq}
            layout="breadthfirst"
          />
        ) : (
          <div className="h-full flex items-center justify-center bg-slate-50 dark:bg-slate-950/50 rounded-2xl border border-slate-200 dark:border-white/10">
            <p className="text-slate-400 dark:text-slate-500 text-sm">
              Select a disease to see the treatment pathway
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function buildPathNodes(result: any) {
  const nodes: any[] = [];
  const seen = new Set<string>();

  if (result.disease && !seen.has(result.disease)) {
    nodes.push({ id: result.disease, label: result.disease, type: "Disease", hop: 1 });
    seen.add(result.disease);
  }

  result.pathway?.pathways?.forEach((p: any) => {
    if (p.specialist_name && !seen.has(p.specialist_name)) {
      nodes.push({ id: p.specialist_name, label: p.specialist_name, type: "Specialist", hop: 2 });
      seen.add(p.specialist_name);
    }
    if (p.treatment_name && !seen.has(p.treatment_name)) {
      nodes.push({ id: p.treatment_name, label: p.treatment_name, type: "Treatment", hop: 2 });
      seen.add(p.treatment_name);
    }
    if (p.drug_name && !seen.has(p.drug_name)) {
      nodes.push({ id: p.drug_name, label: p.drug_name, type: "Drug", hop: 3 });
      seen.add(p.drug_name);
    }
  });

  return nodes;
}

function buildPathEdges(result: any) {
  const edges: any[] = [];
  const seen = new Set<string>();

  result.pathway?.pathways?.forEach((p: any) => {
    const key1 = `${result.disease}->${p.specialist_name}`;
    if (!seen.has(key1)) {
      edges.push({ source: result.disease, target: p.specialist_name, label: "refers" });
      seen.add(key1);
    }
    const key2 = `${result.disease}->${p.treatment_name}`;
    if (!seen.has(key2)) {
      edges.push({
        source: result.disease,
        target: p.treatment_name,
        label: `${(p.success_rate * 100).toFixed(0)}%`,
        weight: p.success_rate,
      });
      seen.add(key2);
    }
    const key3 = `${p.treatment_name}->${p.drug_name}`;
    if (!seen.has(key3)) {
      edges.push({ source: p.treatment_name, target: p.drug_name, label: p.dosage || "" });
      seen.add(key3);
    }
  });

  return edges;
}

function buildPathAnimation(result: any) {
  const disease = result.disease ? [result.disease] : [];
  const specialists = new Set<string>();
  const treatments = new Set<string>();
  const drugs = new Set<string>();

  result.pathway?.pathways?.forEach((p: any) => {
    if (p.specialist_name) specialists.add(p.specialist_name);
    if (p.treatment_name) treatments.add(p.treatment_name);
    if (p.drug_name) drugs.add(p.drug_name);
  });

  return [
    { hop: 1, nodes: disease, edges: [] },
    { hop: 2, nodes: [...specialists, ...treatments], edges: [] },
    { hop: 3, nodes: [...drugs], edges: [] },
  ];
}
