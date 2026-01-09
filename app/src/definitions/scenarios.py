"""Scenario generation functions for different grid layouts.

This module contains functions to generate wall and exit positions
for different evacuation scenarios.
"""
from dataclasses import dataclass
from typing import Literal, Tuple, List
import random


ScenarioType = Literal["OPEN", "MALL", "CORRIDOR", "SEATS", "SNAKE", "RANDOM"]


def get_wall_positions(
    scenario_type: ScenarioType,
    width: int,
    height: int,
    seed: int = 42
) -> List[Tuple[int, int]]:
    """Get wall positions based on scenario type.
    
    Args:
        scenario_type: Type of scenario to generate
        width: Grid width
        height: Grid height
        seed: Random seed for reproducibility
        
    Returns:
        List of (x, y) tuples indicating wall positions
    """
    if scenario_type == "OPEN":
        return _get_open_walls(width, height)
    elif scenario_type == "MALL":
        return _get_mall_walls(width, height)
    elif scenario_type == "CORRIDOR":
        return _get_corridor_walls(width, height)
    elif scenario_type == "SEATS":
        return _get_seats_walls(width, height)
    elif scenario_type == "SNAKE":
        return _get_snake_walls(width, height, seed)
    elif scenario_type == "RANDOM":
        return _get_random_walls(width, height, seed)
    else:
        raise ValueError(f"Unknown scenario type: {scenario_type}")


def get_exit_positions(
    scenario_type: ScenarioType,
    width: int,
    height: int,
    n_exits: int,
    seed: int = 42
) -> List[Tuple[int, int]]:
    """Get exit positions based on scenario type and number of exits.
    
    Args:
        scenario_type: Type of scenario to generate
        width: Grid width
        height: Grid height
        n_exits: Number of exits to place
        seed: Random seed for reproducibility
        
    Returns:
        List of (x, y) tuples indicating exit positions
    """
    if scenario_type == "OPEN":
        return _get_open_exits(width, height, n_exits)
    elif scenario_type == "MALL":
        return _get_mall_exits(width, height, n_exits)
    elif scenario_type == "CORRIDOR":
        return _get_corridor_exits(width, height, n_exits)
    elif scenario_type == "SEATS":
        return _get_seats_exits(width, height, n_exits)
    elif scenario_type == "SNAKE":
        return _get_snake_exits(width, height, n_exits, seed)
    elif scenario_type == "RANDOM":
        return _get_random_exits(width, height, n_exits, seed)
    else:
        raise ValueError(f"Unknown scenario type: {scenario_type}")


# ==================== OPEN SCENARIO ====================
def _get_open_walls(width: int, height: int) -> List[Tuple[int, int]]:
    """OPEN: No walls, just open space."""
    return []


def _get_open_exits(width: int, height: int, n_exits: int) -> List[Tuple[int, int]]:
    """OPEN: Exits on corners and center borders."""
    all_exits = [
        # Corners
        (0, 0),
        (0, height - 1),
        (width - 1, 0),
        (width - 1, height - 1),
        # Center borders
        (0, height // 2),
        (width - 1, height // 2),
        (width // 2, 0),
        (width // 2, height - 1),
    ]
    return all_exits[:n_exits]


# ==================== MALL SCENARIO ====================
@dataclass
class MallConfig:
    """Configuration for MALL scenario."""
    corridor_width: int = 2  # Corridor is 3 cells wide (center ± 1)
    outer_ring: int = 2  # Outer ring is walkable


def _get_mall_walls(width: int, height: int) -> List[Tuple[int, int]]:
    """MALL: 4 crossing corridors with outer ring walkable.
    
    Creates a mall-like structure with:
    - Vertical corridor in the center (width // 2 ± 1)
    - Horizontal corridor in the center (height // 2 ± 1)
    - Outer ring (1 cell from borders) is walkable
    - Rest is walls
    """
    config = MallConfig()
    walls = []
    center_x = width // 2
    center_y = height // 2
    corridor_width = config.corridor_width
    outer_ring = config.outer_ring
    
    for x in range(outer_ring, width - outer_ring):
        for y in range(outer_ring, height - outer_ring):
            
            # Skip vertical corridor
            if abs(x - center_x) <= corridor_width:
                continue
            
            # Skip horizontal corridor
            if abs(y - center_y) <= corridor_width:
                continue
            
            # Everything else is a wall
            walls.append((x, y))
    
    return walls


def _get_mall_exits(width: int, height: int, n_exits: int) -> List[Tuple[int, int]]:
    """MALL: Exits on walls at 1/3 and 2/3 of width/height.
    
    For 1-4 exits: Each border gets one exit (first position).
    For 5-8 exits: Each border gets a second exit (second position).
    Order: top, bottom, left, right, then repeat.
    """
    all_exits = []
    
    # Calculate positions at 1/3 and 2/3
    x_pos1, x_pos2 = int(width * 1 / 3), int(width * 2 / 3)
    y_pos1, y_pos2 = int(height * 1 / 3), int(height * 2 / 3)
    
    # First round (exits 1-4): one per border
    all_exits.append((x_pos1, 0))              # 1: Top border, first position
    all_exits.append((x_pos2, height - 1))     # 2: Bottom border, second position
    all_exits.append((0, y_pos2))              # 7: Left border, second position
    all_exits.append((width - 1, y_pos1))      # 8: Right border, first position
    
    # Second round (exits 5-8): second position per border
    all_exits.append((x_pos2, 0))              # 5: Top border, second position
    all_exits.append((x_pos1, height - 1))     # 6: Bottom border, first position
    all_exits.append((0, y_pos1))              # 3: Left border, first position
    all_exits.append((width - 1, y_pos2))      # 4: Right border, second position
    
    return all_exits[:n_exits]


# ==================== CORRIDOR SCENARIO ====================
@dataclass
class CorridorConfig:
    """Configuration for CORRIDOR scenario."""
    corridor_width: int = 1  # Corridor is 3 cells wide (center ± 1)


def _get_corridor_walls(width: int, height: int) -> List[Tuple[int, int]]:
    """CORRIDOR: Only 4 crossing paths are walkable (simpler version of MALL)."""
    config = CorridorConfig()
    walls = []
    center_x = width // 2
    center_y = height // 2
    corridor_width = config.corridor_width
    
    for x in range(width):
        for y in range(height):
            # Skip vertical corridor
            if abs(x - center_x) <= corridor_width:
                continue
            
            # Skip horizontal corridor
            if abs(y - center_y) <= corridor_width:
                continue
            
            # Everything else is a wall
            walls.append((x, y))
    
    return walls


def _get_corridor_exits(width: int, height: int, n_exits: int) -> List[Tuple[int, int]]:
    """CORRIDOR: Exits at the ends of the corridors."""
    all_exits = [
        # Vertical corridor ends
        (width // 2, 0),
        (width // 2, height - 1),
        # Horizontal corridor ends
        (0, height // 2),
        (width - 1, height // 2),
    ]
    return all_exits[:n_exits]


# ==================== SEATS SCENARIO ====================
@dataclass
class SeatsConfig:
    """Configuration for SEATS scenario."""
    row_width: int = 2  # Each row is 2 cells wide
    aisle_width: int = 2  # Aisles are 2 cells wide
    
    @property
    def gap_seats_every(self) -> int:
        """Calculate gap between seats."""
        return (self.row_width + self.aisle_width) * 2


def _get_seats_walls(width: int, height: int) -> List[Tuple[int, int]]:
    """SEATS: Rows of seats with aisles between them.
    
    Creates a theater/auditorium-like structure:
    - Rows of seats (walls) with aisles between
    - All exits on one side (right side)
    """
    config = SeatsConfig()
    walls = []
    row_width = config.row_width
    aisle_width = config.aisle_width
    gap_seats_every = config.gap_seats_every
    
    x = 0
    while x < width - 5:  # Leave space for exit side
        # Create a row of seats
        for offset in range(row_width):
            if x + offset < width - 5:
                for y in range(1, height - 1):
                    if y % gap_seats_every == 0:
                        continue  # Leave aisle
                    walls.append((x + offset, y))
        x += row_width + aisle_width
    
    return walls


def _get_seats_exits(width: int, height: int, n_exits: int) -> List[Tuple[int, int]]:
    """SEATS: All exits on the right side."""
    all_exits = []
    
    # Distribute exits evenly along the right border
    if n_exits == 1:
        all_exits.append((width - 1, height // 2))
    else:
        for i in range(n_exits):
            y = int((i + 1) * height / (n_exits + 1))
            all_exits.append((width - 1, y))
    
    return all_exits[:n_exits]


# ==================== SNAKE SCENARIO ====================
@dataclass
class SnakeConfig:
    """Configuration for SNAKE scenario."""
    corridor_width: int = 2
    segments: int = 4  # Number of horizontal segments


def _get_snake_walls(width: int, height: int, seed: int = 42) -> List[Tuple[int, int]]:
    """SNAKE: S-shaped or multiple S-shaped corridors.
    
    Creates a snake-like path through the grid.
    """
    config = SnakeConfig()
    walls = []
    corridor_width = config.corridor_width
    
    # Initialize all cells as walls
    all_cells = set((x, y) for x in range(width) for y in range(height))
    walkable = set()
    
    # Create snake path
    segments = config.segments
    segment_height = height // segments
    
    for seg in range(segments):
        y_start = seg * segment_height
        y_end = min((seg + 1) * segment_height, height)
        y_mid = (y_start + y_end) // 2
        
        if seg % 2 == 0:
            # Left to right
            for x in range(width):
                for dy in range(-corridor_width, corridor_width + 1):
                    y = y_mid + dy
                    if 0 <= y < height:
                        walkable.add((x, y))
        else:
            # Right to left
            for x in range(width):
                for dy in range(-corridor_width, corridor_width + 1):
                    y = y_mid + dy
                    if 0 <= y < height:
                        walkable.add((x, y))
        
        # Connect segments vertically
        if seg < segments - 1:
            if seg % 2 == 0:
                x_connect = width - 1
            else:
                x_connect = 0
            
            for y in range(y_mid, y_mid + segment_height):
                if y < height:
                    for dx in range(-corridor_width, corridor_width + 1):
                        x = x_connect + dx
                        if 0 <= x < width:
                            walkable.add((x, y))
    
    # All cells not in walkable are walls
    walls = list(all_cells - walkable)
    
    return walls


def _get_snake_exits(width: int, height: int, n_exits: int, seed: int = 42) -> List[Tuple[int, int]]:
    """SNAKE: Exits at the start and end of the snake."""
    config = SnakeConfig()
    all_exits = [
        (0, height // 8),  # Start of snake (top-left area)
        (0, height - height // 8 - config.corridor_width - 1),  # End of snake (bottom-left area)
        # (0, height // 2),  # Middle-left
        # (width - 1, height // 2),  # Middle-right
    ]
    return all_exits[:n_exits]


# ==================== RANDOM SCENARIO ====================
def _get_random_walls(width: int, height: int, seed: int = 42) -> List[Tuple[int, int]]:
    """RANDOM: Random blobs of walls scattered across the grid.
    
    Creates random obstacle blobs throughout the grid.
    """
    rng = random.Random(seed)
    walls = set()
    
    # Number of blobs
    n_blobs = rng.randint(5, 10)
    
    for _ in range(n_blobs):
        # Random blob center
        center_x = rng.randint(2, width - 3)
        center_y = rng.randint(2, height - 3)
        
        # Random blob size
        blob_size = rng.randint(2, 5)
        
        # Create blob with random shape
        for _ in range(blob_size * 3):
            dx = rng.randint(-blob_size, blob_size)
            dy = rng.randint(-blob_size, blob_size)
            
            x = center_x + dx
            y = center_y + dy
            
            # Keep within bounds and not on borders
            if 1 <= x < width - 1 and 1 <= y < height - 1:
                walls.add((x, y))
    
    return list(walls)


def _get_random_exits(width: int, height: int, n_exits: int, seed: int = 42) -> List[Tuple[int, int]]:
    """RANDOM: Random exits on the borders."""
    rng = random.Random(seed)
    all_exits = []
    
    # Create more exit candidates than needed
    border_positions = []
    
    # Top and bottom borders
    for x in range(width):
        border_positions.append((x, 0))
        border_positions.append((x, height - 1))
    
    # Left and right borders
    for y in range(1, height - 1):  # Skip corners (already added)
        border_positions.append((0, y))
        border_positions.append((width - 1, y))
    
    # Randomly select exits
    rng.shuffle(border_positions)
    return border_positions[:n_exits]
