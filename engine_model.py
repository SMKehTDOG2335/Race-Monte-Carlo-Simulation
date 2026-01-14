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

# =============================================================================
# ENGINE MODEL
# =============================================================================

def engine_power(throttle: float, rpm: float, degradation: float) -> float:
    """
    Calculates engine output power (hp).
    
    Args:
        throttle: Throttle position (0-100%)
        rpm: Engine revolutions per minute
        degradation: Engine wear factor (0-1)
    
    Returns:
        Power output in horsepower
    """
    base_power = 1000  # hp
    return base_power * (throttle / 100) * (rpm / 15000) * (1 - degradation)


def update_engine_deg(current_deg: float, stress: float, lap: int, total_laps: int) -> float:
    """
    Exponential engine degradation model.
    Degradation accelerates in the final third of the race.
    
    Args:
        current_deg: Current degradation level (0-1)
        stress: Engine stress multiplier (0.5-2.0)
        lap: Current lap number
        total_laps: Total laps in race
    
    Returns:
        Updated degradation value (capped at 1.0)
    """
    base_rate = 0.0001
    stress_factor = 1 + (stress - 1) * 0.5
    
    # Exponential wear increase as race progresses
    race_progress = lap / total_laps
    progression_factor = 1 + race_progress * 0.5
    
    wear = base_rate * stress_factor * progression_factor
    noise = np.random.normal(0, 0.0002)
    
    return min(1.0, max(0, current_deg + wear + noise))


def simulate_engine_telemetry(engine_deg: float) -> tuple[float, float, float]:
    """
    Simulates real-time engine telemetry data.
    
    Returns:
        Tuple of (rpm, throttle, temperature)
    """
    rpm = np.random.normal(12000, 400)
    throttle = np.random.uniform(85, 100)
    temperature = 90 + engine_deg * 220 + np.random.normal(0, 1.5)
    return rpm, throttle, temperature


# =============================================================================
# FUEL MODEL
# =============================================================================

def fuel_effect(lap: int, fuel_load_kg: float = 110.0, burn_rate: float = 2.1) -> float:
    """
    Calculates lap time penalty from fuel weight.
    
    Real-world data:
    - F1 fuel load: ~110kg
    - Burn rate: ~2.1 kg/lap
    - Time cost: ~0.03s per kg
    
    Args:
        lap: Current lap number
        fuel_load_kg: Starting fuel load in kg
        burn_rate: Fuel consumption per lap (kg)
    
    Returns:
        Lap time penalty in seconds
    """
    fuel_remaining = max(0, fuel_load_kg - (lap * burn_rate))
    time_penalty = fuel_remaining * 0.03  # 0.03s per kg
    return time_penalty


# =============================================================================
# TYRE MODEL
# =============================================================================

TYRE_COMPOUNDS = {
    'soft':   {'grip_bonus': -0.8, 'base_deg': 0.030, 'cliff_lap': 12},
    'medium': {'grip_bonus':  0.0, 'base_deg': 0.018, 'cliff_lap': 22},
    'hard':   {'grip_bonus': +0.5, 'base_deg': 0.010, 'cliff_lap': 35},
}


def tyre_degradation(stint_lap: int, compound: str = 'medium', deg_factor: float = 1.0) -> tuple[float, float]:
    """
    Non-linear tyre degradation with cliff effect.
    
    The "cliff" is when tyres suddenly lose grip and lap times spike.
    
    Args:
        stint_lap: Laps since last pit stop
        compound: 'soft', 'medium', or 'hard'
        deg_factor: Track abrasiveness multiplier
    
    Returns:
        Tuple of (degradation_penalty, grip_bonus)
    """
    compound_data = TYRE_COMPOUNDS.get(compound, TYRE_COMPOUNDS['medium'])
    cliff_lap = compound_data['cliff_lap']
    base_deg = compound_data['base_deg'] * deg_factor
    grip_bonus = compound_data['grip_bonus']
    
    if stint_lap <= cliff_lap:
        # Linear degradation before cliff
        degradation = base_deg * stint_lap
    else:
        # Exponential penalty after cliff
        over_cliff = stint_lap - cliff_lap
        pre_cliff_deg = base_deg * cliff_lap
        # Penalty also scaled by deg_factor
        cliff_penalty = 0.15 * deg_factor * (1.2 ** over_cliff - 1)
        degradation = pre_cliff_deg + cliff_penalty
    
    return degradation, grip_bonus


# =============================================================================
# SAFETY CAR MODEL
# =============================================================================

def safety_car_check(lap: int, total_laps: int) -> bool:
    """
    Stochastic safety car event simulation.
    
    Real-world data:
    - ~60% of F1 races have at least one SC
    - Higher probability in first 5 and last 5 laps (first lap incidents, fatigue)
    
    Args:
        lap: Current lap number
        total_laps: Total laps in race
    
    Returns:
        True if Safety Car is deployed this lap
    """
    base_prob = 0.012  # ~1.2% per lap gives ~60% over 50 laps
    
    # Higher incident rate at race start and end
    if lap <= 3:
        base_prob = 0.035  # First lap chaos
    elif lap >= total_laps - 5:
        base_prob = 0.020  # Late race desperation
    
    return np.random.random() < base_prob


def safety_car_laps() -> int:
    """
    Returns the duration of a Safety Car period.
    Typically 3-6 laps in real races.
    """
    return np.random.randint(3, 7)
