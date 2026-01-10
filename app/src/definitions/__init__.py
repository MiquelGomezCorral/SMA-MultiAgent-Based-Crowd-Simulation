"""Definitions package for the simulation models."""


from .model_params import basic_model_params

from .agents_params import (
    CrowdAgentEnum,
    STATIC_AGENTS,
    CROWD_AGENT_STATS,
    AGENT_TYPE_COLORS,
)

from .experiments import get_experiments