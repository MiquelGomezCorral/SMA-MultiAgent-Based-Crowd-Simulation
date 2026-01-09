"""Configuration file.

Configuration of project variables that we want to have available
everywhere and considered configuration.
"""
# import os
import dataclasses
from dataclasses import dataclass
from typing import Literal
@dataclass 
class Configuration:
    """Configuration class for the project."""

    seed:     int = 42
    exp_name: str = "base_name"
    width:    int = 10
    height:   int = 10
    initial_agents: int = 10
    track_last_steps: int = 5
    path_finding_algorithm: Literal["MANHATTAN", "BFS", "A*"] = "A*"
    scenario_type: Literal["OPEN", "MALL", "CORRIDOR", "SEATS", "SNAKE", "RANDOM"] = "MALL"
    n_exits: int = 4
    differentiate_exits: bool = True

    n_experiments: int = 1000

    # BEHAVIOR RATIOS
    agent_types_ratios: dict = dataclasses.field(default_factory=lambda: {
        "polite": 0.7,
        "aggressive": 0.2,
        "slow": 0.1,
    })


    def __post_init__(self):
        ...

    def to_dict(self) -> dict:
        """Convert Configuration to dictionary."""
        return dataclasses.asdict(self)