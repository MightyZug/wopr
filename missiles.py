import pygame
from typing import List, Dict, Set, Any
from config import (
    COLOURS, 
    INTERCEPT_RADIUS, 
    MUSHROOM_CLOUD_DURATION, 
    EXPLOSION_RADIUS
)
from city_data import USA_CITIES, USSR_CITIES


class MissileSystem:
    
    def __init__(self):
        self.missile_lines: List[Dict[str, Any]] = []
        self.mushroom_clouds: List[Dict[str, Any]] = []
        self.animation_start_time = 0
    
    def create_missile_lines(self, player_targets: Set[int], ai_targets: Set[int], 
                            player_defenses: Set[int], ai_defenses: Set[int]) -> None:
        self.missile_lines = []
        self.animation_start_time = pygame.time.get_ticks()
        
        self.current_player_defenses = player_defenses
        self.current_ai_defenses = ai_defenses
        
        defense_list = list(player_defenses)
        target_list = list(player_targets)
        for i, target_idx in enumerate(target_list):
            if i < len(defense_list):  
                launch_city_idx = defense_list[i]
                launch_pos = (USA_CITIES[launch_city_idx]["x"], USA_CITIES[launch_city_idx]["y"])
                target_pos = (USSR_CITIES[target_idx]["x"], USSR_CITIES[target_idx]["y"])
                self.missile_lines.append({
                    "start": launch_pos,
                    "end": target_pos,
                    "colour": (255, 255, 0),  
                    "progress": 0.0,
                    "impact_applied": False,
                    "type": "attack",
                    "target_idx": target_idx,
                    "is_ussr_target": True,
                    "intercept_launched": False,
                    "intercepted": False
                })
        
        ai_defense_list = list(ai_defenses)
        ai_target_list = list(ai_targets)
        for i, target_idx in enumerate(ai_target_list):
            if i < len(ai_defense_list):  
                launch_city_idx = ai_defense_list[i]
                launch_pos = (USSR_CITIES[launch_city_idx]["x"], USSR_CITIES[launch_city_idx]["y"])
                target_pos = (USA_CITIES[target_idx]["x"], USA_CITIES[target_idx]["y"])
                self.missile_lines.append({
                    "start": launch_pos,
                    "end": target_pos,
                    "colour": (255, 100, 100),  
                    "progress": 0.0,
                    "impact_applied": False,
                    "type": "attack",
                    "target_idx": target_idx,
                    "is_ussr_target": False,
                    "intercept_launched": False,
                    "intercepted": False
                })
    
    def update_missiles(self) -> bool:
        current_time = pygame.time.get_ticks()
        animation_duration = 3000  
        elapsed = current_time - self.animation_start_time
        
        if elapsed < animation_duration:
            progress = elapsed / animation_duration
            
            if progress >= 0.5:
                for missile in self.missile_lines:
                    if (missile["type"] == "attack" and not missile.get("intercept_launched", False) and 
                        not missile.get("intercepted", False)):
                        target_idx = missile["target_idx"]
                        
                        if not missile["is_ussr_target"] and target_idx in self.current_player_defenses:
                            
                            defending_city_pos = (USA_CITIES[target_idx]["x"], USA_CITIES[target_idx]["y"])
                            
                            start_x, start_y = missile["start"]
                            end_x, end_y = missile["end"]
                            intercept_x = start_x + (end_x - start_x) * 0.5
                            intercept_y = start_y + (end_y - start_y) * 0.5
                            
                            self.missile_lines.append({
                                "start": defending_city_pos,
                                "end": (intercept_x, intercept_y),
                                "colour": (0, 255, 0), 
                                "progress": 0.0,
                                "type": "intercept",
                                "target_missile": missile,
                                "impact_applied": False
                            })
                            missile["intercept_launched"] = True
                        
                        elif missile["is_ussr_target"] and target_idx in self.current_ai_defenses:
                            defending_city_pos = (USSR_CITIES[target_idx]["x"], USSR_CITIES[target_idx]["y"])
                            start_x, start_y = missile["start"]
                            end_x, end_y = missile["end"]
                            intercept_x = start_x + (end_x - start_x) * 0.5
                            intercept_y = start_y + (end_y - start_y) * 0.5
                            
                            self.missile_lines.append({
                                "start": defending_city_pos,
                                "end": (intercept_x, intercept_y),
                                "colour": (0, 255, 0),  
                                "progress": 0.0,
                                "type": "intercept",
                                "target_missile": missile,
                                "impact_applied": False
                            })
                            missile["intercept_launched"] = True
            
            for missile in self.missile_lines:
                if missile["type"] == "intercept":
                    missile["progress"] = min(1.0, (progress - 0.5) * 4)  
                else:
                    missile["progress"] = progress
            
            return False
        else:
            for missile in self.missile_lines:
                missile["progress"] = 1.0
            return True
    
    def check_intercepts(self, player_defenses: Set[int], ai_defenses: Set[int]) -> Set[int]:
        intercepted = set()
        current_time = pygame.time.get_ticks()
        
        for i, missile in enumerate(self.missile_lines):
            if missile["type"] == "intercept" and missile["progress"] >= 0.95 and not missile.get("impact_applied", False):
                target_missile = missile["target_missile"]
                target_missile["intercepted"] = True
                missile["impact_applied"] = True
                
                start_x, start_y = missile["start"]
                end_x, end_y = missile["end"]
                current_x = start_x + (end_x - start_x) * missile["progress"]
                current_y = start_y + (end_y - start_y) * missile["progress"]
                
                self.mushroom_clouds.append({
                    "position": (int(current_x), int(current_y)),
                    "start_time": current_time,
                    "duration": 800 
                })
                
                for j, m in enumerate(self.missile_lines):
                    if m is target_missile:
                        intercepted.add(j)
                        break
        
        return intercepted
    
    def create_explosions(self, intercepted_missiles: Set[int], 
                         usa_destroyed: List[bool], ussr_destroyed: List[bool],
                         us_destroyed_cities: List[str], ussr_destroyed_cities: List[str]):
        current_time = pygame.time.get_ticks()
        
        for missile in self.missile_lines:
            if (missile["type"] == "attack" and missile["progress"] >= 0.98 and 
                not missile.get("impact_applied", False) and not missile.get("intercepted", False)):
                
                target_idx = missile["target_idx"]
                missile["impact_applied"] = True
                
                start_x, start_y = missile["start"]
                end_x, end_y = missile["end"]
                current_x = start_x + (end_x - start_x) * missile["progress"]
                current_y = start_y + (end_y - start_y) * missile["progress"]
                
                if not missile["is_ussr_target"]: 
                    if not usa_destroyed[target_idx]:
                        usa_destroyed[target_idx] = True
                        us_destroyed_cities.append(USA_CITIES[target_idx]["name"])
                        
                        self.mushroom_clouds.append({
                            "position": (int(current_x), int(current_y)),
                            "start_time": current_time,
                            "duration": MUSHROOM_CLOUD_DURATION
                        })
                
                else: 
                    if not ussr_destroyed[target_idx]:
                        ussr_destroyed[target_idx] = True
                        ussr_destroyed_cities.append(USSR_CITIES[target_idx]["name"])
                        
                        self.mushroom_clouds.append({
                            "position": (int(current_x), int(current_y)),
                            "start_time": current_time,
                            "duration": MUSHROOM_CLOUD_DURATION
                        })
    
    def update_mushroom_clouds(self) -> None:
        current_time = pygame.time.get_ticks()
        self.mushroom_clouds = [
            cloud for cloud in self.mushroom_clouds
            if current_time - cloud["start_time"] < MUSHROOM_CLOUD_DURATION
        ]
    
    def draw_missiles(self, screen: pygame.Surface) -> None:
        for missile in self.missile_lines:
            if missile.get("intercepted", False):
                continue
                
            if missile["progress"] > 0:
                start_x, start_y = missile["start"]
                end_x, end_y = missile["end"]
                current_x = start_x + (end_x - start_x) * missile["progress"]
                current_y = start_y + (end_y - start_y) * missile["progress"]
                
                pygame.draw.line(screen, missile["colour"], missile["start"], (current_x, current_y), 2)
                
                pygame.draw.circle(screen, missile["colour"], (int(current_x), int(current_y)), 3)
    
    def draw_mushroom_clouds(self, screen: pygame.Surface) -> None:
        current_time = pygame.time.get_ticks()
        
        for cloud in self.mushroom_clouds:
            elapsed = current_time - cloud["start_time"]
            if elapsed < cloud["duration"]:
                progress = elapsed / cloud["duration"]
                
                current_radius = EXPLOSION_RADIUS * (0.5 + 0.5 * progress)
                alpha = int(255 * (1 - progress))
                
                pos_x, pos_y = cloud["position"]
                
                explosion_surface = pygame.Surface((current_radius * 2, current_radius * 2))
                explosion_surface.set_alpha(alpha)
                explosion_surface = explosion_surface.convert_alpha()

                pygame.draw.circle(explosion_surface, COLOURS["red"], 
                                 (int(current_radius), int(current_radius)), int(current_radius))
                pygame.draw.circle(explosion_surface, COLOURS["yellow"], 
                                 (int(current_radius), int(current_radius)), int(current_radius * 0.7))
                pygame.draw.circle(explosion_surface, COLOURS["white"], 
                                 (int(current_radius), int(current_radius)), int(current_radius * 0.4))
                
                screen.blit(explosion_surface, 
                           (pos_x - current_radius, pos_y - current_radius))
    
    def draw_defense_ranges(self, screen: pygame.Surface, defenses: Set[int], cities: List[dict]) -> None:
        for defense_idx in defenses:
            city = cities[defense_idx]
            pygame.draw.circle(screen, COLOURS["green"], 
                             (city["x"], city["y"]), INTERCEPT_RADIUS, 1)
    
    def reset(self) -> None:
        self.missile_lines = []
        self.mushroom_clouds = []
        self.animation_start_time = 0
