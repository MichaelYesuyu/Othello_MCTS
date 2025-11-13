"""
AI Player for Othello
This is a stub - implement your AI logic here (e.g., MCTS, minimax, etc.)
"""

import random

def get_ai_move(board, color):
    """
    Get the AI's move choice
    
    Args:
        board: OthelloBoard instance
        color: 'black' or 'white' - the AI's color
    
    Returns:
        (row, col): tuple representing the move to make
    
    TODO: Implement your AI logic here
    Current implementation returns a random valid move
    
    For MCTS or other AI implementations, you can:
    1. Access board.board to see the current state
    2. Use board.get_valid_moves(color) to get possible moves
    3. Use board.copy() to simulate moves without affecting the real board
    4. Use board.make_move(row, col, color) on copied boards
    5. Return the best (row, col) move
    """
    valid_moves = board.get_valid_moves(color)
    
    if not valid_moves:
        return None
    
    # TODO: Replace this with your AI logic
    # For now, just return a random valid move
    return random.choice(valid_moves)