import { useEffect, useRef, useState, useCallback } from "react";

const WS_BASE = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export interface Alert {
  type: string;
  patient_id?: string;
  patient_name?: string;
  pain_score?: number;
  new_symptoms?: string[];
  risk_flag?: boolean;
  risk_score?: number;
  source?: string;
  call_sid?: string;
  turn?: number;
  patient_speech?: string;
  extracted?: any;
  timestamp?: string;
}

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [connected, setConnected] = useState(false);
  const [latestAlert, setLatestAlert] = useState<Alert | null>(null);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    const socket = new WebSocket(`${WS_BASE}/ws/alerts`);

    socket.onopen = () => {
      setConnected(true);
      console.log("[WS] Connected");
    };

    socket.onmessage = (event) => {
      const data: Alert = JSON.parse(event.data);
      setAlerts((prev) => [data, ...prev]);
      setLatestAlert(data);
    };

    socket.onclose = () => {
      setConnected(false);
      console.log("[WS] Disconnected, retrying in 3s...");
      setTimeout(connect, 3000);
    };

    socket.onerror = () => socket.close();

    ws.current = socket;
  }, []);

  useEffect(() => {
    connect();
    return () => ws.current?.close();
  }, [connect]);

  const clearLatest = () => setLatestAlert(null);

  return { alerts, latestAlert, connected, clearLatest };
}
