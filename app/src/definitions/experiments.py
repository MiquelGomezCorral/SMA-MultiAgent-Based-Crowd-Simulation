from src.config import Configuration

def get_experiments(CONFIG: Configuration):
    """Define different experiment configurations."""
    EXPERIMENTS = [
        # =====================================================================
        # Experiment: AGENT DENSITY IMPACT
        # =====================================================================
        {
            "title": "Agent Densities MALL",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [10, 25, 50, 75, 100, 125, 150, 175, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "respawn_agents": CONFIG.respawn_agents,
                "polite_ratio": 1.0,
                "aggressive_ratio": 0.0,
                "slow_ratio": 0.0,
                "scenario_type": ["MALL"],
                "n_exits": CONFIG.n_exits,
            }
        },
                {
            "title": "Agent Densities SEATS",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [10, 25, 50, 75, 100, 125, 150, 175, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "respawn_agents": CONFIG.respawn_agents,
                "polite_ratio": 1.0,
                "aggressive_ratio": 0.0,
                "slow_ratio": 0.0,
                "scenario_type": ["SEATS"],
                "n_exits": CONFIG.n_exits,
            }
        },
                {
            "title": "Agent Densities SNAKE",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [10, 25, 50, 75, 100, 125, 150, 175, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "respawn_agents": CONFIG.respawn_agents,
                "polite_ratio": 1.0,
                "aggressive_ratio": 0.0,
                "slow_ratio": 0.0,
                "scenario_type": ["SNAKE"],
                "n_exits": CONFIG.n_exits,
            }
        },
                {
            "title": "Agent Densities CORRIDOR",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [10, 25, 50, 75, 100, 125, 150, 175, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "respawn_agents": CONFIG.respawn_agents,
                "polite_ratio": 1.0,
                "aggressive_ratio": 0.0,
                "slow_ratio": 0.0,
                "scenario_type": ["CORRIDOR"],
                "n_exits": CONFIG.n_exits,
            }
        },

        # =====================================================================
        # Experiment: AGENT DENSITY IMPACT ALL
        # =====================================================================
        {
            "title": "Agent Densities MALL ALL",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [10, 25, 50, 75, 100, 125, 150, 175, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "respawn_agents": CONFIG.respawn_agents,
                "polite_ratio": CONFIG.agent_types_ratios["polite"],
                "aggressive_ratio": CONFIG.agent_types_ratios["aggressive"],
                "slow_ratio": CONFIG.agent_types_ratios["slow"],
                "scenario_type": ["MALL"],
                "n_exits": CONFIG.n_exits,
            }
        },
                {
            "title": "Agent Densities SEATS ALL",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [10, 25, 50, 75, 100, 125, 150, 175, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "respawn_agents": CONFIG.respawn_agents,
                "polite_ratio": CONFIG.agent_types_ratios["polite"],
                "aggressive_ratio": CONFIG.agent_types_ratios["aggressive"],
                "slow_ratio": CONFIG.agent_types_ratios["slow"],
                "scenario_type": ["SEATS"],
                "n_exits": CONFIG.n_exits,
            }
        },
                {
            "title": "Agent Densities SNAKE ALL",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [10, 25, 50, 75, 100, 125, 150, 175, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "respawn_agents": CONFIG.respawn_agents,
                "polite_ratio": CONFIG.agent_types_ratios["polite"],
                "aggressive_ratio": CONFIG.agent_types_ratios["aggressive"],
                "slow_ratio": CONFIG.agent_types_ratios["slow"],
                "scenario_type": ["SNAKE"],
                "n_exits": CONFIG.n_exits,
            }
        },
                {
            "title": "Agent Densities CORRIDOR ALL",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [10, 25, 50, 75, 100, 125, 150, 175, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "respawn_agents": CONFIG.respawn_agents,
                "polite_ratio": CONFIG.agent_types_ratios["polite"],
                "aggressive_ratio": CONFIG.agent_types_ratios["aggressive"],
                "slow_ratio": CONFIG.agent_types_ratios["slow"],
                "scenario_type": ["CORRIDOR"],
                "n_exits": CONFIG.n_exits,
            }
        },
        # =====================================================================
        # Experiment: Vary agent behavior ratios
        # =====================================================================


        {
            "title": "Aggressive Agents Impact",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [125, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "respawn_agents": CONFIG.respawn_agents,
                "polite_ratio": 1.0,
                "aggressive_ratio": [1.0, 0.8, 0.5, 0.25, 0.1, 0.0],
                "slow_ratio": 0.0,
                "scenario_type": ["SEATS"],
                "n_exits": CONFIG.n_exits,
            }
        },
        {
            "title": "Slow Agents Impact",
            "batch_params": {
                "width": CONFIG.width,
                "height": CONFIG.height,
                "initial_agents": [125, 200, 300],
                "track_last_steps": CONFIG.track_last_steps,
                "path_finding_algorithm": CONFIG.path_finding_algorithm,
                "differentiate_exits": CONFIG.differentiate_exits,
                "respawn_agents": CONFIG.respawn_agents,
                "polite_ratio": 1.0,
                "aggressive_ratio": 0.0,
                "slow_ratio": [1.0, 0.8, 0.5, 0.25, 0.1, 0.0],
                "scenario_type": ["SEATS"],
                "n_exits": CONFIG.n_exits,
            }
        },
        # {
        #     "title": "A* vs BFS Path Finding",
        #     "batch_params": {
        #         "width": CONFIG.width,
        #         "height": CONFIG.height,
        #         "initial_agents": CONFIG.initial_agents,
        #         "track_last_steps": CONFIG.track_last_steps,
        #         "path_finding_algorithm": ["A*", "BFS"],
        #         "differentiate_exits": CONFIG.differentiate_exits,
        #         "respawn_agents": CONFIG.respawn_agents,
        #         "polite_ratio": CONFIG.agent_types_ratios["polite"],
        #         "aggressive_ratio": CONFIG.agent_types_ratios["aggressive"],
        #         "slow_ratio": CONFIG.agent_types_ratios["slow"],
        #         "scenario_type": ["MALL", "SEATS", "SNAKE", "CORRIDOR"],
        #         "n_exits": CONFIG.n_exits,
        #     }
        # },
        # {
        #     "title": "Exit preference Impact",
        #     "batch_params": {
        #         "width": CONFIG.width,
        #         "height": CONFIG.height,
        #         "initial_agents": CONFIG.initial_agents,
        #         "track_last_steps": CONFIG.track_last_steps,
        #         "path_finding_algorithm": CONFIG.path_finding_algorithm,
        #         "differentiate_exits": [True, False],
        #         "respawn_agents": CONFIG.respawn_agents,
        #         "polite_ratio": CONFIG.agent_types_ratios["polite"],
        #         "aggressive_ratio": CONFIG.agent_types_ratios["aggressive"],
        #         "slow_ratio": CONFIG.agent_types_ratios["slow"],
        #         "scenario_type": ["MALL", "SEATS", "SNAKE", "CORRIDOR"],
        #         "n_exits": CONFIG.n_exits,
        #     }
        # },

    ]

    return EXPERIMENTS