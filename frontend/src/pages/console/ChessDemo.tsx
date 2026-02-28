import { useEffect, useRef, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play, Zap, RotateCcw, Activity, Clock, Shield, CheckCircle2,
  AlertTriangle, Bot, Cpu, ChevronRight, Circle, FlaskConical,
  Brain, TrendingDown, BarChart2, ListChecks, Swords
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import {
  phoenixSocket, chessApi, WsEvent, ChessMove, Incident,
  CorrectionEvent, InjectionType
} from "@/lib/api";
import { toast } from "sonner";

// ─────────────────────────────────────────────
//  Chess piece rendering from FEN
// ─────────────────────────────────────────────
const PIECES: Record<string, string> = {
  K: "♔", Q: "♕", R: "♖", B: "♗", N: "♘", P: "♙",
  k: "♚", q: "♛", r: "♜", b: "♝", n: "♞", p: "♟",
};

function parseFen(fen: string): (string | null)[][] {
  const rows = fen.split(" ")[0].split("/");
  return rows.map((row) => {
    const cells: (string | null)[] = [];
    for (const ch of row) {
      if (/\d/.test(ch)) for (let i = 0; i < parseInt(ch); i++) cells.push(null);
      else cells.push(ch);
    }
    return cells;
  });
}

function squareName(row: number, col: number): string {
  return String.fromCharCode(97 + col) + String(8 - row);
}

// ─────────────────────────────────────────────
//  Chess Board Component
// ─────────────────────────────────────────────
function ChessBoard({
  fen,
  lastMove,
  status,
}: {
  fen: string;
  lastMove: ChessMove | null;
  status: string;
}) {
  const board = parseFen(fen);

  return (
    <div className="relative select-none">
      {/* Status overlay on error */}
      <AnimatePresence>
        {status === "error" && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-20 flex items-center justify-center rounded-lg bg-red-500/20 backdrop-blur-sm border-2 border-red-500"
          >
            <div className="text-center">
              <AlertTriangle className="h-12 w-12 text-red-500 mx-auto animate-pulse" />
              <p className="text-red-400 font-bold text-lg mt-2">SYSTEM ERROR</p>
              <p className="text-red-300 text-sm">Phoenix Healer Activated</p>
            </div>
          </motion.div>
        )}
        {status === "healing" && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-20 flex items-center justify-center rounded-lg bg-amber-500/10 backdrop-blur-sm border-2 border-amber-500 animate-pulse"
          >
            <div className="text-center">
              <Shield className="h-12 w-12 text-amber-500 mx-auto animate-spin" />
              <p className="text-amber-400 font-bold text-lg mt-2">SELF-HEALING</p>
              <p className="text-amber-300 text-sm">Patching systems...</p>
            </div>
          </motion.div>
        )}
        {status === "healed" && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="absolute inset-0 z-20 flex items-center justify-center rounded-lg bg-green-500/10 backdrop-blur-sm border-2 border-green-500"
          >
            <div className="text-center">
              <CheckCircle2 className="h-14 w-14 text-green-500 mx-auto" />
              <p className="text-green-400 font-bold text-lg mt-2">SELF-HEALED ✓</p>
              <p className="text-green-300 text-sm">Resuming game...</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Board */}
      <div className="grid grid-cols-8 rounded-lg overflow-hidden border-2 border-border shadow-2xl"
           style={{ aspectRatio: "1/1", width: "100%" }}>
        {board.map((row, ri) =>
          row.map((piece, ci) => {
            const sq = squareName(ri, ci);
            const isLight = (ri + ci) % 2 === 0;
            const isFrom = lastMove?.from_sq === sq;
            const isTo = lastMove?.to_sq === sq;
            const isHighlighted = isFrom || isTo;
            const isWhitePiece = piece !== null && piece === piece.toUpperCase();

            return (
              <motion.div
                key={`${ri}-${ci}`}
                className={cn(
                  "relative flex items-center justify-center",
                  isLight ? "bg-[#f0d9b5]" : "bg-[#b58863]",
                  isHighlighted && "ring-2 ring-inset ring-yellow-400"
                )}
                style={{ aspectRatio: "1/1" }}
              >
                {isHighlighted && (
                  <div className={cn(
                    "absolute inset-0 opacity-40",
                    isTo ? "bg-yellow-400" : "bg-yellow-300"
                  )} />
                )}
                {piece && (
                  <motion.span
                    key={`${piece}-${ri}-${ci}`}
                    initial={{ scale: 0.6, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className={cn(
                      "relative z-10 leading-none select-none",
                      "text-[min(4.5vw,3rem)]",
                      isWhitePiece ? "drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]" : "drop-shadow-[0_1px_1px_rgba(255,255,255,0.3)]"
                    )}
                  >
                    {PIECES[piece] ?? piece}
                  </motion.span>
                )}
                {/* Rank/file labels */}
                {ci === 0 && (
                  <span className="absolute top-0.5 left-0.5 text-[0.5rem] font-bold opacity-60 leading-none z-10"
                        style={{ color: isLight ? "#b58863" : "#f0d9b5" }}>
                    {8 - ri}
                  </span>
                )}
                {ri === 7 && (
                  <span className="absolute bottom-0.5 right-0.5 text-[0.5rem] font-bold opacity-60 leading-none z-10"
                        style={{ color: isLight ? "#b58863" : "#f0d9b5" }}>
                    {String.fromCharCode(97 + ci)}
                  </span>
                )}
              </motion.div>
            );
          })
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
//  Agent Card
// ─────────────────────────────────────────────
function AgentCard({
  name, color, thinking, status, lastMove
}: {
  name: string; color: "white" | "black";
  thinking: boolean; status: string; lastMove: ChessMove | null;
}) {
  const isActive = thinking;
  const isWhite = color === "white";

  return (
    <motion.div
      animate={{ scale: isActive ? 1.02 : 1 }}
      transition={{ duration: 0.2 }}
    >
      <Card className={cn(
        "border transition-all duration-300",
        isActive && "border-primary shadow-lg shadow-primary/20",
        status === "error" && "border-red-500",
        status === "healed" && "border-green-500",
      )}>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className={cn(
              "h-10 w-10 rounded-full flex items-center justify-center text-lg border-2",
              isWhite
                ? "bg-white border-zinc-300 text-zinc-800"
                : "bg-zinc-900 border-zinc-600 text-white"
            )}>
              {isWhite ? "♔" : "♚"}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <p className="font-semibold text-sm text-foreground truncate">{name}</p>
                {isActive && (
                  <motion.span
                    animate={{ opacity: [1, 0.3, 1] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                    className="text-[10px] text-primary font-medium"
                  >
                    THINKING...
                  </motion.span>
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                {lastMove && lastMove.color === color
                  ? `Last: ${lastMove.san} (move ${lastMove.move_number})`
                  : "Waiting for turn"}
              </p>
            </div>
            <div className={cn(
              "h-2.5 w-2.5 rounded-full flex-shrink-0",
              isActive ? "bg-green-500 animate-pulse" : "bg-muted-foreground/30"
            )} />
          </div>
          {isActive && (
            <motion.div
              initial={{ width: "0%" }}
              animate={{ width: "100%" }}
              transition={{ duration: AGENT_THINK_SECS, ease: "linear" }}
              className="mt-2 h-0.5 bg-primary rounded-full"
            />
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}

const AGENT_THINK_SECS = 1.4;

// ─────────────────────────────────────────────
//  Incident Stream
// ─────────────────────────────────────────────
const INCIDENT_ICONS: Record<string, { icon: React.ElementType; color: string }> = {
  detection:   { icon: AlertTriangle, color: "text-red-400" },
  analysis:    { icon: Cpu, color: "text-amber-400" },
  isolation:   { icon: Shield, color: "text-orange-400" },
  patch:       { icon: Zap, color: "text-blue-400" },
  verify:      { icon: Activity, color: "text-purple-400" },
  resume:      { icon: Play, color: "text-cyan-400" },
  healed:      { icon: CheckCircle2, color: "text-green-400" },
  error_detected: { icon: AlertTriangle, color: "text-red-500" },
};

function IncidentRow({ incident, index }: { incident: Incident; index: number }) {
  const meta = INCIDENT_ICONS[incident.type] ?? { icon: Circle, color: "text-muted-foreground" };
  const Icon = meta.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className={cn(
        "flex items-start gap-3 p-3 rounded-lg border text-sm",
        incident.type === "healed"
          ? "bg-green-500/10 border-green-500/30"
          : incident.type === "detection" || incident.type === "error_detected"
          ? "bg-red-500/10 border-red-500/30"
          : "bg-muted/40 border-border"
      )}
    >
      <Icon className={cn("h-4 w-4 mt-0.5 flex-shrink-0", meta.color)} />
      <div className="flex-1 min-w-0">
        <p className="text-foreground/90 leading-snug">{incident.message}</p>
        <p className="text-xs text-muted-foreground mt-0.5">
          {new Date(incident.timestamp).toLocaleTimeString()}
        </p>
      </div>
      <Badge
        variant="outline"
        className={cn(
          "text-[10px] flex-shrink-0",
          incident.status === "resolved" ? "border-green-500 text-green-500"
            : "border-amber-500 text-amber-500"
        )}
      >
        {incident.status}
      </Badge>
    </motion.div>
  );
}

// ─────────────────────────────────────────────
//  Move Log
// ─────────────────────────────────────────────
function MoveLog({ moves }: { moves: ChessMove[] }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [moves]);

  const pairs: [ChessMove, ChessMove | null][] = [];
  for (let i = 0; i < moves.length; i += 2) {
    pairs.push([moves[i], moves[i + 1] ?? null]);
  }

  return (
    <div ref={ref} className="overflow-y-auto max-h-48 space-y-0.5 pr-1 scrollbar-thin">
      {pairs.map(([white, black], i) => (
        <div key={i} className="flex items-center gap-2 text-xs">
          <span className="text-muted-foreground w-6 text-right flex-shrink-0">{i + 1}.</span>
          <span className={cn(
            "px-2 py-0.5 rounded font-mono flex-1",
            "bg-muted/50 text-foreground"
          )}>{white.san}</span>
          {black && (
            <span className={cn(
              "px-2 py-0.5 rounded font-mono flex-1",
              "bg-muted/50 text-foreground"
            )}>{black.san}</span>
          )}
          {!black && <span className="flex-1" />}
        </div>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────
//  Injection Lab config
// ─────────────────────────────────────────────
const INJECTIONS: { type: InjectionType; label: string; desc: string; color: string }[] = [
  { type: "illegal_move",       label: "Duplicate King",     desc: "Places a second king on the board — triggers STATUS_TOO_MANY_KINGS",        color: "border-red-500/50 hover:border-red-500" },
  { type: "remove_piece",       label: "Remove Piece",       desc: "Removes a non-king piece + plants illegal back-rank pawn",                   color: "border-orange-500/50 hover:border-orange-500" },
  { type: "duplicate_piece",    label: "Duplicate Piece",    desc: "Spawns extra queen — material count audit detects excess",                   color: "border-yellow-500/50 hover:border-yellow-500" },
  { type: "pawn_backrank",      label: "Corrupt FEN",        desc: "Places pawn on back rank — triggers STATUS_PAWNS_ON_BACKRANK",               color: "border-amber-500/50 hover:border-amber-500" },
  { type: "wrong_turn",         label: "Wrong Turn",         desc: "Flips board.turn — Phoenix detects via expected_turn audit",                 color: "border-purple-500/50 hover:border-purple-500" },
  { type: "board_mutation",     label: "Board Mutation",     desc: "Randomly transposes pieces + illegal pawn — multi-anomaly injection",       color: "border-pink-500/50 hover:border-pink-500" },
  { type: "delay_anomaly",      label: "Delay Anomaly",      desc: "Injects 6−11s latency — triggers SLA breach detection",                     color: "border-cyan-500/50 hover:border-cyan-500" },
  { type: "corrupt_evaluation", label: "Corrupt Evaluation", desc: "Pushes eval beyond ±500 cp bound — scoring pipeline alert triggers",        color: "border-blue-500/50 hover:border-blue-500" },
];

// ─────────────────────────────────────────────
//  Phoenix Metric Gauge
// ─────────────────────────────────────────────
function MetricBar({ label, value, max = 100, good = "high", icon: Icon }: {
  label: string; value: number; max?: number; good?: "high" | "low"; icon: React.ElementType;
}) {
  const pct     = Math.min(100, (value / max) * 100);
  const isGood  = good === "high" ? pct >= 70 : pct <= 30;
  const color   = isGood ? "bg-green-500" : pct > 40 ? "bg-amber-500" : "bg-red-500";
  const textCol = isGood ? "text-green-400" : pct > 40 ? "text-amber-400" : "text-red-400";

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="flex items-center gap-1 text-muted-foreground">
          <Icon className="h-3 w-3" />{label}
        </span>
        <motion.span
          key={value}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn("font-mono font-bold", textCol)}
        >
          {max === 1 ? value.toFixed(3) : `${value.toFixed(1)}${max === 100 ? "%" : ""}`}
        </motion.span>
      </div>
      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
        <motion.div
          className={cn("h-full rounded-full", color)}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
//  Correction Event Card
// ─────────────────────────────────────────────
function CorrectionCard({ evt, index }: { evt: CorrectionEvent; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.06 }}
      className="p-4 rounded-xl border border-green-500/30 bg-green-500/5 space-y-2"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-4 w-4 text-green-400 flex-shrink-0" />
          <span className="text-sm font-semibold text-foreground">{evt.label}</span>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <Badge variant="outline" className="text-[10px] border-green-500/40 text-green-400">
            {evt.confidence.toFixed(1)}% conf
          </Badge>
          <Badge variant="outline" className="text-[10px] border-cyan-500/40 text-cyan-400">
            {evt.correction_latency_ms}ms
          </Badge>
        </div>
      </div>
      <p className="text-xs text-muted-foreground leading-relaxed">{evt.explanation}</p>
      <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
        <span>{evt.anomalies_resolved} anomal{evt.anomalies_resolved === 1 ? "y" : "ies"} resolved</span>
        <span>·</span>
        <span>{new Date(evt.timestamp).toLocaleTimeString()}</span>
      </div>
    </motion.div>
  );
}

// ─────────────────────────────────────────────
//  Main Chess Demo Page
// ─────────────────────────────────────────────
export default function ChessDemo() {
  const [fen, setFen]               = useState("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
  const [status, setStatus]         = useState<string>("idle");
  const [moves, setMoves]           = useState<ChessMove[]>([]);
  const [incidents, setIncidents]   = useState<Incident[]>([]);
  const [corrections, setCorrections] = useState<CorrectionEvent[]>([]);
  const [whiteTh, setWhiteTh]       = useState(false);
  const [blackTh, setBlackTh]       = useState(false);
  const [moveCount, setMoveCount]   = useState(0);
  const [recoveryMs, setRecoveryMs] = useState<number | null>(null);
  const [incidentsToday, setIncidentsToday] = useState(0);
  const [correctionCount, setCorrectionCount] = useState(0);
  const [wsConnected, setWsConnected] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [isInjecting, setIsInjecting] = useState(false);
  const [selectedInj, setSelectedInj] = useState<InjectionType>("illegal_move");
  const [customUci, setCustomUci]     = useState("");
  const [isInjectingCustom, setIsInjectingCustom] = useState(false);

  // Phoenix live metrics
  const [integrity, setIntegrity]   = useState(100);
  const [drift, setDrift]           = useState(0);
  const [confidence, setConfidence] = useState(96);

  // Last anomaly snapshot for display
  const [lastAnomaly, setLastAnomaly] = useState<{
    description: string; board_status_hex: string; anomalies: any[];
  } | null>(null);

  const lastMove = moves.length > 0 ? moves[moves.length - 1] : null;

  // ── Connect WebSocket ──
  useEffect(() => {
    phoenixSocket.connect();

    const unsub = phoenixSocket.on((evt: WsEvent) => {
      switch (evt.type) {
        case "connected":
          setWsConnected(true);
          if ((evt as any).fen)          setFen((evt as any).fen);
          if ((evt as any).status)       setStatus((evt as any).status);
          if ((evt as any).move_history) setMoves((evt as any).move_history);
          if ((evt as any).incidents)    setIncidents((evt as any).incidents);
          if ((evt as any).correction_events) setCorrections((evt as any).correction_events);
          if ((evt as any).metrics) {
            const m = (evt as any).metrics;
            if (m.integrity_score  != null) setIntegrity(m.integrity_score);
            if (m.drift_index      != null) setDrift(m.drift_index);
            if (m.ai_confidence    != null) setConfidence(m.ai_confidence);
            if (m.correction_count != null) setCorrectionCount(m.correction_count);
          }
          break;

        case "game_started":
          setStatus("running"); setIncidents([]); setMoves([]);
          setMoveCount(0); setRecoveryMs(null); setLastAnomaly(null);
          break;

        case "thinking":
          if ((evt as any).color === "white") { setWhiteTh(true); setBlackTh(false); }
          else { setBlackTh(true); setWhiteTh(false); }
          break;

        case "move": {
          const m = evt as unknown as ChessMove;
          setFen(m.fen); setMoveCount(m.move_number);
          setWhiteTh(false); setBlackTh(false);
          setMoves(prev => [...prev, m]);
          break;
        }

        case "injection_confirmed":
          setStatus("error"); setWhiteTh(false); setBlackTh(false);
          toast.error(`⚡ Fault Injected: ${(evt as any).label}`, {
            description: (evt as any).description as string,
            duration: 5000,
          });
          break;

        case "anomaly_detected":
          setIntegrity((evt as any).integrity_score ?? 100);
          setDrift((evt as any).drift_index ?? 0);
          setConfidence((evt as any).ai_confidence ?? 96);
          setLastAnomaly({
            description:      (evt as any).message as string,
            board_status_hex: (evt as any).board_status_hex as string,
            anomalies:        (evt as any).anomalies ?? [],
          });
          break;

        case "incident":
          setIncidents(prev => [evt as unknown as Incident, ...prev].slice(0, 30));
          break;

        case "correction": {
          const c = evt as unknown as CorrectionEvent;
          setCorrections(prev => [c, ...prev].slice(0, 20));
          setIntegrity((evt as any).integrity_score ?? 100);
          setDrift((evt as any).drift_index ?? 0);
          setConfidence((evt as any).ai_confidence ?? 96);
          break;
        }

        case "healed":
          setStatus("healed");
          setRecoveryMs((evt as any).recovery_time_ms as number);
          setIncidentsToday((evt as any).incidents_today ?? 1);
          setCorrectionCount((evt as any).correction_count ?? 0);
          setIntegrity((evt as any).integrity_score ?? 100);
          setConfidence((evt as any).ai_confidence ?? 96);
          setDrift(0);
          toast.success("✅ Phoenix Self-Healing Complete!", {
            description: `Recovered in ${(evt as any).recovery_time_ms}ms`,
            duration: 5000,
          });
          setTimeout(() => setStatus("running"), 2000);
          break;

        case "metrics":
          if ((evt as any).move_count      != null) setMoveCount((evt as any).move_count);
          if ((evt as any).incidents_today != null) setIncidentsToday((evt as any).incidents_today);
          if ((evt as any).integrity_score != null) setIntegrity((evt as any).integrity_score);
          if ((evt as any).drift_index     != null) setDrift((evt as any).drift_index);
          if ((evt as any).ai_confidence   != null) setConfidence((evt as any).ai_confidence);
          if ((evt as any).status)                  setStatus((evt as any).status);
          break;

        case "game_over":
          setStatus("idle"); setWhiteTh(false); setBlackTh(false);
          toast.info(`Game over — ${(evt as any).result}`);
          break;

        case "reset":
          setStatus("idle"); setMoves([]); setIncidents([]); setCorrections([]);
          setMoveCount(0); setRecoveryMs(null); setLastAnomaly(null);
          setIntegrity(100); setDrift(0); setConfidence(96); setCorrectionCount(0);
          setFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
          break;
      }
    });

    return () => { unsub(); phoenixSocket.disconnect(); };
  }, []);

  const handleStart = useCallback(async () => {
    setIsStarting(true);
    try {
      const res = await chessApi.start();
      if (!res.ok) toast.error(res.message);
    } catch { toast.error("Could not connect to backend — is it running?"); }
    finally { setIsStarting(false); }
  }, []);

  const handleInject = useCallback(async () => {
    setIsInjecting(true);
    try {
      const res = await chessApi.inject(selectedInj);
      if (!res.ok) toast.error(res.message ?? "Injection failed");
    } catch { toast.error("Injection failed — backend unreachable"); }
    finally { setIsInjecting(false); }
  }, [selectedInj]);

  const handleReset = useCallback(async () => { await chessApi.reset(); }, []);

  const handleInjectCustom = useCallback(async () => {
    const uci = customUci.trim();
    if (!uci) return;
    setIsInjectingCustom(true);
    try {
      const res = await chessApi.injectCustomMove(uci);
      if (!res.ok) toast.error(`Custom injection failed: ${res.description}`);
      else {
        toast.success(`Custom move injected: ${uci}`);
        setCustomUci("");
      }
    } catch { toast.error("Custom injection failed — backend unreachable"); }
    finally { setIsInjectingCustom(false); }
  }, [customUci]);

  const statusColor = ({
    idle:    "bg-muted text-muted-foreground",
    running: "bg-green-500/20 text-green-400 border border-green-500/40",
    error:   "bg-red-500/20 text-red-400 border border-red-500/40",
    healing: "bg-amber-500/20 text-amber-400 border border-amber-500/40",
    healed:  "bg-green-500/20 text-green-400 border border-green-500/40",
  } as Record<string, string>)[status] ?? "bg-muted text-muted-foreground";

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Bot className="h-6 w-6 text-primary" />
            Chess Agent Live System
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            Two Phoenix agents play autonomously. Inject real faults — watch Phoenix detect and self-heal.
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <div className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium",
            wsConnected ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"
          )}>
            <span className={cn("h-1.5 w-1.5 rounded-full",
              wsConnected ? "bg-green-500 animate-pulse" : "bg-red-500")} />
            {wsConnected ? "Live" : "Disconnected"}
          </div>
          <Badge variant="outline" className={cn("px-3 py-1", statusColor)}>
            {status.toUpperCase()}
          </Badge>
        </div>
      </div>

      {/* ── Phoenix Metrics Bar ── */}
      <Card className="border-border">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricBar label="Integrity Score" value={integrity}   max={100} good="high"  icon={Shield} />
            <MetricBar label="Drift Index"     value={drift}       max={1}   good="low"   icon={TrendingDown} />
            <MetricBar label="AI Confidence"   value={confidence}  max={100} good="high"  icon={Brain} />
          </div>
        </CardContent>
      </Card>

      {/* ── Mini Metrics Row ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: "Moves Played",    value: moveCount,                          icon: ChevronRight, color: "text-primary" },
          { label: "Active Agents",   value: status === "running" ? 2 : 0,        icon: Bot, color: "text-green-400" },
          { label: "Corrections",     value: correctionCount,                     icon: Swords, color: "text-amber-400" },
          { label: "Recovery",        value: recoveryMs ? `${recoveryMs}ms` : "—", icon: Clock, color: "text-cyan-400" },
        ].map((m) => (
          <Card key={m.label} className="border-border">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-1">
                <m.icon className={cn("h-4 w-4", m.color)} />
                <p className="text-xs text-muted-foreground">{m.label}</p>
              </div>
              <motion.p
                key={String(m.value)}
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-2xl font-bold text-foreground"
              >{m.value}</motion.p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* ── Controls ── */}
      <div className="flex gap-2 flex-wrap">
        <Button
          onClick={handleStart}
          disabled={isStarting || status === "running" || status === "healing"}
          className="gap-2 bg-primary hover:bg-primary/90"
        >
          <Play className="h-4 w-4" />
          {isStarting ? "Starting…" : "Start Game"}
        </Button>
        <Button
          onClick={handleReset}
          variant="outline"
          className="gap-2"
        >
          <RotateCcw className="h-4 w-4" />
          Reset
        </Button>
      </div>

      {/* ── Main Tabs ── */}
      <Tabs defaultValue="board">
        <TabsList className="mb-4">
          <TabsTrigger value="board" className="gap-1.5">
            <Activity className="h-3.5 w-3.5" />Game Board
          </TabsTrigger>
          <TabsTrigger value="injections" className="gap-1.5">
            <FlaskConical className="h-3.5 w-3.5" />Injection Lab
          </TabsTrigger>
          <TabsTrigger value="corrections" className="gap-1.5">
            <ListChecks className="h-3.5 w-3.5" />Correction Log
            {corrections.length > 0 && (
              <Badge className="ml-1 h-4 min-w-4 rounded-full bg-green-500 px-1 text-[10px]">{corrections.length}</Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* ── BOARD TAB ── */}
        <TabsContent value="board">
          <div className="grid grid-cols-1 xl:grid-cols-[1fr_380px] gap-6">
            {/* LEFT */}
            <div className="space-y-4">
              <div className="max-w-[520px]">
                <ChessBoard fen={fen} lastMove={lastMove} status={status} />
              </div>
              {moves.length > 0 && (
                <Card className="border-border">
                  <CardHeader className="pb-2 pt-4 px-4">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Move History</CardTitle>
                  </CardHeader>
                  <CardContent className="px-4 pb-4">
                    <MoveLog moves={moves} />
                  </CardContent>
                </Card>
              )}
            </div>
            {/* RIGHT */}
            <div className="space-y-4">
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Agents</h3>
                <AgentCard name="Phoenix-White" color="white" thinking={whiteTh} status={status} lastMove={lastMove} />
                <AgentCard name="Phoenix-Black" color="black" thinking={blackTh} status={status} lastMove={lastMove} />
              </div>

              {/* Anomaly snapshot */}
              <AnimatePresence>
                {lastAnomaly && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 space-y-1.5"
                  >
                    <p className="text-xs font-semibold text-red-400 flex items-center gap-1.5">
                      <AlertTriangle className="h-3.5 w-3.5" />Phoenix Anomaly Detected
                    </p>
                    {lastAnomaly.anomalies.map((a: any, i: number) => (
                      <p key={i} className="text-xs text-muted-foreground leading-snug">• {a.description}</p>
                    ))}
                    <p className="text-[10px] text-muted-foreground font-mono">board.status()={lastAnomaly.board_status_hex}</p>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">Incident Stream</h3>
                  {incidents.length > 0 && (
                    <Badge variant="outline" className="text-xs border-amber-500/40 text-amber-400">
                      {incidents.length} events
                    </Badge>
                  )}
                </div>
                {incidents.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 text-muted-foreground text-sm border border-dashed border-border rounded-lg">
                    <Activity className="h-8 w-8 mb-2 opacity-30" />
                    <p>No incidents — system healthy</p>
                    <p className="text-xs mt-1 opacity-60">Use Injection Lab to trigger self-healing</p>
                  </div>
                ) : (
                  <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
                    <AnimatePresence mode="popLayout">
                      {incidents.map((inc, i) => <IncidentRow key={inc.id} incident={inc} index={i} />)}
                    </AnimatePresence>
                  </div>
                )}
              </div>

              <AnimatePresence>
                {recoveryMs && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="p-4 rounded-xl bg-green-500/10 border border-green-500/40 text-center"
                  >
                    <CheckCircle2 className="h-8 w-8 text-green-500 mx-auto mb-1" />
                    <p className="text-green-400 font-bold text-lg">{recoveryMs}ms</p>
                    <p className="text-green-300 text-xs">Self-healing recovery time</p>
                    <p className="text-muted-foreground text-xs mt-1">Zero data loss · Zero human intervention</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </TabsContent>

        {/* ── INJECTION LAB TAB ── */}
        <TabsContent value="injections">
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
              <p className="text-sm text-amber-400 font-medium flex items-center gap-2">
                <FlaskConical className="h-4 w-4" />
                Injection Lab — Select a fault type, then inject it while the game is running.
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Each injection mutates actual board or game state. Phoenix uses python-chess
                board.status() flags, material audits, and turn tracking to detect the anomaly in real time.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {INJECTIONS.map((inj) => (
                <motion.button
                  key={inj.type}
                  onClick={() => setSelectedInj(inj.type)}
                  whileTap={{ scale: 0.98 }}
                  className={cn(
                    "text-left p-4 rounded-xl border-2 transition-all duration-200 space-y-1",
                    inj.color,
                    selectedInj === inj.type
                      ? "bg-primary/10 border-primary"
                      : "bg-card border-border"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm text-foreground">{inj.label}</span>
                    {selectedInj === inj.type && (
                      <Badge className="text-[10px] bg-primary text-primary-foreground">Selected</Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">{inj.desc}</p>
                </motion.button>
              ))}
            </div>

            <div className="flex items-center gap-3 pt-2">
              <Button
                onClick={handleInject}
                disabled={isInjecting || status !== "running"}
                variant="destructive"
                className="gap-2 px-6"
              >
                <Zap className="h-4 w-4" />
                {isInjecting ? "Injecting…" : `Inject: ${INJECTIONS.find(i => i.type === selectedInj)?.label}`}
              </Button>
              {status !== "running" && (
                <p className="text-xs text-muted-foreground">Start a game first to enable injection</p>
              )}
            </div>

            {/* Custom Move Injection */}
            <div className="border-t border-border pt-4 space-y-3">
              <div>
                <p className="text-sm font-semibold mb-0.5">Custom Move Injection</p>
                <p className="text-xs text-muted-foreground">
                  Type any UCI move (e.g. <code className="text-primary">e2e4</code>, <code className="text-primary">g1h9</code>). Legal moves are pushed onto the board then corrupted; illegal moves teleport the piece and trigger Phoenix.
                </p>
              </div>
              <div className="flex gap-2">
                <Input
                  placeholder="UCI move (e.g. e2e4, g1f3, e7e9)"
                  value={customUci}
                  onChange={(e) => setCustomUci(e.target.value.toLowerCase())}
                  className="flex-1 font-mono text-sm"
                  disabled={status !== "running"}
                  onKeyDown={(e) => e.key === "Enter" && !isInjectingCustom && handleInjectCustom()}
                />
                <Button
                  onClick={handleInjectCustom}
                  disabled={isInjectingCustom || status !== "running" || !customUci.trim()}
                  variant="outline"
                  className="gap-2 border-primary/50 text-primary hover:bg-primary/10"
                >
                  <Zap className="h-4 w-4" />
                  {isInjectingCustom ? "Injecting…" : "Inject Move"}
                </Button>
              </div>
            </div>
          </div>
        </TabsContent>

        {/* ── CORRECTION LOG TAB ── */}
        <TabsContent value="corrections">
          <div className="space-y-3">
            {corrections.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground text-sm border border-dashed border-border rounded-xl">
                <BarChart2 className="h-10 w-10 mb-3 opacity-30" />
                <p className="font-medium">No corrections yet</p>
                <p className="text-xs mt-1 opacity-60">Inject a fault to trigger Phoenix correction engine</p>
              </div>
            ) : (
              <AnimatePresence mode="popLayout">
                {corrections.map((c, i) => <CorrectionCard key={c.id} evt={c} index={i} />)}
              </AnimatePresence>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
