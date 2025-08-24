# WarGames Nuclear Simulation

A Python/Pygame implementation of the nuclear war simulation game inspired by the 1983 movie "WarGames". This refactored version follows clean code principles with proper separation of concerns.

## Architecture Overview

The codebase has been created as a modular architecture with clear separation of concerns:

### Core Modules

#### `config.py`
- **Purpose**: Central configuration and constants
- **Contents**: Game settings, colors, window dimensions, enums for game states and missile types
- **Benefits**: Single source of truth for configuration, easy to modify game parameters

#### `city_data.py`
- **Purpose**: Static data for cities
- **Contents**: USA_CITIES and RUSSIA_CITIES with coordinates and population data
- **Benefits**: Separates data from logic, easy to modify city information

#### `game_state.py`
- **Purpose**: Game state management
- **Contents**: GameStateManager class handling all game state transitions and data
- **Benefits**: Centralized state management, clear state transition logic

#### `ui.py`
- **Purpose**: User interface components
- **Contents**: Button class, CityRenderer class, UI class for all rendering logic
- **Benefits**: Modular UI components, reusable rendering functions

#### `missiles.py`
- **Purpose**: Missile system and animations
- **Contents**: MissileSystem class handling trajectories, intercepts, and explosions
- **Benefits**: Isolated animation logic, clear missile behavior management

#### `WarGames_refactored.py`
- **Purpose**: Main game orchestration
- **Contents**: WarGame class that coordinates all other modules
- **Benefits**: Clean separation between game loop and game logic

## Clean Code Principles Applied

### 1. Single Responsibility Principle
- Each module has a single, well-defined purpose
- Classes focus on one aspect of functionality
- Functions perform specific, atomic operations

### 2. Separation of Concerns
- Configuration separated from logic
- Data separated from behavior
- UI rendering separated from game state
- Animation logic isolated from game flow

### 3. Dependency Injection
- Modules import only what they need
- Clear dependency hierarchy
- Easy to test individual components

### 4. Meaningful Names
- Descriptive class and function names
- Clear variable naming conventions
- Self-documenting code structure

### 5. Small Functions
- Functions perform single operations
- Easy to understand and test
- Logical grouping of related functionality

## Python Best Practices Implemented

### Type Hints
```python
def toggle_defense(self, city_index: int) -> bool:
def draw_city(self, screen: pygame.Surface, city: dict, color: tuple):
```

### Docstrings
```python
def calculate_casualties(self) -> tuple:
    """Calculate casualties for both sides."""
```

### Enums for Constants
```python
class GameState(Enum):
    MENU = 1
    DEFENSIVE = 2
    OFFENSIVE = 3
```

### List Comprehensions and Generator Expressions
```python
us_casualties = sum(USA_CITIES[idx]["population"] 
                   for idx in range(len(USA_CITIES)) 
                   if self.usa_destroyed[idx])
```

### Context Management
```python
try:
    self.background = pygame.image.load('neon_map.png').convert()
except pygame.error:
    # Fallback implementation
```

## Game Features

### Strategic Gameplay
- **Defensive Phase**: Select 5 US cities to defend with missile intercept systems
- **Offensive Phase**: Select 5 Russian cities to target with nuclear missiles
- **AI Opponent**: Computer selects its own defenses and targets

### Visual Effects
- **Missile Animations**: Real-time trajectory rendering with different colors for each side
- **Intercept System**: Visual representation of defensive ranges and missile interceptions
- **Mushroom Clouds**: Animated explosion effects for successful hits
- **City States**: Color-coded cities showing selection, defense, targeting, and destruction states

### Developer Tools
- **Grid Overlay**: Press 'G' to toggle coordinate grid for development
- **ESC Key**: Return to menu from any state
- **Population Display**: Shows casualty numbers and percentages

## Installation and Running

### Prerequisites
- Python 3.9 or higher

### Setup Instructions

1. **Clone the repository** (or download the files)
   ```bash
   git clone <your-repo-url>
   cd wopr
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   ```bash
   # On macOS/Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### File Structure
```
/wopr/
├── WarGames.py           # Main game file
├── config.py             # Configuration constants
├── city_data.py          # City data
├── game_state.py         # State management
├── ui.py                 # UI components
├── missiles.py           # Missile system
├── neon_map.png          # Background image (optional)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

### Running the Game
```bash
# Make sure your virtual environment is activated
python WarGames.py
```

### Deactivating the Virtual Environment
When you're done playing:
```bash
deactivate
```

## Code Quality Improvements

### Before (Monolithic)
- Single 600+ line file
- Mixed concerns (UI, logic, data, config)
- Global variables and functions
- Difficult to test and maintain

### After (Modular)
- 6 focused modules averaging 100-150 lines each
- Clear separation of concerns
- Object-oriented design
- Easy to test individual components
- Maintainable and extensible

## Testing Strategy

The modular architecture enables unit testing of individual components:

- **GameStateManager**: Test state transitions and game logic
- **MissileSystem**: Test trajectory calculations and intercept logic
- **UI Components**: Test rendering and input handling
- **CityRenderer**: Test city state visualization

## Future Enhancements

The clean architecture makes it easy to add new features:

- **Multiplayer Support**: Add network module
- **Advanced AI**: Enhance AI strategy algorithms
- **Save/Load**: Add persistence layer
- **Sound Effects**: Add audio module
- **Different Scenarios**: Add scenario configuration system

## Conclusion

This refactored version demonstrates how proper software architecture can transform a monolithic codebase into a maintainable, extensible, and testable system while preserving all original functionality and enhancing code quality.
