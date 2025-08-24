"""Game state management for WarGames simulation."""

import random
from typing import Set, List, Dict, Any
from config import GameState, DEFENSE_LIMIT, TARGET_LIMIT
from city_data import USA_CITIES, USSR_CITIES


class GameStateManager:
    """Manages the current state of the game and all game data."""
    
    def __init__(self):
        self.current_state = GameState.LOADING
        self.player_defenses: Set[int] = set()
        self.player_targets: Set[int] = set()
        self.ai_defenses: Set[int] = set()
        self.ai_targets: Set[int] = set()
        self.usa_destroyed: List[bool] = [False] * len(USA_CITIES)
        self.ussr_destroyed: List[bool] = [False] * len(USSR_CITIES)
        self.us_cities_destroyed: List[str] = []
        self.ussr_cities_destroyed: List[str] = []
        self.missile_lines: List[Dict[str, Any]] = []
        self.missile_animation_start_time = 0
        self.mushroom_clouds: List[Dict[str, Any]] = []
        self.show_grid = False
        self.show_help = False
    
    def start_new_game(self):
        """Initialize a new game session."""
        self.player_defenses = set()
        self.player_targets = set()
        self.ai_defenses = set()  # AI selections happen only at launch
        self.ai_targets = set()   # AI selections happen only at launch
        self.usa_destroyed = [False] * len(USA_CITIES)
        self.ussr_destroyed = [False] * len(USSR_CITIES)
        self.us_cities_destroyed = []
        self.ussr_cities_destroyed = []
        self.missile_lines = []
        self.mushroom_clouds = []
        self.current_state = GameState.DEFENSIVE
    
    def reset_to_menu(self):
        """Reset everything and return to menu state."""
        self.player_defenses = set()
        self.player_targets = set()
        self.ai_defenses = set()
        self.ai_targets = set()
        self.usa_destroyed = [False] * len(USA_CITIES)
        self.ussr_destroyed = [False] * len(USSR_CITIES)
        self.us_cities_destroyed = []
        self.ussr_cities_destroyed = []
        self.missile_lines = []
        self.mushroom_clouds = []
        self.current_state = GameState.MENU
    
    def reset_game(self):
        """Reset to menu state."""
        self.reset_to_menu()
    
    def toggle_defense(self, city_index: int) -> bool:
        """Toggle defense selection for a US city. Returns True if successful."""
        if city_index in self.player_defenses:
            self.player_defenses.remove(city_index)
            return True
        elif len(self.player_defenses) < DEFENSE_LIMIT:
            self.player_defenses.add(city_index)
            return True
        return False
    
    def toggle_target(self, city_index: int) -> bool:
        """Toggle target selection for a USSR city. Returns True if successful."""
        if city_index in self.player_targets:
            self.player_targets.remove(city_index)
            return True
        elif len(self.player_targets) < TARGET_LIMIT:
            self.player_targets.add(city_index)
            return True
        return False
    
    def can_continue_to_offensive(self) -> bool:
        """Check if player can continue to offensive phase."""
        return len(self.player_defenses) == DEFENSE_LIMIT
    
    def can_launch_missiles(self) -> bool:
        """Check if player can launch missiles."""
        return (len(self.player_defenses) == DEFENSE_LIMIT and 
                len(self.player_targets) == TARGET_LIMIT)
    
    def make_ai_selections(self):
        """Make AI selections for defense and attack when launching missiles."""
        self.ai_defenses = set(random.sample(range(len(USSR_CITIES)), DEFENSE_LIMIT))
        self.ai_targets = set(random.sample(range(len(USA_CITIES)), TARGET_LIMIT))
    
    def toggle_grid(self):
        """Toggle grid display for development."""
        self.show_grid = not self.show_grid
    
    def toggle_help(self):
        """Toggle help display."""
        self.show_help = not self.show_help
    
    def calculate_casualties(self) -> tuple:
        """Calculate casualties for both sides."""
        us_casualties = sum(USA_CITIES[idx]["population"] 
                           for idx in range(len(USA_CITIES)) 
                           if self.usa_destroyed[idx])
        
        ussr_casualties = sum(USSR_CITIES[idx]["population"] 
                               for idx in range(len(USSR_CITIES)) 
                               if self.ussr_destroyed[idx])
        
        total_us_population = sum(city["population"] for city in USA_CITIES)
        total_ussr_population = sum(city["population"] for city in USSR_CITIES)
        
        us_casualty_percent = (us_casualties / total_us_population) * 100 if total_us_population > 0 else 0
        ussr_casualty_percent = (ussr_casualties / total_ussr_population) * 100 if total_ussr_population > 0 else 0
        
        return (us_casualties, ussr_casualties, total_us_population, 
                total_ussr_population, us_casualty_percent, ussr_casualty_percent)
