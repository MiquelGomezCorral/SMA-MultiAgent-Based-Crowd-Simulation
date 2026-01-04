"""Visualization module for the Crowd Model using Mesa's SolaraViz."""

from mesa.visualization import SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle

def agent_portrayal(agent):
    if agent.agent_type == "polite":
        return AgentPortrayalStyle(color="blue", size=50)
    elif agent.agent_type == "aggressive":
        return AgentPortrayalStyle(color="red", size=50)
    elif agent.agent_type == "slow":
        return AgentPortrayalStyle(color="green", size=50)


def create_page(initial_model, model_params):
    # Create renderer with the initial model
    renderer = SpaceRenderer(model=initial_model, backend="matplotlib").render(
        agent_portrayal=agent_portrayal
    )

    page = SolaraViz(
        initial_model,  
        renderer,
        components=[],
        model_params=model_params,
        name="Crowd Model",
    )
    return page