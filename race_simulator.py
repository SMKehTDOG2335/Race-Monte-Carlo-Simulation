"""
Copyright (c) 2026 Steve Mathews Korah. All rights reserved.

DISCLAIMER: This project, "Race-Monte-Carlo-Simulation", is proprietary software. 
Any external use, reproduction, or distribution of this code in any capacity 
without explicit written permission from Steve Mathews Korah is strictly prohibited.

This project utilizes the "Fast-F1" library (theOehrly/Fast-F1). 
We do not claim ownership of the Fast-F1 library or the underlying F1 data 
provided by its API. Use of Fast-F1 data is subject to their own terms and disclaimers.
"""
import numpy as np
import pandas as pd
from engine_model import (
    engine_power, 
    update_engine_deg, 
    simulate_engine_telemetry,
    fuel_effect,
    tyre_degradation,
    safety_car_check,
    safety_car_laps
)


def simulate_race(
    base_lap: float = 90.0,
    lap_std: float = 0.5,
    laps: int = 50,
    pit_lap: int = 25,
    pit_loss: float = 22.0,
    engine_stress: float = 1.0,
    reliability: float = 0.98,
    fuel_load: float = 110.0,
    tyre_compound: str = 'medium',
    enable_safety_car: bool = True,
    deg_factor: float = 1.0
) -> tuple[float, pd.DataFrame, bool, int | None]:
    """
    Simulates a single race with realistic physics.
    
    Features:
    - Fuel load effect (heavier car = slower laps)
    - Non-linear tyre degradation with cliff
    - Safety Car probability
    - Engine reliability and degradation
    
    Args:
        base_lap: Baseline lap time on empty track, fresh tyres, no fuel
        lap_std: Standard deviation for lap time variability
        laps: Total race laps
        pit_lap: Planned pit stop lap
        pit_loss: Time lost during pit stop (seconds)
        engine_stress: Engine stress multiplier (0.5=conservative, 2.0=push)
        reliability: Base engine reliability (0.90-1.0)
        fuel_load: Starting fuel in kg
        tyre_compound: 'soft', 'medium', or 'hard'
        enable_safety_car: Whether to simulate SC events
        deg_factor: Track abrasiveness multiplier
    
    Returns:
        Tuple of (total_time, telemetry_df, dnf_flag, dnf_lap)
    """
    engine_deg = 0.0
    stint_lap = 0
    total_time = 0.0
    telemetry = []
    dnf = False
    dnf_lap = None
    
    # Safety Car state
    sc_active = False
    sc_laps_remaining = 0
    current_compound = tyre_compound

    for lap in range(1, laps + 1):
        stint_lap += 1
        
        # --- Safety Car Check ---
        if enable_safety_car and not sc_active:
            if safety_car_check(lap, laps):
                sc_active = True
                sc_laps_remaining = safety_car_laps()
        
        if sc_active:
            sc_laps_remaining -= 1
            if sc_laps_remaining <= 0:
                sc_active = False
        
        # --- Engine Telemetry ---
        rpm, throttle, temp = simulate_engine_telemetry(engine_deg)
        power = engine_power(throttle, rpm, engine_deg)
        
        # --- Fuel Effect ---
        fuel_penalty = fuel_effect(lap, fuel_load)
        
        # --- Tyre Degradation ---
        tyre_deg_penalty, grip_bonus = tyre_degradation(stint_lap, current_compound, deg_factor)
        
        # --- Lap Time Calculation ---
        if sc_active:
            # Safety Car pace is fixed ~30s slower
            lap_time = base_lap + 30.0
        else:
            lap_time = (
                base_lap
                + fuel_penalty                      # Fuel weight
                + tyre_deg_penalty                  # Tyre wear
                + grip_bonus                        # Compound grip difference
                - (power - 900) * 0.002             # Engine power
                + np.random.normal(0, lap_std)      # Random variance
            )
        
        # --- DNF Check (Engine Failure) ---
        failure_prob = (1 - reliability) * (1 + engine_deg * 10)
        if np.random.random() < failure_prob:
            dnf = True
            dnf_lap = lap
            break
        
        # --- Pit Stop ---
        if lap == pit_lap:
            lap_time += pit_loss
            stint_lap = 0  # Reset tyre age
        
        # --- Update Engine ---
        engine_deg = update_engine_deg(engine_deg, engine_stress, lap, laps)
        total_time += lap_time
        
        # --- Log Telemetry ---
        telemetry.append({
            'Lap': lap,
            'LapTime': lap_time,
            'Power': power,
            'RPM': rpm,
            'Temp': temp,
            'EngineDeg': engine_deg,
            'FuelPenalty': fuel_penalty,
            'TyreDeg': tyre_deg_penalty,
            'SafetyCar': sc_active
        })

    df = pd.DataFrame(telemetry)
    return total_time, df, dnf, dnf_lap


class StrategyOptimizer:
    """
    Optimizes pit stop strategy for a specific track and set of conditions.
    """
    @staticmethod
    def find_optimal_strategy(sim_params, num_sims_per_config=50):
        results = []
        laps = sim_params['laps']
        compounds = ['soft', 'medium', 'hard']
        
        # Test a range of pit laps
        # Exclude early and late laps for realistic windows
        min_pit = max(5, int(laps * 0.2))
        max_pit = min(laps - 5, int(laps * 0.8))
        
        for compound in compounds:
            for pit_lap in range(min_pit, max_pit + 1, 2):
                test_params = sim_params.copy()
                test_params['tyre_compound'] = compound
                test_params['pit_lap'] = pit_lap
                test_params['enable_safety_car'] = False # Reduce noise for optimization
                
                sim_times = []
                for _ in range(num_sims_per_config):
                    t, _, dnf, _ = simulate_race(**test_params)
                    if not dnf:
                        sim_times.append(t)
                
                if sim_times:
                    avg_time = np.mean(sim_times)
                    results.append({
                        'compound': compound,
                        'pit_lap': pit_lap,
                        'expected_time': avg_time
                    })
        
        if not results:
            return None
            
        df = pd.DataFrame(results)
        best_idx = df['expected_time'].idxmin()
        return df, df.loc[best_idx]


def run_monte_carlo(
    num_simulations: int = 1000, 
    **sim_params
) -> pd.DataFrame:
    """
    Runs multiple race simulations for strategy analysis.
    
    Returns:
        DataFrame with simulation results including:
        - SimID, LapsCompleted, Finished, TotalTime, AvgLapTime, SafetyCarLaps
    """
    all_results = []
    
    for i in range(num_simulations):
        total_time, race_df, dnf, dnf_lap = simulate_race(**sim_params)
        
        last_lap = race_df['Lap'].max() if not race_df.empty else 0
        if dnf:
            last_lap = dnf_lap
        
        sc_laps = race_df['SafetyCar'].sum() if not race_df.empty else 0
        
        all_results.append({
            'SimID': i,
            'LapsCompleted': last_lap,
            'Finished': not dnf,
            'TotalTime': total_time if not dnf else np.nan,
            'AvgLapTime': race_df['LapTime'].mean() if not dnf else np.nan,
            'SafetyCarLaps': sc_laps
        })
    
    return pd.DataFrame(all_results)
