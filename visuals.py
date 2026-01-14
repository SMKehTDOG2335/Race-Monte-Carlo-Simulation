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
    Displays race telemetry using Plotly for professional axis labeling and units.
    """
    # Lap Time Evolution
    fig_lap = go.Figure()
    fig_lap.add_trace(go.Scatter(x=df['Lap'], y=df['LapTime'], name='Lap Time', line=dict(color='#3498db', width=2)))
    fig_lap.update_layout(
        title='⏱️ Lap Time Evolution',
        xaxis_title='Lap Number',
        yaxis_title='Lap Time (s)',
        template='plotly_dark',
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_lap, use_container_width=True)

    col1, col2 = st.columns(2)
    
    # Engine Power
    with col1:
        fig_pwr = go.Figure()
        fig_pwr.add_trace(go.Scatter(x=df['Lap'], y=df['Power'], name='Power', line=dict(color='#e74c3c', width=2)))
        fig_pwr.update_layout(
            title='⚡ Engine Power',
            xaxis_title='Lap Number',
            yaxis_title='Power (hp)',
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_pwr, use_container_width=True)
    
    # Engine Temperature
    with col2:
        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(x=df['Lap'], y=df['Temp'], name='Temp', line=dict(color='#f39c12', width=2)))
        fig_temp.update_layout(
            title='🌡️ Engine Temperature',
            xaxis_title='Lap Number',
            yaxis_title='Temperature (°C)',
            template='plotly_dark',
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Fuel and Tyre Effects
    if 'FuelPenalty' in df.columns:
        col3, col4 = st.columns(2)
        
        with col3:
            fig_fuel = go.Figure()
            fig_fuel.add_trace(go.Scatter(x=df['Lap'], y=df['FuelPenalty'], name='Fuel Penalty', line=dict(color='#9b59b6', width=2)))
            fig_fuel.update_layout(
                title='⛽ Fuel Weight Penalty',
                xaxis_title='Lap Number',
                yaxis_title='Time Penalty (s)',
                template='plotly_dark',
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_fuel, use_container_width=True)
        
        with col4:
            fig_tyre = go.Figure()
            fig_tyre.add_trace(go.Scatter(x=df['Lap'], y=df['TyreDeg'], name='Tyre Deg', line=dict(color='#2ecc71', width=2)))
            fig_tyre.update_layout(
                title='🛞 Tyre Degradation Effect',
                xaxis_title='Lap Number',
                yaxis_title='Time Penalty (s)',
                template='plotly_dark',
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig_tyre, use_container_width=True)
    
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
