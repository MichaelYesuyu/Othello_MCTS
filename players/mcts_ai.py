import math
import random
from typing import Optional, Tuple, List
from tqdm import tqdm

from .base import Player, ProgressCallback
from enums import PlayerType
from board import OthelloBoard


class MCTSNode:
    """
    A node in the Monte Carlo search tree.
    Stores statistics (wins, visits), children, and untried moves.
    All rewards are from the root player's perspective.
    """
    def __init__(
        self,
        parent: Optional["MCTSNode"],
        move: Optional[Tuple[int, int]],
        player_to_move: PlayerType,
        untried_moves: List[Tuple[int, int]],
    ):
        self.parent = parent
        self.move = move  # move taken from parent to reach this node
        self.player_to_move = player_to_move

        self.children: List["MCTSNode"] = []
        self.untried_moves: List[Tuple[int, int]] = untried_moves

        self.visits: int = 0
        self.wins: float = 0.0  # cumulative reward from root player's POV

    def uct_select_child(self, exploration_const: float) -> "MCTSNode":
        """
        Select a child node using the UCB1 formula:
        UCT = (wins / visits) + C * sqrt(2 * ln(parent_visits) / visits)
        """
        assert self.children, "No children to select from"

        log_parent_visits = math.log(self.visits)

        def uct_score(child: "MCTSNode") -> float:
            if child.visits == 0:
                return float("inf")
            exploit = child.wins / child.visits
            explore = exploration_const * math.sqrt(
                2.0 * log_parent_visits / child.visits
            )
            return exploit + explore

        return max(self.children, key=uct_score)

    def add_child(
        self,
        move: Tuple[int, int],
        player_to_move: PlayerType,
        untried_moves: List[Tuple[int, int]],
    ) -> "MCTSNode":
        child = MCTSNode(
            parent=self,
            move=move,
            player_to_move=player_to_move,
            untried_moves=untried_moves,
        )
        self.untried_moves.remove(move)
        self.children.append(child)
        return child

    def update(self, reward: float) -> None:
        """Update this node's statistics with the given reward."""
        self.visits += 1
        self.wins += reward

class MCTSPlayer(Player):
    """
    Monte Carlo Tree Search player.
    Runs MCTS for a fixed number of iterations and returns the best move.
    """

    def __init__(
        self,
        color: PlayerType,
        iterations: int = 1000,
        exploration_const: float = 1.4,
        seed: Optional[int] = None,
    ):
        super().__init__(color)
        self.iterations = iterations
        self.exploration_const = exploration_const
        self.rng = random.Random(seed)
        self.root: Optional[MCTSNode] = None

    def notify_move_played(self, move: Optional[Tuple[int, int]], player: PlayerType):
        # call this from outside after every real game move.
        if self.root is None or move is None:
            self.root = None
            return

        # if the move exists among children, jump there. else discard tree.
        for child in self.root.children:
            if child.move == move:
                child.parent = None
                self.root = child
                return

        self.root = None

    def choose_move(self, board: OthelloBoard, progress_callback: Optional[ProgressCallback] = None,) -> Optional[Tuple[int, int]]:
        root_moves = board.get_valid_moves(self.color)
        if not root_moves:
            return None

        if self.root is None:
            root = MCTSNode(
                parent=None,
                move=None,
                player_to_move=self.color,
                untried_moves=root_moves[:],
            )
            self.root = root
        else:
            root = self.root
        
        remaining = max(0, self.iterations - root.visits)

        if remaining == 0:
            # we already hit the budget
            if progress_callback is not None:
                progress_callback(self.iterations, self.iterations)
        else:
            # MCTS iterations
            for i in tqdm(range(remaining), desc="MCTS", leave=False):
                node = root

                sim_board = board.copy()
                player_to_move = self.color

                # SELECTION
                while node.untried_moves == [] and node.children:
                    node = node.uct_select_child(self.exploration_const)

                    if node.move is not None:
                        r, c = node.move
                        sim_board.make_move(r, c, player_to_move)

                    player_to_move = player_to_move.opponent

                # EXPANSION
                if node.untried_moves:
                    move = self.rng.choice(node.untried_moves)
                    r, c = move
                    sim_board.make_move(r, c, player_to_move)
                    next_player = player_to_move.opponent

                    # untried moves for the new node
                    next_moves = sim_board.get_valid_moves(next_player)
                    node = node.add_child(
                        move=move,
                        player_to_move=next_player,
                        untried_moves=next_moves,
                    )
                    player_to_move = next_player

                # SIMULATION
                reward = self._rollout(sim_board, player_to_move)

                # BACKPROPAGATION
                self._backpropagate(node, reward)

                if progress_callback is not None:
                    progress_callback(i + 1, remaining)

        # choose the move with the most visits from the root
        if not root.children:
            return None

        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move


    def _rollout(self, board: OthelloBoard, current_player: PlayerType) -> float:
        """
        Random playout until the game ends.
        Returns reward in [0, 1] from this player's perspective (self.color):
          1.0 win, 0.0 loss, 0.5 tie.
        """

        while not board.is_game_over():
            moves = board.get_valid_moves(current_player)
            if moves:
                move = self.rng.choice(moves)
                r, c = move
                board.make_move(r, c, current_player)
                current_player = current_player.opponent
            else:
                # no moves for current player, check if opponent has moves
                opp_moves = board.get_valid_moves(current_player.opponent)
                if opp_moves:
                    current_player = current_player.opponent
                else:
                    # neither player can move, game over
                    break

        black_score, white_score = board.get_score()

        if self.color is PlayerType.BLACK:
            if black_score > white_score:
                return 1.0
            elif black_score < white_score:
                return 0.0
            else:
                return 0.5
        else:
            if white_score > black_score:
                return 1.0
            elif white_score < black_score:
                return 0.0
            else:
                return 0.5

    def _backpropagate(self, node: MCTSNode, reward: float) -> None:
        """
        Propagate the reward up the tree.
        We stored reward from the root player's perspective,
        so every node gets the same reward.
        """
        while node is not None:
            node.update(reward)
            node = node.parent