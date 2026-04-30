import time
import numpy as np
import plotly.express as px
from scipy.stats import poisson
import streamlit as st

# Setup page styling
st.set_page_config(page_title="Arsenal Run-In Simulator", page_icon="⚽")
st.title("🔴 Arsenal Points Simulator")
st.write(
    "Adjust Arsenal's form and watch the Monte Carlo simulation calculate point probabilities live!"
)

# 1. Team Form Adjustments in Sidebar
st.sidebar.header("🕹️ Team Form Adjustments")
attack_boost = st.sidebar.slider(
    "Arsenal Attack Intensity", 0.5, 2.0, 1.0, 0.1
)
defense_boost = st.sidebar.slider(
    "Arsenal Defense Solidity", 0.5, 2.0, 1.0, 0.1
)

# Baseline Expected Goals per game (normally calculated via real data)
# We will use hardcoded baseline averages here for the remaining 4 games
# Opponents: Fulham, West Ham, Burnley, Crystal Palace
fixtures = [
    {"opponent": "Fulham", "ars_xg": 1.74, "opp_xg": 1.34},
    {"opponent": "West Ham", "ars_xg": 1.74, "opp_xg": 1.2},
    {"opponent": "Burnley", "ars_xg": 1.74, "opp_xg": 0.89},
    {"opponent": "Crystal Palace", "ars_xg": 1.74, "opp_xg": 1.44},
]


# 2. Simulation Logic
def run_simulation(n_sims=10000):
    simulated_totals = []

    for _ in range(n_sims):
        total_pts = 0
        momentum = 1.0  # Start with neutral momentum
        for game in fixtures:
            # Apply sliders directly to the expected goal rates (lambdas)
            ars_lambda = game["ars_xg"] * attack_boost * momentum

            # Dividing by defense_boost because higher defense reduces opponent goals
            opp_lambda = game["opp_xg"] / defense_boost

            # Poisson draw for simulated score
            ars_goals = poisson.rvs(ars_lambda)
            opp_goals = poisson.rvs(opp_lambda)

            # Assign points
            if ars_goals > opp_goals:
                total_pts += 3
                momentum *= 1.1  # Winning boosts confidence
            elif ars_goals == opp_goals:
                total_pts += 1
                momentum *= 0.9  # Draw hurts momentum slightly
            else:
                total_pts += 0
                momentum *= 0.8  # Losing hurts confidence

        simulated_totals.append(total_pts)

    # Convert totals into percentages for all possible outcomes (0 to 12 points)
    probabilities = []
    for pts in range(13):
        prob = (simulated_totals.count(pts) / n_sims) * 100
        probabilities.append(round(prob, 2))

    return probabilities


# 3. Add an exciting "Run" Button
if st.button("🚀 RUN 10,000 SIMULATIONS"):

    # Loading effect
    progress_bar = st.progress(0)
    status_text = st.empty()
    for i in range(1, 101, 10):
        status_text.text(f"Simulating universe #{i*100}...")
        progress_bar.progress(i)
        time.sleep(0.02)
    status_text.empty()
    progress_bar.empty()

    # RUN THE ACTUAL MATH
    points_possible = list(range(13))
    probabilities = run_simulation(10000)

    # 4. Big Stat Callouts
    most_likely_pts = np.argmax(probabilities)
    prob_percentage = probabilities[most_likely_pts]

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Most Likely Points", value=f"{most_likely_pts} Pts")
    with col2:
        st.metric(
            label="Confidence", value=f"{prob_percentage}%", delta="Highest"
        )

    # 5. Create an interactive Plotly bar chart
    fig = px.bar(
        x=points_possible,
        y=probabilities,
        labels={"x": "Total Points Earned", "y": "Probability (%)"},
        title="Real Probability of Final Points Tally",
        color=probabilities,
        color_continuous_scale="Reds",
    )

    fig.update_layout(
        xaxis=dict(tickmode="linear", tick0=0, dtick=1),
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )

    # Render chart
    st.plotly_chart(fig, use_container_width=True)

    # 6. Display a major takeaway headline
    st.success(
        f"🎯 **Verdict:** Based on your settings, the most likely outcome is Arsenal earning **{most_likely_pts} points**!"
    )