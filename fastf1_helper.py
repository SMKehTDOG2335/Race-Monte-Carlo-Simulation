import fastf1
import pandas as pd
import numpy as np
import os

# Create a cache directory for FastF1
CACHE_DIR = 'fastf1_cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

fastf1.Cache.enable_cache(CACHE_DIR)

def get_session_data(year, gp, session_type='R'):
    """
    Fetches session data from FastF1.
    """
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()
        return session
    except Exception as e:
        print(f"Error loading session: {e}")
        return None

def get_driver_laps(session, driver_code):
    """
    Extracts lap data for a specific driver.
    """
    laps = session.laps.pick_driver(driver_code)
    # Filter out invalidated laps or non-timed laps if necessary
    # For simulation base, we want representative lap times
    laps = laps.dropna(subset=['LapTime'])
    
    # Convert LapTime to seconds
    laps['LapTimeSeconds'] = laps['LapTime'].dt.total_seconds()
    
    return laps

def get_race_summary(session, driver_code):
    """
    Returns a summary of the race for the driver to calibrate the simulation.
    """
    laps = get_driver_laps(session, driver_code)
    if laps.empty:
        return None
    
    # Calculate base lap (median of representative laps)
    # We exclude the first lap and pit laps for a better 'base' estimate
    representative_laps = laps[laps['PitInTime'].isna() & laps['PitOutTime'].isna()]
    if representative_laps.empty:
        representative_laps = laps # fallback
        
    base_lap = representative_laps['LapTimeSeconds'].median()
    lap_std = representative_laps['LapTimeSeconds'].std()
    total_laps = int(laps['LapNumber'].max())
    
    # Pit info
    pit_stops = laps[laps['PitInTime'].notna()]
    pit_laps = pit_stops['LapNumber'].tolist()
    
    return {
        'base_lap': float(base_lap),
        'lap_std': float(lap_std) if not np.isnan(lap_std) else 0.5,
        'total_laps': total_laps,
        'pit_laps': pit_laps,
        'driver': driver_code,
        'event': session.event['EventName']
    }

def get_session_drivers(session):
    """
    Returns a list of driver codes in the session.
    """
    return session.results['Abbreviation'].tolist()

def get_track_constants(venue_name):
    """
    Returns historical defaults for specific tracks.
    """
    # Track-specific data (Approximate values for simulation)
    # pit_loss: seconds lost in pit lane
    # deg_factor: multiplier for tyre degradation
    track_db = {
        'Monaco': {'pit_loss': 25.0, 'deg_factor': 0.8},
        'Monza': {'pit_loss': 24.0, 'deg_factor': 0.7},
        'Silverstone': {'pit_loss': 23.0, 'deg_factor': 1.1},
        'Bahrain': {'pit_loss': 22.5, 'deg_factor': 1.4},
        'Spa': {'pit_loss': 21.0, 'deg_factor': 1.0},
        'Montreal': {'pit_loss': 18.0, 'deg_factor': 0.9},
        'Suzuka': {'pit_loss': 22.0, 'deg_factor': 1.2},
        'Singapore': {'pit_loss': 28.0, 'deg_factor': 0.9},
    }
    
    # Simple fuzzy match
    for track, constants in track_db.items():
        if track.lower() in venue_name.lower():
            return constants
            
    # Default fallback
    return {'pit_loss': 22.0, 'deg_factor': 1.0}
