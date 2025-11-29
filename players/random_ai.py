import random
from .base import Player
from board import OthelloBoard
from typing import Optional, Tuple
from enums import PlayerType

class RandomAIPlayer(Player):
    def __init__(self, color: PlayerType, seed: int = None):
        super().__init__(color)
        self.rng = random.Random(seed)

    def choose_move(self, board: OthelloBoard, **kwargs) -> Optional[Tuple[int, int]]:
        valid = board.get_valid_moves(self.color)
        if not valid:
            return None
        return self.rng.choice(valid)