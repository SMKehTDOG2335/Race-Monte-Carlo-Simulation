"""
Monte Carlo Race Strategy Simulator
Race Engineer Approved - v2.0
"""
import streamlit as st
import numpy as np
import pandas as pd
from race_simulator import simulate_race, run_monte_carlo, StrategyOptimizer
from visuals import show_telemetry, plot_comparison, plot_strategy_optimization
from fastf1_helper import get_session_data, get_driver_laps, get_race_summary, get_session_drivers, get_track_constants

st.set_page_config(
    page_title="Monte Carlo Race Strategy", 
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ Monte Carlo Race Strategy Simulator")
st.caption("Professional-grade race simulation with fuel, tyre, and safety car modeling")

# =============================================================================
# SIDEBAR PARAMETERS
# =============================================================================
st.sidebar.header("🔧 Race Parameters")

laps_input = st.sidebar.slider("Total Laps", 30, 70, 50)
base_lap_input = st.sidebar.slider("Base Lap Time (s)", 80.0, 110.0, 90.0)
lap_std_input = st.sidebar.slider("Lap Time Variability", 0.1, 2.0, 0.5)

st.sidebar.header("🏁 FastF1 Real Data Import")
with st.sidebar.expander("Import Real F1 Session"):
    ff1_year = st.selectbox("Year", range(2024, 2018, -1), index=0)
    ff1_gp = st.text_input("GP Name (e.g. Silverstone)", "Silverstone")
    if st.button("Fetch Drivers"):
        with st.spinner("Fetching drivers..."):
            session = get_session_data(ff1_year, ff1_gp)
            if session:
                st.session_state.ff1_session = session
                st.session_state.ff1_drivers = get_session_drivers(session)
            else:
                st.error("Failed to load session.")

    if 'ff1_drivers' in st.session_state:
        driver = st.selectbox("Select Driver", st.session_state.ff1_drivers)
        if st.button("Apply as Base"):
            summary = get_race_summary(st.session_state.ff1_session, driver)
            if summary:
                st.session_state.ff1_real_data = get_driver_laps(st.session_state.ff1_session, driver)
                st.session_state.ff1_summary = summary
                
                # Track calibration
                venue = st.session_state.ff1_session.event['EventName']
                track_data = get_track_constants(venue)
                st.session_state.track_data = track_data
                
                st.success(f"Applied {driver}'s data as baseline for {venue}!")
            else:
                st.error("Could not find representative data.")

# Use session state or defaults for simulation parameters
if 'ff1_summary' in st.session_state:
    laps = st.sidebar.slider("Total Laps", 30, 100, st.session_state.ff1_summary['total_laps'], key="ff1_laps")
    base_lap = st.sidebar.slider("Base Lap Time (s)", 70.0, 120.0, st.session_state.ff1_summary['base_lap'], key="ff1_base")
    lap_std = st.sidebar.slider("Lap Time Variability", 0.1, 2.0, st.session_state.ff1_summary['lap_std'], key="ff1_std")
else:
    laps = laps_input
    base_lap = base_lap_input
    lap_std = lap_std_input

st.sidebar.header("⛽ Fuel & Engine")
fuel_load = st.sidebar.slider("Starting Fuel (kg)", 50.0, 110.0, 100.0)
engine_stress = st.sidebar.slider("Engine Stress", 0.5, 2.0, 1.0)
reliability = st.sidebar.slider("Engine Reliability", 0.90, 1.0, 0.98)

st.sidebar.header("🛞 Tyre Strategy")
tyre_compound = st.sidebar.selectbox("Tyre Compound", ['soft', 'medium', 'hard'], index=1)

# Pit loss auto-calibration
default_pit_loss = 22.0
if 'track_data' in st.session_state:
    default_pit_loss = st.session_state.track_data['pit_loss']

pit_lap = st.sidebar.slider("Pit Stop Lap", 5, laps - 5, laps // 2)
pit_loss = st.sidebar.slider("Pit Loss Time (s)", 15.0, 30.0, default_pit_loss)

# Deg factor auto-calibration
deg_factor = 1.0
if 'track_data' in st.session_state:
    deg_factor = st.session_state.track_data['deg_factor']
    st.sidebar.info(f"📍 Track Calibration: {st.session_state.ff1_session.event['EventName']} (Deg: {deg_factor}x)")

st.sidebar.header("🎲 Simulation")
enable_sc = st.sidebar.checkbox("Enable Safety Car", value=True)
sims = st.sidebar.slider("Monte Carlo Simulations", 500, 10000, 2000)

# Build params dict
sim_params = {
    "base_lap": base_lap,
    "lap_std": lap_std,
    "laps": laps,
    "pit_lap": pit_lap,
    "pit_loss": pit_loss,
    "engine_stress": engine_stress,
    "reliability": reliability,
    "fuel_load": fuel_load,
    "tyre_compound": tyre_compound,
    "enable_safety_car": enable_sc,
    "deg_factor": deg_factor
}

# =============================================================================
# MONTE CARLO ANALYSIS
# =============================================================================
if st.button("🎲 Run Monte Carlo Analysis", type="primary"):
    progress_bar = st.progress(0, text="Initializing simulations...")
    results = []
    
    for i in range(sims):
        t, df, dnf, dnf_lap = simulate_race(**sim_params)
        if not dnf:
            results.append(t)
        
        if (i + 1) % (sims // 10) == 0:
            progress_bar.progress((i + 1) / sims, text=f"Simulating race {i + 1}/{sims}...")
    
    progress_bar.empty()
    
    if results:
        st.success(f"✅ Completed {sims} simulations | {len(results)} finished races")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Expected Time", f"{np.mean(results):.2f}s")
        col2.metric("Best Case (P5)", f"{np.percentile(results, 5):.2f}s")
        col3.metric("Worst Case (P95)", f"{np.percentile(results, 95):.2f}s")
        col4.metric("Finish Rate", f"{100 * len(results) / sims:.1f}%")
        
        st.subheader("📊 Race Time Distribution")
        hist_values, _ = np.histogram(results, bins=40)
        st.bar_chart(hist_values)
    else:
        st.error("❌ All simulations resulted in DNF. Reduce engine stress or increase reliability.")

st.divider()

# =============================================================================
# SINGLE RACE DEEP DIVE
# =============================================================================
st.subheader("🔬 Single Race Analysis")
if st.button("Simulate Individual Race"):
    total_time, race_df, dnf, dnf_lap = simulate_race(**sim_params)
    
    if not dnf:
        st.success(f"🏁 Finished! Total Time: {total_time:.2f}s")
    
    # Comparison plot if real data is available
    if 'ff1_real_data' in st.session_state:
        st.subheader("🏁 Real vs Simulated Comparison")
        comp_plot = plot_comparison(race_df, st.session_state.ff1_real_data, st.session_state.ff1_summary['driver'])
        st.plotly_chart(comp_plot, use_container_width=True)

    show_telemetry(race_df)
    
    with st.expander("📋 Raw Telemetry Data"):
        st.dataframe(race_df)

st.divider()

# =============================================================================
# STRATEGY OPTIMIZER
# =============================================================================
st.subheader("🚀 Winning Strategy Optimizer")
st.markdown("Identifies the ideal pit stop lap and tyre compound for these track conditions.")

if st.button("Find Optimal Strategy"):
    with st.spinner("Analyzing thousands of scenarios..."):
        opt_results = StrategyOptimizer.find_optimal_strategy(sim_params)
        
        if opt_results:
            full_df, best = opt_results
            
            # Display result
            st.success(f"🏆 **Ideal Strategy Found**")
            c1, c2, c3 = st.columns(3)
            c1.metric("Optimal Compound", best['compound'].upper())
            c2.metric("Optimal Pit Lap", f"Lap {best['pit_lap']}")
            c3.metric("Expected Race Time", f"{best['expected_time']:.2f}s")
            
            st.markdown(f"> **Engineer's Note**: For {st.session_state.ff1_session.event['EventName'] if 'ff1_session' in st.session_state else 'this track'}, the best chance of victory is pushing a **{best['compound']}** stint until **Lap {best['pit_lap']}**.")
            
            st.plotly_chart(plot_strategy_optimization(full_df), use_container_width=True)
        else:
            st.error("Optimization failed. All tested strategies resulted in DNF.")
