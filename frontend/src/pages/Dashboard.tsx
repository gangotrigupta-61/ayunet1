import { useState, useEffect } from "react";
import {
  Network,
  Search,
  Pill,
  ArrowRight,
  Shield,
  Phone,
  Bell,
  X,
  Sun,
  Moon,
  Mic,
  Activity,
  ChevronRight,
} from "lucide-react";
import { useWebSocket } from "../hooks/useWebSocket";
import DiagnoseTab from "../components/DiagnoseTab";
import DrugCheckTab from "../components/DrugCheckTab";
import TreatmentPathTab from "../components/TreatmentPathTab";
import RiskAnalysisTab from "../components/RiskAnalysisTab";
import FollowupsTab from "../components/FollowupsTab";
import LiveKitVoice from "../components/LiveKitVoice";

const TABS = [
  { id: "diagnose", label: "Diagnose", icon: Search, color: "indigo" },
  { id: "drugs", label: "Drug Check", icon: Pill, color: "emerald" },
  { id: "treatment", label: "Treatment Path", icon: ArrowRight, color: "amber" },
  { id: "risks", label: "Risk Analysis", icon: Shield, color: "rose" },
  { id: "followups", label: "Follow-ups", icon: Phone, color: "violet" },
  { id: "voice", label: "Voice AI", icon: Mic, color: "fuchsia" },
] as const;

type TabId = (typeof TABS)[number]["id"];

const TAB_COLORS: Record<string, { active: string; icon: string }> = {
  indigo: {
    active: "bg-indigo-50 dark:bg-indigo-500/10 border-indigo-200 dark:border-indigo-500/30 text-indigo-700 dark:text-indigo-300",
    icon: "text-indigo-500",
  },
  emerald: {
    active: "bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/30 text-emerald-700 dark:text-emerald-300",
    icon: "text-emerald-500",
  },
  amber: {
    active: "bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/30 text-amber-700 dark:text-amber-300",
    icon: "text-amber-500",
  },
  rose: {
    active: "bg-rose-50 dark:bg-rose-500/10 border-rose-200 dark:border-rose-500/30 text-rose-700 dark:text-rose-300",
    icon: "text-rose-500",
  },
  violet: {
    active: "bg-violet-50 dark:bg-violet-500/10 border-violet-200 dark:border-violet-500/30 text-violet-700 dark:text-violet-300",
    icon: "text-violet-500",
  },
  fuchsia: {
    active: "bg-fuchsia-50 dark:bg-fuchsia-500/10 border-fuchsia-200 dark:border-fuchsia-500/30 text-fuchsia-700 dark:text-fuchsia-300",
    icon: "text-fuchsia-500",
  },
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabId>("diagnose");
  const { alerts, latestAlert, connected, clearLatest } = useWebSocket();

  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const saved = localStorage.getItem("ayunet-theme");
    return saved === "light" ? "light" : "dark";
  });

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("ayunet-theme", theme);
  }, [theme]);

  const riskAlerts = alerts.filter((a) => a.type === "risk_alert");

  return (
    <div className="h-screen flex bg-slate-50 dark:bg-[#060510] text-slate-900 dark:text-white overflow-hidden transition-colors duration-200">
      {/* ─── Sidebar ─── */}
      <aside className="w-[260px] border-r border-slate-200 dark:border-white/8 bg-white dark:bg-slate-950/80 backdrop-blur flex flex-col transition-colors">
        {/* Logo */}
        <div className="px-6 py-5 border-b border-slate-100 dark:border-white/5">
          <a href="/" className="flex items-center gap-3">
            <div className="h-9 w-9 bg-gradient-to-tr from-indigo-500 to-fuchsia-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Network className="h-5 w-5 text-white" />
            </div>
            <div className="flex flex-col">
              <span className="text-lg font-black tracking-tighter uppercase leading-none">
                AyuNet
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500 mt-0.5">
                Intelligence
              </span>
            </div>
          </a>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          <p className="px-3 pt-2 pb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400/80 dark:text-slate-600">
            Main Menu
          </p>
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            const colors = TAB_COLORS[tab.color];
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-[13px] font-semibold transition-all border ${
                  isActive
                    ? colors.active
                    : "border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-white/5"
                }`}
              >
                <Icon
                  className={`w-[18px] h-[18px] shrink-0 ${
                    isActive ? colors.icon : "opacity-60"
                  }`}
                />
                {tab.label}
                {tab.id === "followups" && riskAlerts.length > 0 && (
                  <span className="ml-auto w-5 h-5 bg-red-500 rounded-full text-[10px] text-white flex items-center justify-center animate-pulse font-bold">
                    {riskAlerts.length}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Status bar */}
        <div className="p-4 border-t border-slate-100 dark:border-white/5">
          <div className="flex items-center gap-2 text-[11px] text-slate-400 dark:text-slate-500 font-medium">
            <div
              className={`w-2 h-2 rounded-full ${
                connected ? "bg-emerald-500" : "bg-red-500"
              }`}
            />
            {connected ? "Connected" : "Disconnected"}
          </div>
        </div>
      </aside>

      {/* ─── Main content ─── */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* ─── Top bar ─── */}
        <header className="h-14 border-b border-slate-200 dark:border-white/8 flex items-center justify-between px-6 bg-white/80 dark:bg-slate-950/60 backdrop-blur shrink-0 transition-colors">
          <div className="flex items-center gap-3">
            <h2 className="text-[13px] font-bold uppercase tracking-[0.15em] text-slate-500 dark:text-slate-400">
              {TABS.find((t) => t.id === activeTab)?.label}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            {riskAlerts.length > 0 && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-full">
                <Bell className="w-3.5 h-3.5 text-red-500 dark:text-red-400 animate-pulse" />
                <span className="text-xs font-bold text-red-600 dark:text-red-300">
                  {riskAlerts.length} Alert{riskAlerts.length > 1 ? "s" : ""}
                </span>
              </div>
            )}
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-400 dark:text-slate-500"
            >
              {theme === "dark" ? (
                <Sun className="w-4 h-4" />
              ) : (
                <Moon className="w-4 h-4" />
              )}
            </button>
          </div>
        </header>

        {/* ─── Alert toast ─── */}
        {latestAlert && latestAlert.type === "risk_alert" && (
          <div className="mx-6 mt-3 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/30 rounded-xl p-4 flex items-center gap-3 animate-in slide-in-from-top">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
              </span>
            </div>
            <div className="flex-1">
              <p className="font-bold text-red-700 dark:text-red-300 text-sm">
                Risk Alert: {latestAlert.patient_name}
              </p>
              <p className="text-xs text-red-500/80 dark:text-red-400/80">
                Pain: {latestAlert.pain_score} | New symptoms:{" "}
                {latestAlert.new_symptoms?.join(", ")}
              </p>
            </div>
            <button
              onClick={clearLatest}
              className="p-1.5 hover:bg-red-100 dark:hover:bg-red-500/20 rounded-lg transition-colors"
            >
              <X className="w-4 h-4 text-red-400 dark:text-red-400" />
            </button>
          </div>
        )}

        {/* ─── Tab content ─── */}
        <div className="flex-1 p-6 overflow-hidden">
          {activeTab === "diagnose" && <DiagnoseTab />}
          {activeTab === "drugs" && <DrugCheckTab />}
          {activeTab === "treatment" && <TreatmentPathTab />}
          {activeTab === "risks" && <RiskAnalysisTab />}
          {activeTab === "followups" && <FollowupsTab alerts={alerts} />}
          {activeTab === "voice" && (
            <div className="h-full flex gap-6">
              <div className="flex-1 max-w-2xl mx-auto flex flex-col gap-6">
                {/* KPI strip */}
                <div className="grid grid-cols-3 gap-4">
                  <KpiCard
                    label="Voice Engine"
                    value="Sarvam AI"
                    sub="bulbul:v1 + saarika:v2"
                    color="indigo"
                  />
                  <KpiCard
                    label="Languages"
                    value="7+"
                    sub="Hindi, Tamil, Telugu, Bengali..."
                    color="violet"
                  />
                  <KpiCard
                    label="Pipeline"
                    value="Real-time"
                    sub="STT → LLM → TTS"
                    color="fuchsia"
                  />
                </div>

                {/* LiveKit voice component */}
                <LiveKitVoice />

                {/* Info card */}
                <div className="bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-white/10 rounded-2xl p-5 shadow-sm dark:shadow-none">
                  <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-3">
                    How it works
                  </h4>
                  <div className="space-y-2">
                    {[
                      "Click 'Start Voice Chat' and speak in any supported language",
                      "AI processes your speech through Sarvam STT in real-time",
                      "Groq LLM generates a contextual healthcare response",
                      "Response is spoken back via Sarvam TTS with a natural voice",
                    ].map((step, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <span className="w-5 h-5 rounded-full bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                          {i + 1}
                        </span>
                        <p className="text-sm text-slate-600 dark:text-slate-400">{step}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function KpiCard({
  label,
  value,
  sub,
  color,
}: {
  label: string;
  value: string;
  sub: string;
  color: string;
}) {
  const colorMap: Record<string, string> = {
    indigo:
      "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-white/10",
    violet:
      "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-white/10",
    fuchsia:
      "bg-white dark:bg-slate-900/60 border-slate-200 dark:border-white/10",
  };
  const accentMap: Record<string, string> = {
    indigo: "text-indigo-600 dark:text-indigo-400",
    violet: "text-violet-600 dark:text-violet-400",
    fuchsia: "text-fuchsia-600 dark:text-fuchsia-400",
  };

  return (
    <div
      className={`rounded-2xl border p-4 shadow-sm dark:shadow-none relative overflow-hidden group ${colorMap[color]}`}
    >
      <div className="absolute -right-4 -top-4 w-20 h-20 bg-slate-50 dark:bg-white/5 rounded-full blur-2xl group-hover:bg-slate-100 dark:group-hover:bg-white/10 transition-colors" />
      <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1 relative z-10">
        {label}
      </p>
      <p
        className={`text-2xl font-black tracking-tight relative z-10 ${accentMap[color]}`}
      >
        {value}
      </p>
      <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1 relative z-10 font-medium">
        {sub}
      </p>
    </div>
  );
}
