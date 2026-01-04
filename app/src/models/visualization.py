"""Visualization module for the Crowd Model using Mesa's SolaraViz."""

from mesa.visualization import SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

def agent_portrayal(agent):
    portrayal = {
        "color": "black",
        "size": 80,         
        "alpha": 0.8,
    }

    if agent.agent_type == "polite":
        portrayal["color"] = "tab:blue"
        portrayal["marker"] = "o"   # Circle
        
    elif agent.agent_type == "aggressive":
        portrayal["color"] = "tab:red"
        portrayal["marker"] = "v"   # Triangle
        
    elif agent.agent_type == "slow":
        portrayal["color"] = "tab:green"
        portrayal["marker"] = "s"   # Square
    
    return AgentPortrayalStyle(**portrayal)


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
