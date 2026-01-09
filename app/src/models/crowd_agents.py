"""Module defining crowd agents for the simulation."""

import numpy as np
from mesa.discrete_space import CellAgent
from src.definitions import CrowdAgentEnum, STATIC_AGENTS, CROWD_AGENT_STATS
# ==================================================================
#                               AGENT
# ==================================================================
class CrowdAgent(CellAgent):
    """And agent that moves in a crowd following simple rules."""

    def __init__(self,
        model,
        agent_type: CrowdAgentEnum = CrowdAgentEnum.POLITE,
        track_last_steps: int = 5,
        number_of_exits: int = None,
        respawn: bool = False,
    ):
        super().__init__(model)
        if track_last_steps <= 0:
            raise ValueError("track_last_steps must be a positive integer.")
        
        self.agent_type = agent_type
        self.respawn = respawn
        self.track_last_steps = track_last_steps
        
        self.exit_idx = (
            model.random.randint(0, number_of_exits - 1) 
            if number_of_exits is not None else None
        )
        
        self.speed = np.random.uniform(*CROWD_AGENT_STATS[agent_type]["speed_range"])
        self.crowd_slowdown_factor = CROWD_AGENT_STATS[agent_type]["crowd_slowdown_factor"]
        self.start_crowd_slowdown_factor = CROWD_AGENT_STATS[agent_type]["start_crowd_slowdown_factor"]
        self.dead_lock_factor = CROWD_AGENT_STATS[agent_type]["dead_lock_factor"]
        self.max_dead_lock_counter = CROWD_AGENT_STATS[agent_type]["max_dead_lock_counter"]

        self._reset_agent_state()

    def step(self):
        """
        Move the agent towards the nearest exit based on its speed.
        Agents have a probability of moving each step based on their speed.
        """
        if self.cell is None:
            return
        
        finished = self._check_agent_finished()

        if not finished:
            # Agent continues moving toward exit
            self.move()
        else:
            # Agent has reached an exit
            self.model.update_evacuated_counter(self.agent_type)
            
            if not self.respawn:
                # Remove agent from the model
                self.cell = None
                self.model.agents.remove(self)
            else:
                # Respawn agent at a random empty cell that's not adjacent to target exit
                self._respawn_agent()
                
        
    
    def move(self):
        """Move to closest exit among empty neighboring cells"""
        moved = False
        
        # Skip movement based on speed probability
        # The speed determines the probability of moving each step
        # The higher the speed, the more likely the agent is to move
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
    
    def _check_agent_finished(self):
        # Remove agent if reached exit (i.e., neighboring an exit cell)
        return self._is_cell_finished(self.cell)
    
    def _is_cell_finished(self, cell):
        """Check if being at a given cell would mean the agent is finished."""
        return any(
            any( # Check if any agent in neighbor cell is an exit matching this agent's exit_idx
                agent.agent_type == CrowdAgentEnum.EXIT 
                and (agent.exit_idx == self.exit_idx or self.exit_idx is None) 
                for agent in neighbor.agents
            ) 
            for neighbor in cell.neighborhood
        )
    
    def _respawn_agent(self):
        """Handle agent respawning logic after reaching an exit."""
        empty_cells = self.model.get_empty_cells()
        
        # Filter out cells adjacent to the agent's target exit to avoid immediate re-finishing
        valid_respawn_cells = [
            cell for cell in empty_cells
            if not self._is_cell_finished(cell)
        ]
        
        if valid_respawn_cells:
            self.cell = self.random.choice(valid_respawn_cells)
            self._reset_agent_state()
        elif empty_cells:
            # Fallback: use any empty cell if no valid respawn cells
            self.cell = self.random.choice(empty_cells)
            self._reset_agent_state()
        else:
            # No empty cells available - remove agent and log warning
            if not hasattr(self.model, 'respawn_warning_logged'):
                self.model.capacity_warning = "⚠️ Respawn failed: No empty cells available. Some agents removed."
                self.model.respawn_warning_logged = True
            self.cell = None
            self.model.agents.remove(self)
    
    def _reset_agent_state(self):
        """Reset agent tracking variables after respawning."""
        self.cells_moved = 0
        self.cells_moved_last_steps = [0] * self.track_last_steps
        self.dead_lock_counter = 0
    
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