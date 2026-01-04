"""Utility functions for the app."""

def get_manhattan_distance(cell1, cell2):
    """
    Calculates the Manhattan distance between two points (pos1 and pos2).
    Both positions should be coordinate tuples (x, y).
    """
    x1, y1 = cell1.coordinate
    x2, y2 = cell2.coordinate
    return abs(x1 - x2) + abs(y1 - y2)