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
from utils.data_manager import get_sensors_data, get_sensor_types, get_mattresses_data

# Page configuration
st.set_page_config(
    page_title="Sensor Details - Medical Mattress Monitoring",
    page_icon="📊",
    layout="wide"
)

# Header
tr = lambda key: get_translation(key, st.session_state.language)
st.title(tr("sensor_details_title"))
st.markdown(tr("sensor_details_description"))

# Get sensors data
sensors_data = get_sensors_data()

# Sidebar filters
st.sidebar.header(tr("select_sensor"))

# Selection by mattress or by sensor type
selection_mode = st.sidebar.radio(
    "Selection Mode",
    options=["By Sensor Type", "By Mattress"]
)

if selection_mode == "By Sensor Type":
    # Get all sensor types
    sensor_types = get_sensor_types()
    selected_type = st.sidebar.selectbox(
        "Select Sensor Type",
        options=sensor_types,
        format_func=lambda x: x.capitalize()
    )
    
    # Filter sensors by selected type
    filtered_sensors = sensors_data[sensors_data['type'] == selected_type]
    
    # Create a dropdown for the filtered sensors
    sensor_options = {s.id: f"{s.name} - {s.mattress_id if s.mattress_id else 'Unassigned'}" 
                     for s in filtered_sensors.itertuples()}
    
    if sensor_options:
        selected_sensor_id = st.sidebar.selectbox(
            tr("select_sensor_prompt"),
            options=list(sensor_options.keys()),
            format_func=lambda x: sensor_options[x]
        )
    else:
        st.sidebar.warning(f"No {selected_type} sensors found.")
        st.stop()
else:  # By Mattress
    # Get all mattresses
    mattresses = get_mattresses_data()
    mattress_options = {m.id: f"{m.name} ({m.location})" for m in mattresses.itertuples()}
    
    selected_mattress_id = st.sidebar.selectbox(
        "Select Mattress",
        options=list(mattress_options.keys()),
        format_func=lambda x: mattress_options[x]
    )
    
    # Filter sensors by selected mattress
    filtered_sensors = sensors_data[sensors_data['mattress_id'] == selected_mattress_id]
    
    # Create a dropdown for the filtered sensors
    sensor_options = {s.id: f"{s.name} ({s.type})" for s in filtered_sensors.itertuples()}
    
    if sensor_options:
        selected_sensor_id = st.sidebar.selectbox(
            tr("select_sensor_prompt"),
            options=list(sensor_options.keys()),
            format_func=lambda x: sensor_options[x]
        )
    else:
        st.sidebar.warning(f"No sensors assigned to this mattress.")
        st.stop()

# Filter to get the selected sensor
selected_sensor = sensors_data[sensors_data['id'] == selected_sensor_id].iloc[0]

# Time range selector for historical data
st.sidebar.header(tr("time_range"))
time_range = st.sidebar.radio(
    tr("select_time_range"),
    options=["1 hour", "24 hours", "7 days", "30 days"]
)

# Map time range to actual delta
time_delta_map = {
    "1 hour": timedelta(hours=1),
    "24 hours": timedelta(days=1),
    "7 days": timedelta(days=7),
    "30 days": timedelta(days=30)
}
selected_delta = time_delta_map[time_range]

# Generate historical data based on time range
# In a real application, this would be fetched from the database
end_time = datetime.now()
start_time = end_time - selected_delta

# Generate sample time series data for this demo
historical_data = generate_sample_data(
    sensor_type=selected_sensor['type'],
    start_time=start_time,
    end_time=end_time,
    interval_seconds=300 if time_range in ["1 hour", "24 hours"] else 3600
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
    
    # Check if power is connected
    power_status = "Connected" if selected_sensor['power_connection'] else "Disconnected"
    power_color = "green" if selected_sensor['power_connection'] else "red"
    
    st.markdown(
        f"""
        <div style="border:1px solid #e0e0e0; border-radius:5px; padding:15px; margin-bottom:15px;">
            <h3 style="margin-top:0; color:#0066cc;">{selected_sensor['name']}</h3>
            <p><strong>{tr('sensor_type')}:</strong> {selected_sensor['type']}</p>
            <p><strong>{tr('mattress_id')}:</strong> {selected_sensor['mattress_id']}</p>
            <p><strong>{tr('status')}:</strong> <span style="color:{status_color};font-weight:bold;">{selected_sensor['status'].upper()}</span></p>
            <p><strong>{tr('power_connection')}:</strong> <span style="color:{power_color};">{power_status}</span></p>
            <p><strong>{tr('signal_strength')}:</strong> {selected_sensor['signal_strength']}/10</p>
            <p><strong>{tr('firmware_version')}:</strong> {selected_sensor['firmware_version']}</p>
            <p><strong>{tr('installation_date')}:</strong> {selected_sensor['installation_date']}</p>
            <p><strong>{tr('last_maintenance')}:</strong> {selected_sensor['last_maintenance']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Historical data chart
    st.subheader(f"{tr('historical_data')} - {time_range}")
    
    if not historical_data.empty:
        fig = create_time_series_chart(
            historical_data,
            title=f"{selected_sensor['name']} - {tr('historical_readings')}",
            sensor_type=selected_sensor['type']
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics for the selected time period
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
    
    # Get the latest value
    latest_value = historical_data['value'].iloc[-1] if not historical_data.empty else 0
    
    # Create a gauge chart for the current reading
    gauge_title = f"{tr('current')} {selected_sensor['type']} {tr('reading')}"
    
    # Different units and thresholds based on sensor type
    if selected_sensor['type'] == 'pressure':
        unit = "mmHg"
        min_val, max_val = 0, 200
    elif selected_sensor['type'] == 'temperature':
        unit = "°C"
        min_val, max_val = 30, 45
    elif selected_sensor['type'] == 'humidity':
        unit = "%"
        min_val, max_val = 0, 100
    elif selected_sensor['type'] == 'movement':
        unit = "units"
        min_val, max_val = 0, 10
    else:
        unit = "units"
        min_val, max_val = 0, 100
    
    fig = create_gauge_chart(
        value=latest_value,
        title=gauge_title,
        suffix=unit,
        min_value=min_val,
        max_value=max_val
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Power status
    if selected_sensor['power_connection']:
        st.success(f"{tr('power_connection')}: {tr('power_status_ok')}")
    else:
        st.error(f"{tr('power_connection')}: {tr('power_status_disconnected')}")
    
    # Signal strength gauge
    signal_fig = create_gauge_chart(
        value=selected_sensor['signal_strength'],
        title=tr("signal_strength"),
        suffix="/10",
        max_value=10
    )
    st.plotly_chart(signal_fig, use_container_width=True)
    
    # Action buttons
    st.subheader(tr("sensor_actions"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.button(tr("test_sensor"), key="test")
        st.button(tr("calibrate_sensor"), key="calibrate")
    
    with col2:
        st.button(tr("restart_sensor"), key="restart")
        st.button(tr("update_firmware"), key="update_firmware")
    
    # Export data button
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
