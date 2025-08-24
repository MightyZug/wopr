from enum import Enum

# Display settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 700
FPS = 60

# Game settings
GAME_TITLE = "Global Thermonuclear War"
CITY_RADIUS = 8
MISSILE_SPEED = 0.001  
INTERCEPT_RADIUS = 60  
DEFENSE_LIMIT = 5
TARGET_LIMIT = 5
SHADOW_OFFSET = 3
EXPLOSION_RADIUS = 30
MUSHROOM_CLOUD_DURATION = 3000  

COLOURS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "green": (60, 255, 60), 
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "gray": (128, 128, 128),
    "dark_gray": (64, 64, 64),
    "light_gray": (192, 192, 192),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128)
}

SELECTED_COLOUR = COLOURS["orange"]
TARGETED_COLOUR = COLOURS["red"]
DEFENDED_COLOUR = COLOURS["orange"]
HIT_COLOUR = COLOURS["purple"]

class GameState(Enum):
    LOADING = 0
    MENU = 1
    DEFENSIVE = 2
    OFFENSIVE = 3
    LAUNCHING = 4
    RESULTS = 5

class MissileType(Enum):
    US_MISSILE = 1
    USSR_MISSILE = 2
