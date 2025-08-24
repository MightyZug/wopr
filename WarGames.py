"""
WarGames Nuclear War Simulation Game
Refactored version with clean code principles and separation of concerns.
"""

import pygame
import sys

# Import our modules
from config import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, GameState, DEFENSE_LIMIT, TARGET_LIMIT, GAME_TITLE
from city_data import USA_CITIES, RUSSIA_CITIES
from game_state import GameStateManager
from ui import UI, get_clicked_city
from missiles import MissileSystem

# Initialize Pygame
pygame.init()


class WarGame:
    """Main game class that orchestrates the WarGames simulation."""
    
    def __init__(self):
        """Initialize the game with all necessary components."""
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        
        # Game components
        self.game_state = GameStateManager()
        self.ui = UI()
        self.missile_system = MissileSystem()
        
        # Load background image
        try:
            self.background = pygame.image.load('neon_map.png').convert()
            self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except pygame.error:
            # Create a simple gradient background if image not found
            self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            for y in range(WINDOW_HEIGHT):
                color_value = int(20 + (y / WINDOW_HEIGHT) * 40)
                pygame.draw.line(self.background, (0, 0, color_value), (0, y), (WINDOW_WIDTH, y))
        
        self.running = True
        self.last_time = pygame.time.get_ticks()
    
    def handle_events(self):
        """Handle all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    self.game_state.toggle_grid()
                elif event.key == pygame.K_h:
                    self.game_state.toggle_help()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)
    
    def _handle_mouse_click(self, mouse_pos: tuple):
        """Handle mouse click events based on current game state."""
        # Check for reset button click (available in all states except menu)
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
            # Check for city clicks
            city_idx = get_clicked_city(mouse_pos, USA_CITIES)
            if city_idx != -1:
                self.game_state.toggle_defense(city_idx)
            
            # Check continue button
            elif (self.game_state.can_continue_to_offensive() and 
                  self.ui.continue_button.is_clicked(mouse_pos)):
                self.game_state.current_state = GameState.OFFENSIVE
        
        elif self.game_state.current_state == GameState.OFFENSIVE:
            # Check for city clicks
            city_idx = get_clicked_city(mouse_pos, RUSSIA_CITIES)
            if city_idx != -1:
                self.game_state.toggle_target(city_idx)
            
            # Check launch button
            elif (self.game_state.can_launch_missiles() and 
                  self.ui.launch_button.is_clicked(mouse_pos)):
                self._start_missile_launch()
        
        elif self.game_state.current_state == GameState.RESULTS:
            if self.ui.close_button.is_clicked(mouse_pos):
                self.game_state.reset_to_menu()
    
    def _start_missile_launch(self):
        """Initiate the missile launch sequence."""
        # Make AI selections at launch time
        self.game_state.make_ai_selections()
        
        self.game_state.current_state = GameState.MISSILE_LAUNCH
        self.missile_system.create_missile_lines(
            self.game_state.player_targets, 
            self.game_state.ai_targets,
            self.game_state.player_defenses,
            self.game_state.ai_defenses
        )
    
    def update(self):
        """Update game state and animations."""
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_time) / 1000.0  # Delta time in seconds
        self.last_time = current_time
        
        if self.game_state.current_state == GameState.MISSILE_LAUNCH:
            # Update missile animations
            animation_complete = self.missile_system.update_missiles(dt)
            
            # Check and launch intercepts at 50% progress
            self.missile_system.check_and_launch_intercepts(
                self.game_state.player_defenses,
                self.game_state.ai_defenses
            )
            
            # Check for intercepts
            intercepted = self.missile_system.check_intercepts(
                self.game_state.player_defenses,
                self.game_state.ai_defenses
            )
            
            # Create explosions for hits
            self.missile_system.create_explosions(
                intercepted,
                self.game_state.usa_destroyed,
                self.game_state.russia_destroyed,
                self.game_state.us_cities_destroyed,
                self.game_state.russian_cities_destroyed
            )
            
            # Update mushroom clouds
            self.missile_system.update_mushroom_clouds()
            
            # Check if animation is complete
            if animation_complete:
                self.game_state.current_state = GameState.RESULTS
        
        elif self.game_state.current_state == GameState.RESULTS:
            # Continue updating mushroom clouds in results
            self.missile_system.update_mushroom_clouds()
    
    def render(self):
        """Render the current game state."""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw grid if enabled
        if self.game_state.show_grid:
            self.ui.draw_grid(self.screen)
        
        # Render based on current state
        if self.game_state.current_state == GameState.MENU:
            self._render_menu()
        
        elif self.game_state.current_state == GameState.DEFENSIVE:
            self._render_defensive_phase()
        
        elif self.game_state.current_state == GameState.OFFENSIVE:
            self._render_offensive_phase()
        
        elif self.game_state.current_state == GameState.MISSILE_LAUNCH:
            self._render_missile_launch()
        
        elif self.game_state.current_state == GameState.RESULTS:
            self._render_results()
        
        pygame.display.flip()
    
    def _render_menu(self):
        """Render the main menu."""
        self.ui.draw_title(self.screen)
        self.ui.begin_button.draw(self.screen)
        self.ui.exit_button.draw(self.screen)
        
        # Always show help prompt at bottom
        self.ui.draw_help_prompt(self.screen)
        
        # Only show help window if toggled on
        if self.game_state.show_help:
            self.ui.draw_comprehensive_help(self.screen)
    
    def _render_defensive_phase(self):
        """Render the defensive selection phase."""
        # Draw title at top
        self.ui.draw_title(self.screen)
        
        # Create instruction text for windowed display
        instruction_lines = [
            "DEFENSIVE PHASE",
            "",
            "Click on US cities to place defenses",
            f"Defenses Selected: {len(self.game_state.player_defenses)}/{DEFENSE_LIMIT}"
        ]
        
        self.ui.draw_windowed_text(self.screen, instruction_lines)
        
        # Show help prompt
        self.ui.draw_help_prompt(self.screen)
        
        # Draw reset button
        self.ui.reset_button.draw(self.screen)
        
        # Draw cities
        self.ui.city_renderer.draw_usa_cities(
            self.screen,
            self.game_state.usa_destroyed,
            self.game_state.player_defenses,
            set(),  # Don't show AI targets in defensive phase - let cities start as default blue
            self.game_state.player_defenses
        )
        
        # Show help window if toggled on
        if self.game_state.show_help:
            self.ui.draw_comprehensive_help(self.screen)
        
        # Don't draw defense ranges during selection - only change dot color
        
      
        # Draw continue button if ready
        if self.game_state.can_continue_to_offensive():
            self.ui.continue_button.draw(self.screen)
    
    def _render_offensive_phase(self):
        """Render the offensive selection phase."""
        # Draw title at top
        self.ui.draw_title(self.screen)
        
        # Create instruction text for windowed display
        instruction_lines = [
            "OFFENSIVE PHASE",
            "",
            "Click on Russian cities to target",
            f"Targets Selected: {len(self.game_state.player_targets)}/{TARGET_LIMIT}"
        ]
        
        self.ui.draw_windowed_text(self.screen, instruction_lines)
        
        # Show help prompt
        self.ui.draw_help_prompt(self.screen)
        
        # Draw reset button
        self.ui.reset_button.draw(self.screen)
        
        # Draw cities
        self.ui.city_renderer.draw_russia_cities(
            self.screen,
            self.game_state.russia_destroyed,
            set(),  # Don't show AI defenses initially - let cities start as default red
            self.game_state.player_targets
        )
        
        # Show help window if toggled on
        if self.game_state.show_help:
            self.ui.draw_comprehensive_help(self.screen)
        
        # Don't draw AI defense ranges during selection - only show dot color changes
        
        # Draw launch button if ready
        if self.game_state.can_launch_missiles():
            self.ui.launch_button.draw(self.screen)
    
    def _render_missile_launch(self):
        """Render the missile launch animation."""
        # Draw title at top
        self.ui.draw_title(self.screen)
        
        # Create status text for windowed display
        status_lines = [
            "MISSILE LAUNCH IN PROGRESS",
            "",
            "Nuclear weapons deployed..."
        ]
        
        self.ui.draw_windowed_text(self.screen, status_lines)
        
        # Show help prompt
        self.ui.draw_help_prompt(self.screen)
        
        # Show help window if toggled on
        if self.game_state.show_help:
            self.ui.draw_comprehensive_help(self.screen)
        
        # Draw reset button
        self.ui.reset_button.draw(self.screen)
        
        # Draw all cities
        self.ui.city_renderer.draw_usa_cities(
            self.screen,
            self.game_state.usa_destroyed,
            self.game_state.player_defenses,
            self.game_state.ai_targets,  # Show AI targets during missile launch
            set()
        )
        
        self.ui.city_renderer.draw_russia_cities(
            self.screen,
            self.game_state.russia_destroyed,
            self.game_state.ai_defenses,  # Show AI defenses during missile launch
            set()
        )
        
        # Draw missiles and explosions
        self.missile_system.draw_missiles(self.screen)
        self.missile_system.draw_mushroom_clouds(self.screen)
    
    def _render_results(self):
        """Render the battle results."""
        # Draw title at top
        self.ui.draw_title(self.screen)
        
        # Draw all cities with final states
        self.ui.city_renderer.draw_usa_cities(
            self.screen,
            self.game_state.usa_destroyed,
            self.game_state.player_defenses,
            self.game_state.ai_targets,  # Show AI targets in results
            set()
        )
        
        self.ui.city_renderer.draw_russia_cities(
            self.screen,
            self.game_state.russia_destroyed,
            self.game_state.ai_defenses,  # Show AI defenses in results
            set()
        )
        
        # Draw remaining mushroom clouds
        self.missile_system.draw_mushroom_clouds(self.screen)
        
        # Draw casualty statistics in windowed format
        casualties = self.game_state.calculate_casualties()
        self.ui.draw_results(
            self.screen,
            casualties[0], casualties[1], casualties[2], casualties[3],
            casualties[4], casualties[5],
            self.game_state.us_cities_destroyed,
            self.game_state.russian_cities_destroyed
        )
        
        # Show help prompt
        self.ui.draw_help_prompt(self.screen)
        
        # Show help window if toggled on
        if self.game_state.show_help:
            self.ui.draw_comprehensive_help(self.screen)
        
        # Draw close button
        self.ui.close_button.draw(self.screen)
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the WarGames simulation."""
    game = WarGame()
    game.run()


if __name__ == "__main__":
    main()
