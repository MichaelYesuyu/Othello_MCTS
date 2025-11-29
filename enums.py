from enum import Enum


class PlayerType(Enum):
    BLACK = 1
    WHITE = -1
    EMPTY = 0

    @property
    def opponent(self) -> "PlayerType":
        if self is PlayerType.BLACK:
            return PlayerType.WHITE
        if self is PlayerType.WHITE:
            return PlayerType.BLACK
        raise ValueError("EMPTY has no opponent")