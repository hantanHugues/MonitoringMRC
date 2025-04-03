import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def get_sensor_status_color(status):
    """
    Returns the color associated with a sensor status
    """
    status_colors = {
        'active': '#28a745',      # Green
        'inactive': '#6c757d',    # Gray
        'error': '#dc3545',       # Red
        'maintenance': '#ffc107', # Yellow/Orange
        'calibrating': '#17a2b8', # Cyan
        'ok': '#28a745',          # Green
        'warning': '#ffc107',     # Yellow/Orange
        'critical': '#dc3545'     # Red
    }
    
    return status_colors.get(status.lower(), '#6c757d')  # Default to gray if status not found

def get_battery_level_color(battery_level):
    """
    Returns the color based on battery level percentage
    """
    if battery_level >= 70:
        return '#28a745'  # Green
    elif battery_level >= 30:
        return '#ffc107'  # Yellow
    else:
        return '#dc3545'  # Red

def generate_sample_data(sensor_type, start_time, end_time, interval_seconds=300):
    """
    Generates sample time series data for a specific sensor type.
    Used for demonstration purposes only.
    
    Parameters:
    - sensor_type: Type of sensor (pressure, temperature, humidity, movement)
    - start_time: Start time for the data
    - end_time: End time for the data
    - interval_seconds: Time interval between data points in seconds
    
    Returns:
    - DataFrame with timestamp and simulated sensor values
    """
    # Calculate number of data points
    total_seconds = (end_time - start_time).total_seconds()
    num_points = int(total_seconds / interval_seconds) + 1
    
    # Generate timestamps
    timestamps = [start_time + timedelta(seconds=i * interval_seconds) for i in range(num_points)]
    
    # Generate values based on sensor type
    if sensor_type == 'pressure':
        # Pressure in mmHg, normal range around 80-120
        base_value = 100
        amplitude = 20
        values = [base_value + amplitude * np.sin(i/50) + random.uniform(-5, 5) for i in range(num_points)]
    
    elif sensor_type == 'temperature':
        # Body temperature in Celsius, normal range around 36-38
        base_value = 37
        amplitude = 0.5
        values = [base_value + amplitude * np.sin(i/100) + random.uniform(-0.2, 0.2) for i in range(num_points)]
    
    elif sensor_type == 'humidity':
        # Humidity percentage, normal range around 40-60%
        base_value = 50
        amplitude = 10
        values = [base_value + amplitude * np.sin(i/80) + random.uniform(-3, 3) for i in range(num_points)]
    
    elif sensor_type == 'movement':
        # Movement intensity on a scale of 0-10
        # Simulate periods of movement and rest
        values = []
        for i in range(num_points):
            if i % 100 < 20:  # Simulate movement every ~8 hours (with 5-minute intervals)
                values.append(random.uniform(3, 8))
            else:
                values.append(random.uniform(0, 1))
    
    else:
        # Generic values between 0-100
        base_value = 50
        amplitude = 25
        values = [base_value + amplitude * np.sin(i/60) + random.uniform(-10, 10) for i in range(num_points)]
    
    # Create DataFrame
    data = {
        'timestamp': timestamps,
        'value': values
    }
    
    return pd.DataFrame(data)
