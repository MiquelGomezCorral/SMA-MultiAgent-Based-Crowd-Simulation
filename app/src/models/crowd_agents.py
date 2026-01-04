"""Module defining crowd agents for the simulation."""

import numpy as np
from mesa.discrete_space import CellAgent

# ==================================================================
#                               AGENT
# ==================================================================
class CrowdAgentEnum(str):
    POLITE = "polite"
    AGGRESSIVE = "aggressive"
    SLOW = "slow"
    EXIT = "exit"
    WALL = "wall"

STATIC_AGENTS = [CrowdAgentEnum.EXIT, CrowdAgentEnum.WALL]

class CrowdAgent(CellAgent):
    """And agent that moves in a crowd following simple rules."""

    def __init__(self, model, agent_type: CrowdAgentEnum = CrowdAgentEnum.POLITE, track_last_steps: int = 5, number_of_exits: int = None):
        super().__init__(model)
        self.agent_type = agent_type
        self.cells_moved = 0
        self.cells_moved_last_steps = [0] * track_last_steps  # For averaging speed over last steps
        self.exit_idx = model.random.randint(0, number_of_exits - 1) if number_of_exits is not None else None
        # The speed determines the probability of moving each step
        # The higher the speed, the more likely the agent is to move
        if agent_type == CrowdAgentEnum.POLITE:
            self.speed = np.random.uniform(0.65, 1.0)
        elif agent_type == CrowdAgentEnum.AGGRESSIVE:
            self.speed = np.random.uniform(0.8, 1.0)
        elif agent_type == CrowdAgentEnum.SLOW:
            self.speed = np.random.uniform(0.5, 0.65)


    def step(self):
        """
        Move the agent towards the nearest exit based on its speed.
        Agents have a probability of moving each step based on their speed.
        """
        if self.cell is None:
            return
        
        # Remove agent if reached exit (i.e., neighboring an exit cell)
        if any(
            any(agent.agent_type == CrowdAgentEnum.EXIT for agent in neighbor.agents) 
            for neighbor in self.cell.neighborhood
        ):
            self.cell = None
            self.model.agents.remove(self)
            return

        # Else move
        self.move()
    
    def move(self):
        """Move to closest exit among empty neighboring cells"""
        # Skip movement based on speed probability
        if self.random.random() > self.speed:
            return 
        
        valid_neighbors = [cell for cell in self.cell.neighborhood if cell.is_empty]
        if valid_neighbors:
            self.cell, moved = self.choose_cell(valid_neighbors)
            self.cells_moved += int(moved)
            # Rotate the last steps list to keep only the last 5 steps
            self.cells_moved_last_steps.pop(0)
            self.cells_moved_last_steps.append(int(moved))

    def choose_cell(self, valid_neighbors):
        """
        Choose the neighboring cell that is closest to any exit.
        :param valid_neighbors: List of neighboring cells that are valid for movement
        """
        def get_cell_min_distance(cell):
            """Get minimum distance from cell to target exit(s)."""
            if self.exit_idx is None:
                # Find distance to closest exit
                return min(dist["Total"] for dist in cell.exit_distances.values())
            else:
                # Get distance to assigned exit only
                exit_distance = cell.exit_distances.get(self.exit_idx)
                return exit_distance["Total"] if exit_distance else float('inf')
        
        # Find the neighbor with minimum distance to target exit
        best_cell = min(valid_neighbors, key=get_cell_min_distance, default=None)
        
        if best_cell is None:
            return self.cell, False
        
        # Check if the best neighbor is better than staying in current cell
        current_min_distance = get_cell_min_distance(self.cell)
        best_min_distance = get_cell_min_distance(best_cell)
        
        if best_min_distance < current_min_distance:
            return best_cell, True
        
        return self.cell, False
    
    
    def compute_local_density(self, proportion: bool = False):
        """
        Compute the local density of agents around this agent within a given radius.
        
        :param radius: Radius around the agent to consider
        :param proportion: If True, return proportion of occupied cells (0 to 1); else return count

        return: Local density as proportion or count
        """
        # Agent has been removed from grid
        if self.cell is None:
            return 0
        
        surounding_agents = [
            cell for cell in self.cell.neighborhood 
            if all([agent.agent_type not in STATIC_AGENTS for agent in cell.agents]) 
            and not cell.is_empty
        ]

        occupied_cells = len(surounding_agents)

        if proportion:
            total_cells = len(self.cell.neighborhood)
            return occupied_cells / total_cells if total_cells > 0 else 0
        else:
            return occupied_cells
  
    
# ==================================================================
#                               OBJECTS
# ==================================================================
class CrowdExit(CellAgent):
    """An exit cell where agents can leave the simulation."""

    def __init__(self, model):
        super().__init__(model)
        self.agent_type = CrowdAgentEnum.EXIT

    def step(self):
        pass

class CrowdWall(CellAgent):
    """A wall cell that agents cannot pass through."""

    def __init__(self, model):
        super().__init__(model)
        self.agent_type = CrowdAgentEnum.WALL

    def step(self):
        pass