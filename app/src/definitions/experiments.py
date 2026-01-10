from src.config import Configuration

def get_experiments(CONFIG: Configuration):
    """Define different experiment configurations."""
    EXPERIMENTS = [
        {
            "title": "...",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [10, 25, 50, 75, 100, 150, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "polite_ratio": 1.0,
                "aggressive_ratio": 0.0,
                "slow_ratio": 0.0,
                "scenario_type": CONFIG.scenario_type,
                "n_exits": CONFIG.n_exits,
            }
        }
    ]

    return EXPERIMENTS