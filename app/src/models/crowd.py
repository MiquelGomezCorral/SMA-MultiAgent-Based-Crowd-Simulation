import numpy as np
from typing import Literal
import mesa
from mesa import DataCollector
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid


from src.config import Configuration
from src.data import compute_total_agents, compute_local_density, compute_evacuation_rate
from src.utils import get_manhattan_distance

# ==================================================================
#                               MODEL
# ==================================================================
class CrowdModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, CONFIG: Configuration):
        super().__init__(seed=CONFIG.seed)
        self.initial_agents = CONFIG.initial_agents
        self.current_agents = CONFIG.initial_agents
        self.agent_types_ratios = CONFIG.agent_types_ratios
        self._normalize_ratios()


        # ========== CREATE GRID ==========
        self.grid = OrthogonalMooreGrid(
            (CONFIG.width, CONFIG.height), 
            torus=False, 
            random=self.random
        )
    
        # ========== CREATE AGENTS ==========
        self._create_agents()
        self._create_exits()

        # ========== CREATE COLLECTORS ==========
        self.datacollector = DataCollector(
            model_reporters={
                "total_agents": compute_total_agents,
                "local_density": compute_local_density,
                "evacuation_rate": compute_evacuation_rate
            },
            agent_reporters={},
        )
        self.datacollector.collect(self)

    def step(self):
        self.agents.shuffle_do("step")
        self._update_agent_count()
        self.datacollector.collect(self)
        self.check_model_end()
    
    def check_model_end(self):
        """Check if there are any active agents left in the model."""
        active_agents = [
            a for a in self.agents 
            if a.agent_type not in ["exit", "wall"]
        ]

        if len(active_agents) == 0:
            self.running = False

    def _update_agent_count(self):
        """Update the current number of active agents."""
        self.current_agents = len([
            a for a in self.agents 
            if a.agent_type not in ["exit", "wall"]
        ])

    def _normalize_ratios(self):
        total = sum(self.agent_types_ratios.values())
        for key in self.agent_types_ratios:
            self.agent_types_ratios[key] /= total

    def _create_agents(self):
        """Create agents and place them randomly on the grid."""
        agents = []
        cells = self.random.sample(self.grid.all_cells.cells, k=self.initial_agents)
        
        for agent_type, ratio in self.agent_types_ratios.items():
            n_type_agents = int(np.round(self.initial_agents * ratio))
            agents += CrowdAgent.create_agents(
                self,
                n_type_agents,
                agent_type = agent_type,
            )

        for agent, cell in zip(agents, cells):
            agent.cell = cell

    def _create_exits(self):
        """Create exit agents at predefined locations and compute distances."""
        self.exit_cells = [
            self.grid[(0, self.grid.height // 2)],
            self.grid[(self.grid.width - 1, self.grid.height // 2)],
        ]
        self.n_exits = len(self.exit_cells)

        for idx, cell in enumerate(self.exit_cells):
            exit_agent = CrowdExit(self)
            exit_agent.cell = cell
            self._compute_exit_distance(cell, idx)

    def _compute_exit_distance(self, exit_cell, idx):
        """Compute and store the distance from all cells to the given exit cell."""
        for cell in self.grid.all_cells.cells:
            if not hasattr(cell, 'exit_distances'):
                cell.exit_distances = {}

            cell.exit_distances[idx] = get_manhattan_distance(cell, exit_cell)


class CrowdModelWrapper(CrowdModel):
    def __init__(self, initial_agents=50, width=10, height=10, seed=42,
                 polite_ratio=0.5, aggressive_ratio=0.3, slow_ratio=0.2):
        config = Configuration(
            initial_agents=initial_agents,
            width=width,
            height=height,
            seed=seed,
            agent_types_ratios={
                "polite": polite_ratio,
                "aggressive": aggressive_ratio,
                "slow": slow_ratio
            }
        )
        super().__init__(config)



# ==================================================================
#                               AGENT
# ==================================================================

class CrowdAgent(CellAgent):
    """And agent that moves in a crowd following simple rules."""

    def __init__(self, model, agent_type: Literal["polite", "aggressive", "slow"] = "polite"):
        super().__init__(model)
        self.agent_type = agent_type

        # The speed determines the probability of moving each step
        # The higher the speed, the more likely the agent is to move
        if agent_type == "polite":
            self.speed = np.random.uniform(0.65, 1.0)
        elif agent_type == "aggressive":
            self.speed = np.random.uniform(0.8, 1.0)
        elif agent_type == "slow":
            self.speed = np.random.uniform(0.5, 0.65)


    def step(self):
        if self.cell is None:
            return
        
        # Remove agent if reached exit
        if min(self.cell.exit_distances.values()) <= 1:
            self.cell = None
            self.model.agents.remove(self)
            return

        # Skip movement based on speed probability
        if self.random.random() > self.speed:
            return 
        
        # Move to closest exit among empty neighboring cells
        valid_neighbors = [cell for cell in self.cell.neighborhood if cell.is_empty]
        if valid_neighbors:
            self.cell = self.choose_cell(valid_neighbors)

    def choose_cell(self, valid_neighbors):
        min_distance = min(self.cell.exit_distances.values())
        chosen_cell = self.cell

        for cell in valid_neighbors:
            for exit_idx, exit_distance in cell.exit_distances.items():
                if exit_distance < min_distance:
                    min_distance = exit_distance
                    chosen_cell = cell

        return chosen_cell
    
    
    def compute_local_density(self, proportion: bool = False):
        """
        Compute the local density of agents around this agent within a given radius.
        
        :param radius: Radius around the agent to consider
        :param proportion: If True, return proportion of occupied cells (0 to 1); else return count

        return: Local density as proportion or count
        """
        surounding_agents = [
            cell for cell in self.cell.neighborhood if all([agent.agent_type != "exit" for agent in cell.agents]) and not cell.is_empty
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
        self.agent_type = "exit"

    def step(self):
        pass