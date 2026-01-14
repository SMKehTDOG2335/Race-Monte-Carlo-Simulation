"""
Copyright (c) 2026 Steve Mathews Korah. All rights reserved.

DISCLAIMER: This project, "Race-Monte-Carlo-Simulation", is proprietary software. 
Any external use, reproduction, or distribution of this code in any capacity 
without explicit written permission from Steve Mathews Korah is strictly prohibited.

This project utilizes the "Fast-F1" library (theOehrly/Fast-F1). 
We do not claim ownership of the Fast-F1 library or the underlying F1 data 
provided by its API. Use of Fast-F1 data is subject to their own terms and disclaimers.
"""
import fastf1
import streamlit as st
import plotly.graph_objects as go
import numpy as np


def show_telemetry(df):
    """
    Displays race telemetry using Streamlit's native charts.
    """
    st.subheader("📈 Lap Time Evolution")
    st.line_chart(df.set_index("Lap")["LapTime"])

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚡ Engine Power")
        st.line_chart(df.set_index("Lap")["Power"])
    
    with col2:
        st.subheader("🌡️ Engine Temperature")
        st.line_chart(df.set_index("Lap")["Temp"])
    
    # New telemetry from v2.0
    if 'FuelPenalty' in df.columns:
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("⛽ Fuel Effect")
            st.line_chart(df.set_index("Lap")["FuelPenalty"])
        
        with col4:
            st.subheader("🛞 Tyre Degradation")
            st.line_chart(df.set_index("Lap")["TyreDeg"])
    
    # Safety Car indicator
    if 'SafetyCar' in df.columns and df['SafetyCar'].any():
        sc_laps = df[df['SafetyCar'] == True]['Lap'].tolist()
        st.info(f"🚗 Safety Car active on laps: {sc_laps}")

def plot_comparison(sim_df, real_df, driver_code):
    """
    Plots a comparison between simulated lap times and real-world F1 data.
    """
    fig = go.Figure()
    
    # Simulated Lap Times
    fig.add_trace(go.Scatter(
        x=sim_df['Lap'], 
        y=sim_df['LapTime'],
        name='Simulated Lap Time',
        line=dict(color='#3498db', width=2)
    ))
    
    # Real Lap Times
    fig.add_trace(go.Scatter(
        x=real_df['LapNumber'], 
        y=real_df['LapTimeSeconds'],
        name=f'Real Lap Time ({driver_code})',
        line=dict(color='#e74c3c', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title='Simulated vs Real Lap Times',
        xaxis_title='Lap Number',
        yaxis_title='Lap Time (s)',
        template='plotly_dark',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig
def plot_strategy_optimization(results_df):
    """
    Plots a heatmap-style line chart for strategy optimization results.
    """
    fig = go.Figure()
    
    compounds = results_df['compound'].unique()
    colors = {'soft': '#ff4b4b', 'medium': '#f1c40f', 'hard': '#ecf0f1'}
    
    for compound in compounds:
        df = results_df[results_df['compound'] == compound]
        fig.add_trace(go.Scatter(
            x=df['pit_lap'], 
            y=df['expected_time'],
            name=f'{compound.capitalize()} Strategy',
            line=dict(color=colors.get(compound, '#95a5a6'), width=3)
        ))
    
    fig.update_layout(
        title='Strategy Optimization Analysis',
        xaxis_title='Pit Stop Lap',
        yaxis_title='Expected Race Time (s)',
        template='plotly_dark',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig
