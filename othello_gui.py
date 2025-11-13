"""
Othello GUI using Pygame
Handles menu, game visualization, and user interaction
"""

import pygame
import sys
from othello_game import OthelloBoard
from ai_player import get_ai_move

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BLUE = (70, 130, 180)
LIGHT_BLUE = (135, 206, 250)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.is_selected = False
    
    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        if self.is_selected:
            pygame.draw.rect(screen, BLUE, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 3)
        else:
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = font.render(self.text, True, WHITE if self.is_selected else BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class OthelloGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Othello")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.state = "menu"  # menu, game, game_over
        self.board = None
        self.board_size = 8
        self.game_mode = "pvp"  # pvp or pva (player vs AI)
        self.human_color = "black"  # Only used in pva mode
        self.ai_thinking = False
        self.ai_move_delay = 500  # ms delay before AI moves
        self.ai_timer = 0
        
        # Menu buttons
        self.create_menu_buttons()
    
    def create_menu_buttons(self):
        # Board size buttons
        self.size_buttons = [
            Button(250, 150, 80, 50, "4x4", LIGHT_GRAY, GRAY),
            Button(360, 150, 80, 50, "6x6", LIGHT_GRAY, GRAY),
            Button(470, 150, 80, 50, "8x8", LIGHT_GRAY, GRAY)
        ]
        self.size_buttons[2].is_selected = True  # 8x8 default
        
        # Game mode buttons
        self.mode_buttons = [
            Button(250, 250, 150, 50, "Player vs Player", LIGHT_GRAY, GRAY),
            Button(430, 250, 150, 50, "Player vs AI", LIGHT_GRAY, GRAY)
        ]
        self.mode_buttons[0].is_selected = True  # PvP default
        
        # Color selection buttons (only shown for PvA)
        self.color_buttons = [
            Button(250, 350, 120, 50, "Black", LIGHT_GRAY, GRAY),
            Button(400, 350, 120, 50, "White", LIGHT_GRAY, GRAY)
        ]
        self.color_buttons[0].is_selected = True  # Black default
        
        # Start button
        self.start_button = Button(300, 480, 200, 60, "Start Game", GREEN, LIGHT_GREEN)
    
    def draw_menu(self):
        self.screen.fill(WHITE)
        
        # Title
        title = self.title_font.render("OTHELLO", True, BLACK)
        title_rect = title.get_rect(center=(400, 70))
        self.screen.blit(title, title_rect)
        
        # Board size label
        size_label = self.text_font.render("Board Size:", True, BLACK)
        self.screen.blit(size_label, (320, 120))
        
        # Board size buttons
        for button in self.size_buttons:
            button.draw(self.screen, self.button_font)
        
        # Game mode label
        mode_label = self.text_font.render("Game Mode:", True, BLACK)
        self.screen.blit(mode_label, (320, 220))
        
        # Game mode buttons
        for button in self.mode_buttons:
            button.draw(self.screen, self.button_font)
        
        # Color selection (only if PvA mode)
        if self.mode_buttons[1].is_selected:
            color_label = self.text_font.render("Your Color:", True, BLACK)
            self.screen.blit(color_label, (320, 320))
            
            for button in self.color_buttons:
                button.draw(self.screen, self.button_font)
        
        # Start button
        self.start_button.draw(self.screen, self.button_font)
    
    def handle_menu_events(self, event):
        # Board size selection
        for i, button in enumerate(self.size_buttons):
            if button.handle_event(event):
                for b in self.size_buttons:
                    b.is_selected = False
                button.is_selected = True
                self.board_size = [4, 6, 8][i]
        
        # Game mode selection
        for i, button in enumerate(self.mode_buttons):
            if button.handle_event(event):
                for b in self.mode_buttons:
                    b.is_selected = False
                button.is_selected = True
                self.game_mode = ["pvp", "pva"][i]
        
        # Color selection
        if self.game_mode == "pva":
            for i, button in enumerate(self.color_buttons):
                if button.handle_event(event):
                    for b in self.color_buttons:
                        b.is_selected = False
                    button.is_selected = True
                    self.human_color = ["black", "white"][i]
        
        # Start button
        if self.start_button.handle_event(event):
            self.start_game()
    
    def start_game(self):
        self.board = OthelloBoard(self.board_size)
        self.state = "game"
        self.ai_thinking = False
        self.ai_timer = 0
        
        # Calculate board display parameters
        self.calculate_board_params()
    
    def calculate_board_params(self):
        """Calculate board drawing parameters based on board size"""
        max_board_size = 500
        self.cell_size = max_board_size // self.board_size
        self.board_pixel_size = self.cell_size * self.board_size
        self.board_offset_x = (800 - self.board_pixel_size) // 2
        self.board_offset_y = (600 - self.board_pixel_size) // 2 + 30
    
    def draw_game(self):
        self.screen.fill(WHITE)
        
        # Draw board
        board_rect = pygame.Rect(self.board_offset_x, self.board_offset_y, 
                                self.board_pixel_size, self.board_pixel_size)
        pygame.draw.rect(self.screen, GREEN, board_rect)
        
        # Draw grid
        for i in range(self.board_size + 1):
            # Vertical lines
            x = self.board_offset_x + i * self.cell_size
            pygame.draw.line(self.screen, BLACK, 
                           (x, self.board_offset_y), 
                           (x, self.board_offset_y + self.board_pixel_size), 2)
            # Horizontal lines
            y = self.board_offset_y + i * self.cell_size
            pygame.draw.line(self.screen, BLACK, 
                           (self.board_offset_x, y), 
                           (self.board_offset_x + self.board_pixel_size, y), 2)
        
        # Draw discs
        for row in range(self.board_size):
            for col in range(self.board_size):
                cell = self.board.get_cell(row, col)
                if cell is not None:
                    center_x = self.board_offset_x + col * self.cell_size + self.cell_size // 2
                    center_y = self.board_offset_y + row * self.cell_size + self.cell_size // 2
                    radius = self.cell_size // 2 - 5
                    
                    color = BLACK if cell == 'black' else WHITE
                    pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
                    pygame.draw.circle(self.screen, DARK_GRAY, (center_x, center_y), radius, 2)
        
        # Draw valid moves for current player
        if not self.ai_thinking:
            valid_moves = self.board.get_valid_moves(self.board.current_player)
            
            # Only show valid moves if it's human's turn in PvA mode
            show_hints = True
            if self.game_mode == "pva":
                show_hints = (self.board.current_player == self.human_color)
            
            if show_hints:
                for row, col in valid_moves:
                    center_x = self.board_offset_x + col * self.cell_size + self.cell_size // 2
                    center_y = self.board_offset_y + row * self.cell_size + self.cell_size // 2
                    radius = self.cell_size // 8
                    pygame.draw.circle(self.screen, GRAY, (center_x, center_y), radius)
        
        # Draw UI info
        self.draw_game_info()
    
    def draw_game_info(self):
        """Draw score and current player info"""
        black_score, white_score = self.board.get_score()
        
        # Current player
        player_text = f"Current Player: {self.board.current_player.capitalize()}"
        if self.game_mode == "pva" and self.board.current_player != self.human_color:
            player_text += " (AI)"
        player_surface = self.text_font.render(player_text, True, BLACK)
        self.screen.blit(player_surface, (20, 20))
        
        # Score
        score_text = f"Black: {black_score}  White: {white_score}"
        score_surface = self.text_font.render(score_text, True, BLACK)
        self.screen.blit(score_surface, (20, 560))
        
        # AI thinking indicator
        if self.ai_thinking:
            thinking_text = "AI is thinking..."
            thinking_surface = self.small_font.render(thinking_text, True, BLUE)
            self.screen.blit(thinking_surface, (650, 560))
    
    def handle_game_click(self, pos):
        """Handle mouse click on the game board"""
        x, y = pos
        
        # Check if click is on board
        if (self.board_offset_x <= x < self.board_offset_x + self.board_pixel_size and
            self.board_offset_y <= y < self.board_offset_y + self.board_pixel_size):
            
            # Calculate board position
            col = (x - self.board_offset_x) // self.cell_size
            row = (y - self.board_offset_y) // self.cell_size
            
            # Try to make move
            current_player = self.board.current_player
            
            # Only allow human moves
            if self.game_mode == "pva" and current_player != self.human_color:
                return
            
            if self.board.make_move(row, col, current_player):
                self.check_game_state()
    
    def check_game_state(self):
        """Check if game is over or if next player needs to pass"""
        if self.board.is_game_over():
            self.state = "game_over"
            return
        
        # Check if current player has no moves (must pass)
        if len(self.board.get_valid_moves(self.board.current_player)) == 0:
            # Pass turn
            opponent = 'white' if self.board.current_player == 'black' else 'black'
            self.board.current_player = opponent
            
            # Check again if game is over
            if self.board.is_game_over():
                self.state = "game_over"
    
    def update_ai(self, dt):
        """Update AI logic"""
        if self.game_mode != "pva":
            return
        
        if self.board.current_player != self.human_color and not self.ai_thinking:
            # Check if AI has valid moves
            if len(self.board.get_valid_moves(self.board.current_player)) == 0:
                # AI must pass
                self.board.current_player = self.human_color
                self.check_game_state()
                return
            
            # Start AI thinking
            self.ai_thinking = True
            self.ai_timer = 0
        
        if self.ai_thinking:
            self.ai_timer += dt
            if self.ai_timer >= self.ai_move_delay:
                # Make AI move
                ai_move = get_ai_move(self.board, self.board.current_player)
                if ai_move:
                    row, col = ai_move
                    self.board.make_move(row, col, self.board.current_player)
                    self.check_game_state()
                
                self.ai_thinking = False
                self.ai_timer = 0
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.draw_game()  # Draw the final board state
        
        # Semi-transparent overlay
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(200)
        overlay.fill(WHITE)
        self.screen.blit(overlay, (0, 0))
        
        # Winner text
        winner = self.board.get_winner()
        if winner == 'tie':
            winner_text = "It's a Tie!"
        else:
            winner_text = f"{winner.capitalize()} Wins!"
        
        winner_surface = self.title_font.render(winner_text, True, BLACK)
        winner_rect = winner_surface.get_rect(center=(400, 200))
        self.screen.blit(winner_surface, winner_rect)
        
        # Final score
        black_score, white_score = self.board.get_score()
        score_text = f"Final Score - Black: {black_score}  White: {white_score}"
        score_surface = self.text_font.render(score_text, True, BLACK)
        score_rect = score_surface.get_rect(center=(400, 280))
        self.screen.blit(score_surface, score_rect)
        
        # Buttons
        play_again_button = Button(250, 350, 150, 50, "Play Again", GREEN, LIGHT_GREEN)
        menu_button = Button(430, 350, 150, 50, "Main Menu", LIGHT_GRAY, GRAY)
        
        play_again_button.draw(self.screen, self.button_font)
        menu_button.draw(self.screen, self.button_font)
        
        return play_again_button, menu_button
    
    def run(self):
        """Main game loop"""
        play_again_button = None
        menu_button = None
        
        while True:
            dt = self.clock.tick(60)  # 60 FPS
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.state == "menu":
                    self.handle_menu_events(event)
                
                elif self.state == "game":
                    if event.type == pygame.MOUSEBUTTONDOWN and not self.ai_thinking:
                        self.handle_game_click(event.pos)
                
                elif self.state == "game_over":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if play_again_button and play_again_button.rect.collidepoint(event.pos):
                            self.start_game()
                        elif menu_button and menu_button.rect.collidepoint(event.pos):
                            self.state = "menu"
                    
                    # Handle hover for game over buttons
                    if event.type == pygame.MOUSEMOTION:
                        if play_again_button:
                            play_again_button.is_hovered = play_again_button.rect.collidepoint(event.pos)
                        if menu_button:
                            menu_button.is_hovered = menu_button.rect.collidepoint(event.pos)
            
            # Update
            if self.state == "game":
                self.update_ai(dt)
            
            # Draw
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "game_over":
                play_again_button, menu_button = self.draw_game_over()
            
            pygame.display.flip()

if __name__ == "__main__":
    game = OthelloGUI()
    game.run()