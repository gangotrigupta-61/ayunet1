import { useState } from "react";
import { AlertTriangle, Shield, Activity, FlaskConical, ChevronRight } from "lucide-react";
import { api } from "../lib/api";
import GraphView from "./GraphView";

const PATIENTS = [
  { id: "aryan", name: "Aryan", language: "hi", conditions: "Dengue (Active)" },
  { id: "priya", name: "Priya", language: "hi", conditions: "Dengue + Diabetes" },
  { id: "karthik", name: "Karthik", language: "ta", conditions: "CAD + Hypertension" },
  { id: "ananya", name: "Ananya", language: "te", conditions: "Lupus + Anemia" },
  { id: "rahul", name: "Rahul", language: "en", conditions: "Hypertension + Diabetes + CAD" },
  { id: "meera", name: "Meera", language: "bn", conditions: "Hypothyroid + Depression + Anemia" },
  { id: "suresh", name: "Suresh", language: "hi", conditions: "Diabetes + CKD + Hypertension" },
  { id: "lakshmi", name: "Lakshmi", language: "ta", conditions: "Asthma + Gastritis" },
  { id: "dev", name: "Dev", language: "en", conditions: "Typhoid (Active)" },
  { id: "fatima", name: "Fatima", language: "hi", conditions: "RA + Migraine" },
];

export default function RiskAnalysisTab() {
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [activeView, setActiveView] = useState<"graph" | "details">("graph");

  async function handleAnalyze() {
    if (!selected) return;
    setLoading(true);
    try {
      const data = await api.patientRisks(selected);
      setResult(data);
      setActiveView("details");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  const graphNodes = result ? buildRiskNodes(result) : [];
  const graphEdges = result ? buildRiskEdges(result) : [];
  const animSeq = result ? buildRiskAnimation(result) : [];
  const predictions = result?.risks?.predictions || [];
  const existingDiseases = result?.risks?.hop1_existing_diseases || [];
  const riskFactors = result?.risks?.hop2_risk_factors || [];

  return (
    <div className="h-full flex gap-4">
      {/* Left — Patient Selector */}
      <div className="w-[260px] shrink-0 flex flex-col">
        <div className="bg-white dark:bg-slate-900/60 backdrop-blur border border-slate-200 dark:border-white/10 rounded-2xl p-4 shadow-sm dark:shadow-none flex flex-col h-full">
          <h3 className="text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-3">
            Select Patient
          </h3>
          <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
            {PATIENTS.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelected(p.id)}
                className={`w-full text-left px-3 py-2.5 rounded-xl transition-all text-sm ${
                  selected === p.id
                    ? "bg-yellow-50 dark:bg-yellow-500/20 border border-yellow-400 dark:border-yellow-500"
                    : "bg-slate-50 dark:bg-slate-800 border border-transparent hover:border-yellow-500/50"
                }`}
              >
                <div className="font-bold text-slate-900 dark:text-white">{p.name}</div>
                <div className="text-xs text-slate-500 dark:text-slate-400 truncate">
                  {p.language.toUpperCase()} | {p.conditions}
                </div>
              </button>
            ))}
          </div>
          <button
            onClick={handleAnalyze}
            disabled={loading || !selected}
            className="w-full mt-3 bg-yellow-600 hover:bg-yellow-500 text-white py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50 transition-colors"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Shield className="w-4 h-4" />
            )}
            Predict Risk
          </button>
        </div>
      </div>

      {/* Right — Results */}
      <div className="flex-1 flex flex-col gap-4 min-w-0">
        {result ? (
          <>
            {/* Top bar: Hop summary + view toggle */}
            <div className="flex items-center gap-3">
              {/* Hop summary pills */}
              <div className="flex items-center gap-2 flex-1 overflow-x-auto">
                <HopPill hop={1} label="Existing" count={existingDiseases.length} color="blue" />
                <ChevronRight className="w-4 h-4 text-slate-400 shrink-0" />
                <HopPill hop={2} label="Risk Factors" count={riskFactors.length} color="amber" />
                <ChevronRight className="w-4 h-4 text-slate-400 shrink-0" />
                <HopPill hop={3} label="Predicted" count={predictions.length} color="red" />
                <ChevronRight className="w-4 h-4 text-slate-400 shrink-0" />
                <HopPill
                  hop={4}
                  label="Tests Needed"
                  count={result?.risks?.hop4_required_tests?.length || 0}
                  color="purple"
                />
              </div>
              {/* View toggle */}
              <div className="flex bg-slate-100 dark:bg-slate-800 rounded-xl p-1 shrink-0">
                <button
                  onClick={() => setActiveView("details")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    activeView === "details"
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                      : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                  }`}
                >
                  Details
                </button>
                <button
                  onClick={() => setActiveView("graph")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                    activeView === "graph"
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                      : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                  }`}
                >
                  Graph
                </button>
              </div>
            </div>

            {activeView === "details" ? (
              /* Detail view — risk predictions */
              <div className="flex-1 overflow-y-auto">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                  {predictions.map((p: any, i: number) => (
                    <div
                      key={i}
                      className={`rounded-2xl p-4 border shadow-sm dark:shadow-none transition-all ${
                        p.risk_score > 2
                          ? "bg-red-50 dark:bg-red-500/10 border-red-300 dark:border-red-500/50"
                          : p.risk_score > 1.5
                          ? "bg-amber-50 dark:bg-amber-500/10 border-amber-300 dark:border-amber-500/50"
                          : "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-white/10"
                      }`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {p.risk_score > 1.5 && (
                            <AlertTriangle
                              className={`w-5 h-5 shrink-0 ${
                                p.risk_score > 2
                                  ? "text-red-500 animate-pulse"
                                  : "text-amber-500"
                              }`}
                            />
                          )}
                          <span className="font-bold text-slate-900 dark:text-white">
                            {p.predicted_disease}
                          </span>
                        </div>
                        <span
                          className={`font-mono text-lg font-black ${
                            p.risk_score > 2
                              ? "text-red-500"
                              : p.risk_score > 1.5
                              ? "text-amber-500"
                              : "text-green-500"
                          }`}
                        >
                          {p.risk_score.toFixed(1)}x
                        </span>
                      </div>

                      <div className="space-y-2 text-sm">
                        <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                          <Activity className="w-3.5 h-3.5 shrink-0" />
                          <span>Via: <span className="font-medium text-slate-800 dark:text-slate-200">{p.via_risk_factor}</span></span>
                        </div>
                        <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
                          <FlaskConical className="w-3.5 h-3.5 shrink-0" />
                          <span>Test: <span className="font-medium text-slate-800 dark:text-slate-200">{p.required_test}</span></span>
                          <span
                            className={`ml-auto text-xs font-bold px-2 py-0.5 rounded-full ${
                              p.test_completed
                                ? "bg-green-100 dark:bg-green-500/20 text-green-700 dark:text-green-300"
                                : "bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-300"
                            }`}
                          >
                            {p.test_completed ? "Done" : "Pending"}
                          </span>
                        </div>
                      </div>

                      {/* Risk bar */}
                      <div className="mt-3 relative">
                        <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-700 ${
                              p.risk_score > 2
                                ? "bg-red-500"
                                : p.risk_score > 1.5
                                ? "bg-amber-500"
                                : "bg-green-500"
                            }`}
                            style={{ width: `${Math.min(p.risk_score * 33, 100)}%` }}
                          />
                        </div>
                        <div
                          className="absolute top-0 h-2 w-0.5 bg-slate-400 dark:bg-white/40"
                          style={{ left: "50%" }}
                        />
                      </div>
                    </div>
                  ))}

                  {predictions.length === 0 && (
                    <div className="col-span-2 text-center py-12 text-slate-400 dark:text-slate-500">
                      No comorbidity risks predicted for this patient.
                    </div>
                  )}
                </div>

                {/* Existing conditions + risk factors summary */}
                {(existingDiseases.length > 0 || riskFactors.length > 0) && (
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    {existingDiseases.length > 0 && (
                      <div className="bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/30 rounded-xl p-3">
                        <h5 className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider mb-2">
                          Hop 1: Existing Diseases
                        </h5>
                        <div className="flex flex-wrap gap-1.5">
                          {existingDiseases.map((d: string) => (
                            <span key={d} className="text-xs px-2 py-1 rounded-lg bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300 font-medium">
                              {d}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {riskFactors.length > 0 && (
                      <div className="bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/30 rounded-xl p-3">
                        <h5 className="text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider mb-2">
                          Hop 2: Risk Factors
                        </h5>
                        <div className="flex flex-wrap gap-1.5">
                          {riskFactors.map((r: string) => (
                            <span key={r} className="text-xs px-2 py-1 rounded-lg bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300 font-medium">
                              {r}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              /* Graph view */
              <div className="flex-1 min-h-0">
                <GraphView
                  nodes={graphNodes}
                  edges={graphEdges}
                  animationSequence={animSeq}
                  layout="concentric"
                />
              </div>
            )}
          </>
        ) : (
          /* Empty state */
          <div className="flex-1 flex items-center justify-center bg-slate-50 dark:bg-slate-950/50 rounded-2xl border border-slate-200 dark:border-white/10">
            <div className="text-center">
              <Shield className="w-12 h-12 text-slate-300 dark:text-slate-700 mx-auto mb-3" />
              <p className="text-slate-400 dark:text-slate-500 text-sm">
                Select a patient and click <b>Predict Risk</b> to run 4-hop comorbidity analysis
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function HopPill({
  hop,
  label,
  count,
  color,
}: {
  hop: number;
  label: string;
  count: number;
  color: string;
}) {
  const colors: Record<string, string> = {
    blue: "bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-500/30",
    amber: "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-500/30",
    red: "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-300 border-red-200 dark:border-red-500/30",
    purple: "bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-500/30",
  };
  return (
    <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold border shrink-0 ${colors[color]}`}>
      <span className="opacity-60">H{hop}</span>
      <span>{label}</span>
      <span className="bg-white/60 dark:bg-black/20 px-1.5 py-0.5 rounded-full text-[10px]">{count}</span>
    </div>
  );
}

function buildRiskNodes(result: any) {
  const nodes: any[] = [];
  const seen = new Set<string>();

  nodes.push({
    id: result.patient_id || "patient",
    label: result.patient_id || "Patient",
    type: "Patient",
    hop: 0,
  });

  result.risks?.hop1_existing_diseases?.forEach((d: string) => {
    if (!seen.has(d)) {
      nodes.push({ id: d, label: d, type: "Disease", hop: 1 });
      seen.add(d);
    }
  });

  result.risks?.hop2_risk_factors?.forEach((r: string) => {
    if (!seen.has(r)) {
      nodes.push({ id: r, label: r, type: "RiskFactor", hop: 2 });
      seen.add(r);
    }
  });

  result.risks?.hop3_predicted_diseases?.forEach((d: string) => {
    if (!seen.has(d)) {
      nodes.push({ id: `pred_${d}`, label: d, type: "Disease", hop: 3, score: 0.8 });
      seen.add(d);
    }
  });

  result.risks?.hop4_required_tests?.forEach((t: string) => {
    if (!seen.has(t)) {
      nodes.push({ id: t, label: t, type: "LabTest", hop: 4 });
      seen.add(t);
    }
  });

  return nodes;
}

function buildRiskEdges(result: any) {
  const edges: any[] = [];
  const pid = result.patient_id || "patient";

  result.risks?.hop1_existing_diseases?.forEach((d: string) => {
    edges.push({ source: pid, target: d, label: "has" });
  });

  result.risks?.predictions?.forEach((p: any) => {
    edges.push({
      source: p.via_risk_factor,
      target: `pred_${p.predicted_disease}`,
      label: `${p.risk_score.toFixed(1)}x`,
      weight: p.risk_score / 3,
    });
    if (p.required_test) {
      edges.push({
        source: `pred_${p.predicted_disease}`,
        target: p.required_test,
        label: "needs",
      });
    }
  });

  return edges;
}

function buildRiskAnimation(result: any) {
  const pid = result.patient_id || "patient";
  return [
    { hop: 1, nodes: [pid], edges: [] },
    { hop: 2, nodes: result.risks?.hop1_existing_diseases || [], edges: [] },
    { hop: 3, nodes: result.risks?.hop2_risk_factors || [], edges: [] },
    {
      hop: 4,
      nodes: [
        ...(result.risks?.hop3_predicted_diseases?.map((d: string) => `pred_${d}`) || []),
        ...(result.risks?.hop4_required_tests || []),
      ],
      edges: [],
    },
  ];
}
