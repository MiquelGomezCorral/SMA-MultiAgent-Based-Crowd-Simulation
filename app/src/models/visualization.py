"""Visualization module for the Crowd Model using Mesa's SolaraViz."""

from mesa.visualization import SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle

def agent_portrayal(agent):
    portrayal = {
        "color": "black",
        "size": 100,         
        "alpha": 1.0,
    }

    if agent.agent_type == "polite":
        portrayal["color"] = "tab:blue"
        portrayal["marker"] = "o"   # Diamond
    elif agent.agent_type == "aggressive":
        portrayal["color"] = "tab:red"
        portrayal["marker"] = "v"   # Triangle
    elif agent.agent_type == "slow":
        portrayal["color"] = "#505469"
        portrayal["marker"] = "o"   # Circle
    elif agent.agent_type == "exit":
        portrayal["color"] = "tab:green"
        portrayal["marker"] = "s"   # Square
        portrayal["size"] = 200
    
    return AgentPortrayalStyle(**portrayal)


def create_page(initial_model, model_params):
    # Create renderer with the initial model
    renderer = SpaceRenderer(model=initial_model, backend="matplotlib").render(
        agent_portrayal=agent_portrayal
    )
    total_agents_plot = make_plot_component("total_agents")


    page = SolaraViz(
        initial_model,  
        renderer,
        components=[total_agents_plot],
        model_params=model_params,
        name="Crowd Model",
    )
    return page
