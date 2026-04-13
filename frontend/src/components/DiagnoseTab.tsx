import { useState, useRef } from "react";
import { Mic, MicOff, Search, Volume2 } from "lucide-react";
import { api } from "../lib/api";
import GraphView from "./GraphView";

export default function DiagnoseTab() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [recording, setRecording] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  async function handleAnalyze() {
    if (!input.trim()) return;
    setLoading(true);
    try {
      const data = await api.analyze(input);
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function handleTTS(text: string, language: string) {
    try {
      const data = await api.tts(text, language);
      if (data.audio_base64) {
        const audio = new Audio(`data:audio/wav;base64,${data.audio_base64}`);
        audio.play();
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function toggleRecording() {
    if (recording) {
      // Stop recording
      mediaRecorderRef.current?.stop();
      setRecording(false);
    } else {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
        chunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) chunksRef.current.push(e.data);
        };

        mediaRecorder.onstop = async () => {
          stream.getTracks().forEach((t) => t.stop());
          const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
          if (audioBlob.size === 0) return;

          setLoading(true);
          try {
            const sttResult = await api.stt(audioBlob, "hi");
            if (sttResult.transcript) {
              setInput(sttResult.transcript);
              // Auto-analyze after STT
              const data = await api.analyze(sttResult.transcript);
              setResult(data);
            }
          } catch (err) {
            console.error("STT failed:", err);
          } finally {
            setLoading(false);
          }
        };

        mediaRecorder.start();
        mediaRecorderRef.current = mediaRecorder;
        setRecording(true);
      } catch (err) {
        console.error("Mic access denied:", err);
      }
    }
  }

  const graphNodes = result ? buildDiagnosisGraphNodes(result) : [];
  const graphEdges = result ? buildDiagnosisGraphEdges(result) : [];
  const animationSeq = result ? buildDiagnosisAnimation(result) : [];

  return (
    <div className="h-full flex gap-6">
      {/* Left: Input Panel */}
      <div className="w-[380px] shrink-0 flex flex-col gap-4">
        <div className="bg-white dark:bg-slate-900/60 backdrop-blur border border-slate-200 dark:border-white/10 rounded-2xl p-5 shadow-sm dark:shadow-none">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-4">
            Describe Symptoms
          </h3>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="e.g. Mujhe do din se bukhar hai, pet mein dard..."
            className="w-full h-28 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-white/10 rounded-xl p-3 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
          />
          <div className="flex gap-2 mt-3">
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50 transition-colors"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Analyze
            </button>
            <button
              onClick={toggleRecording}
              className={`p-2.5 rounded-xl border transition-all ${
                recording
                  ? "bg-red-500/20 border-red-500 text-red-400"
                  : "bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-white/10 text-slate-400 hover:border-indigo-500"
              }`}
            >
              {recording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Extracted symptoms */}
        {result?.extracted && (
          <div className="bg-white dark:bg-slate-900/60 backdrop-blur border border-slate-200 dark:border-white/10 rounded-2xl p-5 shadow-sm dark:shadow-none">
            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-3">
              Extracted ({result.extracted.language})
            </h4>
            <div className="flex flex-wrap gap-2">
              {result.extracted.symptoms?.map((s: string) => (
                <span
                  key={s}
                  className="px-3 py-1 bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-300 rounded-full text-xs font-bold"
                >
                  {s}
                </span>
              ))}
            </div>
            {result.extracted.severity && (
              <div className="mt-2 text-xs text-slate-400 dark:text-slate-500">
                Severity: <span className="text-amber-600 dark:text-amber-400">{result.extracted.severity}</span>
              </div>
            )}
          </div>
        )}

        {/* Diagnosis results */}
        {result?.diagnoses?.diagnoses && (
          <div className="flex-1 overflow-y-auto space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">
              Top Diagnoses
            </h4>
            {result.diagnoses.diagnoses.map((d: any, i: number) => (
              <div
                key={i}
                className="bg-white dark:bg-slate-900/60 backdrop-blur border border-slate-200 dark:border-white/10 rounded-xl p-4 hover:border-red-300 dark:hover:border-red-500/30 transition-colors shadow-sm dark:shadow-none"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h5 className="font-bold text-slate-900 dark:text-white">{d.disease_name}</h5>
                    <span className="text-xs text-slate-500">ICD: {d.icd_code}</span>
                  </div>
                  <button
                    onClick={() =>
                      handleTTS(
                        `The diagnosis is ${d.disease_name}`,
                        result.language || "en"
                      )
                    }
                    className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-indigo-600 hover:text-white transition-colors"
                  >
                    <Volume2 className="w-3.5 h-3.5 text-slate-400" />
                  </button>
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-2 mb-1">
                  <div
                    className="bg-gradient-to-r from-red-500 to-red-400 h-2 rounded-full transition-all"
                    style={{
                      width: `${Math.min(d.confidence_score * 100, 100)}%`,
                    }}
                  />
                </div>
                <div className="flex justify-between text-xs text-slate-500">
                  <span>{d.matched_count} symptoms matched</span>
                  <span>{(d.confidence_score * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Selected node detail */}
        {selectedNode && (
          <div className="bg-white dark:bg-slate-900/60 backdrop-blur border border-indigo-200 dark:border-indigo-500/30 rounded-2xl p-4 shadow-sm dark:shadow-none">
            <h4 className="text-xs font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400 mb-2">
              {selectedNode.type}
            </h4>
            <p className="font-bold text-slate-900 dark:text-white">{selectedNode.label}</p>
          </div>
        )}
      </div>

      {/* Right: Graph */}
      <div className="flex-1 min-h-[500px]">
        {graphNodes.length > 0 ? (
          <GraphView
            nodes={graphNodes}
            edges={graphEdges}
            animationSequence={animationSeq}
            layout="concentric"
            onNodeClick={(_, data) => setSelectedNode(data)}
          />
        ) : (
          <div className="h-full flex items-center justify-center bg-slate-50 dark:bg-slate-950/50 rounded-2xl border border-slate-200 dark:border-white/10">
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-indigo-500/10 flex items-center justify-center mx-auto mb-4">
                <Search className="w-8 h-8 text-indigo-500/50" />
              </div>
              <p className="text-slate-400 dark:text-slate-500 text-sm">
                Enter symptoms to see the graph traversal
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// --- Graph data builders ---

function buildDiagnosisGraphNodes(result: any) {
  const nodes: any[] = [];
  const seen = new Set<string>();

  result.extracted?.symptoms?.forEach((s: string) => {
    if (!seen.has(s)) {
      nodes.push({ id: s, label: s, type: "Symptom", hop: 1 });
      seen.add(s);
    }
  });

  result.diagnoses?.diagnoses?.forEach((d: any) => {
    if (!seen.has(d.disease_id)) {
      nodes.push({
        id: d.disease_id,
        label: d.disease_name,
        type: "Disease",
        score: d.confidence_score,
        hop: 2,
      });
      seen.add(d.disease_id);
    }
  });

  return nodes;
}

function buildDiagnosisGraphEdges(result: any) {
  const edges: any[] = [];
  const symptoms = result.extracted?.symptoms || [];

  result.diagnoses?.diagnoses?.forEach((d: any) => {
    symptoms.forEach((s: string) => {
      edges.push({
        source: s,
        target: d.disease_id,
        label: `${(d.confidence_score / (d.matched_count || 1)).toFixed(1)}`,
        weight: d.confidence_score / (d.matched_count || 1),
      });
    });
  });

  return edges;
}

function buildDiagnosisAnimation(result: any) {
  const symptoms = result.extracted?.symptoms || [];
  const diseases = result.diagnoses?.diagnoses || [];

  if (!symptoms.length || !diseases.length) return [];

  return [
    {
      hop: 1,
      nodes: symptoms,
      edges: [],
    },
    {
      hop: 2,
      nodes: diseases.map((d: any) => d.disease_id),
      edges: [],
    },
  ];
}
