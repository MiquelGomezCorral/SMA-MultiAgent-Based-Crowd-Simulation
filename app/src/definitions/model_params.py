"""Basic model parameters definitions."""


basic_model_params = {
    "n_agents": {
        "type": "SliderInt",
        "value": 50,
        "label": "Number of agents:",
        "min": 10,
        "max": 200,
        "step": 1,
    },
    "width": {
        "type": "SliderInt",
        "value": 10,
        "label": "Grid width:",
        "min": 5,
        "max": 50,
        "step": 1,
    },
    "height": {
        "type": "SliderInt",
        "value": 10,
        "label": "Grid height:",
        "min": 5,
        "max": 50,
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
