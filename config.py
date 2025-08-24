
"""Game configuration and constants."""

from enum import Enum

# Display settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 700
FPS = 60

# Game settings
GAME_TITLE = "Global Thermonuclear War"
CITY_RADIUS = 8
MISSILE_SPEED = 0.001  # Faster speed to match original (was 0.003)
INTERCEPT_RADIUS = 60  # Radius for missile intercepts
DEFENSE_LIMIT = 5
TARGET_LIMIT = 5
SHADOW_OFFSET = 3
EXPLOSION_RADIUS = 30
MUSHROOM_CLOUD_DURATION = 3000  # 3 seconds

# Colors
COLORS = {
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

SELECTED_COLOR = COLORS["orange"]
TARGETED_COLOR = COLORS["red"]
DEFENDED_COLOR = COLORS["orange"]
HIT_COLOR = COLORS["purple"]

class GameState(Enum):
    MENU = 1
    DEFENSIVE = 2
    OFFENSIVE = 3
    MISSILE_LAUNCH = 4
    RESULTS = 5

class MissileType(Enum):
    US_MISSILE = 1
    RUSSIAN_MISSILE = 2
