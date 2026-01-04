"""Functions that compute data from the model."""


def compute_total_agents(model):
    """Compute the total number of agents in the model."""
    return len(model.agents) - len(model.exit_cells)  # Exclude exit agents

def compute_local_density(model, proportion: bool = False):
    """
    Compute the average local density of agents in the model.
    
    :param model: The CrowdModel instance
    :param proportion: If True, compute proportion of occupied cells; else compute count

    :return: Average local density of agents
    """
    real_agents = [
        agent.compute_local_density(proportion=proportion) for agent in model.agents if agent.agent_type != "exit"
    ]
    return (
        sum(real_agents) / compute_total_agents(model) 
        if compute_total_agents(model) > 0 else 0
    )