/**
 * Project Phoenix — API Client
 * Typed REST + WebSocket client for the chess demo backend
 */

// In dev: VITE_BACKEND_URL is empty → Vite proxy forwards /api/* → localhost:8000
// In prod: set VITE_BACKEND_URL=https://your-app.onrender.com
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "";

// In dev: Vite proxy forwards /ws → ws://localhost:8000/ws
// In prod: set VITE_WS_URL=wss://your-app.onrender.com/ws
const WS_URL: string = import.meta.env.VITE_WS_URL
  ?? `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws`;

// ─────────────────────────────────────────────
//  Types
// ─────────────────────────────────────────────
export type InjectionType =
  | "illegal_move"
  | "remove_piece"
  | "duplicate_piece"
  | "pawn_backrank"
  | "wrong_turn"
  | "board_mutation"
  | "delay_anomaly"
  | "corrupt_evaluation";

export interface PhoenixMetrics {
  active_agents: number;
  incidents_today: number;
  success_rate: number;
  integrity_score: number;
  drift_index: number;
  ai_confidence: number;
  correction_count: number;
}

export interface CorrectionEvent {
  id: string;
  injection_type: InjectionType;
  label: string;
  explanation: string;
  confidence: number;
  correction_latency_ms: number;
  anomalies_resolved: number;
  timestamp: string;
}

export interface Anomaly {
  type: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
}

export interface ChessStatus {
  game_id: string;
  status: "idle" | "running" | "error" | "healing" | "healed";
  mode: string;
  move_count: number;
  fen: string;
  active_agents: number;
  incidents_today: number;
  success_rate: number;
  recovery_time_ms: number | null;
  integrity_score: number;
  drift_index: number;
  ai_confidence: number;
  correction_count: number;
  move_history: ChessMove[];
  incidents: Incident[];
  correction_events: CorrectionEvent[];
  white_thinking: boolean;
  black_thinking: boolean;
}

export interface ChessMove {
  move_number: number;
  agent: string;
  color: "white" | "black";
  uci: string;
  san: string;
  from_sq: string;
  to_sq: string;
  fen: string;
  is_capture: boolean;
  gives_check: boolean;
  timestamp: string;
}

export interface Incident {
  id: string;
  type: string;
  message: string;
  timestamp: string;
  status: "open" | "investigating" | "resolved";
}

export type WsEventType =
  | "connected"
  | "game_started"
  | "thinking"
  | "move"
  | "injection_confirmed"
  | "anomaly_detected"
  | "incident"
  | "correction"
  | "healed"
  | "game_over"
  | "reset"
  | "metrics"
  | "pong";

export interface WsEvent {
  type: WsEventType;
  timestamp: string;
  [key: string]: unknown;
}

// ─────────────────────────────────────────────
//  REST helpers
// ─────────────────────────────────────────────
async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BACKEND_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

// ─────────────────────────────────────────────
//  Chess API
// ─────────────────────────────────────────────
export const chessApi = {
  health: () => apiFetch<{ status: string }>("/api/health"),
  status: () => apiFetch<ChessStatus>("/api/chess/status"),
  start: () =>
    apiFetch<{ ok: boolean; game_id: string; message: string }>("/api/chess/start", {
      method: "POST",
    }),
  inject: (type: InjectionType) =>
    apiFetch<{ ok: boolean; injection_type: string; description: string; message?: string }>(
      "/api/chess/inject",
      { method: "POST", body: JSON.stringify({ type }) }
    ),
  injectCustomMove: (move_uci: string, piece?: string) =>
    apiFetch<{ ok: boolean; description: string }>("/api/chess/inject-custom", {
      method: "POST",
      body: JSON.stringify({ move_uci, piece }),
    }),
  /** Legacy single-button wrapper — maps to illegal_move */
  injectError: () => chessApi.inject("illegal_move"),
  corrections: () => apiFetch<{ corrections: CorrectionEvent[]; total: number }>("/api/chess/corrections"),
  reset: () =>
    apiFetch<{ ok: boolean }>("/api/chess/reset", { method: "POST" }),
};

// ─────────────────────────────────────────────
//  WebSocket manager (singleton)
// ─────────────────────────────────────────────
type Handler = (event: WsEvent) => void;

class PhoenixSocket {
  private ws: WebSocket | null = null;
  private handlers = new Set<Handler>();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private url: string;
  public connected = false;

  constructor(url: string) {
    this.url = url;
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      this.connected = true;
      this.dispatch({ type: "connected" as WsEventType, timestamp: new Date().toISOString() });
      // Keep-alive ping every 20s
      setInterval(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({ type: "ping" }));
        }
      }, 20_000);
    };

    this.ws.onmessage = (e) => {
      try {
        const evt = JSON.parse(e.data) as WsEvent;
        this.dispatch(evt);
      } catch { /* ignore */ }
    };

    this.ws.onerror = () => { this.connected = false; };

    this.ws.onclose = () => {
      this.connected = false;
      // Auto-reconnect after 3 seconds
      this.reconnectTimer = setTimeout(() => this.connect(), 3000);
    };
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
    this.connected = false;
  }

  private dispatch(evt: WsEvent) {
    this.handlers.forEach((h) => {
      try { h(evt); } catch { /* ignore */ }
    });
  }

  on(handler: Handler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }
}

export const phoenixSocket = new PhoenixSocket(WS_URL);
