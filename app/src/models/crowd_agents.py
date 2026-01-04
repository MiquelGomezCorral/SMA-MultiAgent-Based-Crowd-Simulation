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

    def __init__(self, model, agent_type: CrowdAgentEnum = CrowdAgentEnum.POLITE, track_last_steps: int = 5):
        super().__init__(model)
        self.agent_type = agent_type
        self.cells_moved = 0
        self.cells_moved_last_steps = [0] * track_last_steps  # For averaging speed over last steps

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

        # Skip movement based on speed probability
        if self.random.random() > self.speed:
            return 
        
        # Move to closest exit among empty neighboring cells
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
        min_distance = min([val["Total"] for val in self.cell.exit_distances.values()])
        chosen_cell = self.cell
        moved = False
        for cell in valid_neighbors:
            for exit_idx, exit_distance in cell.exit_distances.items():
                if exit_distance["Total"] < min_distance:
                    min_distance = exit_distance["Total"]
                    chosen_cell = cell
                    moved = True

        return chosen_cell, moved
    
    
    def compute_local_density(self, proportion: bool = False):
        """
        Compute the local density of agents around this agent within a given radius.
        
        :param radius: Radius around the agent to consider
        :param proportion: If True, return proportion of occupied cells (0 to 1); else return count

        return: Local density as proportion or count
        """
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