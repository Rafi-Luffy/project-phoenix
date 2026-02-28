import { useEffect } from 'react';
import ChessBoard2D from '@/components/game/ChessBoard2D';
import ErrorInjector from '@/components/game/ErrorInjector';
import { useGameStore } from '@/store/gameStore';

const Index = () => {
  const initWebSocket = useGameStore((s) => s.initWebSocket);
  const moveHistory   = useGameStore((s) => s.moveHistory);
  const currentTurn   = useGameStore((s) => s.currentTurn);
  const aiConfidence  = useGameStore((s) => s.aiConfidence);

  // Initialize WebSocket once on mount
  useEffect(() => {
    const cleanup = initWebSocket();
    return cleanup;
  }, [initWebSocket]);

  return (
    <main className="min-h-screen bg-background text-foreground flex flex-col items-center py-8 px-4 gap-6">
      {/* Header */}
      <div className="text-center space-y-1 max-w-lg">
        <h1 className="text-xl font-bold tracking-tight">
          Project Phoenix — Chess Testbed
        </h1>
        <p className="text-sm text-muted-foreground">
          Autonomous self-healing game simulation &bull; Inject faults, watch Phoenix correct them
        </p>
      </div>

      {/* Main layout: board left, controls right */}
      <div className="flex flex-col lg:flex-row items-start gap-8 w-full max-w-4xl">
        {/* Board */}
        <div className="flex-shrink-0 flex flex-col items-center gap-4">
          <ChessBoard2D />

          {/* Turn indicator */}
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <div className={`h-3 w-3 rounded-full border-2 ${currentTurn === 'white' ? 'bg-white border-white' : 'bg-zinc-900 border-zinc-400'}`} />
            <span>{currentTurn === 'white' ? 'White Agent' : 'Black Agent'} to move</span>
            <span className="text-zinc-600">&bull;</span>
            <span>Conf: <span className="text-foreground font-mono">{aiConfidence.toFixed(1)}%</span></span>
          </div>
        </div>

        {/* Controls + Injector */}
        <div className="flex-1 w-full lg:max-w-sm">
          <ErrorInjector />
        </div>
      </div>

      {/* Move history */}
      {moveHistory.length > 0 && (
        <div className="w-full max-w-4xl">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">Move History</h2>
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <div className="max-h-36 overflow-y-auto divide-y divide-border">
              {moveHistory.map((m, i) => (
                <div key={i} className="flex items-center gap-3 px-4 py-1.5 text-xs hover:bg-muted/20 transition-colors">
                  <span className="text-muted-foreground font-mono w-6 text-right shrink-0">{m.move_number}.</span>
                  <div className={`h-2.5 w-2.5 rounded-full border shrink-0 ${m.color === 'white' ? 'bg-white border-white' : 'bg-zinc-800 border-zinc-500'}`} />
                  <span className="font-mono text-primary">{m.san || m.uci}</span>
                  {m.is_capture && <span className="text-amber-400 text-[10px]">×capture</span>}
                  {m.gives_check && <span className="text-red-400 text-[10px]">+check</span>}
                  <span className="ml-auto font-mono text-[10px] text-muted-foreground">{m.evaluation > 0 ? '+' : ''}{m.evaluation}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Footer link back to dashboard */}
      <div className="text-xs text-muted-foreground">
        Logs from this session appear in your{' '}
        <a href="http://localhost:8080/console" target="_blank" rel="noreferrer" className="text-primary hover:underline">
          Phoenix Dashboard
        </a>
      </div>
    </main>
  );
};

export default Index;
