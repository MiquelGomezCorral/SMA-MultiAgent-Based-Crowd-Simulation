"""Module defining crowd agents for the simulation."""

import numpy as np
from mesa.discrete_space import CellAgent
from src.definitions import CrowdAgentEnum, STATIC_AGENTS, CROWD_AGENT_STATS
# ==================================================================
#                               AGENT
# ==================================================================
class CrowdAgent(CellAgent):
    """And agent that moves in a crowd following simple rules."""

    def __init__(self, model, agent_type: CrowdAgentEnum = CrowdAgentEnum.POLITE, track_last_steps: int = 5, number_of_exits: int = None):
        super().__init__(model)
        if track_last_steps <= 0:
            raise ValueError("track_last_steps must be a positive integer.")
        
        self.agent_type = agent_type
        self.cells_moved = 0
        self.cells_moved_last_steps = [0] * track_last_steps  # For averaging speed over last steps
        self.exit_idx = (
            model.random.randint(0, number_of_exits - 1) 
            if number_of_exits is not None else None
        )
        # The speed determines the probability of moving each step
        # The higher the speed, the more likely the agent is to move
        self.speed = np.random.uniform(*CROWD_AGENT_STATS[agent_type]["speed_range"])
        self.crowd_slowdown_factor = CROWD_AGENT_STATS[agent_type]["crowd_slowdown_factor"]
        self.start_crowd_slowdown_factor = CROWD_AGENT_STATS[agent_type]["start_crowd_slowdown_factor"]
        self.dead_lock_factor = CROWD_AGENT_STATS[agent_type]["dead_lock_factor"]
        self.dead_lock_counter = 0
        self.max_dead_lock_counter = CROWD_AGENT_STATS[agent_type]["max_dead_lock_counter"]

    def step(self):
        """
        Move the agent towards the nearest exit based on its speed.
        Agents have a probability of moving each step based on their speed.
        """
        if self.cell is None:
            return
        
        # Remove agent if reached exit (i.e., neighboring an exit cell)
        if any(
            any( # Check if any agent in neighbor cell is an exit matching this agent's exit_idx
                agent.agent_type == CrowdAgentEnum.EXIT 
                and (agent.exit_idx == self.exit_idx or self.exit_idx is None) 
                for agent in neighbor.agents
            ) 
            for neighbor in self.cell.neighborhood
        ):
            self.cell = None
            self.model.agents.remove(self)
            return

        # Else move
        self.move()
    
    def move(self):
        """Move to closest exit among empty neighboring cells"""
        
        moved = False
        
        # Skip movement based on speed probability
        if self.random.random() <= self.speed:
            # Apply crowd slowdown factor
            agent_neighbors = self.get_agent_neighbors()
            crowd = 8 - len(agent_neighbors)
            slowdown = (
                self.crowd_slowdown_factor * 
                (crowd - self.start_crowd_slowdown_factor) / 
                (8 - self.start_crowd_slowdown_factor)
            )

            if self.random.random() >= slowdown:
                valid_neighbors = self.get_empty_neighbors()
                self.cell, moved = self.choose_cell(valid_neighbors)
                self.cells_moved += int(moved)
                if moved:
                    self.dead_lock_counter = max(0, self.dead_lock_counter - 2)
                else:
                    # Increase own counter and add damped influence from neighbors
                    neighbor_influence = 0
                    if agent_neighbors:
                        avg_neighbor_deadlock = np.mean([a.dead_lock_counter for a in agent_neighbors])
                        neighbor_influence = 0.1 * (avg_neighbor_deadlock - self.dead_lock_counter)
                    
                    self.dead_lock_counter += 1 + neighbor_influence
                    # Optional: cap to prevent unbounded growth
                    self.dead_lock_counter = min(self.dead_lock_counter, 30)

        # Always update tracking for this step (moved or not)
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
        if best_min_distance <= current_min_distance + self.dead_lock_factor * self.dead_lock_counter:
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
        
        surrounding_agents = [
            cell for cell in self.cell.neighborhood 
            if all([agent.agent_type not in STATIC_AGENTS for agent in cell.agents]) 
            and not cell.is_empty
        ]

        occupied_cells = len(surrounding_agents)

        if proportion:
            total_cells = len(self.cell.neighborhood)
            return occupied_cells / total_cells if total_cells > 0 else 0
        else:
            return occupied_cells
    
    def get_empty_neighbors(self):
        """Get list of empty neighboring cells."""
        return [
            neighbor for neighbor in self.cell.neighborhood 
            if neighbor.is_empty
        ]
    def get_agent_neighbors(self):
        """Get list of neighboring cells that contain agents."""
        return [
            agent 
            for neighbor in self.cell.neighborhood 
                if any(
                    agent.agent_type not in STATIC_AGENTS 
                    for agent in neighbor.agents
                )
            for agent in neighbor.agents
        ]
        
    
    def get_dead_lock_factor(self):
        """Get the dead lock factor for this agent."""
        return self.dead_lock_factor * self.dead_lock_counter
    
# ==================================================================
#                               OBJECTS
# ==================================================================
class CrowdExit(CellAgent):
    """An exit cell where agents can leave the simulation."""

    def __init__(self, model, exit_idx: int):
        super().__init__(model)
        self.agent_type = CrowdAgentEnum.EXIT
        self.exit_idx = exit_idx

    def step(self):
        pass

class CrowdWall(CellAgent):
    """A wall cell that agents cannot pass through."""

    def __init__(self, model):
        super().__init__(model)
        self.agent_type = CrowdAgentEnum.WALL

    def step(self):
        pass