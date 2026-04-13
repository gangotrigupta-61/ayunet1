import { useState, useRef, useCallback, useEffect } from "react";
import { Mic, MicOff, Phone, PhoneOff, Volume2, Loader2 } from "lucide-react";
import { api } from "../lib/api";

type SessionState = "idle" | "connecting" | "greeting" | "listening" | "processing" | "speaking" | "ended";

interface Turn {
  role: "assistant" | "patient";
  text: string;
  turn?: number;
}

export default function LiveKitVoice() {
  const [state, setState] = useState<SessionState>("idle");
  const [roomName, setRoomName] = useState("");
  const [transcript, setTranscript] = useState<Turn[]>([]);
  const [riskFlag, setRiskFlag] = useState(false);
  const [error, setError] = useState("");

  // Audio recording
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  // Audio playback
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [transcript]);

  const startSession = useCallback(async () => {
    setState("connecting");
    setError("");
    setTranscript([]);
    setRiskFlag(false);

    try {
      const tokenData = await api.livekitToken("Patient", "hi");
      if (tokenData.error) {
        setError(tokenData.error);
        setState("idle");
        return;
      }

      setRoomName(tokenData.room_name);

      // Get greeting
      setState("greeting");
      const greeting = await api.livekitGreeting(tokenData.room_name);

      if (greeting.text) {
        setTranscript([{ role: "assistant", text: greeting.text }]);

        // Play greeting audio
        if (greeting.audio_b64) {
          await playAudio(greeting.audio_b64);
        }
      }

      // Start listening after greeting
      setState("listening");
      await startRecording();
    } catch (err: any) {
      setError(err.message || "Failed to start session");
      setState("idle");
    }
  }, []);

  const endSession = useCallback(async () => {
    stopRecording();
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    if (roomName) {
      try {
        await api.livekitEnd(roomName);
      } catch (err) {
        console.error("Failed to end session:", err);
      }
    }

    setState("ended");
    setRoomName("");
  }, [roomName]);

  const playAudio = useCallback((audioB64: string): Promise<void> => {
    return new Promise((resolve) => {
      const audio = new Audio(`data:audio/wav;base64,${audioB64}`);
      audioRef.current = audio;
      audio.onended = () => resolve();
      audio.onerror = () => resolve();
      audio.play().catch(() => resolve());
    });
  }, []);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
        if (audioBlob.size === 0) return;

        setState("processing");

        try {
          // STT
          const sttResult = await api.stt(audioBlob, "hi");
          const speechText = sttResult.transcript || "";

          if (!speechText.trim()) {
            setState("listening");
            await startRecording();
            return;
          }

          // Add patient speech to transcript
          setTranscript((prev) => [...prev, { role: "patient", text: speechText }]);

          // Get AI response
          const response = await api.livekitRespond(roomName, speechText);

          if (response.response_text) {
            setTranscript((prev) => [
              ...prev,
              { role: "assistant", text: response.response_text, turn: response.turn },
            ]);
          }

          if (response.risk_flag) setRiskFlag(true);

          // Play response audio
          if (response.response_audio_b64) {
            setState("speaking");
            await playAudio(response.response_audio_b64);
          }

          // Continue or end
          if (response.should_continue) {
            setState("listening");
            await startRecording();
          } else {
            await endSession();
          }
        } catch (err: any) {
          console.error("Processing failed:", err);
          setState("listening");
          await startRecording();
        }
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
    } catch (err) {
      console.error("Mic access denied:", err);
      setError("Microphone access denied");
      setState("idle");
    }
  }, [roomName, playAudio, endSession]);

  const stopRecording = useCallback(() => {
    mediaRecorderRef.current?.stop();
    mediaRecorderRef.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }, []);

  const handleStopTalking = useCallback(() => {
    // Stop recording to trigger processing
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  }, []);

  const stateLabels: Record<SessionState, string> = {
    idle: "Start Voice Chat",
    connecting: "Connecting...",
    greeting: "AI Speaking...",
    listening: "Listening...",
    processing: "Thinking...",
    speaking: "AI Speaking...",
    ended: "Session Ended",
  };

  const isActive = state !== "idle" && state !== "ended";

  return (
    <div className="bg-white dark:bg-slate-900/60 backdrop-blur border border-slate-200 dark:border-white/10 rounded-2xl overflow-hidden shadow-sm dark:shadow-none">
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-100 dark:border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center">
            <Volume2 className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">
              Live Voice Assistant
            </h3>
            <p className="text-[11px] text-slate-400">
              Real-time AI conversation
            </p>
          </div>
        </div>

        {riskFlag && (
          <span className="px-2 py-1 bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-300 text-xs font-bold rounded-full animate-pulse">
            RISK FLAGGED
          </span>
        )}
      </div>

      {/* Transcript area */}
      <div ref={scrollRef} className="h-[280px] overflow-y-auto p-4 space-y-3">
        {transcript.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <p className="text-slate-400 dark:text-slate-500 text-sm text-center">
              Start a voice session to talk with AyuNet AI
            </p>
          </div>
        ) : (
          transcript.map((t, i) => (
            <div
              key={i}
              className={`flex ${t.role === "patient" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm ${
                  t.role === "patient"
                    ? "bg-indigo-600 text-white rounded-br-md"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white rounded-bl-md"
                }`}
              >
                {t.text}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Controls */}
      <div className="px-5 py-4 border-t border-slate-100 dark:border-white/5 flex items-center gap-3">
        {!isActive ? (
          <button
            onClick={state === "ended" ? () => { setState("idle"); setTranscript([]); } : startSession}
            className="flex-1 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all"
          >
            <Phone className="w-4 h-4" />
            {state === "ended" ? "New Session" : "Start Voice Chat"}
          </button>
        ) : (
          <>
            {/* Status indicator */}
            <div className="flex-1 flex items-center gap-3">
              {state === "listening" ? (
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-sm font-medium text-slate-600 dark:text-slate-300">
                    Listening... tap when done
                  </span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  {(state === "processing" || state === "connecting") && (
                    <Loader2 className="w-4 h-4 text-indigo-500 animate-spin" />
                  )}
                  {(state === "speaking" || state === "greeting") && (
                    <Volume2 className="w-4 h-4 text-indigo-500 animate-pulse" />
                  )}
                  <span className="text-sm font-medium text-slate-500 dark:text-slate-400">
                    {stateLabels[state]}
                  </span>
                </div>
              )}
            </div>

            {state === "listening" && (
              <button
                onClick={handleStopTalking}
                className="px-4 py-2.5 bg-indigo-100 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-300 rounded-xl text-sm font-bold transition-all hover:bg-indigo-200 dark:hover:bg-indigo-500/30"
              >
                <Mic className="w-4 h-4" />
              </button>
            )}

            <button
              onClick={endSession}
              className="px-4 py-2.5 bg-red-600 hover:bg-red-500 text-white rounded-xl text-sm font-bold flex items-center gap-2 transition-all"
            >
              <PhoneOff className="w-4 h-4" />
              End
            </button>
          </>
        )}
      </div>

      {error && (
        <div className="px-5 pb-3">
          <p className="text-xs text-red-500">{error}</p>
        </div>
      )}
    </div>
  );
}
