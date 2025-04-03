import pandas as pd
from datetime import datetime, timedelta
import random

def get_sensors_data():
    """
    Returns sample sensor data for demonstration
    
    In a real application, this would fetch data from a database
    """
    # Sensor types
    sensor_types = ['pressure', 'temperature', 'humidity', 'movement']
    
    # Status options
    status_options = ['active', 'inactive', 'maintenance', 'error']
    status_weights = [0.7, 0.1, 0.1, 0.1]  # Weights for random selection
    
    # Generate random sensor data
    sensors = []
    
    for i in range(1, 21):  # Generate 20 sensors
        sensor_id = f"SEN-{200 + i}"
        sensor_type = sensor_types[i % len(sensor_types)]
        status = random.choices(status_options, weights=status_weights, k=1)[0]
        
        # Power connection (all sensors are plugged in)
        power_connection = True
        
        # Signal strength based on status
        if status == 'active':
            signal_strength = random.randint(7, 10)
        elif status == 'error':
            signal_strength = random.randint(1, 4)
        else:
            signal_strength = random.randint(4, 8)
        
        # Firmware version
        firmware_version = f"v{random.choice(['1.5', '1.8', '2.0', '2.1'])}"
        
        # Installation date (between 1 and 2 years ago)
        days_ago = random.randint(365, 730)
        installation_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Last maintenance (between 1 and 180 days ago)
        maintenance_days_ago = random.randint(1, 180)
        last_maintenance = (datetime.now() - timedelta(days=maintenance_days_ago)).strftime('%Y-%m-%d')
        
        # Assign to a mattress (some may be unassigned)
        if random.random() < 0.9:  # 90% chance of being assigned
            mattress_id = f"MAT-{101 + (i // 3)}"  # Distribute sensors across mattresses
        else:
            mattress_id = None
        
        sensors.append({
            'id': sensor_id,
            'name': f"{sensor_type.capitalize()} Sensor {i}",
            'type': sensor_type,
            'status': status,
            'power_connection': power_connection,
            'signal_strength': signal_strength,
            'firmware_version': firmware_version,
            'installation_date': installation_date,
            'last_maintenance': last_maintenance,
            'mattress_id': mattress_id
        })
    
    return pd.DataFrame(sensors)

def get_mattresses_data():
    """
    Returns sample mattress data for demonstration
    
    In a real application, this would fetch data from a database
    """
    # Status options
    status_options = ['active', 'maintenance', 'inactive']
    status_weights = [0.8, 0.1, 0.1]  # Weights for random selection
    
    # Locations
    locations = ['Ward A', 'Ward B', 'ICU', 'Recovery']
    
    # Generate random mattress data
    mattresses = []
    
    for i in range(1, 8):  # Generate 7 mattresses
        mattress_id = f"MAT-{100 + i}"
        status = random.choices(status_options, weights=status_weights, k=1)[0]
        
        # Patient ID
        patient_id = f"P-{1000 + i}"
        
        # Location
        location = random.choice(locations)
        
        # Installation date (between 1 and 3 years ago)
        days_ago = random.randint(365, 1095)
        installation_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Last maintenance (between 1 and 180 days ago)
        maintenance_days_ago = random.randint(1, 180)
        last_maintenance = (datetime.now() - timedelta(days=maintenance_days_ago)).strftime('%Y-%m-%d')
        
        mattresses.append({
            'id': mattress_id,
            'name': f"Mattress {i}",
            'status': status,
            'patient_id': patient_id,
            'location': location,
            'installation_date': installation_date,
            'last_maintenance': last_maintenance
        })
    
    return pd.DataFrame(mattresses)

def get_alerts_data():
    """
    Returns sample alert data for demonstration
    
    In a real application, this would fetch data from a database
    """
    # Priority options
    priority_options = ['critical', 'high', 'medium', 'low']
    
    # Status options
    status_options = ['active', 'acknowledged', 'resolved']
    
    # Generate random alert data
    alerts = []
    alert_id = 1
    
    # Sample alert templates
    alert_templates = [
        {
            'title': 'Power Issue',
            'description': 'Sensor power connection unstable',
            'priority': 'high'
        },
        {
            'title': 'Power Disconnected',
            'description': 'Sensor disconnected from power source',
            'priority': 'critical'
        },
        {
            'title': 'Sensor Offline',
            'description': 'Sensor has been offline for more than 30 minutes',
            'priority': 'high'
        },
        {
            'title': 'Calibration Due',
            'description': 'Sensor calibration is overdue',
            'priority': 'medium'
        },
        {
            'title': 'Signal Strength Low',
            'description': 'Sensor signal strength is weak',
            'priority': 'medium'
        },
        {
            'title': 'Sensor Error',
            'description': 'Sensor reported an error code',
            'priority': 'critical'
        },
        {
            'title': 'Maintenance Due',
            'description': 'Routine maintenance is due',
            'priority': 'low'
        },
        {
            'title': 'Firmware Update Available',
            'description': 'New firmware version available for sensor',
            'priority': 'low'
        }
    ]
    
    # Create a mix of active and historical alerts
    for i in range(20):  # Generate 20 alerts
        # Select a random alert template
        template = random.choice(alert_templates)
        
        # Generate a timestamp within the last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        timestamp = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Determine status based on age and priority
        if days_ago < 2:  # Recent alerts are more likely to be active
            status = random.choices(status_options, weights=[0.7, 0.2, 0.1], k=1)[0]
        else:  # Older alerts are more likely to be resolved
            status = random.choices(status_options, weights=[0.1, 0.3, 0.6], k=1)[0]
        
        # Make critical alerts more likely to be active
        if template['priority'] == 'critical' and random.random() < 0.8:
            status = 'active'
        
        # Select a random mattress and sensor
        mattress_id = f"MAT-{101 + random.randint(0, 6)}"
        sensor_id = f"SEN-{201 + random.randint(0, 19)}"
        
        alerts.append({
            'id': alert_id,
            'title': template['title'],
            'description': template['description'],
            'priority': template['priority'],
            'status': status,
            'timestamp': timestamp,
            'mattress_id': mattress_id,
            'sensor_id': sensor_id
        })
        
        alert_id += 1
    
    return pd.DataFrame(alerts)

def get_sensor_types():
    """
    Returns the list of available sensor types
    """
    return ['pressure', 'temperature', 'humidity', 'movement']
