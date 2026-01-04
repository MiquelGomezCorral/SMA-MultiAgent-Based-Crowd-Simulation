"""Functions that compute data from the model."""


def compute_total_agents(model):
    """Compute the total number of agents in the model."""
    return len(model.agents) - len(model.exit_cells)  # Exclude exit agents