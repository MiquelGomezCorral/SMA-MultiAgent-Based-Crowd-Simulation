"""Visualization module for the Crowd Model using Mesa's SolaraViz."""

import numpy as np
import solara
import matplotlib.pyplot as plt
from mesa.visualization import SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle

from .crowd_agents import CrowdAgentEnum
# ==================================================================
#                           VISUALIZATION
# ==================================================================
def create_page(initial_model, model_params):
    # Create renderer with the initial model
    renderer = SpaceRenderer(model=initial_model, backend="matplotlib").render(
        agent_portrayal=agent_portrayal
    )
    total_agents_plot = make_plot_component("total_agents")
    rates_plot = make_plot_component(["local_density", "evacuation_rate"])
    average_speed_plot = make_plot_component(["macro_average_speed", "micro_average_speed"])


    page = SolaraViz(
        initial_model,  
        renderer,
        components=[
            simulation_stats,
            total_agents_plot,
            rates_plot,
            average_speed_plot,
            heatmap_component,
        ],
        model_params=model_params,
        name="Crowd Model",
    )
    return page


# ==================================================================
#                           PORTRAYAL
# ==================================================================

def agent_portrayal(agent):
    portrayal = {
        "color": "black",
        "size": 100,         
        "alpha": 1.0,
    }

    if agent.agent_type == CrowdAgentEnum.POLITE:
        portrayal["color"] = "tab:blue"
        portrayal["marker"] = "o"   # Diamond
    elif agent.agent_type == CrowdAgentEnum.AGGRESSIVE:
        portrayal["color"] = "tab:red"
        portrayal["marker"] = "v"   # Triangle
    elif agent.agent_type == CrowdAgentEnum.SLOW:
        portrayal["color"] = "#179665"
        portrayal["marker"] = "o"   # Circle
    elif agent.agent_type == CrowdAgentEnum.EXIT:
        portrayal["color"] = "tab:green"
        portrayal["marker"] = "s"   # Square
        portrayal["size"] = 200
    elif agent.agent_type == CrowdAgentEnum.WALL:
        portrayal["color"] = "tab:gray"
        portrayal["marker"] = "s"   # Square
        portrayal["size"] = 200
    
    return AgentPortrayalStyle(**portrayal)


# ==================================================================
#                           OTHER COMPONENTS
# ==================================================================
def simulation_stats(model):
    """
    Displays dynamic text stats.
    """
    # ========== Data ==========
    step = model.steps
    last_density = model.datacollector.model_vars["local_density"][-1]
    avg_density = np.mean(model.datacollector.model_vars["local_density"])
    last_count = model.datacollector.model_vars["total_agents"][-1]
    evacuation_rate = model.datacollector.model_vars["evacuation_rate"][-1]
    macro_average_speed = model.datacollector.model_vars["macro_average_speed"][-1]
    micro_average_speed = model.datacollector.model_vars["micro_average_speed"][-1]

    
    # ========== formatting the text ==========
    text_content = f"""
    ### Simulation Status
    | Metric | Current | Max | Avg |
    | :--- | --- | --- | ---: |
    | **Step** | {step} | --- | --- |
    | **Active Agents** | {last_count} | {model.initial_agents} | --- |
    | **Local Density** | {last_density:.2f} | {model.max_density:.2f} | {avg_density:.2f} |
    | **Evacuation Rate** | --- | {model.max_evacuation_rate:.2f} | {evacuation_rate:.2f} |
    | **Macro Avg Speed** | --- | {model.max_macro_average_speed:.2f} | {macro_average_speed:.2f} |
    | **Micro Avg Speed** | {micro_average_speed:.2f} | {model.max_micro_average_speed:.2f} | --- |
    """
    
    if not model.running:
        text_content += f"**FINISHED!** Total time: `{step}` steps."

    return solara.Markdown(text_content)

def heatmap_component(model):
    """
    Renders a heatmap of a specific cell property.
    """
    fig = plt.Figure(figsize=(5, 5))
    ax = fig.subplots()
    
    # Extract Data into a Matrix
    w, h = model.grid.width, model.grid.height
    data = np.zeros((h, w)) 

    for cell in model.grid.all_cells:
        x, y = cell.coordinate
        exit_distances = getattr(cell, "exit_distances", {})
        if exit_distances:
            data[y, x] = min([val["Total"] for val in exit_distances.values()])
        else:
            data[y, x] = np.nan  # or some other value indicating no exit

    #. Plot Heatmap
    im = ax.imshow(data, origin='lower', cmap='viridis', interpolation='nearest')
    
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04) 
    ax.set_title("Closest Exit Distance Heatmap")
    ax.set_xticks([]) # Hide ticks for cleanliness
    ax.set_yticks([])

    return solara.FigureMatplotlib(fig)