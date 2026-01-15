# Analysis of Crowd Simulation Experiments

This document presents a professional analysis of the multi-agent crowd simulation experiments conducted to evaluate the impact of various parameters on evacuation efficiency and crowd dynamics.

## 1. Introduction

The objective of this study was to understand how different environmental factors and agent behaviors influence crowd dynamics and evacuation times in varied scenarios. The simulations measured the **Maximum Steps** required for all agents to evacuate, alongside detailed **Behavioral Metrics** (speed, density, deadlock, flow) to understand the *quality* of the movement.

The following variables were analyzed:

1. **Agent Density**: Impact of increasing crowd size.
2. **Aggressive Behavior**: Effect of agent competitivity.
3. **Slow Agents**: Impact of mobility-impaired or slow-moving agents.
4. **Pathfinding Algorithms**: Comparison between A* and BFS.
5. **Exit Preferences**: Impact of pre-assigned vs. opportunistic exit selection.
6. **Number of Exits**: Efficiency gains from multiple egress points.
7. **Exit Width**: Impact of widening bottlenecks.

## 2. Methodology

Experiments were run across four distinct scenarios, each representing different spatial constraints:

* **Corridor**: A linear, constrained space.
* **Mall**: An open space with obstacles.
* **Seats**: A highly structured environment (like a theater).
* **Snake**: A winding path with forced turns.

Metrics Collected:

* **Evacuation Time (Max Steps)**: Time to clear the simulation.
* **Evacuation Rate**: % of agents exiting per step (Flow).
* **Macro Average Speed**: Average speed of all active agents.
* **Deadlock Factor**: Proportion of agents unable to move due to blockage.
* **Local Density**: Average number of neighbors within perception range.

---

## 3. Analysis of Evacuation Time (Efficiency)

### 3.1. Agent Density

**Observation**: Evacuation time increases non-linearly with agent count.

* **Results**: Increasing agents from 10 to 300 caused increases in evacuation time ranging from +80% (Corridor) to +370% (Seats).
* **Insight**: Structured environments (Seats) are highly sensitive to density, while open corridors handle load more linearly.

### 3.2. Aggressive Agents

**Observation**: Aggression can improve efficiency in specific contexts.

* **Results**: In the **Seats** scenario, 100% aggressive agents exited ~14% faster than polite agents (205 vs 238 steps).
* **Insight**: Aggressive agents push through gaps that polite agents would hesitate at, effectively "greasing" the flow in high-conflict zones.

### 3.3. Slow Agents

**Observation**: Slow agents act as dynamic obstacles.

* **Results**: 100% slow agents increased evacuation time by ~45%.
* **Insight**: The high variability ($\sigma$ increases significantly) suggests that *where* slow agents are located (blocking a bottleneck vs. open space) matters as much as *how many* there are.

### 3.4. Pathfinding Algorithms

**Observation**: Algorithm performance is topology-dependent.

* **Results**: A* is superior in open maps (Mall: +33% faster), while BFS is more robust in obstacle-dense grids (Seats).
* **Insight**: A* heuristics can lead agents into local minima (traps) in complex layouts, whereas BFS guarantees finding the true path around obstacles.

### 3.5. Exit Preferences

**Observation**: Rigid exit assignment is catastrophic for efficiency compared to opportunistic behavior.

* **Results**: "With Preference" increased evacuation times by +100% to +1000%.
* **Insight**: Agents bypassing free exits to reach distant "preferred" exits creates unnecessary travel and jams.

### 3.6. Number of Exits

**Observation**: Diminishing returns after saturation.

* **Results**: Gains plateau after ~4 exits.
* **Insight**: Once exit capacity exceeds internal flow rate, the bottleneck shifts from the door to the room itself.

### 3.7. Exit Width

**Observation**: Wider exits significantly reduce bottlenecks.

* **Results**: Increasing width multiplier from 1 to 4 improved flow metrics consistently.
* **Insight**: Wider exits allow parallel egress, directly countering the "arch" effect seen at narrow doors.

---

## 4. Behavioral Metrics Analysis

This section analyzes the *quality* of the crowd movement using four key behavioral indicators: **Evacuation Rate**, **Macro Average Speed**, **Deadlock Factor**, and **Local Density**.

### 4.1. Impact of Agent Density on Behavior

As the number of agents increases (10 $\to$ 300), we observe clear degradation in movement quality but an increase in system throughput:

* **Throughput vs. Efficiency Trade-off**: As agent count rises, the **Evacuation Rate** (agents exiting per step) increases significantly (from ~0.5 to ~5.5), simply because more agents are pressing against the exits. However, individual efficiency drops: **Macro Average Speed** decreases by 32% (0.43 to 0.29). In short: **More agents mean a higher collective flow rate, but slower individual movement.**
* **Congestion**: Local Density increases linearly from **0.18** to **2.10**, indicating extreme crowding.
* **Variability**: The standard deviation of the evacuation rate increases with density, meaning the flow becomes more volatile (bursts of agents leaving followed by pauses).
* **Gridlock**: Deadlock Factor rises sharply from negligible (**0.00**) at low density to **0.22** at 300 agents. This means >20% of the crowd is stuck at any given moment in high-density runs.
* **Correlation**: There is a strong inverse correlation between Local Density and Average Speed, confirming that density is the primary driver of friction.

### 4.2. Behavioral Traits: Aggression vs. Slowness

Comparing the impact of agent "personality" on flow dynamics reveals similar directional trends but with opposite effects:

| Metric                    | Polite (Baseline) | Aggressive (100%)     | Slow (100%)           | Insight                                                                                                                                     |
| :------------------------ | :---------------- | :-------------------- | :-------------------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| **Evacuation Rate** | ~2.40             | **2.76** (+15%) | 1.74 (-27%)           | Aggression improves flow rate; Slowness cripples it.                                                                                        |
| **Deadlock Factor** | 0.73              | **0.61** (-16%) | 0.70 (~)              | **Surprising Result:** Aggressive agents cause *less* deadlocks. They resolve conflicts faster by taking spots rather than waiting. |
| **Avg Speed**       | 0.37              | 0.38 (~)              | **0.26** (-30%) | Aggressiveness maintains speed/flow; Slowness reduces it significantly.                                                                     |

**Key Finding**: In this simulation model, "Aggression" acts as a conflict-resolution mechanism that prevents freezing behaviors, leading to smoother overall flow despite the implied lack of politeness. Conversely, slow agents reduce the effective flow rate of the entire system.

### 3. Strategic Factors: Exits and Preferences

The choice of exit strategy exhibits the most dramatic impact on behavioral metrics:

* **Exit Preference (Forced)**:

  * **Deadlock Factor** skyrockets to **3.33** (compared to 0.13 without preference). This massive irregularity suggests agents are physically blocking each other while trying to cross paths to reach distant exits.
  * **Evacuation Rate** plummets to **0.61** (vs 2.10). **Having preferences for specific exits significantly slows down the evacuation rate.**
  * **Conclusion**: Rigid behaviors in crowd dynamics lead to systemic failure (gridlock).
* **Number of Exits**:

  * **Flow & Distribution**: More exits lead to faster evacuation, but there are diminishing returns. Once all borders have at least one exit (e.g., 4 exits), adding more yields minimal improvement.
  * **Deadlock Drop**: Crucially, increasing the number of exits causes the **Deadlock Factor** to drop significantly (0.75 wiht 1 exit $\to$ 0.07 with 4 exits). This confirms that distributing agents to multiple points allows them to spread out, reducing local congestion.
* **Exit Width (Widening)**:

  * **Deadlock Factor** drops systematically: 0.42 (Width x1) $\to$ **0.03** (Width x3/x4).
  * **Local Density** decreases: 2.03 $\to$ 1.06.
  * **Conclusion**: Widening exits solves the "arch" clogging problem, virtually eliminating interaction-based delays at the exit point.

### 4.4. Summary of Correlations

* **Local Density** is the master variable: it inversely correlates with Speed and Flow. High density guarantees lower individual agent performance.
* **Deadlock** is a symptom of poor layout (Narrow Exits) or poor strategy (Exit Preference), but *not* necessarily high density alone (unless density is extreme).
* **Aggression** negatively correlates with Deadlock (more aggression = less deadlock), challenging the assumption that polite behavior is always optimal for crowds.

## 5. Overall Conclusions

The comprehensive analysis of evacuation simulations, combining aggregate metrics (Sections 3-4) with temporal evolution patterns (Section 6), yields the following key findings:

### 5.1. Critical Success Factors

1. **Opportunistic > Strategic**: Agents should always choose the nearest valid exit. Pre-planning (Preferences) fails under dynamic conditions. Temporal analysis (Section 6.1) reveals that preferences cause congestion to begin **48% earlier** (2.7% vs 5.2% of simulation time) and persist **twice as long** (32.8% vs 16.2% in high-congestion state). The 722% increase in peak deadlock demonstrates that preferences create cross-traffic gridlock, not just inefficiency.
2. **Aggression is Efficient**: In high-density evacuations, hesitance (politeness) is fatal to flow. Decisive (aggressive) movement clears bottlenecks faster. Aggressive agents reduce deadlock by 16% and increase evacuation rate by 15% by resolving conflicts immediately rather than waiting.
3. **Geometry Dictates Flow, But Context Matters**: The most effective interventions are geometric (Wider Exits, More Exits, Open Space), but their impact is **scenario-dependent**:

- In **open spaces**, exit width is critical (Width x1 Deadlock = 0.42 → Width x4 Deadlock = 0.03)
- In **structured environments** (SEATS), internal navigation dominates, and exit width 1x → 4x provides <1% improvement
- Design must prioritize the **actual bottleneck location**, not assume exits are always the limiting factor

### 5.2. Temporal Insights for Real-Time Monitoring

4. **Speed as Early Warning**: Agent speed degradation precedes deadlock spikes by 10-20 percentage points of simulation time. Monitoring average speed in real-time crowd systems could provide advance warning before visible gridlock occurs, enabling preventive interventions (Section 6.1.2).
5. **Flow Stability Matters**: The coefficient of variation in evacuation rate indicates system stability. Exit preferences increase CV by 12%, creating "stop-and-go" dynamics that reduce predictability and increase psychological stress (Section 6.1.3).
6. **Congestion is Not Always at Exits**: Temporal analysis reveals that in preference-based routing, deadlock peaks occur in **open spaces** due to cross-traffic, not at exit bottlenecks. Traditional exit-focused interventions (widening, adding exits) cannot solve cross-traffic gridlock caused by poor routing strategy (Section 6.1.1).

### 5.3. Design Recommendations

**For New Facilities:**

- Implement **dynamic nearest-exit routing** with real-time updates, never fixed preferences
- In open spaces (malls, plazas): Prioritize exit width and multiple exits
- In structured spaces (theaters, stadiums): Prioritize aisle width and internal navigation before expanding exits
- Design for **multiple egress routes** (4+ exits), with diminishing returns beyond saturation

**For Real-Time Systems:**

- Monitor **average agent speed** as the primary early-warning metric
- Track **evacuation rate variance** to detect stop-and-go instability
- Deploy interventions when speed drops >10% from baseline, before deadlock becomes visible
- Use opportunistic routing algorithms that re-route agents to less congested exits dynamically

**For Agent Behavior:**

- Encourage moderate aggressiveness (decisive movement) over excessive politeness
- Account for slow/mobility-impaired agents in capacity planning (+45% time impact)
- Never assign fixed exit preferences; always use nearest-available exit strategy

---

---

## 6. Temporal Evolution Analysis: Exit Strategy and Geometry

The previous sections analyzed **aggregate final outcomes** (total evacuation time, mean behavioral metrics). This section examines **how key metrics evolve throughout the simulation**, revealing the underlying dynamics that produce those final results. Understanding temporal patterns is critical for:

- Identifying **when** congestion develops and how long it persists
- Determining whether interventions accelerate resolution or prevent onset
- Assessing flow **stability** versus erratic "stop-and-go" patterns

We focus on **Exit Preference** and **Exit Width** experiments, analyzing the evolution of **Deadlock Factor**, **Agent Speed**, and **Evacuation Rate** across normalized simulation time.

### 6.1. Exit Preference: Temporal Dynamics

#### 6.1.1. Deadlock Evolution Pattern

**Observation**: Exit preferences create **sustained high-congestion periods** rather than brief bottlenecks.

| Metric                                        | No Preference | With Preference | Impact                 |
| --------------------------------------------- | ------------- | --------------- | ---------------------- |
| **Congestion Onset** (% of sim)         | 5.2%          | 2.7%            | **48% earlier**  |
| **Time to Peak Congestion**             | 27.6%         | 25.9%           | 6% earlier             |
| **Peak Deadlock Factor**                | 0.48          | 3.94            | **+722% higher** |
| **High-Congestion Duration** (% of sim) | 16.2%         | 32.8%           | **+102% longer** |
| **Speed During Congestion**             | 0.47          | 0.45            | -5% slower             |

**Key Findings**:

1. **Earlier Onset**: When agents have exit preferences, congestion begins at **2.7%** of the simulation versus **5.2%** without preferences—nearly **twice as early**. This occurs because agents immediately cross paths traveling to distant preferred exits, even when nearby exits are free.
2. **Catastrophic Peak**: The peak deadlock factor reaches **3.94** with preferences versus **0.48** without—a **722% increase**. This extreme gridlock indicates that agents are not just slowed but completely immobilized in cross-traffic jams.
3. **Sustained Gridlock**: The high-congestion phase (deadlock > 0.3) lasts for **32.8%** of the simulation with preferences versus **16.2%** without—**twice as long**. The system spends one-third of its lifetime in severe gridlock.
4. **Path Crossing Effect**: The visualization shows that deadlock remains elevated throughout the middle 60-70% of the simulation when preferences are enabled, indicating persistent cross-traffic conflicts rather than a brief bottleneck at exits.

**Interpretation**: Exit preferences transform evacuation from a **convergent flow problem** (agents moving toward nearest exits) into a **divergent cross-traffic problem** (agents bypassing nearby exits to reach distant ones). The deadlock is not at the exits themselves but in the **open space** where opposing agent flows collide.

#### 6.1.2. Speed Degradation Pattern

**Observation**: Speed collapses early and never recovers when preferences are enabled.

- **No Preference**: Speed starts at 0.44 and maintains an average of 0.47 during congestion (actually *increasing* slightly as agents spread toward different exits). The system exhibits **negative speed degradation** (-11.7%), meaning agents maintain or improve mobility throughout evacuation.
- **With Preference**: Speed starts at 0.47 but drops to 0.45 during congestion, representing **5.7% degradation**. More critically, the temporal plot shows speed crashes within the first **10-20%** of the simulation and never recovers above 0.46.

**Speed Collapse Timeline**:

- **0-5% of simulation**: Both configurations show similar initial speeds (~0.45-0.47)
- **5-10%**: With preferences, speed drops sharply to ~0.42 as cross-traffic conflicts emerge
- **10-80%**: Speed remains depressed at 0.42-0.46 with preferences, while no-preference maintains 0.46-0.48
- **80-100%**: Both configurations show slight speed increases as remaining agents have more space

**Key Insight**: The speed metric **precedes** the deadlock metric. Speed degradation begins at 5% of simulation time, *before* severe deadlock peaks. This suggests **speed monitoring could serve as an early warning system** for imminent gridlock in real evacuation scenarios.

#### 6.1.3. Flow Stability Analysis

The **coefficient of variation (CV)** of evacuation rate measures flow consistency:

- **No Preference**: CV = 0.39 (relatively stable flow)
- **With Preference**: CV = 0.43 (+12% more variable)

**Interpretation**: Preference-based routing creates **"stop-and-go" evacuation dynamics**—bursts of agents exiting (when a pathway temporarily clears) followed by prolonged stalls (when cross-traffic re-blocks the flow). This instability reduces system predictability and increases psychological stress in real scenarios.

Temporal plots confirm this: the evacuation rate line for "With Preference" shows larger oscillations throughout the simulation, while "No Preference" exhibits a smoother, more consistent evacuation rate that gradually increases as density decreases.

### 6.2. Exit Width: Temporal Dynamics

#### 6.2.1. Deadlock Resolution Speed

**Observation**: Wider exits don't prevent congestion—they **accelerate its resolution**.

| Exit Width   | Peak Deadlock | Time at Peak | High Congestion Duration | Total Steps |
| ------------ | ------------- | ------------ | ------------------------ | ----------- |
| **1x** | 1.13          | 42.2%        | 20.5% of sim             | 449.1       |
| **2x** | 1.09          | 35.3%        | 19.4%                    | 455.9       |
| **3x** | 1.24          | 49.0%        | 20.2%                    | 499.6       |
| **4x** | 1.10          | 43.8%        | 20.0%                    | 449.4       |

**Surprising Result**: All exit widths reach **similar peak deadlock values** (~1.10-1.24). The width of the exit does not prevent initial congestion buildup, which is driven by **internal density** as agents converge toward exit zones.

**Key Findings**:

1. **Similar Peaks**: Peak deadlock varies only 3-13% across widths (1.09 to 1.24), with no clear monotonic relationship. This indicates that initial congestion is caused by agents **approaching** the exit, not the exit capacity itself.
2. **Consistent Duration**: High-congestion duration is remarkably consistent across all widths (19.4% to 20.5% of simulation). Wider exits do not significantly shorten the congestion phase when normalized to simulation time.
3. **Minimal Total Time Difference**: Total evacuation steps for width 1x (449.1) and width 4x (449.4) are virtually identical—a **0.1% difference**. This contradicts the hypothesis that wider exits drastically reduce evacuation time.

**Explanation**: The SEATS scenario used in this experiment has a **fixed initial density of 125 agents**. The congestion is primarily caused by agents moving through internal obstacles (seats) toward exits. Once agents reach the exit zone, even a narrow (1x) exit can handle the flow rate because agents arrive gradually, not in a single wave. In this configuration, **exit width is not the bottleneck**—internal navigation is.

#### 6.2.2. Phase Analysis

Despite similar overall times, temporal evolution reveals different congestion **patterns**:

**Width 1x**:

- Congestion onset: ~15-20% of simulation
- Peak congestion: 42% of simulation (mid-point)
- Resolution start: 59% of simulation
- Pattern: **Symmetric** buildup and resolution

**Width 2x**:

- Congestion onset: ~10-15% (slightly earlier)
- Peak congestion: 35% (earlier than 1x)
- Resolution start: 48% (10% earlier than 1x)
- Pattern: **Front-loaded** congestion that resolves faster

**Width 4x**:

- Congestion onset: ~15-20%
- Peak congestion: 44%
- Resolution start: 57%
- Pattern: Similar to 1x but with slightly smoother curves (lower variance in deadlock over time)

**Interpretation**: Wider exits shift the congestion peak **earlier** in the simulation and allow slightly **faster resolution** once the peak is reached. However, because the internal navigation time dominates, this advantage is minimal in absolute terms.

#### 6.2.3. Speed Stability

All exit widths maintain similar speeds during congestion (~0.41), with negligible differences:

- Width 1x: 0.413 congestion speed
- Width 4x: 0.413 congestion speed (0.2% difference)

This reinforces that **exit width does not affect agent mobility** in the SEATS scenario—agents are slowed by navigating around obstacles, not by waiting at exits.

### 6.3. Combined Insights and Implications

#### 6.3.1. Exit Preference is a Flow Destroyer

The temporal analysis confirms that exit preferences are **fundamentally incompatible** with efficient evacuation:

- **722% increase** in peak deadlock
- **102% longer** high-congestion duration
- **48% earlier** congestion onset
- **12% more variable** flow (stop-and-go dynamics)

**Mechanism**: Preferences convert evacuation from a **simple convergent flow** to a **complex cross-traffic problem**. Agents traveling to distant preferred exits must traverse the paths of agents heading to nearer exits, creating gridlock in open spaces where no physical bottleneck exists.

**Real-World Analogy**: This is similar to a roundabout where all cars insist on taking the third exit, forcing them to cross the paths of cars taking the first or second exit, even when those exits lead to the same destination.

#### 6.3.2. Width is Scenario-Dependent

The exit width experiment reveals a **critical limitation** of one-size-fits-all design rules:

- In the SEATS scenario (structured obstacles, gradual arrival), width 1x vs 4x makes **<1% difference** in total time
- In earlier analysis of open spaces (Section 3.7), width increases showed significant improvements

**Implication**: Exit width matters when **exit capacity is the bottleneck**, which occurs in:

- High-density open spaces where agents arrive simultaneously
- Panic scenarios with rapid convergence
- Venues with few internal obstacles

Exit width is **less critical** when:

- Internal obstacles slow agent approach
- Agents arrive at exits gradually
- Density is moderate relative to available space

#### 6.3.3. Speed as an Early Warning System

The temporal analysis reveals that **speed degradation precedes deadlock spikes**:

- Speed drops at ~5-10% of simulation time
- Deadlock peaks at ~25-45% of simulation time
- **10-20 percentage point lag** between speed drop and deadlock peak

**Application**: In real-time monitoring systems for stadiums, transit hubs, or events, tracking **average agent speed** could provide 10-20% advance warning before visible gridlock occurs, allowing interventions (opening emergency exits, redirecting crowds, halting entry) to prevent catastrophic congestion.

#### 6.3.4. Design Recommendations

1. **Never Use Exit Preferences**: The temporal analysis shows no phase of the simulation where preferences provide any advantage. They increase congestion from the very beginning (2.7% vs 5.2% onset) and maintain it throughout (32.8% vs 16.2% duration). **Opportunistic routing should be mandatory.**
2. **Optimize Internal Flow Before Exits**: In structured environments (theaters, stadiums with seating), invest in **aisle width, obstacle removal, and internal navigation** before expanding exit width. The SEATS data shows that exit width 1x → 4x provides minimal benefit because agents are slowed *before* reaching exits.
3. **Monitor Speed, Not Just Density**: Real-time systems should track **average speed** as a leading indicator of congestion, not just crowd density or headcount. Speed drops signal imminent gridlock with enough lead time for intervention.
4. **Dynamic Exit Assignment**: Instead of fixed preferences, implement **dynamic nearest-exit routing** that updates as congestion develops. Agents should re-route to less congested exits in real-time, maintaining opportunistic behavior throughout evacuation.

