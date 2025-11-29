from enums import PlayerType
from typing import List, Tuple

class OthelloBoard:
    DIRECTIONS = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ]

    def __init__(self, size: int = 8):
        if size not in (4, 6, 8):
            raise ValueError("Board size must be 4, 6, or 8")

        self.size = size
        self.board: List[List[PlayerType]] = [
            [PlayerType.EMPTY for _ in range(size)] for _ in range(size)
        ]

        mid = size // 2
        self.board[mid-1][mid-1] = PlayerType.WHITE
        self.board[mid-1][mid]   = PlayerType.BLACK
        self.board[mid][mid-1]   = PlayerType.BLACK
        self.board[mid][mid]     = PlayerType.WHITE

    def __getitem__(self, idx: int) -> List[PlayerType]:
        # so you can do board[r][c]
        return self.board[idx]

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.size and 0 <= c < self.size

    def _discs_to_flip_in_direction(
        self,
        row: int,
        col: int,
        color: PlayerType,
        dr: int,
        dc: int,
    ) -> List[Tuple[int, int]]:
        r, c = row + dr, col + dc
        discs: List[Tuple[int, int]] = []

        while self.in_bounds(r, c):
            cell = self.board[r][c]
            if cell is PlayerType.EMPTY:
                return []  # hit empty, no flip
            if cell is color:
                return discs  # found own color, flip collected if any
            discs.append((r, c))
            r += dr
            c += dc

        # ran off the board
        return []

    def discs_to_flip(self, row: int, col: int, color: PlayerType) -> List[Tuple[int, int]]:
        if self.board[row][col] is not PlayerType.EMPTY:
            return []

        all_flips: List[Tuple[int, int]] = []
        for dr, dc in self.DIRECTIONS:
            all_flips.extend(self._discs_to_flip_in_direction(row, col, color, dr, dc))
        return all_flips

    def is_valid_move(self, row: int, col: int, color: PlayerType) -> bool:
        return len(self.discs_to_flip(row, col, color)) > 0

    def get_valid_moves(self, color: PlayerType) -> List[Tuple[int, int]]:
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if self.is_valid_move(r, c, color):
                    moves.append((r, c))
        return moves

    def make_move(self, row: int, col: int, color: PlayerType) -> bool:
        flips = self.discs_to_flip(row, col, color)
        if not flips:
            return False

        self.board[row][col] = color
        for r, c in flips:
            self.board[r][c] = color
        return True

    def get_score(self) -> tuple[int, int]:
        black = white = 0
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] is PlayerType.BLACK:
                    black += 1
                elif self.board[r][c] is PlayerType.WHITE:
                    white += 1
        return black, white

    def is_full(self) -> bool:
        return all(cell is not PlayerType.EMPTY for row in self.board for cell in row)

    def is_game_over(self) -> bool:
        # game is over when board is full or no valid moves for both
        return self.is_full() or (
            not self.get_valid_moves(PlayerType.BLACK)
            and not self.get_valid_moves(PlayerType.WHITE)
        )

    def copy(self) -> "OthelloBoard":
        new = OthelloBoard(self.size)
        new.board = [row[:] for row in self.board]
        return new
