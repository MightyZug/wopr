import pygame
from typing import Optional
from config import WINDOW_WIDTH, WINDOW_HEIGHT


class LoadingScreen:
    def __init__(self):
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.background_colour = (0, 0, 0)  
        self.text_colour = (0, 255, 0)  
        
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
        
        self.current_line = 0
        self.current_char = 0
        self.last_char_time = 0
        self.char_delay = 50 
        self.line_delay = 200  
        self.loading_complete = False
        
        self.user_input = ""
        self.input_prompt = "PLEASE SELECT A GAME: "
        self.show_input = False
        self.error_message = ""
        self.error_time = 0
        
        self.showing_games = True
        self.waiting_for_input = False
        
    def update(self) -> Optional[str]:
        current_time = pygame.time.get_ticks()
        
        if self.showing_games and not self.loading_complete:
            if current_time - self.last_char_time > self.char_delay:
                if self.current_line < len(self.games):
                    current_game = self.games[self.current_line]
                    if self.current_char < len(current_game):
                        self.current_char += 1
                        self.last_char_time = current_time
                    else:
                        self.current_line += 1
                        self.current_char = 0
                        self.last_char_time = current_time + self.line_delay
                else:
                    self.loading_complete = True
                    self.show_input = True
                    self.waiting_for_input = True
        
        if self.error_message and current_time - self.error_time > 3000:
            self.error_message = ""
            
        return None
    
    def handle_keypress(self, key: int, unicode_char: str) -> Optional[str]:
        if not self.waiting_for_input:
            return None
            
        if key == pygame.K_RETURN:
            user_game = self.user_input.upper().strip()
            if user_game == "GLOBAL THERMONUCLEAR WAR":
                return "start_game"
            elif user_game in [game.upper() for game in self.games if game]:
                self.error_message = f"UNABLE TO FIND PROGRAM: {user_game}"
                self.error_time = pygame.time.get_ticks()
                self.user_input = ""
            else:
                self.error_message = "INVALID SELECTION"
                self.error_time = pygame.time.get_ticks()
                self.user_input = ""
                
        elif key == pygame.K_BACKSPACE:
            if self.user_input:
                self.user_input = self.user_input[:-1]
                
        elif unicode_char and unicode_char.isprintable():
            self.user_input += unicode_char.upper()
            
        return None
    
    def draw(self, screen: pygame.Surface):
        screen.fill(self.background_colour)
        
        title = "W.O.P.R."
        title_surface = self.font.render(title, True, self.text_colour)
        screen.blit(title_surface, (50, 30))
        
        subtitle = "WAR OPERATION PLAN RESPONSE"
        subtitle_surface = self.small_font.render(subtitle, True, self.text_colour)
        screen.blit(subtitle_surface, (50, 60))
        
        pygame.draw.line(screen, self.text_colour, (50, 90), (WINDOW_WIDTH - 50, 90), 1)
        
        y_pos = 120
        for i in range(min(self.current_line + 1, len(self.games))):
            game = self.games[i]
            if i == self.current_line:
                displayed_text = game[:self.current_char]
            else:
                displayed_text = game
                
            if displayed_text:
                game_surface = self.font.render(displayed_text, True, self.text_colour)
                screen.blit(game_surface, (80, y_pos))
            y_pos += 30
        
        if self.show_input:
            input_y = y_pos + 30
            prompt_surface = self.font.render(self.input_prompt, True, self.text_colour)
            screen.blit(prompt_surface, (50, input_y))
            
            input_surface = self.font.render(self.user_input, True, self.text_colour)
            screen.blit(input_surface, (50 + prompt_surface.get_width(), input_y))
            
            if pygame.time.get_ticks() % 1000 < 500:  
                cursor_x = 50 + prompt_surface.get_width() + input_surface.get_width()
                cursor_rect = pygame.Rect(cursor_x, input_y, 12, 24) 
                pygame.draw.rect(screen, self.text_colour, cursor_rect)
        
        if self.error_message:
            error_y = WINDOW_HEIGHT - 100
            error_surface = self.font.render(self.error_message, True, (255, 100, 100)) 
            screen.blit(error_surface, (50, error_y))
            
        if self.waiting_for_input:
            instruction = "TYPE GAME NAME AND PRESS ENTER"
            instruction_surface = self.small_font.render(instruction, True, self.text_colour)
            screen.blit(instruction_surface, (50, WINDOW_HEIGHT - 50))
