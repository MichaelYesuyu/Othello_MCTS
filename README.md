# Othello/Reversi Game

A fully functional Othello game with GUI using Pygame, ready for AI implementation.

## Features

- ✅ Complete Othello game rules
- ✅ Three board sizes: 4x4, 6x6, 8x8
- ✅ Player vs Player mode
- ✅ Player vs AI mode (with AI stub ready for your implementation)
- ✅ Choose your color when playing against AI
- ✅ Visual hints showing valid moves
- ✅ Score tracking
- ✅ Game over detection with winner announcement

## Installation

```bash
pip install pygame
```

## Running the Game

```bash
python main.py
```

## Project Structure

```
othello_game.py    # Core game logic (board state, move validation, rules)
ai_player.py       # AI stub - IMPLEMENT YOUR AI HERE
othello_gui.py     # Pygame GUI (menu, board display, user interaction)
main.py           # Entry point
```

## File Descriptions

### `othello_game.py`
Contains the `OthelloBoard` class with all game logic:
- Board initialization with configurable size
- Move validation (checks flanking in all 8 directions)
- Move execution (places disc and flips pieces)
- Score calculation
- Game over detection
- Board copying (for AI simulations)
- Valid move caching for efficiency

### `ai_player.py`
**THIS IS WHERE YOU IMPLEMENT YOUR AI**

The stub function:
```python
def get_ai_move(board, color):
    """
    Args:
        board: OthelloBoard instance
        color: 'black' or 'white'
    
    Returns:
        (row, col): tuple for the move to make
    """
    # TODO: Implement your AI (MCTS, minimax, etc.)
    pass
```

### `othello_gui.py`
Complete Pygame GUI with:
- Main menu (board size, game mode, color selection)
- Game board visualization
- Mouse input handling
- AI integration
- Game over screen

## How to Implement Your AI

### Basic Template

Replace the content of `get_ai_move()` in `ai_player.py`:

```python
def get_ai_move(board, color):
    # 1. Get valid moves
    valid_moves = board.get_valid_moves(color)
    
    if not valid_moves:
        return None
    
    # 2. Evaluate each move
    best_move = None
    best_score = float('-inf')
    
    for move in valid_moves:
        # Create a copy to simulate
        test_board = board.copy()
        row, col = move
        test_board.make_move(row, col, color)
        
        # Evaluate this position
        score = evaluate_position(test_board, color)
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move

def evaluate_position(board, color):
    # Your evaluation function
    # Simple example: just count discs
    black_score, white_score = board.get_score()
    return black_score if color == 'black' else white_score
```

### For MCTS Implementation

```python
def get_ai_move(board, color):
    # Your MCTS implementation
    root = MCTSNode(board, color)
    
    # Run simulations
    for _ in range(num_simulations):
        node = root
        sim_board = board.copy()
        
        # Selection
        while node.is_fully_expanded() and node.children:
            node = node.select_child()
            # Apply node's move to sim_board
        
        # Expansion
        if not sim_board.is_game_over():
            node = node.expand(sim_board)
        
        # Simulation
        result = simulate_game(sim_board, color)
        
        # Backpropagation
        node.backpropagate(result)
    
    # Return best move
    return root.best_child().move
```

### Useful OthelloBoard Methods for AI

```python
# Get all valid moves
valid_moves = board.get_valid_moves(color)  # Returns [(row, col), ...]

# Check if specific move is valid
is_valid = board.is_valid_move(row, col, color)  # Returns bool

# Make a move (modifies board)
success = board.make_move(row, col, color)  # Returns bool

# Get current score
black_count, white_count = board.get_score()  # Returns (int, int)

# Check if game is over
game_over = board.is_game_over()  # Returns bool

# Get winner
winner = board.get_winner()  # Returns 'black', 'white', or 'tie'

# Copy board for simulation (doesn't affect original)
test_board = board.copy()  # Returns new OthelloBoard

# Access board state directly
cell_value = board.board[row][col]  # None, 'black', or 'white'
current_player = board.current_player  # 'black' or 'white'
board_size = board.size  # 4, 6, or 8
```

## Game Rules

1. **Starting Position**: 2x2 center formation with alternating colors
2. **Valid Moves**: Must flank (surround) at least one opponent disc
3. **Flanking**: Opponent discs between your new disc and existing disc flip to your color
4. **Passing**: If no valid moves, turn passes to opponent
5. **Game End**: When neither player has valid moves (usually full board)
6. **Winner**: Player with most discs

## Optimization Tips for AI

### Current Optimizations
- Valid move caching (invalidated after each move)
- Early termination in direction checking
- Efficient board copying for simulations

### For Heavy AI (MCTS/Deep Search)
Consider these optimizations if needed:
- Use numpy arrays instead of lists for board state
- Implement bitboards for ultra-fast operations
- Add transposition tables for position caching
- Parallel MCTS simulations
- Profile your code to find bottlenecks

### Typical MCTS Performance
- 4x4 board: Very fast, can do 10,000+ simulations
- 6x6 board: Fast, 5,000-10,000 simulations reasonable
- 8x8 board: Start with 1,000-5,000 simulations, optimize as needed

## Testing Your AI

1. Start with Player vs AI mode
2. Choose different board sizes to test scalability
3. Play both colors to ensure AI works for both sides
4. Watch for:
   - AI move time (should be < 2 seconds for good UX)
   - Move quality (does it make sensible moves?)
   - Edge cases (corners, passing, endgame)

## Common Othello Strategies (for AI evaluation)

- **Corners**: Most valuable (can't be flipped)
- **Edges**: Valuable but risky
- **Mobility**: Number of valid moves
- **Stability**: Discs that can't be flipped
- **Parity**: Who makes the last move

## Example: Simple Heuristic AI

```python
def get_ai_move(board, color):
    valid_moves = board.get_valid_moves(color)
    if not valid_moves:
        return None
    
    best_move = None
    best_score = float('-inf')
    
    for move in valid_moves:
        score = evaluate_move(board, move, color)
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move

def evaluate_move(board, move, color):
    row, col = move
    score = 0
    
    # Corner bonus
    corners = [(0, 0), (0, board.size-1), (board.size-1, 0), (board.size-1, board.size-1)]
    if move in corners:
        score += 100
    
    # Edge bonus (but not next to corner)
    if row == 0 or row == board.size-1 or col == 0 or col == board.size-1:
        if move not in corners:
            score += 10
    
    # Count flips
    test_board = board.copy()
    before_black, before_white = test_board.get_score()
    test_board.make_move(row, col, color)
    after_black, after_white = test_board.get_score()
    
    if color == 'black':
        score += after_black - before_black
    else:
        score += after_white - before_white
    
    return score
```

## Troubleshooting

**Game runs but AI doesn't move:**
- Check that `get_ai_move()` returns a valid `(row, col)` tuple
- Ensure your AI doesn't take too long (watch console for errors)

**AI makes invalid moves:**
- Use `board.get_valid_moves(color)` to get valid options
- Always validate your move before returning it

**Performance issues:**
- Profile your AI code to find bottlenecks
- Reduce number of simulations/search depth
- Consider caching or memoization

## Future Enhancements (Optional)

- Save/load games
- Move history with undo
- AI difficulty levels
- Network multiplayer
- Tournament mode
- Move hints for humans
- Animation for flipping discs

## License

Free to use and modify. Good luck with your AI implementation!