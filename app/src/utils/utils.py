"""Utility functions for the app."""

import matplotlib.colors as mcolors
import random

def get_manhattan_distance(cell1, cell2):
    """
    Calculates the Manhattan distance between two points (pos1 and pos2).
    Both positions should be coordinate tuples (x, y).
    """
    x1, y1 = cell1.coordinate
    x2, y2 = cell2.coordinate
    return abs(x1 - x2) + abs(y1 - y2)

def get_l2_distance(cell1, cell2):
    """
    Calculates the L2 (Euclidean) distance between two points (pos1 and pos2).
    Both positions should be coordinate tuples (x, y).
    """
    x1, y1 = cell1.coordinate
    x2, y2 = cell2.coordinate
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def get_varied_color(base_color, agent_id, noise_level=0.25):
    """
    Returns a consistent variation of a base color based on the agent_id.
    
    :param base_color: The starting color (e.g., "tab:red", "#FF0000")
    :param agent_id: Unique seed to make the variation consistent
    :param noise_level: How much to deviate from the base (0.0 to 1.0)
    :return: Hex color string (e.g., "#FF5733")
    """
    # 1. Convert named color to RGB (0-1 range)
    rgb = mcolors.to_rgb(base_color)
    
    # 2. Seed random generator with agent_id so the color stays constant per agent
    #    (If you want them to shimmer every step, remove the seed)
    r_gen = random.Random(agent_id)
    
    # 3. Add consistent noise to each channel
    #    We subtract 0.5 so the noise is centered (some lighter, some darker)
    new_rgb = []
    for channel in rgb:
        noise = (r_gen.random() - 0.5) * noise_level
        new_val = max(0, min(1, channel + noise)) # Clip to valid 0-1 range
        new_rgb.append(new_val)
    
    # 4. Convert back to hex string for consistency with matplotlib
    return mcolors.to_hex(new_rgb)

