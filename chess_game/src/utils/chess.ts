export type PieceType = 'pawn' | 'rook' | 'knight' | 'bishop' | 'queen' | 'king';
export type Team = 'alpha' | 'omega';

export interface ChessPiece {
  type: PieceType;
  team: Team;
  id: string;
}

export interface ChessMove {
  from: [number, number];
  to: [number, number];
  captured?: boolean;
}

export const createInitialBoard = (): (ChessPiece | null)[][] => {
  const board: (ChessPiece | null)[][] = Array(8).fill(null).map(() => Array(8).fill(null));
  const backRow: PieceType[] = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'];

  for (let col = 0; col < 8; col++) {
    board[0][col] = { type: backRow[col], team: 'omega', id: `omega-${backRow[col]}-${col}` };
    board[1][col] = { type: 'pawn', team: 'omega', id: `omega-pawn-${col}` };
    board[7][col] = { type: backRow[col], team: 'alpha', id: `alpha-${backRow[col]}-${col}` };
    board[6][col] = { type: 'pawn', team: 'alpha', id: `alpha-pawn-${col}` };
  }

  return board;
};

// Ruy Lopez opening sequence
export const PRESET_MOVES: ChessMove[] = [
  { from: [6, 4], to: [4, 4] },             // 1. e4
  { from: [1, 4], to: [3, 4] },             // 1... e5
  { from: [7, 6], to: [5, 5] },             // 2. Nf3
  { from: [0, 1], to: [2, 2] },             // 2... Nc6
  { from: [7, 5], to: [3, 1] },             // 3. Bb5
  { from: [1, 0], to: [2, 0] },             // 3... a6
  { from: [3, 1], to: [2, 2], captured: true }, // 4. Bxc6
  { from: [1, 3], to: [2, 2], captured: true }, // 4... dxc6
  { from: [6, 3], to: [4, 3] },             // 5. d4
  { from: [3, 4], to: [4, 3], captured: true }, // 5... exd4
  { from: [5, 5], to: [4, 3], captured: true }, // 6. Nxd4
  { from: [0, 5], to: [2, 3] },             // 6... Bd6
  { from: [7, 1], to: [5, 2] },             // 7. Nc3
  { from: [0, 6], to: [2, 5] },             // 7... Nf6
];

export const ALPHA_REASONINGS = [
  "Seizing central control. Aggressive opening stance.",
  "Deploying cavalry. Kingside pressure initiated.",
  "Ruy Lopez selected. Maximum positional tension.",
  "Exchanging on c6. Damaging pawn structure.",
  "Central expansion. Territory dominance protocol.",
  "Recapturing with tempo. Knight centralized optimally.",
  "Full mobilization. Queenside development complete.",
];

export const OMEGA_REASONINGS = [
  "Symmetrical response. Maintaining equilibrium.",
  "Knight developed. Central defense fortified.",
  "Prophylactic a6. Denying bishop's pressure.",
  "Structure concession accepted. Activity compensates.",
  "Counter-strike initiated. Central tension exploited.",
  "Bishop deployed. Key diagonal controlled.",
  "Knight to f6. Counterplay channels opening.",
];
