"""Run experiments with different configurations."""

import os
import sys
import mesa 
import numpy as np
import pandas as pd
from maikol_utils.print_utils import print_separator, print_color

from src.config import Configuration
from src.models import CrowdModelWrapper
from src.definitions import get_experiments

def run_experiments(DEFAULT_CONFIG: Configuration):
    """Run experiments based on provided arguments."""
    # DEFAULT_CONFIG = Configuration()
    EXPERIMENTS = get_experiments(DEFAULT_CONFIG)
        
    for EXP in EXPERIMENTS:
        print_separator(f"Running configuration {EXP['title']}", sep_type="START")
        rng = np.random.default_rng(DEFAULT_CONFIG.seed)
        seed_values = rng.integers(0, sys.maxsize, size=(DEFAULT_CONFIG.n_experiments,))

        results = mesa.batch_run(
            model_cls=CrowdModelWrapper,
            parameters=EXP['batch_params'],
            rng=seed_values.tolist(),
            max_steps=EXP.get("max_steps", 2000),
            number_processes=DEFAULT_CONFIG.n_processes,
            data_collection_period=1,
            display_progress=True,
        )

        results_df = pd.DataFrame(results)
        results_df.to_csv(os.path.join(DEFAULT_CONFIG.LOGS_DIR, f"experiments_results_{EXP['title'].replace(' ', '_').lower()}.csv"), index=False)