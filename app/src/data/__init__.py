"""Data.

Functions to manage, clean and process data.
"""

from .compute_data import (
    compute_local_density, compute_evacuation_rate,
    compute_macro_average_speed, compute_micro_average_speed,
    compute_evacuation_rate_by_type, compute_macro_average_speed_by_type,
    compute_average_dead_lock_factor
)