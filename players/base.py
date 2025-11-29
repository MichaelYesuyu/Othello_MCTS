from abc import ABC, abstractmethod
from typing import Optional, Tuple, Callable, Protocol
from enums import PlayerType
from board import OthelloBoard

class Player(ABC):
    def __init__(self, color: PlayerType):
        if color is PlayerType.EMPTY:
            raise ValueError("Player color must be BLACK or WHITE")
        self.color = color
        self.moves: list[Tuple[int, int]] = []

    @abstractmethod
    def choose_move(self, board) -> Optional[Tuple[int, int]]:
        """
        Return (row, col) for the move, or None to pass.
        """
        ...

ProgressCallback = Callable[[int, int], None]  # (done_iterations, total_iterations)


class ProgressPlayer(Player):
    """
    Player that supports a long-running search with progress updates.
    Subclasses implement choose_move_with_progress; the default choose_move
    just calls it with a dummy callback.
    """

    @abstractmethod
    def choose_move_with_progress(
        self,
        board: OthelloBoard,
        progress_callback: ProgressCallback,
    ) -> Optional[Tuple[int, int]]:
        ...

    def choose_move(self, board: OthelloBoard) -> Optional[Tuple[int, int]]:
        # Fallback if you call it like a normal Player (no progress UI)
        return self.choose_move_with_progress(board, lambda done, total: None)