"""Basic model parameters definitions."""


basic_model_params = {
    "initial_agents": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 1,
        "max": 100,
        "step": 1,
    },
    "width": {
        "type": "SliderInt",
        "value": 30,
        "label": "Grid width:",
        "min": 5,
        "max": 50,
        "step": 1,
    },
    "height": {
        "type": "SliderInt",
        "value": 30,
        "label": "Grid height:",
        "min": 5,
        "max": 50,
        "step": 1,
    },
    "track_last_steps": {
        "type": "SliderInt",
        "value": 5,
        "label": "Track last steps for speed:",
        "min": 1,
        "max": 20,
        "step": 1,
    },
    "polite_ratio": {
        "type": "SliderFloat",
        "value": 0.5,
        "label": "Polite ratio:",
        "min": 0.0,
        "max": 1.0,
        "step": 0.1,
    },
    "aggressive_ratio": {
        "type": "SliderFloat",
        "value": 0.3,
        "label": "Aggressive ratio:",
        "min": 0.0,
        "max": 1.0,
        "step": 0.1,
    },
    "slow_ratio": {
        "type": "SliderFloat",
        "value": 0.2,
        "label": "Slow ratio:",
        "min": 0.0,
        "max": 1.0,
        "step": 0.1,
    },
}
