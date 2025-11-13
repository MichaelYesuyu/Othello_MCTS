"""
Othello/Reversi Game Logic
Handles board state, move validation, and game rules
"""

class OthelloBoard:
    def __init__(self, size=8):
        """
        Initialize an Othello board
        size: 4, 6, or 8
        """
        if size not in [4, 6, 8]:
            raise ValueError("Board size must be 4, 6, or 8")
        
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.current_player = 'black'
        
        # Set up initial pieces (center 2x2)
        mid = size // 2
        self.board[mid-1][mid-1] = 'white'
        self.board[mid-1][mid] = 'black'
        self.board[mid][mid-1] = 'black'
        self.board[mid][mid] = 'white'
        
        # Cache for valid moves
        self._valid_moves_cache = None
        self._cache_player = None
    
    def get_cell(self, row, col):
        """Get the value at a board position"""
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.board[row][col]
        return None
    
    def get_valid_moves(self, color):
        """
        Get all valid moves for a player
        Returns: list of (row, col) tuples
        """
        # Use cache if available
        if self._valid_moves_cache is not None and self._cache_player == color:
            return self._valid_moves_cache
        
        valid_moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.is_valid_move(row, col, color):
                    valid_moves.append((row, col))
        
        # Cache the result
        self._valid_moves_cache = valid_moves
        self._cache_player = color
        
        return valid_moves
    
    def is_valid_move(self, row, col, color):
        """
        Check if a move is valid
        A move is valid if:
        1. The cell is empty
        2. It flanks at least one opponent disc
        """
        if self.board[row][col] is not None:
            return False
        
        opponent = 'white' if color == 'black' else 'black'
        
        # Check all 8 directions
        directions = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1),           (0, 1),
                     (1, -1),  (1, 0),  (1, 1)]
        
        for dr, dc in directions:
            if self._check_direction(row, col, dr, dc, color, opponent):
                return True
        
        return False
    
    def _check_direction(self, row, col, dr, dc, color, opponent):
        """
        Check if placing a disc at (row, col) would flip pieces in direction (dr, dc)
        """
        r, c = row + dr, col + dc
        found_opponent = False
        
        while 0 <= r < self.size and 0 <= c < self.size:
            cell = self.board[r][c]
            
            if cell is None:
                return False
            elif cell == opponent:
                found_opponent = True
            elif cell == color:
                return found_opponent
            
            r += dr
            c += dc
        
        return False
    
    def make_move(self, row, col, color):
        """
        Make a move and flip all flanked pieces
        Returns: True if move was made, False if invalid
        """
        if not self.is_valid_move(row, col, color):
            return False
        
        # Place the disc
        self.board[row][col] = color
        
        # Flip pieces in all valid directions
        opponent = 'white' if color == 'black' else 'black'
        directions = [(-1, -1), (-1, 0), (-1, 1),
                     (0, -1),           (0, 1),
                     (1, -1),  (1, 0),  (1, 1)]
        
        for dr, dc in directions:
            if self._check_direction(row, col, dr, dc, color, opponent):
                self._flip_pieces(row, col, dr, dc, color, opponent)
        
        # Invalidate cache
        self._valid_moves_cache = None
        self._cache_player = None
        
        # Switch player
        self.current_player = opponent
        
        return True
    
    def _flip_pieces(self, row, col, dr, dc, color, opponent):
        """
        Flip all opponent pieces in the given direction
        """
        r, c = row + dr, col + dc
        pieces_to_flip = []
        
        while 0 <= r < self.size and 0 <= c < self.size:
            cell = self.board[r][c]
            
            if cell == opponent:
                pieces_to_flip.append((r, c))
            elif cell == color:
                # Flip all collected pieces
                for flip_r, flip_c in pieces_to_flip:
                    self.board[flip_r][flip_c] = color
                break
            
            r += dr
            c += dc
    
    def get_score(self):
        """
        Get current score
        Returns: (black_count, white_count)
        """
        black_count = 0
        white_count = 0
        
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 'black':
                    black_count += 1
                elif self.board[row][col] == 'white':
                    white_count += 1
        
        return black_count, white_count
    
    def is_game_over(self):
        """
        Check if the game is over
        Game is over when neither player has valid moves
        """
        black_moves = self.get_valid_moves('black')
        white_moves = self.get_valid_moves('white')
        
        return len(black_moves) == 0 and len(white_moves) == 0
    
    def get_winner(self):
        """
        Get the winner of the game
        Returns: 'black', 'white', or 'tie'
        """
        black_score, white_score = self.get_score()
        
        if black_score > white_score:
            return 'black'
        elif white_score > black_score:
            return 'white'
        else:
            return 'tie'
    
    def copy(self):
        """
        Create a deep copy of the board (useful for AI simulations)
        """
        new_board = OthelloBoard(self.size)
        new_board.board = [row[:] for row in self.board]
        new_board.current_player = self.current_player
        return new_board