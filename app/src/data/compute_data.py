"""Functions that compute data from the model."""
import numpy as np 

def compute_local_density(model, proportion: bool = False):
    """
    Compute the average local density of agents in the model.
    
    :param model: The CrowdModel instance
    :param proportion: If True, compute proportion of occupied cells; else compute count

    :return: Average local density of agents
    """
    real_agents = [
        agent.compute_local_density(proportion=proportion) for agent in model.get_moving_agents()
    ]
    return (
        sum(real_agents) / model.current_agents 
        if model.current_agents > 0 else 0
    )

def compute_evacuation_rate(model):
    """Compute the evacuation rate of agents in the model."""
    return compute_evacuation_rate_by_type(model, "Total")

def compute_macro_average_speed(model):
    """Compute the average speed of agents in the model for the whole simulation."""
    return compute_macro_average_speed_by_type(model, "Total")

def compute_micro_average_speed(model):
    """Compute the average blocks agents move per tick (last N steps)."""
    real_agents = model.get_moving_agents()
    if len(real_agents) == 0:
        return 0
    
    total_cells_moved = np.sum([
        np.sum(agent.cells_moved_last_steps)
        for agent in real_agents
    ])
    return total_cells_moved / (model.track_last_steps * len(real_agents))

def compute_evacuation_rate_by_type(model, agent_type):
    """Compute the evacuation rate for a specific agent type."""
    
    initial_count = model.initial_agents.get(agent_type, 0)
    if initial_count == 0 or model.steps == 0:
        return 0
    
    current_count = model.compute_agents_by_type(agent_type)
    evacuated_agents = initial_count - current_count
    return evacuated_agents / model.steps

def compute_macro_average_speed_by_type(model, agent_type):
    """Compute the macro average speed for a specific agent type."""
    agents_of_type = model.get_agents_by_type(agent_type)
    
    if model.steps == 0 or len(agents_of_type) == 0:
        return 0
    
    total_cells_moved = np.sum([agent.cells_moved for agent in agents_of_type])
    return total_cells_moved / (model.steps * len(agents_of_type))

def compute_average_dead_lock_factor(model):
    """Compute the average dead lock factor for all moving agents."""
    return np.mean([
        agent.get_dead_lock_factor() for agent in model.get_moving_agents()
    ]) if model.current_agents > 0 else 0