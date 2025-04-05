import pandas as pd
from datetime import datetime, timedelta
import random
import streamlit as st
import logging
from utils.direct_simulator import get_direct_simulator, initialize_direct_simulator

def get_sensors_data():
    """
    Returns sensor data, combining MQTT data for mattress 1 and simulated data for others

    For sensors on mattress 1 (MAT-101), data is sourced from MQTT broker when available
    For other mattresses, data is simulated
    """
    # Sensor types avec leurs unités et noms
    sensor_types = [
        ('temperature', 'Capteur de température', '°C'),
        ('humidity', 'Capteur d\'humidité', '%'),
        ('debit_urinaire', 'Débit urinaire', 'ml/h'),
        ('poul', 'Pouls', 'bpm'),
        ('creatine', 'Créatinine', 'mg/dL')
    ]

    # Status options
    status_options = ['active', 'inactive', 'maintenance', 'error']
    status_weights = [0.7, 0.1, 0.1, 0.1]  # Weights for random selection

    # Initialize direct simulator if not already done
    try:
        # Try to initialize direct simulator if not already present
        if 'direct_simulator' not in st.session_state:
            direct_simulator = initialize_direct_simulator()
        else:
            direct_simulator = st.session_state['direct_simulator']
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation du simulateur direct: {e}")
        direct_simulator = None

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

        # Check if we have MQTT data for any mattress
        is_mqtt_updated = False
        if mattress_id:  # If sensor is assigned to a mattress
            # 1. First try to get data from MQTT broker (highest priority)
            if 'mqtt_integration' in st.session_state:
                mqtt_integration = st.session_state['mqtt_integration']
                if mqtt_integration and hasattr(mqtt_integration, 'connected') and mqtt_integration.connected:
                    mqtt_data = mqtt_integration.get_latest_data(sensor_id)

                    if mqtt_data and isinstance(mqtt_data, dict) and 'value' in mqtt_data:
                        # Update with MQTT data
                        is_mqtt_updated = True
                        # Force the sensor to be active when receiving MQTT data
                        status = 'active'
                        # Ensure signal strength is good
                        signal_strength = random.randint(8, 10)

                        # Add a log to show we're using MQTT data
                        logging.info(f"Using MQTT data for sensor {sensor_id} on mattress {mattress_id}")

            # 2. If no MQTT data, try the direct simulator (fallback)
            if not is_mqtt_updated:
                direct_simulator = None
                if 'direct_simulator' in st.session_state:
                    direct_simulator = st.session_state['direct_simulator']

                if direct_simulator:
                    simulated_data = direct_simulator.get_latest_data(sensor_id)
                    if simulated_data:
                        # Update with simulated data 
                        is_mqtt_updated = True
                        # Force the sensor to be active when receiving simulated data
                        status = 'active'
                        # Ensure signal strength is good
                        signal_strength = random.randint(8, 10)

                        # Add a log to show we're using simulated data
                        logging.info(f"Using simulated data for sensor {sensor_id} on mattress {mattress_id}")

        sensors.append({
            'id': sensor_id,
            'name': f"{sensor_type[1]} {i}", # Corrected line: Accessing the sensor name from the tuple
            'type': sensor_type[0], # Corrected line: Accessing the sensor type from the tuple
            'status': status,
            'power_connection': power_connection,
            'signal_strength': signal_strength,
            'firmware_version': firmware_version,
            'installation_date': installation_date,
            'last_maintenance': last_maintenance,
            'mattress_id': mattress_id,
            'is_mqtt_updated': is_mqtt_updated
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

# Stockage temporaire des données MQTT
mqtt_data_store = {
    'sensors': {},
    'last_update': None
}

def update_mqtt_data(sensor_id, value, timestamp, unit):
    """Mettre à jour le stockage temporaire avec les nouvelles données MQTT"""
    if sensor_id not in mqtt_data_store['sensors']:
        mqtt_data_store['sensors'][sensor_id] = []
    
    mqtt_data_store['sensors'][sensor_id].append({
        'value': value,
        'timestamp': timestamp,
        'unit': unit
    })
    
    # Garder seulement les 100 dernières valeurs
    if len(mqtt_data_store['sensors'][sensor_id]) > 100:
        mqtt_data_store['sensors'][sensor_id] = mqtt_data_store['sensors'][sensor_id][-100:]
    
    mqtt_data_store['last_update'] = timestamp

def get_sensor_readings(sensor_id, sensor_type, timeframe='day'):
    """
    Get sensor readings for a specific sensor, using MQTT data when available

    Parameters:
    - sensor_id: ID of the sensor
    - sensor_type: Type of the sensor
    - timeframe: 'hour', 'day', 'week', or 'month'

    Returns:
    - DataFrame with timestamp and value columns
    """
    from utils.sensor_utils import generate_sample_data
    from datetime import datetime, timedelta

    # Define the time range based on the timeframe
    end_time = datetime.now()
    if timeframe == 'hour':
        start_time = end_time - timedelta(hours=1)
        interval_seconds = 60  # 1 reading per minute
    elif timeframe == 'day':
        start_time = end_time - timedelta(days=1)
        interval_seconds = 300  # 5 minutes
    elif timeframe == 'week':
        start_time = end_time - timedelta(weeks=1)
        interval_seconds = 3600  # 1 hour
    elif timeframe == 'month':
        start_time = end_time - timedelta(days=30)
        interval_seconds = 7200  # 2 hours
    else:
        start_time = end_time - timedelta(days=1)
        interval_seconds = 300

    # Check if sensor is on mattress 1 and using MQTT
    mattress_id = None
    sensors_df = get_sensors_data()
    if not sensors_df.empty:
        sensor_row = sensors_df[sensors_df['id'] == sensor_id]
        if not sensor_row.empty:
            mattress_id = sensor_row.iloc[0]['mattress_id']
            is_mqtt_updated = sensor_row.iloc[0].get('is_mqtt_updated', False)

            # For Mattress 1 sensors with MQTT or simulated data, use the real-time values
            if mattress_id == "MAT-101" and is_mqtt_updated:
                # 1. First try to get MQTT data (highest priority)
                try:
                    if 'mqtt_integration' in st.session_state:
                        mqtt_integration = st.session_state['mqtt_integration']
                        if mqtt_integration and mqtt_integration.connected:
                            # Get the historical data from MQTT if available
                            mqtt_history = mqtt_integration.get_latest_data(sensor_id, history=True)

                            if mqtt_history and isinstance(mqtt_history, list) and len(mqtt_history) > 0:
                                # Convert MQTT history to DataFrame
                                history_data = []
                                for entry in mqtt_history:
                                    try:
                                        # Parse timestamp string to datetime object if it's a string
                                        timestamp = entry.get('timestamp')
                                        if isinstance(timestamp, str):
                                            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

                                        # Add to history data
                                        history_data.append({
                                            'timestamp': timestamp,
                                            'value': entry.get('value', 0)
                                        })
                                    except Exception as e:
                                        logging.error(f"Error parsing MQTT history entry: {e}")

                                if history_data:
                                    # Create DataFrame from MQTT history and sort by timestamp
                                    mqtt_df = pd.DataFrame(history_data)
                                    mqtt_df = mqtt_df.sort_values('timestamp')
                                    logging.info(f"Using MQTT history data for sensor {sensor_id} with {len(mqtt_df)} values")
                                    return mqtt_df
                except Exception as e:
                    logging.error(f"Error getting MQTT data for sensor {sensor_id}: {e}")

                # 2. Fallback to simulated data if MQTT data is not available
                try:
                    if 'direct_simulator' in st.session_state:
                        direct_simulator = st.session_state['direct_simulator']
                        simulated_data = direct_simulator.get_latest_data(sensor_id)
                        if simulated_data:
                            value = simulated_data.get('value')
                            logging.info(f"Using simulated data for sensor {sensor_id}: {value}")

                            # Generate sample data for historical values, but incorporate simulated value for latest
                            df = generate_sample_data(sensor_type, start_time, end_time, interval_seconds)

                            # Replace the latest value with simulated data
                            if not df.empty:
                                # Add random variation to simulate slightly changing values
                                factor = random.uniform(0.95, 1.05) 
                                df.iloc[-1, df.columns.get_loc('value')] = value * factor

                            return df
                except Exception as e:
                    logging.error(f"Error getting simulated data for sensor {sensor_id}: {e}")

    # For all other sensors, generate sample data
    return generate_sample_data(sensor_type, start_time, end_time, interval_seconds)