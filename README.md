# Motorsport Monte Carlo Simulation

A stochastic simulation tool for motorsport racing scenarios.

## Features

- **Engine Modeling**: Degradation based on RPM, throttle, and driver stress.
- **Monte Carlo Analysis**: Run hundreds of simulations to predict DNF probability and lap time consistency.
- **Interactive Dashboard**: Explore results and telemetry using Streamlit and Plotly.

## Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:

   ```bash
   streamlit run app.py
   ```

## Files

- `app.py`: Streamlit dashboard.
- `engine_model.py`: Core logic for engine telemetry.
- `race_simulator.py`: Monte Carlo simulation driver.
- `visuals.py`: Plotly visualization functions.
