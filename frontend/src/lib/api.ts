const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  analyze: (text: string) =>
    request<any>("/api/analyze", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  drugCheck: (drugs: string[]) =>
    request<any>("/api/drug-check", {
      method: "POST",
      body: JSON.stringify({ drugs }),
    }),

  treatmentPath: (disease: string) =>
    request<any>("/api/treatment-path", {
      method: "POST",
      body: JSON.stringify({ disease }),
    }),

  rareDisease: (symptoms: string[]) =>
    request<any>("/api/rare-disease", {
      method: "POST",
      body: JSON.stringify({ symptoms }),
    }),

  patientRisks: (patientId: string) =>
    request<any>(`/api/patient/${patientId}/risks`),

  diseaseRankings: () => request<any>("/api/disease-rankings"),

  patientContext: (patientId: string) =>
    request<any>(`/api/patient/${patientId}/context`),

  graphOverview: () => request<any>("/api/graph/overview"),

  // Voice
  tts: (text: string, language: string) =>
    request<any>("/api/voice/tts", {
      method: "POST",
      body: JSON.stringify({ text, language }),
    }),

  stt: async (audioBlob: Blob, language: string) => {
    const form = new FormData();
    form.append("audio", audioBlob);
    form.append("language", language);
    const res = await fetch(`${API_BASE}/api/voice/stt`, {
      method: "POST",
      body: form,
    });
    return res.json();
  },

  // Calls
  initiateCall: (patientId: string) =>
    request<any>("/api/calls/initiate", {
      method: "POST",
      body: JSON.stringify({ patient_id: patientId }),
    }),

  endCall: (callSid: string) =>
    request<any>(`/api/calls/end/${callSid}`, { method: "POST" }),

  demoTrigger: () =>
    request<any>("/api/calls/demo-trigger", { method: "POST" }),

  dueFollowups: () => request<any>("/api/calls/followups/due"),

  // Call by phone number
  callNumber: (phone_number: string, patient_name?: string, language?: string) =>
    request<any>("/api/calls/call-number", {
      method: "POST",
      body: JSON.stringify({ phone_number, patient_name: patient_name || "Patient", language: language || "hi" }),
    }),

  // LiveKit
  livekitToken: (patient_name?: string, language?: string) =>
    request<any>("/api/livekit/token", {
      method: "POST",
      body: JSON.stringify({ patient_name: patient_name || "Patient", language: language || "hi" }),
    }),

  livekitGreeting: (room_name: string) =>
    request<any>("/api/livekit/greeting", {
      method: "POST",
      body: JSON.stringify({ room_name }),
    }),

  livekitRespond: (room_name: string, speech_text: string) =>
    request<any>("/api/livekit/respond", {
      method: "POST",
      body: JSON.stringify({ room_name, speech_text }),
    }),

  livekitEnd: (room_name: string) =>
    request<any>("/api/livekit/end", {
      method: "POST",
      body: JSON.stringify({ room_name }),
    }),

  livekitStatus: () => request<any>("/api/livekit/status"),
};
