import pygame
import math
from typing import Set, List
from config import (COLOURS, WINDOW_WIDTH, WINDOW_HEIGHT, CITY_RADIUS, 
                   SELECTED_COLOUR, TARGETED_COLOR, DEFENDED_COLOR, HIT_COLOR, GAME_TITLE)
from city_data import USA_CITIES, USSR_CITIES


class Button:
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: tuple = COLOURS["green"], text_color: tuple = COLOURS["green"]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 24)
        self.enabled = True
    
    def draw(self, screen: pygame.Surface) -> None:
        mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse)
        
        color = COLOURS["green"] if self.enabled else (60, 60, 60)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        
        inner_rect = self.rect.inflate(-6, -6)
        pygame.draw.rect(screen, COLOURS["black"], inner_rect, border_radius=6)
        
        text_color = COLOURS["green"] if self.enabled else (100, 100, 100)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, mouse_pos: tuple) -> bool:
        return self.enabled and self.rect.collidepoint(mouse_pos)


class CityRenderer:
    
    def __init__(self):
        self.font = pygame.font.Font(None, 18)
    
    def _get_city_color(self, is_destroyed: bool, is_defended: bool, 
                       is_selected: bool, is_targeted: bool, is_us_city: bool = True) -> tuple:
        if is_destroyed:
            return HIT_COLOR
        elif is_selected:
            return SELECTED_COLOUR
        elif is_defended:
            return DEFENDED_COLOR
        elif is_targeted:
            return TARGETED_COLOR
        else:
            return COLOURS["blue"] if is_us_city else COLOURS["red"]
    
    def draw_city(self, screen: pygame.Surface, city: dict, color: tuple, 
                  is_destroyed: bool = False, is_defended: bool = False, 
                  is_selected: bool = False, is_us_city: bool = True):
        x, y = city["x"], city["y"]
        size = CITY_RADIUS
        
        if is_destroyed:
            pygame.draw.line(screen, COLOURS["black"], (x-size, y-size), (x+size, y+size), 3)
            pygame.draw.line(screen, COLOURS["black"], (x-size, y+size), (x+size, y-size), 3)
            text_color = HIT_COLOR
        else:
            pygame.draw.circle(screen, color, (x, y), size)
            text_color = COLOURS["blue"] if is_us_city else COLOURS["red"]

        text_surface = self.font.render(city["name"], True, text_color)
        text_x = x + 12  
        text_y = y - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
    
    def draw_usa_cities(self, screen: pygame.Surface, destroyed: List[bool], 
                       defenses: Set[int], targets: Set[int], 
                       selected_defenses: Set[int]):
        for idx, city in enumerate(USA_CITIES):
            is_defended = idx in defenses
            is_selected = idx in selected_defenses
            is_targeted = idx in targets
            is_destroyed = destroyed[idx]
            
            color = self._get_city_color(is_destroyed, is_defended, 
                                       is_selected, is_targeted, is_us_city=True)
            self.draw_city(screen, city, color, is_destroyed, is_defended, is_selected, is_us_city=True)
    
    def draw_ussr_cities(self, screen: pygame.Surface, destroyed: List[bool], 
                          defenses: Set[int], selected_targets: Set[int]):
        for idx, city in enumerate(USSR_CITIES):
            is_defended = idx in defenses
            is_selected = idx in selected_targets
            is_destroyed = destroyed[idx]
            
            color = self._get_city_color(is_destroyed, is_defended, 
                                       is_selected, False, is_us_city=False)
            self.draw_city(screen, city, color, is_destroyed, is_defended, is_selected, is_us_city=False)


class UI:
    
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.city_renderer = CityRenderer()
        
        self.title_surface = self.font.render(GAME_TITLE, True, COLOURS["white"])
        self.title_rect = self.title_surface.get_rect(center=(WINDOW_WIDTH // 2, 17))
        
        self.help_content = [
            "GLOBAL THERMONUCLEAR WAR - HELP",
            "",
            "GAME OVERVIEW:",
            "Select US cities to defend and USSR cities to attack",
            "AI will simultaneously choose targets and defenses",
            "",
            "CONTROLS:",
            "Left Click = Select cities/buttons",
            "H Key = Toggle this help window",
            "G Key = Toggle grid overlay",
            "",
            "GAME PHASES:",
            "1. DEFENSIVE - Select 5 US cities to defend",
            "2. OFFENSIVE - Select 5 USSR cities to target", 
            "3. LAUNCH - Watch missiles fly and intercepts",
            "4. RESULTS - View battle outcome",
            "",
            "CITY COLORS:",
            "Blue circles = US Cities",
            "Red circles = USSR Cities",
            "Orange circles = Selected cities",
            "Green circles = Defended cities",
            "Purple crosses = Destroyed cities",
            "",
            "Press H to close this help window"
        ]
    
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
            WINDOW_WIDTH - 200, WINDOW_HEIGHT - 140, 180, 50, "RESET", COLOURS["green"], COLOURS["green"]
        )
    
    def draw_grid(self, screen: pygame.Surface) -> None:
        grid_size = 50
        for x in range(0, WINDOW_WIDTH, grid_size):
            pygame.draw.line(screen, COLOURS["dark_gray"], (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, grid_size):
            pygame.draw.line(screen, COLOURS["dark_gray"], (0, y), (WINDOW_WIDTH, y))
        
        font = pygame.font.Font(None, 16)
        for x in range(0, WINDOW_WIDTH, grid_size * 2):
            for y in range(0, WINDOW_HEIGHT, grid_size * 2):
                coord_text = f"({x},{y})"
                text_surface = font.render(coord_text, True, COLOURS["gray"])
                screen.blit(text_surface, (x + 2, y + 2))
    
    def draw_windowed_text(self, screen: pygame.Surface, text_lines: List[str], y_position: int = None) -> None:
        if not text_lines:
            return
        
        max_width = 0
        line_height = 22
        for line in text_lines:
            surf = self.small_font.render(line, True, COLOURS["green"])
            max_width = max(max_width, surf.get_width())
        
        box_width = max_width + 40  
        box_height = len(text_lines) * line_height + 40 
        box_x = (WINDOW_WIDTH - box_width) // 2
        
        if y_position is None:
            box_y = WINDOW_HEIGHT - box_height - 50
        else:
            box_y = y_position
        
        pygame.draw.rect(screen, COLOURS["green"], (box_x - 4, box_y - 4, box_width + 8, box_height + 8))  
        pygame.draw.rect(screen, COLOURS["black"], (box_x, box_y, box_width, box_height)) 
        

        y = box_y + 20
        for line in text_lines:
            surf = self.small_font.render(line, True, COLOURS["green"])
            x = box_x + (box_width - surf.get_width()) // 2  
            screen.blit(surf, (x, y))
            y += line_height

    def draw_title(self, screen: pygame.Surface):
        screen.blit(self.title_surface, self.title_rect)
    
    def draw_instruction(self, screen: pygame.Surface, instruction: str, y_pos: int = WINDOW_HEIGHT - 150):
        self.draw_windowed_text(screen, [instruction], y_pos)
    
    def draw_selection_counter(self, screen: pygame.Surface, current: int, 
                              maximum: int, label: str, y_pos: int = WINDOW_HEIGHT - 120):
        counter_text = f"{label}: {current}/{maximum}"
        self.draw_windowed_text(screen, [counter_text], y_pos)
    
    def draw_results(self, screen: pygame.Surface, us_casualties: int, 
                    ussr_casualties: int, total_us: int, total_ussr: int,
                    us_percent: float, ussr_percent: float,
                    us_destroyed_cities: List[str], ussr_destroyed_cities: List[str]):
        text_lines = [
            "BATTLE RESULTS",
            "",
            f"US Casualties: {us_casualties:,} / {total_us:,} ({us_percent:.1f}%)",
            f"USSR Casualties: {ussr_casualties:,} / {total_ussr:,} ({ussr_percent:.1f}%)",
        ]
        
        if us_destroyed_cities:
            text_lines.append("")
            us_cities_text = ", ".join(us_destroyed_cities)
            if len(us_cities_text) > 50:
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
        
        if ussr_destroyed_cities:
            text_lines.append("")
            ussr_cities_text = ", ".join(ussr_destroyed_cities)
            if len(ussr_cities_text) > 50:
                cities_per_line = []
                current_line = "USSR Cities Destroyed: "
                
                for i, city in enumerate(ussr_destroyed_cities):
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
                text_lines.append("USSR Cities Destroyed: " + ussr_cities_text)
        
        self.draw_windowed_text(screen, text_lines)

    def draw_help_prompt(self, screen: pygame.Surface):
        help_text = "Press H for Help"
        help_surface = pygame.font.Font(None, 20).render(help_text, True, COLOURS["green"])
        screen.blit(help_surface, (10, WINDOW_HEIGHT - 25))
    
    def draw_comprehensive_help(self, screen: pygame.Surface):
        self.draw_windowed_text(screen, self.help_content, 30)


def get_clicked_city(mouse_pos: tuple, cities: List[dict]) -> int:
    for idx, city in enumerate(cities):
        distance = math.sqrt((mouse_pos[0] - city["x"])**2 + (mouse_pos[1] - city["y"])**2)
        if distance <= CITY_RADIUS:
            return idx
    return -1
