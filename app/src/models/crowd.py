import numpy as np
from typing import Literal
import mesa
from mesa import DataCollector
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid


from src.config import Configuration
from src.data import compute_total_agents
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
            self.speed = np.random.uniform(0.6, 1.0)
        elif agent_type == "aggressive":
            self.speed = np.random.uniform(0.8, 1.0)
        elif agent_type == "slow":
            self.speed = np.random.uniform(0.4, 0.6)


    def step(self):
        valid_neightbors = [cell for cell in self.cell.neighborhood if cell.is_empty]
        if not valid_neightbors:
            return
        
        if self.agent_type == "polite":
            chosen_cell = self.random.choice(valid_neightbors)
        elif self.agent_type == "aggressive":
            chosen_cell = self.random.choice(valid_neightbors)
        elif self.agent_type == "slow":
            chosen_cell = self.random.choice(valid_neightbors)
            

        if self.random.random() > self.speed:
            chosen_cell = self.cell
        else:
            chosen_cell = self.random.choice(valid_neightbors)


        self.cell = chosen_cell

# ==================================================================
#                               MODEL
# ==================================================================
class CrowdModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, CONFIG: Configuration):
        super().__init__(seed=CONFIG.seed)
        self.n_agents = CONFIG.n_agents
        self.agent_types_ratios = CONFIG.agent_types_ratios
        self._normalize_ratios()

        # ========== CREATE COLLECTORS ==========
        self.datacollector = DataCollector(
            model_reporters={"total_agents": compute_total_agents},
            agent_reporters={},
        )
        self.datacollector.collect(self)

        # ========== CREATE GRID ==========
        self.grid = OrthogonalMooreGrid(
            (CONFIG.width, CONFIG.height), 
            torus=False, 
            random=self.random
        )
        
    
        # ========== CREATE AGENTS ==========
        agents = []
        cells = self.random.sample(self.grid.all_cells.cells, k=self.n_agents)
        
        for agent_type, ratio in self.agent_types_ratios.items():
            n_type_agents = int(self.n_agents * ratio)
            agents += CrowdAgent.create_agents(
                self,
                n_type_agents,
                agent_type = agent_type,
            )

        for agent, cell in zip(agents, cells):
            agent.cell = cell

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)


    def _normalize_ratios(self):
        total = sum(self.agent_types_ratios.values())
        for key in self.agent_types_ratios:
            self.agent_types_ratios[key] /= total

class CrowdModelWrapper(CrowdModel):
    def __init__(self, n_agents=50, width=10, height=10, seed=42,
                 polite_ratio=0.5, aggressive_ratio=0.3, slow_ratio=0.2):
        config = Configuration(
            n_agents=n_agents,
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


