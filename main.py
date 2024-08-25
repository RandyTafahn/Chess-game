#this code require some libraries such as python-chess, and pygame
#the libraries are included in venv in this case

import chess
import chess.engine
import pygame
import os
import random

class ChessGame:
    def __init__(self):
        # Initialize the chess board and engine
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci("C:/Users/user/Documents/chess_game/stockfish/stockfish-windows-x86-64-avx2.exe")
        self.difficulty = "random_novice"  # Default difficulty
        
        # Pygame setup
        pygame.init()
        self.square_size = 80
        self.width = self.height = 8 * self.square_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess Game")
        self.load_pieces()

        # Additional attributes
        self.selected_square = None
        self.player_color = chess.WHITE
        self.font = pygame.font.Font(None, 24)
        self.state = "menu"  # Game state: menu or playing
        self.message = None
        self.message_time = 0
        self.message_duration = 0

        # Move history for undo/redo functionality
        self.move_history = []
        self.redo_stack = []

        # UI elements
        self.button_color = pygame.Color(70, 130, 180)  # Steel Blue
        self.button_hover_color = pygame.Color(100, 149, 237)  # Cornflower Blue
        self.background_color = pygame.Color(240, 248, 255)  # Alice Blue

        # Difficulties
        self.difficulties = [
            "Random Novice", "Uncertain Beginner", "Casual Player",
            "Learning Strategist", "Emerging Player", "Intermediate Thinker",
            "Tactical Ponderer", "Strategic Player", "Advanced Planner",
            "Perfect Strategist"
        ]
        self.current_difficulty_index = 0  # Default to "Random Novice"

    def __del__(self):
        self.engine.quit()
        pygame.quit()

    def load_pieces(self):
        self.pieces = {}
        for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
            img = pygame.image.load(f"pieces/{piece}.png")
            self.pieces[piece] = pygame.transform.scale(img, (self.square_size, self.square_size))
            img = pygame.image.load(f"pieces/w{piece}.png")
            self.pieces[piece.upper()] = pygame.transform.scale(img, (self.square_size, self.square_size))

    def draw_menu(self):
        self.screen.fill(self.background_color)
        
        # Draw a decorative chess board pattern in the background
        pattern_size = 40
        for row in range(0, self.height, pattern_size):
            for col in range(0, self.width, pattern_size):
                color = pygame.Color(220, 220, 220) if (row // pattern_size + col // pattern_size) % 2 == 0 else pygame.Color(200, 200, 200)
                pygame.draw.rect(self.screen, color, (col, row, pattern_size, pattern_size))

        title_font = pygame.font.Font(None, 72)
        title = title_font.render("Chess Game", True, pygame.Color("black"))
        title_shadow = title_font.render("Chess Game", True, pygame.Color(100, 100, 100))
        self.screen.blit(title_shadow, (self.width // 2 - title.get_width() // 2 + 2, 52))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        button_width = 300
        button_height = 50
        button_spacing = 20
        start_y = self.height // 2 - (3 * button_height + 2 * button_spacing) // 2

        # Difficulty selector
        difficulty_button = pygame.Rect(self.width // 2 - button_width // 2, start_y, button_width, button_height)
        self.draw_button(difficulty_button, self.difficulties[self.current_difficulty_index])

        # Left arrow
        left_arrow = pygame.Rect(difficulty_button.left - 40, difficulty_button.centery - 15, 30, 30)
        pygame.draw.polygon(self.screen, self.button_color, 
                            [(left_arrow.right, left_arrow.top), (left_arrow.left, left_arrow.centery), (left_arrow.right, left_arrow.bottom)])

        # Right arrow
        right_arrow = pygame.Rect(difficulty_button.right + 10, difficulty_button.centery - 15, 30, 30)
        pygame.draw.polygon(self.screen, self.button_color, 
                            [(right_arrow.left, right_arrow.top), (right_arrow.right, right_arrow.centery), (right_arrow.left, right_arrow.bottom)])

        # Load Game button
        load_button = pygame.Rect(self.width // 2 - button_width // 2, start_y + button_height + button_spacing, button_width, button_height)
        self.draw_button(load_button, "Load Game")

        # Quit button
        quit_button = pygame.Rect(self.width // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height)
        self.draw_button(quit_button, "Quit")

        pygame.display.flip()

    def draw_button(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        color = self.button_hover_color if rect.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, pygame.Color("black"), rect, 2, border_radius=10)
        text_surf = self.font.render(text, True, pygame.Color("white"))
        self.screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))

    def handle_menu_click(self, pos):
        button_width = 300
        button_height = 50
        button_spacing = 20
        start_y = self.height // 2 - (3 * button_height + 2 * button_spacing) // 2

        difficulty_button = pygame.Rect(self.width // 2 - button_width // 2, start_y, button_width, button_height)
        load_button = pygame.Rect(self.width // 2 - button_width // 2, start_y + button_height + button_spacing, button_width, button_height)
        quit_button = pygame.Rect(self.width // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height)

        left_arrow = pygame.Rect(difficulty_button.left - 40, difficulty_button.centery - 15, 30, 30)
        right_arrow = pygame.Rect(difficulty_button.right + 10, difficulty_button.centery - 15, 30, 30)

        if difficulty_button.collidepoint(pos):
            self.start_game(self.difficulties[self.current_difficulty_index].lower().replace(" ", "_"))
        elif load_button.collidepoint(pos):
            self.load_game_menu()
        elif quit_button.collidepoint(pos):
            pygame.quit()
        elif left_arrow.collidepoint(pos):
            self.current_difficulty_index = (self.current_difficulty_index - 1) % len(self.difficulties)
        elif right_arrow.collidepoint(pos):
            self.current_difficulty_index = (self.current_difficulty_index + 1) % len(self.difficulties)

    def start_game(self, difficulty):
        self.difficulty = difficulty
        self.start_new_game()
        self.state = "playing"

    def load_game_menu(self):
        filename = input("Enter the filename to load: ")  # For simplicity, using console input
        self.load_game(filename)
        self.state = "playing"

    def draw_board(self):
        colors = [pygame.Color("white"), pygame.Color("gray")]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self.screen, color, pygame.Rect(col * self.square_size, row * self.square_size, self.square_size, self.square_size))
        
        # Highlight checks
        if self.board.is_check():
            king_square = self.board.king(self.player_color)
            x = chess.square_file(king_square) * self.square_size
            y = (7 - chess.square_rank(king_square)) * self.square_size
            pygame.draw.rect(self.screen, pygame.Color("red"), pygame.Rect(x, y, self.square_size, self.square_size), 3)

        # Draw board notations
        for i in range(8):
            # Draw file labels (a-h)
            label = self.font.render(chess.FILE_NAMES[i], True, pygame.Color("black"))
            self.screen.blit(label, (i * self.square_size + 5, self.height - 20))
            
            # Draw rank labels (1-8)
            label = self.font.render(str(8 - i), True, pygame.Color("black"))
            self.screen.blit(label, (5, i * self.square_size + 5))

    def draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                x = chess.square_file(square) * self.square_size
                y = (7 - chess.square_rank(square)) * self.square_size
                self.screen.blit(self.pieces[piece.symbol()], pygame.Rect(x, y, self.square_size, self.square_size))

    def highlight_legal_moves(self):
        if self.selected_square:
            for move in self.board.legal_moves:
                if move.from_square == self.selected_square:
                    x = chess.square_file(move.to_square) * self.square_size
                    y = (7 - chess.square_rank(move.to_square)) * self.square_size
                    pygame.draw.rect(self.screen, pygame.Color("lightblue"), pygame.Rect(x, y, self.square_size, self.square_size), 3)

    def make_move(self, move):
        if chess.Move.from_uci(move) in self.board.legal_moves:
            self.board.push_uci(move)
            self.move_history.append(chess.Move.from_uci(move))
            self.redo_stack.clear()  # Clear redo stack when a new move is made
            return True
        return False

    def get_bot_move(self):
        if self.is_game_over():
            return None
        
        randomness = {
            "random_novice": 1.0,
            "uncertain_beginner": 0.8,
            "casual_player": 0.6,
            "learning_strategist": 0.4,
            "emerging_player": 0.3,
            "intermediate_thinker": 0.2,
            "tactical_ponderer": 0.1,
            "strategic_player": 0.05,
            "advanced_planner": 0.02,
            "perfect_strategist": 0.0
        }

        if random.random() < randomness[self.difficulty]:
            return self.get_random_move()
        else:
            return self.get_best_move()

    def get_random_move(self):
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        return random.choice(legal_moves)

    def get_best_move(self):
        result = self.engine.play(self.board, chess.engine.Limit(time=1.0))
        return result.move

    def is_game_over(self):
        return self.board.is_game_over()

    def save_game(self, filename):
        with open(filename, 'w') as f:
            f.write(self.board.fen())
        print(f"Game saved to {filename}")
        self.show_message(f"Game saved to {filename}")

    def load_game(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                fen = f.read()
                self.board = chess.Board(fen)
            print(f"Game loaded from {filename}")
            self.show_message(f"Game loaded from {filename}")
        else:
            print(f"File {filename} not found.")
            self.show_message(f"File {filename} not found.")

    def start_new_game(self):
        self.board = chess.Board()
        self.selected_square = None
        self.player_color = chess.WHITE
        self.move_history.clear()
        self.redo_stack.clear()

    def handle_click(self, pos):
        col = pos[0] // self.square_size
        row = 7 - (pos[1] // self.square_size)
        square = chess.square(col, row)

        if self.selected_square is None:
            # Selecting a piece
            piece = self.board.piece_at(square)
            if piece and piece.color == self.player_color:
                self.selected_square = square
        else:
            # Moving a piece
            move = chess.Move(self.selected_square, square)
            
            # Check for pawn promotion
            if self.board.piece_at(self.selected_square).piece_type == chess.PAWN:
                if (self.player_color == chess.WHITE and row == 7) or (self.player_color == chess.BLACK and row == 0):
                    promotion_piece = self.get_promotion_choice()
                    move = chess.Move(self.selected_square, square, promotion=promotion_piece)
            
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                self.redo_stack.clear()
                self.player_color = not self.player_color  # Switch turns
                self.selected_square = None
                return True
            else:
                self.selected_square = None
        return False

    def get_promotion_choice(self):
        promotion_pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        piece_names = ["Queen", "Rook", "Bishop", "Knight"]
        
        # Create a surface for the promotion menu
        menu_height = 200
        menu_width = 200
        menu_surface = pygame.Surface((menu_width, menu_height))
        menu_surface.fill(pygame.Color("pink"))
        
        # Draw the options
        for i, name in enumerate(piece_names):
            text = self.font.render(name, True, pygame.Color("black"))
            text_rect = text.get_rect(center=(menu_width // 2, (i + 1) * menu_height // 5))
            menu_surface.blit(text, text_rect)
        
        # Display the menu
        menu_pos = ((self.width - menu_width) // 2, (self.height - menu_height) // 2)
        self.screen.blit(menu_surface, menu_pos)
        pygame.display.flip()
        
        # Wait for player choice
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    relative_pos = (mouse_pos[0] - menu_pos[0], mouse_pos[1] - menu_pos[1])
                    
                    if 0 <= relative_pos[0] < menu_width and 0 <= relative_pos[1] < menu_height:
                        choice = relative_pos[1] // (menu_height // 4)
                        return promotion_pieces[choice]
        
        # Default to Queen if something goes wrong
        return chess.QUEEN

    def show_message(self, message, duration=2000):
        self.message = message
        self.message_time = pygame.time.get_ticks()
        self.message_duration = duration

    def undo_move(self):
        if len(self.move_history) > 0:
            move = self.board.pop()
            self.move_history.pop()
            self.redo_stack.append(move)
            self.player_color = not self.player_color #switch turn

    def redo_move(self):
        if len(self.redo_stack) > 0:
            move = self.redo_stack.pop()
            self.board.push(move)
            self.move_history.append(move)
            self.player_color = not self.player_color

    def highlight_square(self, square):
        x = chess.square_file(square) * self.square_size
        y = (7 - chess.square_rank(square)) * self.square_size
        pygame.draw.rect(self.screen, pygame.Color("yellow"), pygame.Rect(x, y, self.square_size, self.square_size), 3)

    def draw_game_over(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 48)
        text = font.render("Game Over", True, pygame.Color("white"))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)
        
        result = self.board.result()
        result_text = font.render(f"Result: {result}", True, pygame.Color("white"))
        result_rect = result_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(result_text, result_rect)

    def play_game(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        if self.state == "menu":
                            self.handle_menu_click(event.pos)
                        elif self.state == "playing":
                            if self.handle_click(event.pos):
                                # Player made a move, now it's bot's turn
                                bot_move = self.get_bot_move()
                                if bot_move:
                                    self.board.push(bot_move)
                                    self.move_history.append(bot_move)
                                    self.redo_stack.clear()
                                    self.player_color = not self.player_color
                                if self.is_game_over():
                                    self.draw_game_over()
                                    pygame.display.flip()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.state = "menu"
                        elif self.state == "menu":
                            running = False
                    elif event.key == pygame.K_s:
                        self.save_game("saved_game.fen")
                    elif event.key == pygame.K_z:  # Undo move
                        self.undo_move()
                    elif event.key == pygame.K_y:  # Redo move
                        self.redo_move()

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.draw_board()
                self.draw_pieces()
                self.highlight_legal_moves()
                if self.selected_square:
                    self.highlight_square(self.selected_square)
                
                if self.is_game_over():
                    self.draw_game_over()
                
                if self.message and pygame.time.get_ticks() - self.message_time < self.message_duration:
                    font = pygame.font.Font(None, 36)
                    text = font.render(self.message, True, pygame.Color("white"))
                    text_rect = text.get_rect(center=(self.width // 2, self.height - 30))
                    self.screen.blit(text, text_rect)
                
                pygame.display.flip()

            clock.tick(60)

        self.engine.quit()
        pygame.quit()

# Usage
if __name__ == "__main__":
    game = ChessGame()
    game.play_game()