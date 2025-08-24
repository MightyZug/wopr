"""
WarGames Nuclear War Simulation Game
"""

import pygame
import sys

from config import WINDOW_WIDTH, WINDOW_HEIGHT, GameState, DEFENSE_LIMIT, TARGET_LIMIT, GAME_TITLE
from city_data import USA_CITIES, USSR_CITIES
from game_state import GameStateManager
from ui import UI, get_clicked_city
from missiles import MissileSystem
from loading_screen import LoadingScreen

pygame.init()


class WarGame:
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        self.game_state = GameStateManager()
        self.ui = UI()
        self.missile_system = MissileSystem()
        self.loading_screen = LoadingScreen()
        
        try:
            self.background = pygame.image.load('neon_map.png').convert()
            self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except pygame.error:
            self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            for y in range(WINDOW_HEIGHT):
                colour_value = int(20 + (y / WINDOW_HEIGHT) * 40)
                pygame.draw.line(self.background, (0, 0, colour_value), (0, y), (WINDOW_WIDTH, y))
        
        self.running = True
        self.last_time = pygame.time.get_ticks()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.game_state.current_state == GameState.LOADING:
                    result = self.loading_screen.handle_keypress(event.key, event.unicode)
                    if result == "start_game":
                        self.game_state.current_state = GameState.MENU
                elif event.key == pygame.K_g:
                    self.game_state.toggle_grid()
                elif event.key == pygame.K_h:
                    self.game_state.toggle_help()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  
                    self._handle_mouse_click(event.pos)
    
    def _handle_mouse_click(self, mouse_pos: tuple):
        if self.game_state.current_state == GameState.LOADING:
            return
            
        if (self.game_state.current_state != GameState.MENU and 
            self.ui.reset_button.is_clicked(mouse_pos)):
            self.game_state.reset_to_menu()
            return
        
        if self.game_state.current_state == GameState.MENU:
            if self.ui.begin_button.is_clicked(mouse_pos):
                self.game_state.start_new_game()
            elif self.ui.exit_button.is_clicked(mouse_pos):
                self.running = False
        
        elif self.game_state.current_state == GameState.DEFENSIVE:
            city_idx = get_clicked_city(mouse_pos, USA_CITIES)
            if city_idx != -1:
                self.game_state.toggle_defense(city_idx)
            
            elif (self.game_state.can_continue_to_offensive() and 
                  self.ui.continue_button.is_clicked(mouse_pos)):
                self.game_state.current_state = GameState.OFFENSIVE
        
        elif self.game_state.current_state == GameState.OFFENSIVE:
            city_idx = get_clicked_city(mouse_pos, USSR_CITIES)
            if city_idx != -1:
                self.game_state.toggle_target(city_idx)
            
            elif (self.game_state.can_launch_missiles() and 
                  self.ui.launch_button.is_clicked(mouse_pos)):
                self._start_missile_launch()
        
        elif self.game_state.current_state == GameState.RESULTS:
            if self.ui.close_button.is_clicked(mouse_pos):
                self.game_state.reset_to_menu()
    
    def _start_missile_launch(self):
        self.game_state.make_ai_selections()
        
        self.game_state.current_state = GameState.LAUNCHING
        self.missile_system.create_missile_lines(
            self.game_state.player_targets, 
            self.game_state.ai_targets,
            self.game_state.player_defenses,
            self.game_state.ai_defenses
        )
    
    def update(self):
        current_time = pygame.time.get_ticks()
        self.last_time = current_time
        
        if self.game_state.current_state == GameState.LOADING:
            self.loading_screen.update()
            
        elif self.game_state.current_state == GameState.LAUNCHING:
            animation_complete = self.missile_system.update_missiles()
            
            intercepted = self.missile_system.check_intercepts(
                self.game_state.player_defenses,
                self.game_state.ai_defenses
            )
            
            self.missile_system.create_explosions(
                intercepted,
                self.game_state.usa_destroyed,
                self.game_state.ussr_destroyed,
                self.game_state.us_cities_destroyed,
                self.game_state.ussr_cities_destroyed
            )
            
            self.missile_system.update_mushroom_clouds()
            
            if animation_complete:
                self.game_state.current_state = GameState.RESULTS
        
        elif self.game_state.current_state == GameState.RESULTS:
            self.missile_system.update_mushroom_clouds()
    
    def render(self):
        if self.game_state.current_state == GameState.LOADING:
            self.loading_screen.draw(self.screen)
            pygame.display.flip()
            return
            
        self.screen.blit(self.background, (0, 0))
        
        if self.game_state.show_grid:
            self.ui.draw_grid(self.screen)
        
        if self.game_state.current_state == GameState.MENU:
            self._render_menu()
        
        elif self.game_state.current_state == GameState.DEFENSIVE:
            self._render_defensive_phase()
        
        elif self.game_state.current_state == GameState.OFFENSIVE:
            self._render_offensive_phase()
        
        elif self.game_state.current_state == GameState.LAUNCHING:
            self._render_missile_launch()
        
        elif self.game_state.current_state == GameState.RESULTS:
            self._render_results()
        
        pygame.display.flip()
    
    def _render_menu(self):
        self.ui.draw_title(self.screen)
        self.ui.begin_button.draw(self.screen)
        self.ui.exit_button.draw(self.screen)
        
        self.ui.draw_help_prompt(self.screen)
        
        if self.game_state.show_help:
            self.ui.draw_comprehensive_help(self.screen)
    
    def _render_defensive_phase(self):
        self.ui.draw_title(self.screen)
        
        instruction_lines = [
            "DEFENSIVE PHASE",
            "",
            "Click on US cities to place defenses",
            f"Defenses Selected: {len(self.game_state.player_defenses)}/{DEFENSE_LIMIT}"
        ]
        
        self.ui.draw_windowed_text(self.screen, instruction_lines)
        
        self.ui.draw_help_prompt(self.screen)
        
        self.ui.reset_button.draw(self.screen)
        
        self.ui.city_renderer.draw_usa_cities(
            self.screen,
            self.game_state.usa_destroyed,
            self.game_state.player_defenses,
            set(),  
            self.game_state.player_defenses
        )
        
        if self.game_state.show_help:
            self.ui.draw_comprehensive_help(self.screen)
        
        if self.game_state.can_continue_to_offensive():
            self.ui.continue_button.draw(self.screen)
    
    def _render_offensive_phase(self):
        self.ui.draw_title(self.screen)
        
        instruction_lines = [
            "OFFENSIVE PHASE",
            "",
            "Click on USSR cities to target",
            f"Targets Selected: {len(self.game_state.player_targets)}/{TARGET_LIMIT}"
        ]
        
        self.ui.draw_windowed_text(self.screen, instruction_lines)
        
        self.ui.draw_help_prompt(self.screen)
        
        self.ui.reset_button.draw(self.screen)
        
        self.ui.city_renderer.draw_ussr_cities(
            self.screen,
            self.game_state.ussr_destroyed,
            set(),  
            self.game_state.player_targets
        )
        
        if self.game_state.show_help:
            self.ui.draw_comprehensive_help(self.screen)
        
        if self.game_state.can_launch_missiles():
            self.ui.launch_button.draw(self.screen)
    
    def _render_missile_launch(self):
        self.ui.draw_title(self.screen)
        
        status_lines = [
            "MISSILE LAUNCH IN PROGRESS",
            "",
            "Nuclear weapons deployed..."
        ]
        
        self.ui.draw_windowed_text(self.screen, status_lines)
        
        self.ui.draw_help_prompt(self.screen)
        
        if self.game_state.show_help:
            self.ui.draw_comprehensive_help(self.screen)
        
        self.ui.reset_button.draw(self.screen)
        
        self.ui.city_renderer.draw_usa_cities(
            self.screen,
            self.game_state.usa_destroyed,
            self.game_state.player_defenses,
            self.game_state.ai_targets, 
            set()
        )
        
        self.ui.city_renderer.draw_ussr_cities(
            self.screen,
            self.game_state.ussr_destroyed,
            self.game_state.ai_defenses, 
            set()
        )
        
        self.missile_system.draw_missiles(self.screen)
        self.missile_system.draw_mushroom_clouds(self.screen)
    
    def _render_results(self):
        self.ui.draw_title(self.screen)
        
        self.ui.city_renderer.draw_usa_cities(
            self.screen,
            self.game_state.usa_destroyed,
            self.game_state.player_defenses,
            self.game_state.ai_targets,  
            set()
        )
        
        self.ui.city_renderer.draw_ussr_cities(
            self.screen,
            self.game_state.ussr_destroyed,
            self.game_state.ai_defenses, 
            set()
        )
        
        self.missile_system.draw_mushroom_clouds(self.screen)
        
        casualties = self.game_state.calculate_casualties()
        self.ui.draw_results(
            self.screen,
            casualties[0], casualties[1], casualties[2], casualties[3],
            casualties[4], casualties[5],
            self.game_state.us_cities_destroyed,
            self.game_state.ussr_cities_destroyed
        )
        
        self.ui.draw_help_prompt(self.screen)
        
        if self.game_state.show_help:
            self.ui.draw_comprehensive_help(self.screen)
        
        self.ui.close_button.draw(self.screen)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    game = WarGame()
    game.run()


if __name__ == "__main__":
    main()
