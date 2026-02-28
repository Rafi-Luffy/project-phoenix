import { create } from 'zustand';

const BACKEND_API  = 'http://localhost:8000';
const BACKEND_WS   = 'ws://localhost:8000/ws';
const INITIAL_FEN  = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

type GameStatus = 'idle' | 'running' | 'paused' | 'error' | 'healing' | 'healed';

interface MoveRecord {
  move_number: number;
  agent: string;
  color: string;
  uci: string;
  san: string;
  from_sq: string;
  to_sq: string;
  fen: string;
  evaluation: number;
  is_capture: boolean;
  gives_check: boolean;
}

interface IncidentRecord {
  id: string;
  type: string;
  message: string;
  timestamp: string;
  status: string;
}

interface GameState {
  // Board state
  fen: string;
  moveHistory: MoveRecord[];
  moveCount: number;

  // Connection
  wsConnected: boolean;
  backendOnline: boolean;

  // Game state
  gameStatus: GameStatus;
  isPaused: boolean;
  currentTurn: 'white' | 'black';
  thinkingAgent: string | null;

  // Metrics
  integrityScore: number;
  driftIndex: number;
  aiConfidence: number;

  // Error / freeze state
  isFrozen: boolean;           // anomaly detected → freeze board overlay
  errorCode: string;           // cryptic hex code e.g. ERR::0xDEADBEEF
  errorRawType: string;        // injection_type from backend
  errorDesc: string;           // human description
  isHealing: boolean;          // Phoenix is actively correcting
  isFixed: boolean;            // correction done, show Resume
  incidents: IncidentRecord[]; // healing step trace
  correctionExplanation: string;
  correctionLatencyMs: number;
  correctionCount: number;

  // Injection input
  injectionInput: string;
  isInjecting: boolean;

  // Actions
  setInjectionInput: (v: string) => void;
  startGame: () => Promise<void>;
  stopGame: () => Promise<void>;
  togglePause: () => void;
  userResume: () => void;       // user clicks Resume after fix
  injectError: (type: string, customUci?: string) => Promise<void>;
  initWebSocket: () => () => void;
}

function generateErrorCode(): string {
  const hex = () => Math.floor(Math.random() * 0xFFFFFFFF).toString(16).toUpperCase().padStart(8, '0');
  return `ERR::0x${hex()}::0x${hex().slice(0, 4)}`;
}

export const useGameStore = create<GameState>((set, get) => ({
  fen: INITIAL_FEN,
  moveHistory: [],
  moveCount: 0,

  wsConnected: false,
  backendOnline: false,

  gameStatus: 'idle',
  isPaused: false,
  currentTurn: 'white',
  thinkingAgent: null,

  integrityScore: 100,
  driftIndex: 0,
  aiConfidence: 96,

  isFrozen: false,
  errorCode: '',
  errorRawType: '',
  errorDesc: '',
  isHealing: false,
  isFixed: false,
  incidents: [],
  correctionExplanation: '',
  correctionLatencyMs: 0,
  correctionCount: 0,

  injectionInput: '',
  isInjecting: false,

  setInjectionInput: (v) => set({ injectionInput: v }),

  startGame: async () => {
    try {
      const res = await fetch(`${BACKEND_API}/api/chess/start`, { method: 'POST' });
      const data = await res.json();
      if (data.ok) {
        set({
          gameStatus: 'running',
          isFrozen: false,
          isFixed: false,
          isHealing: false,
          incidents: [],
          errorCode: '',
          errorDesc: '',
          moveHistory: [],
          moveCount: 0,
          fen: INITIAL_FEN,
        });
      }
    } catch {
      set({ backendOnline: false });
    }
  },

  stopGame: async () => {
    try {
      await fetch(`${BACKEND_API}/api/chess/reset`, { method: 'POST' });
      set({
        gameStatus: 'idle',
        isFrozen: false,
        isFixed: false,
        isHealing: false,
        incidents: [],
        errorCode: '',
        errorDesc: '',
        fen: INITIAL_FEN,
        moveHistory: [],
        moveCount: 0,
        thinkingAgent: null,
      });
    } catch {
      set({ backendOnline: false });
    }
  },

  togglePause: () => {
    const { isPaused, gameStatus } = get();
    if (gameStatus !== 'running' && gameStatus !== 'paused') return;
    set({ isPaused: !isPaused, gameStatus: isPaused ? 'running' : 'paused' });
  },

  userResume: () => {
    // User acknowledges the fix — clear the frozen overlay
    set({
      isFrozen: false,
      isFixed: false,
      isHealing: false,
      errorCode: '',
      errorDesc: '',
      incidents: [],
      correctionExplanation: '',
    });
  },

  injectError: async (type: string, customUci?: string) => {
    set({ isInjecting: true });
    try {
      let url = `${BACKEND_API}/api/chess/inject`;
      let body: Record<string, string> = { type };
      if (type === 'custom' && customUci) {
        url = `${BACKEND_API}/api/chess/inject-custom`;
        body = { move_uci: customUci };
      }
      await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
    } catch {
      set({ backendOnline: false });
    } finally {
      set({ isInjecting: false });
    }
  },

  initWebSocket: () => {
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let destroyed = false;

    const connect = () => {
      if (destroyed) return;
      ws = new WebSocket(BACKEND_WS);

      ws.onopen = () => {
        set({ wsConnected: true, backendOnline: true });
      };

      ws.onclose = () => {
        set({ wsConnected: false });
        if (!destroyed) {
          reconnectTimer = setTimeout(connect, 4000);
        }
      };

      ws.onerror = () => {
        set({ backendOnline: false });
        ws?.close();
      };

      ws.onmessage = (e) => {
        let data: Record<string, unknown>;
        try { data = JSON.parse(e.data); } catch { return; }

        const type = (data.type as string) ?? '';
        const { isPaused } = get();

        switch (type) {
          case 'move':
            if (!isPaused) {
              set((s) => ({
                fen: (data.fen as string) ?? s.fen,
                moveCount: (data.move_number as number) ?? s.moveCount,
                currentTurn: (data.color as string) === 'white' ? 'black' : 'white',
                moveHistory: [data as unknown as MoveRecord, ...s.moveHistory].slice(0, 80),
                thinkingAgent: null,
              }));
            }
            break;

          case 'thinking':
            set({ thinkingAgent: data.agent as string });
            break;

          case 'metrics':
            set({
              integrityScore: (data.integrity_score as number) ?? 100,
              driftIndex: (data.drift_index as number) ?? 0,
              aiConfidence: (data.ai_confidence as number) ?? 96,
            });
            break;

          case 'game_started':
            set({ gameStatus: 'running', isFrozen: false, isFixed: false });
            break;

          case 'game_over':
            set({ gameStatus: 'idle', thinkingAgent: null });
            break;

          case 'reset':
            set({
              gameStatus: 'idle',
              fen: INITIAL_FEN,
              moveHistory: [],
              moveCount: 0,
              isFrozen: false,
              isFixed: false,
              isHealing: false,
              incidents: [],
              errorCode: '',
            });
            break;

          case 'anomaly_detected':
          case 'injection_confirmed':
            set({
              isFrozen: true,
              isFixed: false,
              isHealing: false,
              errorCode: generateErrorCode(),
              errorRawType: (data.injection_type as string) ?? 'UNKNOWN_FAULT',
              errorDesc: (data.description as string) ?? (data.message as string) ?? '',
              gameStatus: 'error',
              incidents: [],
            });
            break;

          case 'incident':
            set((s) => ({
              isHealing: true,
              incidents: [...s.incidents, data as unknown as IncidentRecord].slice(0, 20),
            }));
            break;

          case 'correction':
            set({
              correctionExplanation: (data.explanation as string) ?? '',
              correctionLatencyMs: (data.correction_latency_ms as number) ?? 0,
              correctionCount: ((get().correctionCount) + 1),
              gameStatus: 'healed',
            });
            break;

          case 'healed':
            set((s) => ({
              isHealing: false,
              isFixed: true,        // now show Resume button
              gameStatus: 'healed',
              correctionCount: (data.correction_count as number) ?? s.correctionCount,
              integrityScore: (data.integrity_score as number) ?? s.integrityScore,
              aiConfidence: (data.ai_confidence as number) ?? s.aiConfidence,
              driftIndex: 0,
            }));
            break;

          default:
            break;
        }
      };
    };

    connect();

    return () => {
      destroyed = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
    };
  },
}));
