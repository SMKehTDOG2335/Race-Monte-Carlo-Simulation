# Motorsport Monte Carlo Simulation

## 📄 Legal & Licensing

**Copyright (c) 2026 Steve Mathews Korah. All rights reserved.**

### ⚠️ Proprietary Notice & Disclaimer

This project is proprietary and confidential. Any external use, distribution, or reproduction of the "Race-Monte-Carlo-Simulation" codebase or its outputs in any capacity is strictly prohibited without explicit written permission from Steve Mathews Korah.

### 🤝 Partnerships & Attributions

This project proudly utilizes **[Fast-F1](https://github.com/theOehrly/Fast-F1)** by theOehrly for real-world telemetry data and session results.

- We acknowledge the significant contribution of the Fast-F1 community to the motorsport data ecosystem.
- **Data Disclaimer**: All Formula 1 data is fetched via the Fast-F1 API. We do not own this data, and its use is subject to the terms and conditions set by Fast-F1 and the official F1 data providers.

---

## 🏎️ Overview

A high-fidelity Monte Carlo simulation tool designed for Formula 1 race strategy optimization.

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
