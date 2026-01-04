"""Functions that compute data from the model."""

def compute_total_agents(model):
    """Compute the total number of agents in the model."""
    return model.current_agents

def compute_local_density(model, proportion: bool = False):
    """
    Compute the average local density of agents in the model.
    
    :param model: The CrowdModel instance
    :param proportion: If True, compute proportion of occupied cells; else compute count

    :return: Average local density of agents
    """
    real_agents = [
        agent.compute_local_density(proportion=proportion) for agent in model.agents if agent.agent_type not in model.STATIC_AGENTS
    ]
    return (
        sum(real_agents) / model.current_agents 
        if model.current_agents > 0 else 0
    )

def compute_evacuation_rate(model):
    """Compute the evacuation rate of agents in the model."""
    evacuated_agents = model.initial_agents - model.current_agents
    return evacuated_agents / model.steps if model.steps > 0 else 0

def compute_macro_average_speed(model):
    """Compute the average speed of agents in the model for the whole simulation."""
    real_agents = [agent for agent in model.agents if agent.agent_type not in model.STATIC_AGENTS]
    total_cells_moved = sum(agent.cells_moved for agent in real_agents)
    return (
        total_cells_moved / (model.steps * len(real_agents)) 
        if model.steps > 0 and len(real_agents) > 0 else 0
    )

def compute_micro_average_speed(model):
    """Compute the average speed of agents in the model for the last track_last_steps steps."""
    real_agents = [agent for agent in model.agents if agent.agent_type not in model.STATIC_AGENTS]
    total_cells_moved = sum(
        sum(agent.cells_moved_last_steps) / model.track_last_steps 
        for agent in real_agents
    )

    return (
        total_cells_moved / (model.steps * len(real_agents)) 
        if model.steps > 0 and len(real_agents) > 0 else 0
    )