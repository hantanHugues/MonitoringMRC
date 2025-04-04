import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time
from utils.sensor_utils import get_sensor_status_color, generate_sample_data
from utils.visualization import create_time_series_chart, create_gauge_chart
from utils.translation import get_translation
from utils.data_manager import get_sensors_data, get_sensor_types, get_mattresses_data, get_sensor_readings

# Page configuration
st.set_page_config(
    page_title="Sensor Details - Medical Mattress Monitoring",
    page_icon="📊",
    layout="wide"
)

# Header
if 'language' not in st.session_state:
    st.session_state['language'] = 'en'

if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now()

tr = lambda key: get_translation(key, st.session_state.language)
st.title(tr("sensor_details_title"))
st.markdown(tr("sensor_details_description"))

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
filtered_sensors = sensors_data[sensors_data['mattress_id'] == selected_mattress_id].copy()

# Add units for each sensor type
unit_map = {
    'temperature': '°C',
    'humidity': '%',
    'pressure': 'mmHg',
    'movement': 'units',
    'debit_urinaire': 'L/h',
    'poul': 'bpm',
    'creatine': 'mg/dL'
}

# Add units to filtered sensors
filtered_sensors['unit'] = filtered_sensors['type'].map(unit_map)

# Create a dropdown for the filtered sensors with units
sensor_options = {s.id: f"{s.name} ({s.type} - {s.unit})" for s in filtered_sensors.itertuples()}

if sensor_options:
    selected_sensor_id = st.sidebar.selectbox(
        tr("select_sensor_prompt"),
        options=list(sensor_options.keys()),
        format_func=lambda x: sensor_options[x]
    )

    # Get the selected sensor data
    selected_sensor = filtered_sensors[filtered_sensors['id'] == selected_sensor_id].iloc[0]
else:
    st.sidebar.warning(f"No sensors assigned to this mattress.")
    st.stop()

# Time range selector for historical data
st.sidebar.header(tr("time_range"))
time_range = st.sidebar.radio(
    tr("select_time_range"),
    options=["1 hour", "24 hours", "7 days", "30 days"]
)

# Map time range to actual delta
time_map = {
    "1 hour": "hour",
    "24 hours": "day",
    "7 days": "week",
    "30 days": "month"
}
timeframe = time_map.get(time_range, "day")

# Get historical data
historical_data = get_sensor_readings(
    sensor_id=selected_sensor_id,
    sensor_type=selected_sensor['type'],
    timeframe=timeframe
)

# Display last refresh time
st.sidebar.info(f"{tr('last_update')}: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

# Refresh button
if st.sidebar.button(tr("refresh_data")):
    st.rerun()

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # Sensor details card
    st.subheader(tr("sensor_details"))
    status_color = get_sensor_status_color(selected_sensor['status'])

    st.markdown(
        f"""
        <div style="border:1px solid #e0e0e0; border-radius:5px; padding:15px; margin-bottom:15px;">
            <h3 style="margin-top:0; color:#0066cc;">{selected_sensor['name']}</h3>
            <p><strong>{tr('sensor_type')}:</strong> {selected_sensor['type']}</p>
            <p><strong>{tr('mattress_id')}:</strong> {selected_sensor['mattress_id']}</p>
            <p><strong>{tr('status')}:</strong> <span style="color:{status_color};font-weight:bold;">{selected_sensor['status'].upper()}</span></p>
            <p><strong>{tr('power_connection')}:</strong> <span style="color:green;">Connected</span></p>
            <p><strong>{tr('signal_strength')}:</strong> {selected_sensor['signal_strength']}/10</p>
            <p><strong>{tr('firmware_version')}:</strong> {selected_sensor['firmware_version']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Création de containers pour les données en temps réel
    mqtt_live_container = st.empty()
    history_container = st.empty()
    info_container = st.empty()

    # Containers pour les graphiques
    historical_chart_container = st.empty()
    stats_container = st.empty()

    # Create real-time line chart
    if not historical_data.empty:
        with historical_chart_container:
            st.subheader(f"{tr('historical_data')}")
            fig = create_time_series_chart(
                historical_data,
                title=f"{selected_sensor['name']} - {tr('historical_readings')}",
                sensor_type=selected_sensor['type']
            )
            st.plotly_chart(fig, use_container_width=True)

        # Statistics for the selected time period
        with stats_container:
            if 'value' in historical_data.columns:
                st.subheader(tr("statistics_for_period"))
                stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                stats_col1.metric(tr("min_value"), f"{historical_data['value'].min():.2f}")
                stats_col2.metric(tr("max_value"), f"{historical_data['value'].max():.2f}")
                stats_col3.metric(tr("avg_value"), f"{historical_data['value'].mean():.2f}")
                stats_col4.metric(tr("std_dev"), f"{historical_data['value'].std():.2f}")
    else:
        st.warning(tr("no_historical_data_available"))

with col2:
    # Current readings
    st.subheader(tr("current_readings"))

    # Display current value
    if not historical_data.empty:
        latest_value = historical_data['value'].iloc[-1]
        unit = selected_sensor.get('unit', '')
        st.metric(
            label=f"{tr('current')} {selected_sensor['type']} {tr('reading')}",
            value=f"{latest_value:.2f} {unit}"
        )

    # Power status
    if selected_sensor['power_connection']:
        st.success(f"{tr('power_connection')}: {tr('power_status_ok')}")
    else:
        st.error(f"{tr('power_connection')}: {tr('power_status_disconnected')}")

    # Signal strength
    st.metric(
        label=tr("signal_strength"),
        value=f"{selected_sensor['signal_strength']}/10"
    )

    # Action buttons
    st.subheader(tr("sensor_actions"))
    col1, col2 = st.columns(2)
    with col1:
        st.button(tr("test_sensor"), key="test")
        st.button(tr("calibrate_sensor"), key="calibrate")
    with col2:
        st.button(tr("restart_sensor"), key="restart")
        st.button(tr("update_firmware"), key="update")

    # Export data button
    if not historical_data.empty:
        st.download_button(
            label=tr("export_data"),
            data=historical_data.to_csv(index=False).encode('utf-8'),
            file_name=f"{selected_sensor['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

# Additional information section
st.subheader(tr("maintenance_history"))

# Generate some sample maintenance history
maintenance_history = pd.DataFrame({
    'date': [
        datetime.now() - timedelta(days=30),
        datetime.now() - timedelta(days=90),
        datetime.now() - timedelta(days=180)
    ],
    'type': [
        tr("firmware_update"),
        tr("calibration"),
        tr("maintenance_check")
    ],
    'technician': ['Tech1', 'Tech2', 'Tech1'],
    'notes': [
        tr("regular_update"),
        tr("scheduled_calibration"),
        tr("preventive_maintenance")
    ]
})

# Display the maintenance history
st.dataframe(
    maintenance_history,
    column_config={
        'date': st.column_config.DatetimeColumn(tr("date"), format="DD/MM/YYYY"),
        'type': tr("maintenance_type"),
        'technician': tr("technician"),
        'notes': tr("notes")
    },
    hide_index=True
)

# Footer
st.markdown("---")
st.caption(f"© {datetime.now().year} MediMat Monitor - {tr('version')} 1.0.0")