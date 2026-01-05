"""Visualization module for the Crowd Model using Mesa's SolaraViz."""

import numpy as np
import solara
import matplotlib.pyplot as plt
from mesa.visualization import SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle
import pandas as pd

from .crowd_agents import CrowdAgentEnum, STATIC_AGENTS
from src.utils import get_varied_color

# Centralized color mapping for agent types
AGENT_TYPE_COLORS = {
    # Plot metrics
    "total_agents": "black",
    "polite_agents": "tab:blue",
    "aggressive_agents": "tab:red",
    "slow_agents": "#179665",
    # Agent types for portrayal
    CrowdAgentEnum.POLITE: "tab:blue",
    CrowdAgentEnum.AGGRESSIVE: "tab:red",
    CrowdAgentEnum.SLOW: "#179665",
    CrowdAgentEnum.EXIT: "tab:green",
    CrowdAgentEnum.WALL: "tab:gray",
}

# Agent markers for different types
AGENT_TYPE_MARKERS = {
    CrowdAgentEnum.POLITE: "d",      # Diamond
    CrowdAgentEnum.AGGRESSIVE: "v",  # Triangle
    CrowdAgentEnum.SLOW: "o",        # Circle
    CrowdAgentEnum.EXIT: "s",        # Square
    CrowdAgentEnum.WALL: "s",        # Square
}

# Agent sizes for different types
AGENT_TYPE_SIZES = {
    CrowdAgentEnum.POLITE: 100,
    CrowdAgentEnum.AGGRESSIVE: 100,
    CrowdAgentEnum.SLOW: 100,
    CrowdAgentEnum.EXIT: 200,
    CrowdAgentEnum.WALL: 200,
}
# ==================================================================
#                           VISUALIZATION
# ==================================================================

def agent_count_plot(model):
    """Custom plot for agent counts with specific colors."""
    return make_custom_plot(
        model, 
        ["total_agents", "polite_agents", "aggressive_agents", "slow_agents"],
        "Agent Counts"
    )

def make_custom_plot(model, metrics, title):
    """Create a custom plot with specific colors for agent types."""
    df = model.datacollector.get_model_vars_dataframe()
    
    fig = plt.Figure(figsize=(6, 4))
    ax = fig.subplots()
    
    for metric in metrics:
        if metric in df.columns:
            color = AGENT_TYPE_COLORS.get(metric, None)
            ax.plot(df.index, df[metric], label=metric, color=color)
    
    ax.set_xlabel("Step")
    ax.set_ylabel("Count")
    ax.set_title(title)
    ax.legend()
    
    return solara.FigureMatplotlib(fig)

def create_page(initial_model, model_params):
    # Create renderer with the initial model
    renderer = SpaceRenderer(model=initial_model, backend="matplotlib").render(
        agent_portrayal=agent_portrayal
    )
    total_agents_plot = agent_count_plot
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
    """Generate agent portrayal using centralized configuration."""
    portrayal = {
        "color": AGENT_TYPE_COLORS.get(agent.agent_type, "black"),
        "marker": AGENT_TYPE_MARKERS.get(agent.agent_type, "o"),
        "size": AGENT_TYPE_SIZES.get(agent.agent_type, 100),
        "alpha": 1.0,
    }

    # Agents assigned to specific exits get colored accordingly
    if hasattr(agent, "exit_idx") and agent.exit_idx is not None:  
        portrayal["color"] = f"C{agent.exit_idx}"

    # Use unique_id so every agent looks distinct but keeps their color
    if agent.agent_type not in STATIC_AGENTS:
        portrayal["color"] = get_varied_color(portrayal["color"], agent.unique_id)
    
    return AgentPortrayalStyle(**portrayal)


# ==================================================================
#                           OTHER COMPONENTS
# ==================================================================
def get_metric_value(model, metric, index=-1):
    """Helper to safely get metric value from datacollector."""
    return model.datacollector.model_vars[metric][index]

def simulation_stats(model):
    """
    Displays dynamic text stats.
    """
    # ========== Data ==========
    step = model.steps
    last_density = get_metric_value(model, "local_density")
    avg_density = np.mean(model.datacollector.model_vars["local_density"])
    last_count = get_metric_value(model, "total_agents")
    evacuation_rate = get_metric_value(model, "evacuation_rate")
    macro_average_speed = get_metric_value(model, "macro_average_speed")
    micro_average_speed = get_metric_value(model, "micro_average_speed")

    
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

def extract_grid_data(model, property_name="exit_distances", aggregator=None):
    """Extract data from grid cells into a matrix."""
    w, h = model.grid.width, model.grid.height
    data = np.zeros((h, w))
    
    for cell in model.grid.all_cells:
        x, y = cell.coordinate
        value = getattr(cell, property_name, None)
        
        if value:
            if aggregator:
                data[y, x] = aggregator(value)
            else:
                data[y, x] = value
        else:
            data[y, x] = np.nan
    
    return data

def heatmap_component(model):
    """Renders a heatmap of a specific cell property."""
    fig = plt.Figure(figsize=(5, 5))
    ax = fig.subplots()
    
    # Extract exit distances and get minimum
    data = extract_grid_data(
        model, 
        "exit_distances",
        aggregator=lambda distances: min([val["Total"] for val in distances.values()])
    )

    # Plot Heatmap
    im = ax.imshow(data, origin='lower', cmap='viridis', interpolation='nearest')
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Closest Exit Distance Heatmap")
    ax.set_xticks([])
    ax.set_yticks([])

    return solara.FigureMatplotlib(fig)



