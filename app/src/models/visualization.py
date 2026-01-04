"""Visualization module for the Crowd Model using Mesa's SolaraViz."""
import solara

from mesa.visualization import SolaraViz, SpaceRenderer, make_plot_component
from mesa.visualization.components import AgentPortrayalStyle

# ==================================================================
#                           VISUALIZATION
# ==================================================================
def create_page(initial_model, model_params):
    # Create renderer with the initial model
    renderer = SpaceRenderer(model=initial_model, backend="matplotlib").render(
        agent_portrayal=agent_portrayal
    )
    total_agents_plot = make_plot_component("total_agents")
    local_density_plot = make_plot_component("local_density")
    evacuation_rate_plot = make_plot_component("evacuation_rate")


    page = SolaraViz(
        initial_model,  
        renderer,
        components=[
            simulation_stats,
            total_agents_plot,
            local_density_plot,
            evacuation_rate_plot
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
    last_count = model.datacollector.model_vars["total_agents"][-1]
    evacuation_rate = model.datacollector.model_vars["evacuation_rate"][-1]

    
    # ========== formatting the text ==========
    text_content = f"""
    # Simulation Status
    - **Step:** `          {step}`
    - **Active Agents:** `{last_count}`
    - **Local Density:** `{last_density:.2f}`
    - **Evacuation Rate:** `{evacuation_rate:.2f}`
    """
    
    if not model.running:
        text_content += f"\n**FINISHED!** Total time: `{step}` steps."

    return solara.Markdown(text_content)