"""
Othello GUI using Pygame
Handles menu, game visualization, and user interaction
"""

import sys
from typing import Optional

import pygame
from players import RandomAIPlayer, MCTSPlayer

from board import OthelloBoard
from enums import PlayerType
import threading

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BLUE = (70, 130, 180)


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

        # Game & GUI state
        self.state = "menu"  # "menu", "game", "game_over"
        self.board: Optional[OthelloBoard] = None
        self.board_size = 8

        self.game_mode = "pvp"  # "pvp" or "pva"
        self.human_color: PlayerType = PlayerType.BLACK
        self.ai_color: Optional[PlayerType] = None
        self.ai_player: Optional[RandomAIPlayer] = None
        self.ai_type = "random"

        self.current_color: PlayerType = PlayerType.BLACK

        self.ai_thinking = False
        self.ai_move_delay = 500  # ms delay before AI moves
        self.ai_timer = 0

        # progress and thread
        self.ai_progress = 0.0     # 0.0–1.0 for progress bar
        self.ai_thread = None      # threading.Thread | None
        self.ai_done = False       # did the AI thread finish?
        self.ai_result_move = None # (row, col) or None

        # Board rendering parameters
        self.cell_size = 0
        self.board_pixel_size = 0
        self.board_offset_x = 0
        self.board_offset_y = 0

        # Menu buttons
        self.create_menu_buttons()

    # -------------------- Menu setup -------------------- #

    def create_menu_buttons(self):
        # Board size buttons
        self.size_buttons = [
            Button(250, 150, 80, 50, "4x4", LIGHT_GRAY, GRAY),
            Button(360, 150, 80, 50, "6x6", LIGHT_GRAY, GRAY),
            Button(470, 150, 80, 50, "8x8", LIGHT_GRAY, GRAY),
        ]
        self.size_buttons[2].is_selected = True  # 8x8 default

        # Game mode buttons
        self.mode_buttons = [
            Button(250, 250, 150, 50, "Player vs Player", LIGHT_GRAY, GRAY),
            Button(430, 250, 150, 50, "Player vs AI", LIGHT_GRAY, GRAY),
        ]
        self.mode_buttons[0].is_selected = True  # PvP default

        # Color selection buttons (only shown for PvA)
        self.color_buttons = [
            Button(250, 350, 120, 50, "Black", LIGHT_GRAY, GRAY),
            Button(400, 350, 120, 50, "White", LIGHT_GRAY, GRAY),
        ]
        self.color_buttons[0].is_selected = True  # Black default

        # AI type buttons
        self.ai_type_buttons = [
            Button(250, 420, 120, 50, "Random", LIGHT_GRAY, GRAY),
            Button(400, 420, 120, 50, "MCTS", LIGHT_GRAY, GRAY),
        ]
        self.ai_type_buttons[0].is_selected = True  # Random default

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
        if self.game_mode == "pva":
            color_label = self.text_font.render("Your Color:", True, BLACK)
            self.screen.blit(color_label, (320, 320))

            for button in self.color_buttons:
                button.draw(self.screen, self.button_font)

            ai_type_label = self.text_font.render("AI Type:", True, BLACK)
            self.screen.blit(ai_type_label, (320, 390))

            for button in self.ai_type_buttons:
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

        # Color selection (only if PvA)
        if self.game_mode == "pva":
            for i, button in enumerate(self.color_buttons):
                if button.handle_event(event):
                    for b in self.color_buttons:
                        b.is_selected = False
                    button.is_selected = True
                    self.human_color = [PlayerType.BLACK, PlayerType.WHITE][i]
                    
            for i, button in enumerate(self.ai_type_buttons):
                if button.handle_event(event):
                    for b in self.ai_type_buttons:
                        b.is_selected = False
                    button.is_selected = True
                    self.ai_type = ["random", "mcts"][i]

        # Start button
        if self.start_button.handle_event(event):
            self.start_game()

    # -------------------- Game setup -------------------- #

    def start_game(self):
        self.board = OthelloBoard(self.board_size)
        self.state = "game"
        self.ai_thinking = False
        self.ai_timer = 0

        # Black always starts
        self.current_color = PlayerType.BLACK

        # Setup AI player
        if self.game_mode == "pva":
            self.ai_color = self.human_color.opponent

            if self.ai_type == "random":
                self.ai_player = RandomAIPlayer(self.ai_color)

            elif self.ai_type == "mcts":
                # You can choose iterations based on user preferences
                self.ai_player = MCTSPlayer(self.ai_color, iterations=800)

        else:
            self.ai_color = None
            self.ai_player = None
            
        # Calculate board display parameters
        self.calculate_board_params()

    def calculate_board_params(self):
        """Calculate board drawing parameters based on board size"""
        max_board_size = 500
        self.cell_size = max_board_size // self.board_size
        self.board_pixel_size = self.cell_size * self.board_size
        self.board_offset_x = (800 - self.board_pixel_size) // 2
        self.board_offset_y = (600 - self.board_pixel_size) // 2 + 30

    # -------------------- Drawing -------------------- #

    def draw_game(self):
        self.screen.fill(WHITE)

        # Draw board background
        board_rect = pygame.Rect(
            self.board_offset_x,
            self.board_offset_y,
            self.board_pixel_size,
            self.board_pixel_size,
        )
        pygame.draw.rect(self.screen, GREEN, board_rect)

        # Draw grid
        for i in range(self.board_size + 1):
            # Vertical lines
            x = self.board_offset_x + i * self.cell_size
            pygame.draw.line(
                self.screen,
                BLACK,
                (x, self.board_offset_y),
                (x, self.board_offset_y + self.board_pixel_size),
                2,
            )
            # Horizontal lines
            y = self.board_offset_y + i * self.cell_size
            pygame.draw.line(
                self.screen,
                BLACK,
                (self.board_offset_x, y),
                (self.board_offset_x + self.board_pixel_size, y),
                2,
            )

        # Draw discs
        for row in range(self.board_size):
            for col in range(self.board_size):
                cell = self.board[row][col]
                if cell is not PlayerType.EMPTY:
                    center_x = self.board_offset_x + col * self.cell_size + self.cell_size // 2
                    center_y = self.board_offset_y + row * self.cell_size + self.cell_size // 2
                    radius = self.cell_size // 2 - 5

                    disc_color = BLACK if cell is PlayerType.BLACK else WHITE
                    pygame.draw.circle(self.screen, disc_color, (center_x, center_y), radius)
                    pygame.draw.circle(self.screen, DARK_GRAY, (center_x, center_y), radius, 2)

        # Draw valid moves (hints)
        if not self.ai_thinking:
            valid_moves = self.board.get_valid_moves(self.current_color)

            show_hints = True
            if self.game_mode == "pva":
                show_hints = (self.current_color == self.human_color)

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
        player_name = "Black" if self.current_color is PlayerType.BLACK else "White"
        player_text = f"Current Player: {player_name}"
        if self.game_mode == "pva" and self.current_color == self.ai_color:
            player_text += " (AI)"
        player_surface = self.text_font.render(player_text, True, BLACK)
        self.screen.blit(player_surface, (20, 20))

        # Score
        score_text = f"Black: {black_score}  White: {white_score}"
        score_surface = self.text_font.render(score_text, True, BLACK)
        self.screen.blit(score_surface, (20, 560))

        # AI thinking indicator + TRUE progress bar
        if self.ai_thinking:
            thinking_text = "AI is thinking..."
            thinking_surface = self.small_font.render(thinking_text, True, BLUE)
            self.screen.blit(thinking_surface, (600, 520))

            bar_x = 600
            bar_y = 545
            bar_width = 180
            bar_height = 15

            # Border
            pygame.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height), 2)

            # Fill based on ai_progress [0, 1]
            progress = max(0.0, min(self.ai_progress, 1.0))
            fill_width = int((bar_width - 4) * progress)

            if fill_width > 0:
                pygame.draw.rect(
                    self.screen,
                    BLUE,
                    (bar_x + 2, bar_y + 2, fill_width, bar_height - 4),
                )

    # -------------------- Input handling -------------------- #

    def handle_game_click(self, pos):
        """Handle mouse click on the game board"""
        x, y = pos

        # Check if click is on board
        if not (
            self.board_offset_x <= x < self.board_offset_x + self.board_pixel_size
            and self.board_offset_y <= y < self.board_offset_y + self.board_pixel_size
        ):
            return

        # Don't allow moves while AI is thinking
        if self.game_mode == "pva" and self.current_color == self.ai_color:
            return

        # Calculate board position
        col = (x - self.board_offset_x) // self.cell_size
        row = (y - self.board_offset_y) // self.cell_size

        # Attempt move for current player
        if self.board.make_move(row, col, self.current_color):
            self.on_move_made()

    def on_move_made(self):
        """Common logic after any move (human or AI) is made"""
        # Switch to opponent
        self.current_color = self.current_color.opponent
        self.check_game_state()

    def check_game_state(self):
        """Check if game is over or if next player needs to pass"""
        if self.board.is_game_over():
            self.state = "game_over"
            return

        # If current player has no moves, they must pass
        if not self.board.get_valid_moves(self.current_color):
            self.current_color = self.current_color.opponent
            # If opponent also has no moves, game over
            if not self.board.get_valid_moves(self.current_color):
                self.state = "game_over"

    def update_ai(self, dt):
        """Update AI logic (only in PvA mode, non-blocking with thread)."""
        if self.game_mode != "pva" or self.ai_player is None:
            return

        # If it's AI's turn
        if self.current_color == self.ai_color:
            # If not already thinking, start the background search
            if not self.ai_thinking:
                # Check if AI has any moves; if not, pass
                if not self.board.get_valid_moves(self.ai_color):
                    self.current_color = self.human_color
                    self.check_game_state()
                    return

                self.start_ai_thinking()

            else:
                # Already thinking: check if thread finished
                if self.ai_done:
                    move = self.ai_result_move
                    if move is not None:
                        row, col = move
                        if self.board.make_move(row, col, self.current_color):
                            self.on_move_made()

                    # Reset thread state
                    self.ai_thinking = False
                    self.ai_thread = None
                    self.ai_result_move = None
                    self.ai_done = False
                    self.ai_progress = 0.0


    def start_ai_thinking(self):
        """Start the AI search in a background thread (non-blocking)."""
        if self.ai_player is None:
            return

        # Mark thinking state
        self.ai_thinking = True
        self.ai_progress = 0.0
        self.ai_done = False
        self.ai_result_move = None

        # Work on a copy so the AI doesn't mutate the live board
        board_copy = self.board.copy()

        def progress_cb(done: int, total: int):
            # This is called from the AI thread; just update a float
            if total > 0:
                self.ai_progress = done / total
            else:
                self.ai_progress = 1.0

        def worker():
            move = self.ai_player.choose_move(board_copy, progress_callback=progress_cb)
            self.ai_result_move = move
            self.ai_done = True

        self.ai_thread = threading.Thread(target=worker, daemon=True)
        self.ai_thread.start()

    # -------------------- Game over screen -------------------- #

    def draw_game_over(self):
        """Draw game over screen"""
        self.draw_game()  # Draw final board state

        # Semi-transparent overlay
        overlay = pygame.Surface((800, 600))
        overlay.set_alpha(200)
        overlay.fill(WHITE)
        self.screen.blit(overlay, (0, 0))

        # Winner text
        black_score, white_score = self.board.get_score()
        if black_score > white_score:
            winner_text = "Black Wins!"
        elif white_score > black_score:
            winner_text = "White Wins!"
        else:
            winner_text = "It's a Tie!"

        winner_surface = self.title_font.render(winner_text, True, BLACK)
        winner_rect = winner_surface.get_rect(center=(400, 200))
        self.screen.blit(winner_surface, winner_rect)

        # Final score
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

    # -------------------- Main loop -------------------- #

    def run(self):
        """Main game loop"""
        play_again_button = None
        menu_button = None

        while True:
            dt = self.clock.tick(60)  # milliseconds per frame at ~60 FPS

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
    gui = OthelloGUI()
    gui.run()
