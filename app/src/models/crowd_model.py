"""Model module for the Crowd Simulation."""


import heapq
import mesa
from collections import Counter
from mesa import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid

from src.config import Configuration
from src.data import (
    compute_local_density, compute_evacuation_rate,
    compute_macro_average_speed, compute_micro_average_speed,
    compute_evacuation_rate_by_type, compute_macro_average_speed_by_type,
    compute_average_dead_lock_factor
)
from src.utils import get_manhattan_distance, get_l2_distance

from src.definitions import CrowdAgentEnum, STATIC_AGENTS
from src.definitions.scenarios import get_wall_positions, get_exit_positions
from .crowd_agents import CrowdAgent, CrowdExit, CrowdWall

# ==================================================================
#                               MODEL
# ==================================================================
class CrowdModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, CONFIG: Configuration):
        super().__init__(seed=CONFIG.seed)
        self.initial_agents = {
            "Total": CONFIG.initial_agents
        }
        self.current_agents = CONFIG.initial_agents
        self.agent_types_ratios = CONFIG.agent_types_ratios
        self.track_last_steps = CONFIG.track_last_steps
        self.path_finding_algorithm = CONFIG.path_finding_algorithm
        self.differentiate_exits = CONFIG.differentiate_exits
        self.scenario_type = CONFIG.scenario_type
        self.n_exits = CONFIG.n_exits
        self.respawn_agents = CONFIG.respawn_agents
        self.STATIC_AGENTS = STATIC_AGENTS
        self.capacity_warning = None
        self._normalize_ratios()
        self.evacuated_counter = Counter()


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
                "total_agents": lambda m: m.current_agents,
                "polite_agents": lambda m: 
                    m.compute_agents_by_type(CrowdAgentEnum.POLITE),
                "aggressive_agents": lambda m: 
                    m.compute_agents_by_type(CrowdAgentEnum.AGGRESSIVE),
                "slow_agents": lambda m: 
                    m.compute_agents_by_type(CrowdAgentEnum.SLOW),

                "local_density": compute_local_density,
                "evacuation_rate": compute_evacuation_rate,
                "macro_average_speed": compute_macro_average_speed,
                "micro_average_speed": compute_micro_average_speed,
                
                # Per-type metrics
                "polite_evacuation_rate": lambda m: compute_evacuation_rate_by_type(m, CrowdAgentEnum.POLITE),
                "aggressive_evacuation_rate": lambda m: compute_evacuation_rate_by_type(m, CrowdAgentEnum.AGGRESSIVE),
                "slow_evacuation_rate": lambda m: compute_evacuation_rate_by_type(m, CrowdAgentEnum.SLOW),
                
                "polite_macro_speed": lambda m: compute_macro_average_speed_by_type(m, CrowdAgentEnum.POLITE),
                "aggressive_macro_speed": lambda m: compute_macro_average_speed_by_type(m, CrowdAgentEnum.AGGRESSIVE),
                "slow_macro_speed": lambda m: compute_macro_average_speed_by_type(m, CrowdAgentEnum.SLOW),

                "dead_lock_factor": compute_average_dead_lock_factor,
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
        # Don't end simulation if respawn is enabled
        if self.respawn_agents:
            return
            
        active_agents = [
            a for a in self.agents 
            if a.agent_type not in ["exit", "wall"]
        ]

        if len(active_agents) == 0:
            self.running = False

    def get_moving_agents(self):
        """Get all agents that can move (i.e., not static)."""
        return [
            agent for agent in self.agents 
            if agent.agent_type not in self.STATIC_AGENTS
        ]
    
    def get_agents_by_type(self, agent_type: CrowdAgentEnum):
        """Get all agents of a specific type."""
        if agent_type == "Total":
            return self.get_moving_agents()
        
        return [
            agent for agent in self.agents 
            if hasattr(agent, 'agent_type') 
            and agent.agent_type == agent_type
        ]

    def compute_agents_by_type(self, agent_type: CrowdAgentEnum):
        """Compute the number of agents of a specific type."""
        return len(self.get_agents_by_type(agent_type))
    
    def update_evacuated_counter(self, agent_type: CrowdAgentEnum):
        """Update the evacuated counter for a specific agent type."""
        self.evacuated_counter[agent_type] += 1
        self.evacuated_counter["Total"] += 1
    
    def _update_agent_count(self):
        """Update the current number of active agents."""
        self.current_agents = len(self.get_moving_agents())

    def _normalize_ratios(self):
        total = sum(self.agent_types_ratios.values())
        for key in self.agent_types_ratios:
            self.agent_types_ratios[key] /= total

    def _create_agents(self):
        """Create agents and place them randomly on the grid."""
        self.priority_agents = []
        self.other_agents = []
        # =================== PROPER AGENT DISTRIBUTION ===================
        cells = self._get_initial_cells()
        
        # =================== PROPER AGENT DISTRIBUTION ===================
        agent_counts = self._get_initial_agent_counts()
        
        # =================== AGENT CREATION ===================
        for agent_type, n_type_agents in agent_counts.items():
            agents = CrowdAgent.create_agents(
                self,
                n_type_agents,
                agent_type = agent_type,
                track_last_steps = self.track_last_steps,
                number_of_exits = self.n_exits if self.differentiate_exits else None,
                respawn = self.respawn_agents,
            )
            if agent_type == CrowdAgentEnum.AGGRESSIVE:
                self.priority_agents.extend(agents)
            else: 
                self.other_agents.extend(agents)

            self.initial_agents[agent_type] = len(agents)

        for agent, cell in zip(self.priority_agents + self.other_agents, cells):
            agent.cell = cell

    def _create_walls(self):
        """Create wall agents based on scenario type."""
        wall_positions = get_wall_positions(
            scenario_type=self.scenario_type,
            width=self.grid.width,
            height=self.grid.height,
            seed=self.random.randint(0, 1000000)
        )
        
        for x, y in wall_positions:
            wall_agent = CrowdWall(self)
            wall_agent.cell = self.grid[(x, y)]

    def _create_exits(self):
        """Create exit agents based on scenario type and number of exits."""
        exit_positions = get_exit_positions(
            scenario_type=self.scenario_type,
            width=self.grid.width,
            height=self.grid.height,
            n_exits=self.n_exits,
            seed=self.random.randint(0, 1000000)
        )
        
        self.exit_cells = [self.grid[(x, y)] for x, y in exit_positions]
        self.n_exits = len(self.exit_cells)

        for idx, cell in enumerate(self.exit_cells):
            exit_agent = CrowdExit(self, exit_idx=idx)
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
                        open_cell.exit_distances[idx]["F"] = 0.5*get_l2_distance(open_cell, exit_cell)
                    
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
        """Initialize the maximum recorded values for various metrics."""
        self.max_density = self.datacollector.model_vars["local_density"][-1]
        self.max_evacuation_rate = self.datacollector.model_vars["evacuation_rate"][-1]
        self.max_macro_average_speed = self.datacollector.model_vars["macro_average_speed"][-1]
        self.max_micro_average_speed = self.datacollector.model_vars["micro_average_speed"][-1]

    def _update_max_values(self):
        """Update the maximum recorded values for various metrics."""
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

    def get_empty_cells(self):
        """Get a list of all empty cells in the grid."""
        return [c for c in self.grid.all_cells if c.is_empty]
    
    def _get_initial_cells(self):
        """Get a list of initial cells to place agents."""
        empty_cells = self.get_empty_cells()
        if len(empty_cells) < self.initial_agents["Total"]:
            original_count = self.initial_agents["Total"]
            self.initial_agents["Total"] = len(empty_cells)
            self.current_agents = len(empty_cells)
            self.capacity_warning = f"⚠️ Reduced agents from {original_count} to {len(empty_cells)} due to grid capacity."
        return self.random.sample(empty_cells, k=self.initial_agents["Total"])
    
    def _get_initial_agent_counts(self):
        """Get the initial number of agents per type based on ratios."""
        agent_counts = {}
        
        # Calculate base counts (floor) and remainders
        exact_counts = {agent_type: self.initial_agents["Total"] * ratio 
                       for agent_type, ratio in self.agent_types_ratios.items()}
        base_counts = {agent_type: int(count) 
                      for agent_type, count in exact_counts.items()}
        remainders = {agent_type: exact_counts[agent_type] - base_counts[agent_type] 
                     for agent_type in exact_counts}
        
        # Distribute remaining agents to types with largest remainders
        remaining = self.initial_agents["Total"] - sum(base_counts.values())
        sorted_types = sorted(remainders.keys(), key=lambda k: remainders[k], reverse=True)
        
        for agent_type in sorted_types:
            agent_counts[agent_type] = base_counts[agent_type]
            if remaining > 0:
                agent_counts[agent_type] += 1
                remaining -= 1

        return agent_counts

class CrowdModelWrapper(CrowdModel):
    def __init__(
        self,
        initial_agents=75,
        width=30,
        height=30,
        seed=42,
        polite_ratio=0.7,
        aggressive_ratio=0.2,
        slow_ratio=0.1,
        track_last_steps=4,
        path_finding_algorithm="A*",
        scenario_type="MALL",
        n_exits=4,
        differentiate_exits=True,
        respawn_agents=False,
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
            scenario_type=scenario_type,
            n_exits=n_exits,
            respawn_agents=respawn_agents,
        )
        super().__init__(config)


