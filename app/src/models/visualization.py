"""Visualization module for the Crowd Model using Mesa's SolaraViz."""

import numpy as np
import solara
import matplotlib.pyplot as plt
from mesa.visualization import SolaraViz, SpaceRenderer
from mesa.visualization.components import AgentPortrayalStyle

from src.definitions import CrowdAgentEnum, STATIC_AGENTS, CROWD_AGENT_STATS, AGENT_TYPE_COLORS
from src.data import compute_evacuation_rate_by_type, compute_macro_average_speed_by_type
from src.utils import get_varied_color

# ==================================================================
#                           VISUALIZATION
# ==================================================================
def create_page(initial_model, model_params):
    # Create renderer with the initial model
    renderer = SpaceRenderer(model=initial_model, backend="matplotlib").render(
        agent_portrayal=agent_portrayal
    )

    page = SolaraViz(
        initial_model,  
        renderer,
        components=[
            simulation_stats,
            agent_count_plot,
            evacuation_rate_plot,
            macro_speed_plot,
            micro_density_plot,
            heatmap_component,
        ],
        model_params=model_params,
        name="Crowd Model",
    )
    return page



# ==================================================================
#                       VISUALIZATION HELPERS
# ==================================================================
def agent_count_plot(model):
    """Custom plot for agent counts with specific colors."""
    return make_custom_plot(
        model, 
        ["total_agents", "polite_agents", "aggressive_agents", "slow_agents"],
        "Agent Counts"
    )

def evacuation_rate_plot(model):
    """Custom plot for evacuation rates by agent type."""
    return make_custom_plot(
        model,
        ["evacuation_rate", "polite_evacuation_rate", "aggressive_evacuation_rate", "slow_evacuation_rate"],
        "Evacuation Rate by Agent Type"
    )

def macro_speed_plot(model):
    """Custom plot for macro average speed by agent type."""
    return make_custom_plot(
        model,
        ["macro_average_speed", "polite_macro_speed", "aggressive_macro_speed", "slow_macro_speed", "micro_average_speed"],
        "Macro Average Speed by Agent Type"
    )

def micro_density_plot(model):
    """Custom plot for micro density."""
    return make_custom_plot(
        model,
        ["local_density", "dead_lock_factor"],
        "Density / Speed Over Time"
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


# ==================================================================
#                           PORTRAYAL
# ==================================================================

def agent_portrayal(agent):
    """Generate agent portrayal using centralized configuration."""
    # Use CROWD_AGENT_STATS directly for consistency
    agent_stats = CROWD_AGENT_STATS.get(agent.agent_type, {})
    
    portrayal = {
        "color": agent_stats.get("color", "black"),
        "marker": agent_stats.get("marker", "o"),
        "size": agent_stats.get("size", 100),
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
    active_agent_types = [agent_type for agent_type in list(CrowdAgentEnum) if agent_type not in STATIC_AGENTS]
    active_agent_types_display = [agent_type.value.capitalize() for agent_type in active_agent_types]
    empty_line_separator = "|".join(["---"] * len(active_agent_types))
    
     # Create the markdown text
    text_content = f"""### Simulation Status
| Metric | Current | Max | Avg | {"|".join(active_agent_types_display)} |
| :--- | --- | --- | --- | {empty_line_separator} |
| **Step** | {step} | --- | --- | {empty_line_separator} |
| **Active Agents** | {last_count} | {model.initial_agents["Total"]} | --- | {"|".join(str(get_metric_value(model, f"{agent_type.value}_agents")) for agent_type in active_agent_types)} |
| **Local Density** | {last_density:.2f} | {model.max_density:.2f} | {avg_density:.2f} | {empty_line_separator} |
| **Evacuation Rate** | --- | {model.max_evacuation_rate:.2f} | {evacuation_rate:.2f} | {"|".join(f"{get_metric_value(model, f'{agent_type.value}_evacuation_rate'):.2f}" for agent_type in active_agent_types)} |
| **Macro Avg Speed** | --- | {model.max_macro_average_speed:.2f} | {macro_average_speed:.2f} | {"|".join(f"{get_metric_value(model, f'{agent_type.value}_macro_speed'):.2f}" for agent_type in active_agent_types)} |
| **Micro Avg Speed** | {micro_average_speed:.2f} | {model.max_micro_average_speed:.2f} | --- | {empty_line_separator} |
"""
    if not model.running:
        text_content += f"\n**FINISHED!** Total time: `{step}` steps."

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



