"""WOPR Loading Screen for WarGames simulation."""

import pygame
from typing import List, Optional
from config import COLOURS, WINDOW_WIDTH, WINDOW_HEIGHT


class LoadingScreen:
    """Handles the WOPR computer interface loading screen."""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.background_color = (0, 0, 0)  # Black background
        self.text_color = (0, 255, 0)  # Green text like old computers
        
        # Game options from the movie
        self.games = [
            "CHESS",
            "POKER", 
            "FIGHTER COMBAT",
            "GUERRILLA ENGAGEMENT",
            "DESERT WARFARE",
            "AIR-TO-GROUND ACTIONS",
            "THEATERWIDE TACTICAL WARFARE",
            "THEATERWIDE BIOTOXIC AND CHEMICAL WARFARE",
            "",
            "GLOBAL THERMONUCLEAR WAR"
        ]
        
        # Animation state
        self.current_line = 0
        self.current_char = 0
        self.last_char_time = 0
        self.char_delay = 50  # milliseconds between characters
        self.line_delay = 200  # milliseconds between lines
        self.loading_complete = False
        
        # User input
        self.user_input = ""
        self.input_prompt = "PLEASE SELECT A GAME: "
        self.show_input = False
        self.error_message = ""
        self.error_time = 0
        
        # State management
        self.showing_games = True
        self.waiting_for_input = False
        
    def update(self) -> Optional[str]:
        """Update the loading screen animation. Returns 'start_game' when ready."""
        current_time = pygame.time.get_ticks()
        
        if self.showing_games and not self.loading_complete:
            # Animate text appearing character by character
            if current_time - self.last_char_time > self.char_delay:
                if self.current_line < len(self.games):
                    current_game = self.games[self.current_line]
                    if self.current_char < len(current_game):
                        self.current_char += 1
                        self.last_char_time = current_time
                    else:
                        # Move to next line
                        self.current_line += 1
                        self.current_char = 0
                        self.last_char_time = current_time + self.line_delay
                else:
                    # All games displayed
                    self.loading_complete = True
                    self.show_input = True
                    self.waiting_for_input = True
        
        # Clear error message after 3 seconds
        if self.error_message and current_time - self.error_time > 3000:
            self.error_message = ""
            
        return None
    
    def handle_keypress(self, key: int, unicode_char: str) -> Optional[str]:
        """Handle keyboard input for game selection."""
        if not self.waiting_for_input:
            return None
            
        if key == pygame.K_RETURN:
            # Check if input matches valid game
            user_game = self.user_input.upper().strip()
            if user_game == "GLOBAL THERMONUCLEAR WAR":
                return "start_game"
            elif user_game in [game.upper() for game in self.games if game]:
                # Valid game but not available
                self.error_message = f"UNABLE TO FIND PROGRAM: {user_game}"
                self.error_time = pygame.time.get_ticks()
                self.user_input = ""
            else:
                # Invalid input
                self.error_message = "INVALID SELECTION"
                self.error_time = pygame.time.get_ticks()
                self.user_input = ""
                
        elif key == pygame.K_BACKSPACE:
            if self.user_input:
                self.user_input = self.user_input[:-1]
                
        elif unicode_char and unicode_char.isprintable():
            # Add character to input (automatically convert to uppercase)
            self.user_input += unicode_char.upper()
            
        return None
    
    def draw(self, screen: pygame.Surface):
        """Draw the loading screen."""
        screen.fill(self.background_color)
        
        # Draw title
        title = "W.O.P.R."
        title_surface = self.font.render(title, True, self.text_color)
        screen.blit(title_surface, (50, 30))
        
        # Draw subtitle
        subtitle = "WAR OPERATION PLAN RESPONSE"
        subtitle_surface = self.small_font.render(subtitle, True, self.text_color)
        screen.blit(subtitle_surface, (50, 60))
        
        # Draw separator line
        pygame.draw.line(screen, self.text_color, (50, 90), (WINDOW_WIDTH - 50, 90), 1)
        
        # Draw games list with animation
        y_pos = 120
        for i in range(min(self.current_line + 1, len(self.games))):
            game = self.games[i]
            if i == self.current_line:
                # Current line being typed
                displayed_text = game[:self.current_char]
            else:
                # Fully displayed line
                displayed_text = game
                
            if displayed_text:  # Don't render empty lines
                game_surface = self.font.render(displayed_text, True, self.text_color)
                screen.blit(game_surface, (80, y_pos))
            y_pos += 30
        
        # Draw input prompt and user input
        if self.show_input:
            input_y = y_pos + 30
            prompt_surface = self.font.render(self.input_prompt, True, self.text_color)
            screen.blit(prompt_surface, (50, input_y))
            
            # Draw user input
            input_surface = self.font.render(self.user_input, True, self.text_color)
            screen.blit(input_surface, (50 + prompt_surface.get_width(), input_y))
            
            # Draw cursor following the text (blinking block cursor)
            if pygame.time.get_ticks() % 1000 < 500:  # Blink every 500ms
                cursor_x = 50 + prompt_surface.get_width() + input_surface.get_width()
                # Draw a block cursor instead of underscore for more authentic terminal look
                cursor_rect = pygame.Rect(cursor_x, input_y, 12, 24)  # Block cursor
                pygame.draw.rect(screen, self.text_color, cursor_rect)
        
        # Draw error message
        if self.error_message:
            error_y = WINDOW_HEIGHT - 100
            error_surface = self.font.render(self.error_message, True, (255, 100, 100))  # Red error text
            screen.blit(error_surface, (50, error_y))
            
        # Draw instructions at bottom
        if self.waiting_for_input:
            instruction = "TYPE GAME NAME AND PRESS ENTER"
            instruction_surface = self.small_font.render(instruction, True, self.text_color)
            screen.blit(instruction_surface, (50, WINDOW_HEIGHT - 50))
