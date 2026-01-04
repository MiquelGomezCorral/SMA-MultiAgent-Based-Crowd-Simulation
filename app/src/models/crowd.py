import mesa
from mesa.discrete_space import CellAgent, OrthogonalMooreGrid
from typing import Literal

from src.config import Configuration

class CrowdAgent(CellAgent):
    """And agent that moves in a crowd following simple rules."""

    def __init__(self, model, agent_type: Literal["polite", "aggressive", "slow"] = "polite"):
        super().__init__(model)
        self.agent_type = agent_type


    def step(self):
        valid_neightbors = [cell for cell in self.cell.neighborhood if cell.is_empty]
        if not valid_neightbors:
            return
        
        if self.agent_type == "polite":
            chosen_cell = self.random.choice(valid_neightbors)
        elif self.agent_type == "aggressive":
            chosen_cell = self.random.choice(valid_neightbors)
        elif self.agent_type == "slow":
            if self.random.random() < 0.5:
                chosen_cell = self.cell
            else:
                chosen_cell = self.random.choice(valid_neightbors)

        self.cell = chosen_cell


class CrowdModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, CONFIG: Configuration):
        super().__init__(seed=CONFIG.seed)
        self.n_agents = CONFIG.n_agents
        self.agent_types_ratios = CONFIG.agent_types_ratios
        self._normalize_ratios()
        
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

    def _normalize_ratios(self):
        total = sum(self.agent_types_ratios.values())
        for key in self.agent_types_ratios:
            self.agent_types_ratios[key] /= total

