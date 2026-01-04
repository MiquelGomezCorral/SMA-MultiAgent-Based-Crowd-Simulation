"""Model module for the Crowd Simulation."""

import heapq
import numpy as np
import mesa
from mesa import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid

from src.config import Configuration
from src.data import (
    compute_total_agents, compute_local_density, compute_evacuation_rate,
    compute_macro_average_speed, compute_micro_average_speed
)
from src.utils import get_manhattan_distance, get_l2_distance

from .crowd_agents import CrowdAgent, CrowdExit, CrowdAgentEnum, CrowdWall, STATIC_AGENTS

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
        self.track_last_steps = CONFIG.track_last_steps
        self.path_finding_algorithm = CONFIG.path_finding_algorithm
        self.STATIC_AGENTS = STATIC_AGENTS
        self._normalize_ratios()


        # ========== CREATE GRID ==========
        self.grid = OrthogonalMooreGrid(
            (CONFIG.width, CONFIG.height), 
            torus=False, 
            random=self.random
        )
    
        # ========== CREATE AGENTS ==========
        self._create_walls()
        self._create_exits()
        self._create_agents()

        # ========== CREATE COLLECTORS ==========
        self.datacollector = DataCollector(
            model_reporters={
                "total_agents": compute_total_agents,
                "local_density": compute_local_density,
                "evacuation_rate": compute_evacuation_rate,
                "macro_average_speed": compute_macro_average_speed,
                "micro_average_speed": compute_micro_average_speed,
            },
            agent_reporters={},
        )
        self.datacollector.collect(self)
        self._initialize_max_values()

    def step(self):
        priority = self.agents.select(lambda a: a in self.priority_agents)
        others = self.agents.select(lambda a: a in self.other_agents)
        # 2. Step them in order
        priority.shuffle_do("step")  # Priority moves first
        others.shuffle_do("step")

        self._update_agent_count()
        self.datacollector.collect(self)
        self._update_max_values()
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
        self.priority_agents = []
        self.other_agents = []
        empty_cells = [c for c in self.grid.all_cells if c.is_empty]
        if len(empty_cells) < self.initial_agents:
            raise ValueError("Not enough empty cells to place all agents.")
        cells = self.random.sample(empty_cells, k=self.initial_agents)
        
        for agent_type, ratio in self.agent_types_ratios.items():
            n_type_agents = int(np.round(self.initial_agents * ratio))
            agents = CrowdAgent.create_agents(
                self,
                n_type_agents,
                agent_type = agent_type,
                track_last_steps = self.track_last_steps,
                exit_idx = np.random.randint(0, self.n_exits)
            )
            if agent_type == CrowdAgentEnum.AGGRESSIVE:
                self.priority_agents.extend(agents)
            else: 
                self.other_agents.extend(agents)

        for agent, cell in zip(self.priority_agents + self.other_agents, cells):
            agent.cell = cell

    def _create_walls(self):
        """Create wall agents around the grid perimeter."""
        for xx in range(-1, 1):
            x = xx + self.grid.width // 2 
            for y in range(3, self.grid.height - 3):
                if y == self.grid.height // 2 or y == (self.grid.height // 2) - 1 or y == (self.grid.height // 2) + 1:
                    continue  # Leave exit gap
                wall_agent = CrowdWall(self)
                wall_agent.cell = self.grid[(x, y)]

    def _create_exits(self):
        """Create exit agents at predefined locations and compute distances."""
        self.exit_cells = [
            self.grid[(0, 0)],
            # self.grid[(0, self.grid.height // 2)],
            # self.grid[(self.grid.width - 1, self.grid.height // 2)],
            # self.grid[(self.grid.width // 3, self.grid.height // 2)],
            # self.grid[(2 * self.grid.width // 3, self.grid.height // 2)],
        ]
        self.n_exits = len(self.exit_cells)

        for idx, cell in enumerate(self.exit_cells):
            exit_agent = CrowdExit(self)
            exit_agent.cell = cell
            self._compute_exit_distance(cell, idx)

    def _compute_exit_distance(self, exit_cell, idx):
        """Compute and store the distance from all cells to the given exit cell."""
        if self.path_finding_algorithm == "MANHATTAN":
            for cell in self.grid.all_cells.cells:
                if not hasattr(cell, 'exit_distances'):
                    cell.exit_distances = {}

                cell.exit_distances[idx] = {
                    "Total": get_manhattan_distance(cell, exit_cell)
                }
        elif self.path_finding_algorithm == "BFS" or self.path_finding_algorithm == "A*":
            visited, queue, queue_count = set(), [], 0

            if not hasattr(exit_cell, 'exit_distances'):
                exit_cell.exit_distances = {}
            exit_cell.exit_distances[idx] = {
                "G": 0,
                "F": 0,
                "Total": 0
            }
            heapq.heappush(queue, (0, 0, exit_cell))

            while queue:
                cell = heapq.heappop(queue)[2]
                if cell in visited:
                    continue
                visited.add(cell)

                # Cells that are at distance 1 and are not static and have not been visited
                open_cells = [
                    neighbor for neighbor in cell.neighborhood 
                    if neighbor not in visited
                    and neighbor not in queue
                    and (
                        neighbor.is_empty 
                        or all(agent.agent_type not in STATIC_AGENTS for agent in neighbor.agents)
                    )
                ]    

                for open_cell in open_cells:
                    queue_count += 1
                    if not hasattr(open_cell, 'exit_distances'):
                        open_cell.exit_distances = {}
                    open_cell.exit_distances[idx] = {
                        "G": cell.exit_distances[idx]["G"] + 1,
                        "F": 0,
                    }

                    if self.path_finding_algorithm == "A*":
                        open_cell.exit_distances[idx]["F"] = get_l2_distance(open_cell, exit_cell)
                    
                    open_cell.exit_distances[idx]["Total"] = (
                        open_cell.exit_distances[idx]["G"] + open_cell.exit_distances[idx]["F"]
                    )
                    heapq.heappush(
                        queue, (
                            open_cell.exit_distances[idx]["Total"], 
                            queue_count, # For tie-breaking
                            open_cell
                        )
                    )
        else:
            raise ValueError(f"Unknown path finding algorithm: {self.path_finding_algorithm}")
                
    def _initialize_max_values(self):
        self.max_density = self.datacollector.model_vars["local_density"][-1]
        self.max_evacuation_rate = self.datacollector.model_vars["evacuation_rate"][-1]
        self.max_macro_average_speed = self.datacollector.model_vars["macro_average_speed"][-1]
        self.max_micro_average_speed = self.datacollector.model_vars["micro_average_speed"][-1]

    def _update_max_values(self):
        self.max_density = (
            self.datacollector.model_vars["local_density"][-1]
            if self.datacollector.model_vars["local_density"][-1] > self.max_density 
            else self.max_density
        )
        self.max_evacuation_rate = (
            self.datacollector.model_vars["evacuation_rate"][-1]
            if self.datacollector.model_vars["evacuation_rate"][-1] > self.max_evacuation_rate 
            else self.max_evacuation_rate
        )
        self.max_macro_average_speed = (
            self.datacollector.model_vars["macro_average_speed"][-1]
            if self.datacollector.model_vars["macro_average_speed"][-1] > self.max_macro_average_speed 
            else self.max_macro_average_speed
        )
        self.max_micro_average_speed = (
            self.datacollector.model_vars["micro_average_speed"][-1]
            if self.datacollector.model_vars["micro_average_speed"][-1] > self.max_micro_average_speed 
            else self.max_micro_average_speed
        )

class CrowdModelWrapper(CrowdModel):
    def __init__(
        self,
        initial_agents=50,
        width=30,
        height=30,
        seed=42,
        polite_ratio=0.5,
        aggressive_ratio=0.3,
        slow_ratio=0.2,
        track_last_steps=5,
        path_finding_algorithm="A*",
        differentiate_exits=True,
    ):
        config = Configuration(
            initial_agents=initial_agents,
            width=width,
            height=height,
            seed=seed,
            track_last_steps=track_last_steps,
            agent_types_ratios={
                CrowdAgentEnum.POLITE: polite_ratio,
                CrowdAgentEnum.AGGRESSIVE: aggressive_ratio,
                CrowdAgentEnum.SLOW: slow_ratio
            },
            path_finding_algorithm=path_finding_algorithm,
            differentiate_exits=differentiate_exits,
        )
        super().__init__(config)


