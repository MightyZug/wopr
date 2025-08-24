"""UI components for WarGames simulation."""

import pygame
import math
from typing import Set, List
from config import (COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, CITY_RADIUS, 
                   SELECTED_COLOR, TARGETED_COLOR, DEFENDED_COLOR, HIT_COLOR, GAME_TITLE)
from city_data import USA_CITIES, RUSSIA_CITIES


class Button:
    """A simple button class for UI elements - styled like original WarGames."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: tuple = COLORS["green"], text_color: tuple = COLORS["green"]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 24)
        self.enabled = True
    
    def draw(self, screen: pygame.Surface):
        """Draw the button in original WarGames style."""
        # Get mouse position for hover effect
        mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse)
        
        # Use green color like original
        color = COLORS["green"] if self.enabled else (60, 60, 60)
        
        # Draw outer border with rounded corners
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        
        # Draw inner black rectangle
        inner_rect = self.rect.inflate(-6, -6)
        pygame.draw.rect(screen, COLORS["black"], inner_rect, border_radius=6)
        
        # Draw text
        text_color = COLORS["green"] if self.enabled else (100, 100, 100)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, mouse_pos: tuple) -> bool:
        """Check if the button was clicked."""
        return self.enabled and self.rect.collidepoint(mouse_pos)


class CityRenderer:
    """Handles rendering of cities and their states."""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 18)
    
    def _get_city_color(self, is_destroyed: bool, is_defended: bool, 
                       is_selected: bool, is_targeted: bool, is_us_city: bool = True) -> tuple:
        """Determine the color for a city based on its state."""
        if is_destroyed:
            return HIT_COLOR
        elif is_selected:
            return SELECTED_COLOR
        elif is_defended:
            return DEFENDED_COLOR
        elif is_targeted:
            return TARGETED_COLOR
        else:
            # Default city colors: blue for US, red for Russia
            return COLORS["blue"] if is_us_city else COLORS["red"]
    
    def draw_city(self, screen: pygame.Surface, city: dict, color: tuple, 
                  is_destroyed: bool = False, is_defended: bool = False, 
                  is_selected: bool = False, is_us_city: bool = True):
        """Draw a single city using its state color for the dot."""
        x, y = city["x"], city["y"]
        size = CITY_RADIUS
        
        if is_destroyed:
            # Black cross for destroyed cities (like original)
            pygame.draw.line(screen, COLORS["black"], (x-size, y-size), (x+size, y+size), 3)
            pygame.draw.line(screen, COLORS["black"], (x-size, y+size), (x+size, y-size), 3)
            text_color = HIT_COLOR
        else:
            # The `color` parameter from _get_city_color determines the dot color
            pygame.draw.circle(screen, color, (x, y), size)
            # Text color is always original (blue for US, red for Russia) unless destroyed
            text_color = COLORS["blue"] if is_us_city else COLORS["red"]

        text_surface = self.font.render(city["name"], True, text_color)
        text_x = x + 12  # Position to the right like original
        text_y = y - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def draw_usa_cities(self, screen: pygame.Surface, destroyed: List[bool], 
                       defenses: Set[int], targets: Set[int], 
                       selected_defenses: Set[int]):
        """Draw all USA cities with their current states."""
        for idx, city in enumerate(USA_CITIES):
            is_defended = idx in defenses
            is_selected = idx in selected_defenses
            is_targeted = idx in targets
            is_destroyed = destroyed[idx]
            
            color = self._get_city_color(is_destroyed, is_defended, 
                                       is_selected, is_targeted, is_us_city=True)
            self.draw_city(screen, city, color, is_destroyed, is_defended, is_selected, is_us_city=True)
    
    def draw_russia_cities(self, screen: pygame.Surface, destroyed: List[bool], 
                          defenses: Set[int], selected_targets: Set[int]):
        """Draw all Russian cities with their current states."""
        for idx, city in enumerate(RUSSIA_CITIES):
            is_defended = idx in defenses
            is_selected = idx in selected_targets
            is_destroyed = destroyed[idx]
            
            color = self._get_city_color(is_destroyed, is_defended, 
                                       is_selected, False, is_us_city=False)
            self.draw_city(screen, city, color, is_destroyed, is_defended, is_selected, is_us_city=False)


class UI:
    """Main UI controller for the game."""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.city_renderer = CityRenderer()
        
        # Pre-render the title surface for better performance
        self.title_surface = self.font.render(GAME_TITLE, True, COLORS["white"])
        self.title_rect = self.title_surface.get_rect(center=(WINDOW_WIDTH // 2, 17))
        
        # Comprehensive help content
        self.help_content = [
            "GLOBAL THERMONUCLEAR WAR - HELP",
            "",
            "GAME OVERVIEW:",
            "Select US cities to defend and Russian cities to attack",
            "AI will simultaneously choose targets and defenses",
            "",
            "CONTROLS:",
            "Left Click = Select cities/buttons",
            "H Key = Toggle this help window",
            "G Key = Toggle grid overlay",
            "",
            "GAME PHASES:",
            "1. DEFENSIVE - Select 5 US cities to defend",
            "2. OFFENSIVE - Select 5 Russian cities to target", 
            "3. LAUNCH - Watch missiles fly and intercepts",
            "4. RESULTS - View battle outcome",
            "",
            "CITY COLORS:",
            "Blue circles = US Cities",
            "Red circles = Russian Cities",
            "Orange circles = Selected cities",
            "Green circles = Defended cities",
            "Purple crosses = Destroyed cities",
            "",
            "Press H to close this help window"
        ]
        
        # Create buttons in original WarGames style and positions
        self.begin_button = Button(
            WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 30, 300, 60, "BEGIN"
        )
        self.exit_button = Button(
            WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 50, 300, 60, "EXIT"
        )
        self.continue_button = Button(
            WINDOW_WIDTH - 200, WINDOW_HEIGHT - 80, 180, 50, "CONTINUE"
        )
        self.launch_button = Button(
            WINDOW_WIDTH - 200, WINDOW_HEIGHT - 80, 180, 50, "LAUNCH"
        )
        self.close_button = Button(
            WINDOW_WIDTH - 200, WINDOW_HEIGHT - 80, 180, 50, "RESET"
        )
        self.reset_button = Button(
            WINDOW_WIDTH - 200, WINDOW_HEIGHT - 140, 180, 50, "RESET", COLORS["green"], COLORS["green"]
        )
    
    def draw_grid(self, screen: pygame.Surface):
        """Draw development grid overlay."""
        grid_size = 50
        for x in range(0, WINDOW_WIDTH, grid_size):
            pygame.draw.line(screen, COLORS["dark_gray"], (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, grid_size):
            pygame.draw.line(screen, COLORS["dark_gray"], (0, y), (WINDOW_WIDTH, y))
        
        # Draw coordinates at intersections
        font = pygame.font.Font(None, 16)
        for x in range(0, WINDOW_WIDTH, grid_size * 2):
            for y in range(0, WINDOW_HEIGHT, grid_size * 2):
                coord_text = f"({x},{y})"
                text_surface = font.render(coord_text, True, COLORS["gray"])
                screen.blit(text_surface, (x + 2, y + 2))
    
    def draw_windowed_text(self, screen: pygame.Surface, text_lines: List[str], y_position: int = None):
        """Draw text in a windowed panel like the original game."""
        if not text_lines:
            return
        
        # Calculate box dimensions
        max_width = 0
        line_height = 22
        for line in text_lines:
            surf = self.small_font.render(line, True, COLORS["green"])
            max_width = max(max_width, surf.get_width())
        
        box_width = max_width + 40  # padding
        box_height = len(text_lines) * line_height + 40  # padding
        box_x = (WINDOW_WIDTH - box_width) // 2
        
        # Position in lower half if y_position not specified
        if y_position is None:
            box_y = WINDOW_HEIGHT - box_height - 50
        else:
            box_y = y_position
        
        # Draw bordered rectangle with black background (like original)
        pygame.draw.rect(screen, COLORS["green"], (box_x - 4, box_y - 4, box_width + 8, box_height + 8))  # border
        pygame.draw.rect(screen, COLORS["black"], (box_x, box_y, box_width, box_height))  # background
        
        # Draw text lines
        y = box_y + 20
        for line in text_lines:
            surf = self.small_font.render(line, True, COLORS["green"])
            x = box_x + (box_width - surf.get_width()) // 2  # center text
            screen.blit(surf, (x, y))
            y += line_height

    def draw_title(self, screen: pygame.Surface):
        """Draw the game title at top of screen."""
        screen.blit(self.title_surface, self.title_rect)
    
    def draw_instruction(self, screen: pygame.Surface, instruction: str, y_pos: int = WINDOW_HEIGHT - 150):
        """Draw instruction text in a windowed panel."""
        self.draw_windowed_text(screen, [instruction], y_pos)
    
    def draw_selection_counter(self, screen: pygame.Surface, current: int, 
                              maximum: int, label: str, y_pos: int = WINDOW_HEIGHT - 120):
        """Draw selection counter in a windowed panel."""
        counter_text = f"{label}: {current}/{maximum}"
        self.draw_windowed_text(screen, [counter_text], y_pos)
    
    def draw_results(self, screen: pygame.Surface, us_casualties: int, 
                    russia_casualties: int, total_us: int, total_russia: int,
                    us_percent: float, russia_percent: float,
                    us_destroyed_cities: List[str], russian_destroyed_cities: List[str]):
        """Draw battle results in a windowed panel."""
        # Create text lines for the results window
        text_lines = [
            "BATTLE RESULTS",
            "",
            f"US Casualties: {us_casualties:,} / {total_us:,} ({us_percent:.1f}%)",
            f"Russian Casualties: {russia_casualties:,} / {total_russia:,} ({russia_percent:.1f}%)",
        ]
        
        if us_destroyed_cities:
            text_lines.append("")
            # Split US cities across multiple lines if needed
            us_cities_text = ", ".join(us_destroyed_cities)
            if len(us_cities_text) > 50:
                # Split into multiple lines
                cities_per_line = []
                current_line = "US Cities Destroyed: "
                
                for i, city in enumerate(us_destroyed_cities):
                    if i == 0:
                        current_line += city
                    else:
                        test_line = current_line + ", " + city
                        if len(test_line) > 50:
                            cities_per_line.append(current_line)
                            current_line = city
                        else:
                            current_line = test_line
                
                if current_line:
                    cities_per_line.append(current_line)
                
                text_lines.extend(cities_per_line)
            else:
                text_lines.append("US Cities Destroyed: " + us_cities_text)
        
        if russian_destroyed_cities:
            text_lines.append("")
            # Split Russian cities across multiple lines if needed
            russia_cities_text = ", ".join(russian_destroyed_cities)
            if len(russia_cities_text) > 50:
                # Split into multiple lines
                cities_per_line = []
                current_line = "Russian Cities Destroyed: "
                
                for i, city in enumerate(russian_destroyed_cities):
                    if i == 0:
                        current_line += city
                    else:
                        test_line = current_line + ", " + city
                        if len(test_line) > 50:
                            cities_per_line.append(current_line)
                            current_line = city
                        else:
                            current_line = test_line
                
                if current_line:
                    cities_per_line.append(current_line)
                
                text_lines.extend(cities_per_line)
            else:
                text_lines.append("Russian Cities Destroyed: " + russia_cities_text)
        
        self.draw_windowed_text(screen, text_lines)

    def draw_help_prompt(self, screen: pygame.Surface):
        """Draw simple help prompt at bottom of screen."""
        help_text = "Press H for Help"
        help_surface = pygame.font.Font(None, 20).render(help_text, True, COLORS["green"])
        screen.blit(help_surface, (10, WINDOW_HEIGHT - 25))
    
    def draw_comprehensive_help(self, screen: pygame.Surface):
        """Draw the comprehensive help window."""
        self.draw_windowed_text(screen, self.help_content, 30)


def get_clicked_city(mouse_pos: tuple, cities: List[dict]) -> int:
    """Return the index of the clicked city, or -1 if none."""
    for idx, city in enumerate(cities):
        distance = math.sqrt((mouse_pos[0] - city["x"])**2 + (mouse_pos[1] - city["y"])**2)
        if distance <= CITY_RADIUS:
            return idx
    return -1
