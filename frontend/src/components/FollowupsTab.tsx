import { useState, useEffect } from "react";
import {
  Phone,
  PhoneOff,
  PhoneCall,
  Clock,
  CheckCircle2,
  AlertTriangle,
  PhoneOutgoing,
  Loader2,
} from "lucide-react";
import { api } from "../lib/api";
import type { Alert } from "../hooks/useWebSocket";

interface Props {
  alerts: Alert[];
}

export default function FollowupsTab({ alerts }: Props) {
  const [followups, setFollowups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [callingId, setCallingId] = useState<string | null>(null);
  const [callStatus, setCallStatus] = useState<Record<string, string>>({});
  const [callSids, setCallSids] = useState<Record<string, string>>({});
  const [transcripts, setTranscripts] = useState<Alert[]>([]);

  // Quick Call state
  const [quickPhone, setQuickPhone] = useState("");
  const [quickName, setQuickName] = useState("");
  const [quickLang, setQuickLang] = useState("hi");
  const [quickCalling, setQuickCalling] = useState(false);
  const [quickCallSid, setQuickCallSid] = useState("");

  useEffect(() => {
    loadFollowups();
  }, []);

  useEffect(() => {
    const callAlerts = alerts.filter(
      (a) => a.type === "call_transcript" || a.type === "risk_alert"
    );
    setTranscripts(callAlerts);
  }, [alerts]);

  async function loadFollowups() {
    setLoading(true);
    try {
      const data = await api.dueFollowups();
      setFollowups(data.followups?.patients || []);
    } catch (err) {
      console.error(err);
      setFollowups([
        {
          patient_id: "aryan",
          patient_name: "Aryan",
          phone: "+91-7985582272",
          language: "hi",
          condition: "Dengue Fever",
          followup_day: 1,
          scheduled_date: new Date().toISOString().split("T")[0],
        },
        {
          patient_id: "karthik",
          patient_name: "Karthik",
          phone: "+91-XXXXXXXX",
          language: "ta",
          condition: "Post-surgery",
          followup_day: 7,
          scheduled_date: new Date().toISOString().split("T")[0],
        },
        {
          patient_id: "priya",
          patient_name: "Priya",
          phone: "+91-XXXXXXXX",
          language: "hi",
          condition: "Dengue + Diabetes",
          followup_day: 3,
          scheduled_date: new Date().toISOString().split("T")[0],
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleCall(patientId: string) {
    setCallingId(patientId);
    setCallStatus((prev) => ({ ...prev, [patientId]: "preparing" }));

    try {
      const data = await api.initiateCall(patientId);
      if (data.call_sid) {
        setCallSids((prev) => ({ ...prev, [patientId]: data.call_sid }));
      }
      setCallStatus((prev) => ({
        ...prev,
        [patientId]: "ringing",
      }));
      setTimeout(() => {
        setCallStatus((prev) => ({
          ...prev,
          [patientId]: "in-progress",
        }));
      }, 3000);
    } catch (err) {
      console.error(err);
      setCallStatus((prev) => ({ ...prev, [patientId]: "failed" }));
      setCallingId(null);
    }
  }

  async function handleEndCall(patientId: string) {
    const callSid = callSids[patientId];
    if (!callSid) return;

    try {
      await api.endCall(callSid);
    } catch (err) {
      console.error("Failed to end call:", err);
    }
    setCallStatus((prev) => ({ ...prev, [patientId]: "completed" }));
    setCallingId(null);
  }

  async function handleDemoTrigger() {
    setCallingId("demo");
    try {
      const data = await api.demoTrigger();
      if (data.patient) {
        const pid = data.patient.patient_id;
        if (data.call_sid) {
          setCallSids((prev) => ({ ...prev, [pid]: data.call_sid }));
        }
        setCallStatus((prev) => ({
          ...prev,
          [pid]: "ringing",
        }));
        setCallingId(pid);
        setTimeout(() => {
          setCallStatus((prev) => ({
            ...prev,
            [pid]: "in-progress",
          }));
        }, 3000);
      }
    } catch (err) {
      console.error(err);
      setCallingId(null);
    }
  }

  async function handleQuickCall() {
    if (!quickPhone.trim()) return;
    setQuickCalling(true);
    try {
      const data = await api.callNumber(quickPhone, quickName || "Patient", quickLang);
      if (data.call_sid) {
        setQuickCallSid(data.call_sid);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setQuickCalling(false);
    }
  }

  async function handleEndQuickCall() {
    if (!quickCallSid) return;
    try {
      await api.endCall(quickCallSid);
    } catch (err) {
      console.error(err);
    }
    setQuickCallSid("");
  }

  const statusColors: Record<string, string> = {
    preparing: "text-yellow-600 dark:text-yellow-400",
    ringing: "text-blue-600 dark:text-blue-400",
    "in-progress": "text-emerald-600 dark:text-emerald-400",
    completed: "text-slate-500 dark:text-slate-400",
    failed: "text-red-500 dark:text-red-400",
  };

  const statusIcons: Record<string, any> = {
    preparing: Clock,
    ringing: PhoneCall,
    "in-progress": Phone,
    completed: CheckCircle2,
    failed: PhoneOff,
  };

  return (
    <div className="h-full flex gap-6">
      {/* Left: Follow-up list + Quick Call */}
      <div className="w-[400px] shrink-0 flex flex-col gap-4">
        {/* Quick Call card */}
        <div className="bg-white dark:bg-slate-900/60 backdrop-blur border border-slate-200 dark:border-white/10 rounded-2xl p-5 shadow-sm dark:shadow-none">
          <div className="flex items-center gap-2 mb-4">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center">
              <PhoneOutgoing className="w-3.5 h-3.5 text-white" />
            </div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              Quick Call
            </h3>
          </div>

          <div className="space-y-2.5">
            <input
              type="tel"
              value={quickPhone}
              onChange={(e) => setQuickPhone(e.target.value)}
              placeholder="Phone number (e.g. +91...)"
              className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-white/10 rounded-xl px-3 py-2.5 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
            />
            <div className="flex gap-2">
              <input
                type="text"
                value={quickName}
                onChange={(e) => setQuickName(e.target.value)}
                placeholder="Patient name"
                className="flex-1 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-white/10 rounded-xl px-3 py-2 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500"
              />
              <select
                value={quickLang}
                onChange={(e) => setQuickLang(e.target.value)}
                className="w-20 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-white/10 rounded-xl px-2 py-2 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              >
                <option value="hi">HI</option>
                <option value="en">EN</option>
                <option value="ta">TA</option>
                <option value="te">TE</option>
                <option value="bn">BN</option>
                <option value="kn">KN</option>
                <option value="mr">MR</option>
              </select>
            </div>

            {!quickCallSid ? (
              <button
                onClick={handleQuickCall}
                disabled={quickCalling || !quickPhone.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 disabled:opacity-50 transition-all"
              >
                {quickCalling ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Phone className="w-4 h-4" />
                )}
                Call Number
              </button>
            ) : (
              <button
                onClick={handleEndQuickCall}
                className="w-full bg-red-600 hover:bg-red-500 text-white py-2.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all"
              >
                <PhoneOff className="w-4 h-4" />
                End Call
              </button>
            )}
          </div>
        </div>

        {/* Follow-up list */}
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500">
            Today's Follow-ups
          </h3>
          <button
            onClick={handleDemoTrigger}
            className="px-3 py-1.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-lg text-[11px] font-bold transition-colors hover:bg-slate-700 dark:hover:bg-slate-200"
          >
            Demo Trigger
          </button>
        </div>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-24 bg-slate-100 dark:bg-slate-900/60 rounded-xl animate-pulse border border-slate-200 dark:border-white/5"
              />
            ))}
          </div>
        ) : (
          <div className="space-y-3 flex-1 overflow-y-auto">
            {followups.map((fu) => {
              const status = callStatus[fu.patient_id];
              const StatusIcon = statusIcons[status] || Clock;

              return (
                <div
                  key={fu.patient_id}
                  className={`bg-white dark:bg-slate-900/60 backdrop-blur border rounded-xl p-4 transition-all shadow-sm dark:shadow-none ${
                    status === "in-progress"
                      ? "border-emerald-300 dark:border-emerald-500/30"
                      : status === "ringing"
                      ? "border-blue-300 dark:border-blue-500/30"
                      : "border-slate-200 dark:border-white/10"
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-bold text-slate-900 dark:text-white text-sm">
                        {fu.patient_name}
                      </h4>
                      <div className="text-[11px] text-slate-400 dark:text-slate-500 space-x-2 mt-0.5 font-medium">
                        <span>{fu.language?.toUpperCase()}</span>
                        <span>|</span>
                        <span>{fu.condition}</span>
                        <span>|</span>
                        <span>Day {fu.followup_day}</span>
                      </div>
                    </div>
                    {status && (
                      <div
                        className={`flex items-center gap-1.5 ${statusColors[status]}`}
                      >
                        <StatusIcon className="w-3.5 h-3.5" />
                        <span className="text-[11px] font-bold capitalize">{status}</span>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() =>
                      status === "in-progress"
                        ? handleEndCall(fu.patient_id)
                        : handleCall(fu.patient_id)
                    }
                    disabled={
                      status === "preparing" ||
                      status === "ringing" ||
                      status === "completed" ||
                      (!!callingId &&
                        callingId !== fu.patient_id &&
                        status !== "in-progress")
                    }
                    className={`w-full py-2 rounded-xl text-sm font-bold flex items-center justify-center gap-2 transition-all ${
                      status === "in-progress"
                        ? "bg-red-600 hover:bg-red-500 text-white"
                        : "bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50"
                    }`}
                  >
                    {status === "in-progress" ? (
                      <>
                        <PhoneOff className="w-3.5 h-3.5" /> End Call
                      </>
                    ) : status === "ringing" ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        Ringing...
                      </>
                    ) : status === "preparing" ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        Preparing...
                      </>
                    ) : (
                      <>
                        <Phone className="w-3.5 h-3.5" /> Call Now
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Right: Live transcript + alerts */}
      <div className="flex-1 flex flex-col gap-4">
        <div className="bg-white dark:bg-slate-900/60 backdrop-blur border border-slate-200 dark:border-white/10 rounded-2xl p-5 flex-1 overflow-y-auto shadow-sm dark:shadow-none">
          <h4 className="text-xs font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-4">
            Live Call Transcript
          </h4>
          {transcripts.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <p className="text-slate-400 dark:text-slate-500 text-sm">
                Call a patient to see the live transcript here
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {transcripts.map((t, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-xl border ${
                    t.type === "risk_alert"
                      ? "bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/30"
                      : "bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-white/5"
                  }`}
                >
                  {t.type === "risk_alert" ? (
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-red-500 dark:text-red-400 animate-pulse" />
                      <span className="font-bold text-red-600 dark:text-red-300 text-sm">
                        RISK ALERT: {t.patient_name}
                      </span>
                      <span className="ml-auto text-xs text-red-500 dark:text-red-400">
                        Pain: {t.pain_score} | Symptoms:{" "}
                        {t.new_symptoms?.join(", ")}
                      </span>
                    </div>
                  ) : (
                    <>
                      <div className="text-[11px] text-slate-400 dark:text-slate-500 mb-1 font-medium">
                        Turn {t.turn} | {t.call_sid?.slice(0, 10)}
                      </div>
                      <p className="text-sm text-slate-900 dark:text-white">
                        {t.patient_speech}
                      </p>
                      {t.extracted && (
                        <div className="mt-2 flex flex-wrap gap-2">
                          {t.extracted.pain_score != null && (
                            <span className="text-[11px] px-2 py-0.5 rounded-lg bg-amber-50 dark:bg-amber-500/10 text-amber-700 dark:text-amber-300 font-semibold border border-amber-200 dark:border-amber-500/20">
                              Pain: {t.extracted.pain_score}
                            </span>
                          )}
                          {t.extracted.took_medication != null && (
                            <span className="text-[11px] px-2 py-0.5 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 font-semibold border border-emerald-200 dark:border-emerald-500/20">
                              Medication:{" "}
                              {t.extracted.took_medication ? "Yes" : "No"}
                            </span>
                          )}
                          {t.extracted.new_symptoms?.length > 0 && (
                            <span className="text-[11px] px-2 py-0.5 rounded-lg bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-300 font-semibold border border-red-200 dark:border-red-500/20">
                              New: {t.extracted.new_symptoms.join(", ")}
                            </span>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
