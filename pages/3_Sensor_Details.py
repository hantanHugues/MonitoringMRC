
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import threading
from utils.sensor_utils import get_sensor_status_color, generate_sample_data
from utils.visualization import create_time_series_chart, create_gauge_chart
from utils.translation import get_translation
from utils.data_manager import get_sensors_data, get_mattresses_data

# Page configuration
st.set_page_config(
    page_title="Sensor Details - Medical Mattress Monitoring",
    page_icon="📊",
    layout="wide"
)

# Header
if 'language' not in st.session_state:
    st.session_state['language'] = 'en'

tr = lambda key: get_translation(key, st.session_state.language)
st.title(tr("sensor_details_title"))

# Get data
sensors_data = get_sensors_data()
mattresses_data = get_mattresses_data()

# Sidebar filters
st.sidebar.header(tr("select_sensor"))

# Selection by mattress
mattress_options = {m.id: f"{m.name} ({m.location})" for m in mattresses_data.itertuples()}
selected_mattress_id = st.sidebar.selectbox(
    tr("select_mattress"),
    options=list(mattress_options.keys()),
    format_func=lambda x: mattress_options[x]
)

# Filter sensors by selected mattress
filtered_sensors = []
for sensor_type, name, unit in [
    ('temperature', 'Capteur de température', '°C'),
    ('humidity', 'Capteur d\'humidité', '%'),
    ('debit_urinaire', 'Capteur de débit urinaire', 'L/h'),
    ('poul', 'Capteur de pouls', 'bpm'),
    ('creatine', 'Capteur de créatine', 'mg/dL')
]:
    sensor_id = f"SEN-{201 + len(filtered_sensors)}"
    filtered_sensors.append({
        'id': sensor_id,
        'name': name,
        'type': sensor_type,
        'unit': unit,
        'mattress_id': selected_mattress_id,
        'status': 'active'
    })

filtered_sensors = pd.DataFrame(filtered_sensors)

# Create sensor selection dropdown
sensor_options = {s.id: f"{s.name} ({s.type} - {s.unit})" for s in filtered_sensors.itertuples()}
selected_sensor_id = st.sidebar.selectbox(
    tr("select_sensor_prompt"),
    options=list(sensor_options.keys()),
    format_func=lambda x: sensor_options[x]
)

# Get selected sensor
selected_sensor = filtered_sensors[filtered_sensors['id'] == selected_sensor_id].iloc[0]

# Main content layout
col1, col2 = st.columns([2, 1])

with col1:
    # Create containers for real-time updates
    current_data_container = st.empty()
    historical_chart_container = st.empty()

    # Initialize historical data
    historical_data = generate_sample_data(
        start_time=datetime.now() - timedelta(hours=1),
        end_time=datetime.now(),
        interval_seconds=60,
        sensor_type=selected_sensor['type']
    )

# Function to update sensor data in real-time
def update_sensor_data():
    while True:
        try:
            # Get MQTT data
            mqtt_data = None
            if 'mqtt_integration' in st.session_state:
                mqtt_integration = st.session_state['mqtt_integration']
                if mqtt_integration and mqtt_integration.connected:
                    mqtt_data = mqtt_integration.get_latest_data(selected_sensor_id)
            
            # Get direct simulator data if MQTT not available
            if not mqtt_data and 'direct_simulator' in st.session_state:
                direct_simulator = st.session_state['direct_simulator']
                if direct_simulator:
                    mqtt_data = direct_simulator.get_latest_data(selected_sensor_id)

            if mqtt_data:
                with current_data_container:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            label="Valeur actuelle",
                            value=f"{mqtt_data.get('value', 0):.1f} {selected_sensor['unit']}",
                            delta=None
                        )
                    with col2:
                        st.metric(
                            label="Dernière mise à jour",
                            value=datetime.now().strftime("%H:%M:%S")
                        )

                # Update historical data
                if not historical_data.empty:
                    new_data = pd.DataFrame({
                        'timestamp': [datetime.now()],
                        'value': [mqtt_data.get('value', 0)]
                    })
                    historical_data = pd.concat([historical_data, new_data]).tail(100)

                    # Update chart
                    with historical_chart_container:
                        fig = create_time_series_chart(
                            historical_data,
                            title=f"{selected_sensor['name']} - {tr('historical_readings')}",
                            sensor_type=selected_sensor['type']
                        )
                        st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error updating data: {e}")

        time.sleep(2)  # Update every 2 seconds

# Start auto-refresh in a separate thread
if 'update_thread' not in st.session_state:
    update_thread = threading.Thread(target=update_sensor_data, daemon=True)
    update_thread.start()
    st.session_state['update_thread'] = update_thread

with col2:
    # Sensor info
    st.subheader("Sensor Information")
    st.write(f"**ID:** {selected_sensor['id']}")
    st.write(f"**Type:** {selected_sensor['type']}")
    st.write(f"**Unit:** {selected_sensor['unit']}")
    st.write(f"**Status:** {selected_sensor['status']}")
    st.write(f"**Mattress:** {selected_sensor['mattress_id']}")

# Display last refresh time
st.sidebar.info(f"{tr('last_update')}: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
