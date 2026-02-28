import { useGameStore } from '@/store/gameStore';

// Map FEN piece chars to unicode symbols
const PIECE_UNICODE: Record<string, string> = {
  K: '♔', Q: '♕', R: '♖', B: '♗', N: '♘', P: '♙',
  k: '♚', q: '♛', r: '♜', b: '♝', n: '♞', p: '♟',
};

// White pieces = uppercase in FEN → render lighter; black = lowercase → render muted
const isWhitePiece = (ch: string) => ch === ch.toUpperCase();

// Parse FEN position part into 8x8 array of piece chars ('' for empty)
function fenToGrid(fen: string): string[][] {
  const position = fen.split(' ')[0];
  const rows = position.split('/');
  return rows.map((row) => {
    const cells: string[] = [];
    for (const ch of row) {
      const num = parseInt(ch, 10);
      if (!isNaN(num)) {
        for (let i = 0; i < num; i++) cells.push('');
      } else {
        cells.push(ch);
      }
    }
    return cells;
  });
}

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];

const ChessBoard2D = () => {
  const fen          = useGameStore((s) => s.fen);
  const isFrozen     = useGameStore((s) => s.isFrozen);
  const thinkingAgent = useGameStore((s) => s.thinkingAgent);
  const moveHistory  = useGameStore((s) => s.moveHistory);
  const grid         = fenToGrid(fen);

  const lastMove = moveHistory[0] ?? null;
  const lastFrom = lastMove?.from_sq ?? '';
  const lastTo   = lastMove?.to_sq ?? '';

  const squareName = (r: number, c: number) => `${FILES[c]}${8 - r}`;

  return (
    <div className="relative select-none">
      {/* Rank labels (left side) */}
      <div className="flex">
        <div className="flex flex-col justify-around pr-1 pb-5">
          {[8, 7, 6, 5, 4, 3, 2, 1].map((rank) => (
            <span key={rank} className="text-[10px] text-muted-foreground w-3 text-right leading-none" style={{ height: '3.5rem' }}>
              {rank}
            </span>
          ))}
        </div>

        <div className="flex flex-col">
          {/* Board grid */}
          {/* Freeze overlay — solid coverage so it works in both light and dark mode */}
          <div className="relative">
          {isFrozen && (
            <div className="absolute inset-0 z-10 rounded-lg flex flex-col items-center justify-center bg-black/70 backdrop-blur-[2px] border-2 border-destructive/70">
              <span className="text-4xl mb-2">🔒</span>
              <span className="text-destructive font-bold text-sm tracking-widest uppercase">System Halted</span>
              <span className="text-xs text-red-400/80 mt-1 font-mono">Awaiting resolution</span>
            </div>
          )}
          <div
            className={`inline-grid grid-cols-8 border-2 rounded-lg overflow-hidden shadow-xl transition-all duration-300 ${
              isFrozen
                ? 'border-destructive/60 shadow-destructive/20'
                : 'border-border'
            }`}
          >
            {grid.map((row, r) =>
              row.map((piece, c) => {
                const sq = squareName(r, c);
                const isDark = (r + c) % 2 === 1;
                const isFrom = sq === lastFrom;
                const isTo   = sq === lastTo;

                return (
                  <div
                    key={`${r}-${c}`}
                    className={`w-12 h-12 sm:w-14 sm:h-14 flex items-center justify-center text-2xl sm:text-3xl transition-colors duration-200 ${
                      isFrom || isTo
                        ? 'bg-primary/30'
                        : isDark
                        ? 'bg-[hsl(var(--board-dark))]'
                        : 'bg-[hsl(var(--board-light))]'
                    }`}
                  >
                    {piece && (
                      <span
                        title={piece}
                        className={`drop-shadow-sm transition-opacity ${
                          isWhitePiece(piece) ? 'text-white drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]' : 'text-zinc-900 drop-shadow-[0_1px_1px_rgba(255,255,255,0.3)]'
                        }`}
                      >
                        {PIECE_UNICODE[piece] ?? piece}
                      </span>
                    )}
                  </div>
                );
              })
            )}
          </div>

          {/* File labels (bottom) */}
          <div className="flex pt-1 pl-0">
            {FILES.map((f) => (
              <span key={f} className="text-[10px] text-muted-foreground text-center" style={{ width: '3.5rem' }}>
                {f}
              </span>
            ))}
          </div>
          </div>{/* end relative wrapper for freeze overlay */}
        </div>
      </div>

      {/* Thinking indicator */}
      {thinkingAgent && !isFrozen && (
        <div className="absolute bottom-7 left-0 right-0 flex justify-center">
          <span className="px-3 py-1 text-xs bg-muted/80 backdrop-blur-sm rounded-full text-muted-foreground animate-pulse border border-border">
            Thinking...
          </span>
        </div>
      )}
    </div>
  );
};

export default ChessBoard2D;
