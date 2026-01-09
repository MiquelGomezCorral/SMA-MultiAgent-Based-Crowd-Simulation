"""
Centralized visualization configuration for agent types
Color mapping for plot metrics (uses CROWD_AGENT_STATS for agent type colors)
"""

from enum import Enum

class CrowdAgentEnum(str, Enum):
    POLITE = "polite"
    AGGRESSIVE = "aggressive"
    SLOW = "slow"
    EXIT = "exit"
    WALL = "wall"

STATIC_AGENTS = [CrowdAgentEnum.EXIT, CrowdAgentEnum.WALL]

CROWD_AGENT_STATS = {
    CrowdAgentEnum.POLITE: {
        "label": "Polite",
        "color": "tab:blue",
        "marker": "d",
        "size": 100,
        "speed_range": (0.65, 1.0),
        "crowd_slowdown_factor": 0.3,
        "start_crowd_slowdown_factor": 3,
        "dead_lock_factor": 1.0,
        "max_dead_lock_counter": 50,
    },
    CrowdAgentEnum.AGGRESSIVE: {
        "label": "Aggressive",
        "color": "tab:red",
        "marker": "v",
        "size": 100,
        "speed_range": (0.8, 1.0),
        "crowd_slowdown_factor": 0.1,
        "start_crowd_slowdown_factor": 3,
        "dead_lock_factor": 0.1,
        "max_dead_lock_counter": 50,
    },
    CrowdAgentEnum.SLOW: {
        "label": "Slow",
        "color": "#179665",
        "marker": "o",
        "size": 100,
        "speed_range": (0.5, 0.65),
        "crowd_slowdown_factor": 0.5,
        "start_crowd_slowdown_factor": 3,
        "dead_lock_factor": 0.5,
        "max_dead_lock_counter": 50,
    },
    CrowdAgentEnum.EXIT: {
        "label": "Exit",
        "color": "tab:green",
        "marker": "s",
        "size": 200,
    },
    CrowdAgentEnum.WALL: {
        "label": "Wall",
        "color": "tab:gray",
        "marker": "s", 
        "size": 200,
    }
}



AGENT_TYPE_COLORS = {
    # Plot metrics
    "total_agents": "black",
    "polite_agents": CROWD_AGENT_STATS[CrowdAgentEnum.POLITE]["color"],
    "aggressive_agents": CROWD_AGENT_STATS[CrowdAgentEnum.AGGRESSIVE]["color"],
    "slow_agents": CROWD_AGENT_STATS[CrowdAgentEnum.SLOW]["color"],
    # Per-type evacuation rates
    "local_density": CROWD_AGENT_STATS[CrowdAgentEnum.POLITE]["color"],
    "evacuation_rate": "black",
    "polite_evacuation_rate": CROWD_AGENT_STATS[CrowdAgentEnum.POLITE]["color"],
    "aggressive_evacuation_rate": CROWD_AGENT_STATS[CrowdAgentEnum.AGGRESSIVE]["color"],
    "slow_evacuation_rate": CROWD_AGENT_STATS[CrowdAgentEnum.SLOW]["color"],
    # Per-type macro speeds
    "micro_average_speed": "tab:orange",
    "macro_average_speed": "black",
    "polite_macro_speed": CROWD_AGENT_STATS[CrowdAgentEnum.POLITE]["color"],
    "aggressive_macro_speed": CROWD_AGENT_STATS[CrowdAgentEnum.AGGRESSIVE]["color"],
    "slow_macro_speed": CROWD_AGENT_STATS[CrowdAgentEnum.SLOW]["color"],
    "dead_lock_factor": "tab:red",
}

    