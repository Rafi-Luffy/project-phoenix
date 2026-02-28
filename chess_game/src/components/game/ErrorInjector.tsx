import { useState } from 'react';
import {
  Play,
  Square,
  Pause,
  RefreshCcw,
  Zap,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Terminal,
  Wifi,
  WifiOff,
  RotateCcw,
} from 'lucide-react';
import { useGameStore } from '@/store/gameStore';

const INJECTION_TYPES = [
  { id: 'illegal_move',    label: 'Illegal Move',    color: 'text-orange-400' },
  { id: 'duplicate_piece', label: 'Duplicate Piece', color: 'text-yellow-400' },
  { id: 'wrong_turn',      label: 'Wrong Turn',      color: 'text-pink-400'   },
];

// Cryptic error overlay shown when a fault is injected
const ErrorOverlay = () => {
  const errorCode     = useGameStore((s) => s.errorCode);
  const errorRawType  = useGameStore((s) => s.errorRawType);
  const errorDesc     = useGameStore((s) => s.errorDesc);
  const isHealing     = useGameStore((s) => s.isHealing);
  const isFixed       = useGameStore((s) => s.isFixed);
  const incidents     = useGameStore((s) => s.incidents);
  const userResume    = useGameStore((s) => s.userResume);
  const corrExplain   = useGameStore((s) => s.correctionExplanation);
  const corrLatency   = useGameStore((s) => s.correctionLatencyMs);

  return (
    <div className="w-full rounded-xl border border-destructive/40 bg-black/90 p-5 font-mono space-y-4 shadow-2xl shadow-destructive/20 backdrop-blur-sm">
      {/* Error header */}
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-6 w-6 text-destructive shrink-0 mt-0.5 animate-pulse" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-destructive text-sm font-bold tracking-widest">SYSTEM HALT</span>
            <span className="text-[10px] text-muted-foreground bg-muted/20 px-1.5 py-0.5 rounded border border-border">
              {errorRawType.toUpperCase().replaceAll('_', '_')}
            </span>
          </div>
          <code className="block text-amber-400 text-xs mt-1 break-all">{errorCode}</code>
        </div>
      </div>

      {/* Stack trace style output */}
      <div className="bg-zinc-950 rounded-lg p-3 border border-zinc-800 text-[11px] space-y-1 leading-relaxed text-zinc-400">
        <div className="text-zinc-500"># board integrity audit</div>
        <div><span className="text-red-400">FAULT</span> {errorDesc || 'Unspecified board state corruption detected'}</div>
        <div><span className="text-zinc-500">STACK</span> <span className="text-amber-300/70">phoenix://monitor/scan → phoenix://engine/validate → phoenix://board/state</span></div>
        <div><span className="text-zinc-500">STATUS</span> <span className={isHealing ? 'text-blue-400 animate-pulse' : isFixed ? 'text-green-400' : 'text-red-400'}>
          {isFixed ? 'CORRECTED — board restored from checkpoint' : isHealing ? 'HEALING IN PROGRESS...' : 'HALTED — awaiting phoenix correction pipeline'}
        </span></div>
      </div>

      {/* Healing trace */}
      {incidents.length > 0 && (
        <div className="space-y-1 max-h-28 overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-700 pr-1">
          {incidents.map((inc, i) => (
            <div key={inc.id ?? i} className="flex items-start gap-1.5 text-[10px] text-zinc-500">
              <span className={`shrink-0 mt-0.5 ${inc.status === 'resolved' ? 'text-green-400' : 'text-blue-400'}`}>▸</span>
              <span className="break-words">{inc.message}</span>
            </div>
          ))}
        </div>
      )}

      {/* Healing progress or resolved */}
      {isHealing && (
        <div className="flex items-center gap-2 text-xs text-blue-400">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          Phoenix correction pipeline active...
        </div>
      )}

      {isFixed && (
        <div className="space-y-3">
          {corrExplain && (
            <div className="text-[10px] text-green-400/80 leading-relaxed border-l-2 border-green-500/30 pl-2">
              {corrExplain}
            </div>
          )}
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <CheckCircle2 className="h-3.5 w-3.5 text-green-400" />
            Self-healed in <span className="text-green-400 font-bold">{corrLatency}ms</span>
          </div>
          <button
            onClick={userResume}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-green-500/20 border border-green-500/40 text-green-300 text-sm font-semibold tracking-wide hover:bg-green-500/30 transition-colors"
          >
            <Play className="h-4 w-4" />
            Resume Game
          </button>
        </div>
      )}
    </div>
  );
};

const ErrorInjector = () => {
  const gameStatus    = useGameStore((s) => s.gameStatus);
  const isPaused      = useGameStore((s) => s.isPaused);
  const isFrozen      = useGameStore((s) => s.isFrozen);
  const wsConnected   = useGameStore((s) => s.wsConnected);
  const startGame     = useGameStore((s) => s.startGame);
  const stopGame      = useGameStore((s) => s.stopGame);
  const togglePause   = useGameStore((s) => s.togglePause);
  const injectError   = useGameStore((s) => s.injectError);
  const isInjecting   = useGameStore((s) => s.isInjecting);
  const injectionInput = useGameStore((s) => s.injectionInput);
  const setInjectionInput = useGameStore((s) => s.setInjectionInput);
  const moveCount     = useGameStore((s) => s.moveCount);
  const correctionCount = useGameStore((s) => s.correctionCount);
  const integrityScore = useGameStore((s) => s.integrityScore);
  const driftIndex    = useGameStore((s) => s.driftIndex);

  const [selectedType, setSelectedType] = useState<string>('illegal_move');
  const [injectionMode, setInjectionMode] = useState<'preset' | 'custom'>('preset');

  const isRunning = gameStatus === 'running';
  const canInject = isRunning && !isFrozen && !isInjecting;

  const handleInject = async () => {
    if (!canInject) return;
    if (injectionMode === 'custom') {
      const uci = injectionInput.trim();
      if (!uci) return;
      await injectError('custom', uci);
    } else {
      await injectError(selectedType);
    }
  };

  return (
    <div className="w-full max-w-md space-y-4">
      {/* Connection + status bar */}
      <div className="flex items-center gap-2 text-xs">
        <div className={`flex items-center gap-1 px-2 py-1 rounded-full border ${wsConnected ? 'border-green-500/30 bg-green-500/10 text-green-400' : 'border-zinc-700 bg-zinc-900 text-zinc-500'}`}>
          {wsConnected ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
          {wsConnected ? 'Backend connected' : 'Backend offline'}
        </div>
        <div className="flex-1" />
        <span className="text-muted-foreground font-mono">
          Moves: <span className="text-foreground">{moveCount}</span>
        </span>
        <span className="text-muted-foreground font-mono">
          Fixes: <span className="text-green-400">{correctionCount}</span>
        </span>
      </div>

      {/* Integrity metrics */}
      <div className="grid grid-cols-3 gap-2 text-[11px]">
        <div className="bg-card border border-border rounded-lg p-2 text-center">
          <div className="text-muted-foreground mb-0.5">Integrity</div>
          <div className={`font-bold font-mono ${integrityScore > 90 ? 'text-green-400' : integrityScore > 70 ? 'text-amber-400' : 'text-red-400'}`}>
            {integrityScore.toFixed(1)}%
          </div>
        </div>
        <div className="bg-card border border-border rounded-lg p-2 text-center">
          <div className="text-muted-foreground mb-0.5">Drift</div>
          <div className={`font-bold font-mono ${driftIndex < 0.1 ? 'text-green-400' : 'text-amber-400'}`}>
            {driftIndex.toFixed(3)}
          </div>
        </div>
        <div className="bg-card border border-border rounded-lg p-2 text-center">
          <div className="text-muted-foreground mb-0.5">Status</div>
          <div className={`font-bold capitalize ${
            isFrozen ? 'text-red-400' :
            gameStatus === 'running' ? 'text-green-400' :
            gameStatus === 'healing' ? 'text-blue-400 animate-pulse' :
            gameStatus === 'healed' ? 'text-green-300' :
            'text-muted-foreground'
          }`}>
            {isFrozen ? 'halted' : gameStatus}
          </div>
        </div>
      </div>

      {/* Game controls */}
      <div className="flex gap-2">
        {gameStatus === 'idle' || gameStatus === 'healed' ? (
          <button
            onClick={startGame}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            <Play className="h-4 w-4" />
            Start Game
          </button>
        ) : (
          <>
            <button
              onClick={togglePause}
              disabled={isFrozen}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-input bg-card text-foreground text-sm font-medium hover:bg-accent transition-colors disabled:opacity-40"
            >
              {isPaused ? <><Play className="h-4 w-4" /> Resume</> : <><Pause className="h-4 w-4" /> Pause</>}
            </button>
            <button
              onClick={stopGame}
              className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-destructive/20 border border-destructive/30 text-destructive text-sm font-medium hover:bg-destructive/30 transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </button>
          </>
        )}
      </div>

      {/* Error overlay when frozen */}
      {isFrozen && <ErrorOverlay />}

      {/* Inject section — only show when game is running and not frozen */}
      {isRunning && !isFrozen && (
        <div className="space-y-3 border border-border rounded-xl p-4 bg-card/50">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium">Fault Injector</span>
          </div>

          {/* Mode toggle */}
          <div className="flex gap-1 p-1 bg-muted rounded-lg text-xs">
            <button
              onClick={() => setInjectionMode('preset')}
              className={`flex-1 py-1 rounded-md transition-colors font-medium ${injectionMode === 'preset' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
            >
              Preset Fault
            </button>
            <button
              onClick={() => setInjectionMode('custom')}
              className={`flex-1 py-1 rounded-md transition-colors font-medium ${injectionMode === 'custom' ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
            >
              Custom Move (UCI)
            </button>
          </div>

          {injectionMode === 'preset' ? (
            <div className="grid grid-cols-3 gap-1.5">
              {INJECTION_TYPES.map((t) => (
                <button
                  key={t.id}
                  onClick={() => setSelectedType(t.id)}
                  className={`text-left px-2.5 py-2 rounded-lg border text-xs transition-colors ${
                    selectedType === t.id
                      ? 'border-primary/60 bg-primary/10 text-primary'
                      : 'border-border bg-card hover:border-border/80 text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <span className={t.color}>▸ </span>{t.label}
                </button>
              ))}
            </div>
          ) : (
            <div className="space-y-1.5">
              <input
                type="text"
                value={injectionInput}
                onChange={(e) => setInjectionInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleInject()}
                placeholder="UCI move e.g. e2e4, e7e9, a1b8"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
              <p className="text-[10px] text-muted-foreground">
                Legal moves execute normally then corrupt the board. Illegal moves teleport the piece.
              </p>
            </div>
          )}

          <button
            onClick={handleInject}
            disabled={!canInject || (injectionMode === 'custom' && !injectionInput.trim())}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-amber-500/20 border border-amber-500/40 text-amber-300 text-sm font-semibold hover:bg-amber-500/30 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isInjecting ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Injecting...</>
            ) : (
              <><Zap className="h-4 w-4" /> Inject Fault</>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default ErrorInjector;
