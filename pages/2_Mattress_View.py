import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import random
from utils.sensor_utils import get_sensor_status_color, get_battery_level_color
from utils.translation import get_translation
from utils.data_manager import get_sensors_data, get_mattresses_data

# Page configuration
st.set_page_config(
    page_title="Mattress View - Medical Mattress Monitoring",
    page_icon="🛏️",
    layout="wide"
)

# Header
tr = lambda key: get_translation(key, st.session_state.language)
st.title(tr("mattress_view_title"))
st.markdown(tr("mattress_view_description"))

# Get data
mattresses_data = get_mattresses_data()
sensors_data = get_sensors_data()

# Mattress selector
st.sidebar.header(tr("select_mattress"))

# Get unique mattress IDs and names for selection
mattress_options = {m.id: f"{m.name} (Patient: {m.patient_id})" for m in mattresses_data.itertuples()}
selected_mattress_id = st.sidebar.selectbox(
    tr("select_mattress_prompt"),
    options=list(mattress_options.keys()),
    format_func=lambda x: mattress_options[x]
)

# Filter to get the selected mattress
selected_mattress = mattresses_data[mattresses_data['id'] == selected_mattress_id].iloc[0]

# Get sensors for this mattress
mattress_sensors = sensors_data[sensors_data['mattress_id'] == selected_mattress_id]

# Display last refresh time
st.sidebar.info(f"{tr('last_update')}: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

# Refresh button
if st.sidebar.button(tr("refresh_data")):
    st.rerun()

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    # Mattress details card
    st.subheader(tr("mattress_details"))
    
    status_color = get_sensor_status_color(selected_mattress['status'])
    
    st.markdown(
        f"""
        <div style="border:1px solid #e0e0e0; border-radius:5px; padding:15px; margin-bottom:15px;">
            <h3 style="margin-top:0; color:#0066cc;">{selected_mattress['name']}</h3>
            <p><strong>{tr('status')}:</strong> <span style="color:{status_color};font-weight:bold;">{selected_mattress['status'].upper()}</span></p>
            <p><strong>{tr('patient_id')}:</strong> {selected_mattress['patient_id']}</p>
            <p><strong>{tr('location')}:</strong> {selected_mattress['location']}</p>
            <p><strong>{tr('installation_date')}:</strong> {selected_mattress['installation_date']}</p>
            <p><strong>{tr('last_maintenance')}:</strong> {selected_mattress['last_maintenance']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Mattress visualization with sensor placements
    st.subheader(tr("mattress_visualization"))
    
    # Create a visual representation of the mattress with sensor placements
    # This is a simplified representation where we'll use a rectangle to represent the mattress
    # and circles to represent sensor positions
    
    fig = go.Figure()
    
    # Define mattress dimensions
    mattress_length = 200  # cm
    mattress_width = 90    # cm
    
    # Draw the mattress outline
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=mattress_length, y1=mattress_width,
        line=dict(color="lightblue", width=2),
        fillcolor="lightblue",
        opacity=0.3
    )
    
    # Add pillow area
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=50, y1=mattress_width,
        line=dict(color="lightblue", width=1),
        fillcolor="lightblue",
        opacity=0.5
    )
    
    # Place sensors on the mattress
    for i, sensor in enumerate(mattress_sensors.itertuples()):
        # Define sensor positions based on sensor type or predefined positions
        # In a real application, these positions would come from a database
        sensor_type = sensor.type
        
        # Based on sensor type, determine position
        if sensor_type == 'pressure':
            positions = [(50, 20), (100, 45), (150, 20), (150, 70)]
            pos = positions[i % len(positions)]
        elif sensor_type == 'temperature':
            positions = [(25, 45), (175, 45)]
            pos = positions[i % len(positions)]
        elif sensor_type == 'humidity':
            positions = [(75, 15), (125, 75)]
            pos = positions[i % len(positions)]
        elif sensor_type == 'movement':
            positions = [(75, 45), (125, 45)]
            pos = positions[i % len(positions)]
        else:
            # Random position for other sensor types
            pos = (random.randint(10, mattress_length-10), random.randint(10, mattress_width-10))
        
        # Set color based on sensor status
        color = get_sensor_status_color(sensor.status)
        
        # Add sensor as a circle
        fig.add_trace(go.Scatter(
            x=[pos[0]], 
            y=[pos[1]], 
            mode='markers',
            marker=dict(
                size=15,
                color=color,
                line=dict(
                    color='white',
                    width=1
                )
            ),
            text=f"{sensor.name} ({sensor.type})<br>Status: {sensor.status.upper()}<br>Battery: {sensor.battery_level}%",
            hoverinfo='text',
            name=sensor.name
        ))
        
        # Add sensor label
        fig.add_annotation(
            x=pos[0], y=pos[1] + 5,
            text=sensor.name,
            showarrow=False,
            font=dict(
                size=10,
                color="#333"
            )
        )
    
    # Update layout
    fig.update_layout(
        title=f"{tr('sensor_placement_on')} {selected_mattress['name']}",
        xaxis=dict(
            range=[-10, mattress_length + 10],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        yaxis=dict(
            range=[-10, mattress_width + 10],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Legend
    st.markdown(tr("status_legend"))
    
    legend_col1, legend_col2, legend_col3, legend_col4 = st.columns(4)
    with legend_col1:
        st.markdown(f'<span style="color:{get_sensor_status_color("active")};font-weight:bold;">● {tr("status_active")}</span>', unsafe_allow_html=True)
    with legend_col2:
        st.markdown(f'<span style="color:{get_sensor_status_color("inactive")};font-weight:bold;">● {tr("status_inactive")}</span>', unsafe_allow_html=True)
    with legend_col3:
        st.markdown(f'<span style="color:{get_sensor_status_color("maintenance")};font-weight:bold;">● {tr("status_maintenance")}</span>', unsafe_allow_html=True)
    with legend_col4:
        st.markdown(f'<span style="color:{get_sensor_status_color("error")};font-weight:bold;">● {tr("status_error")}</span>', unsafe_allow_html=True)

with col2:
    # Sensors list
    st.subheader(tr("sensors_on_mattress"))
    
    if not mattress_sensors.empty:
        for sensor in mattress_sensors.itertuples():
            status_color = get_sensor_status_color(sensor.status)
            battery_color = get_battery_level_color(sensor.battery_level)
            
            with st.container():
                st.markdown(
                    f"""
                    <div style="border:1px solid #e0e0e0; border-radius:5px; padding:10px; margin-bottom:10px;">
                        <h4 style="margin-top:0;">{sensor.name} ({sensor.type})</h4>
                        <p><strong>{tr('status')}:</strong> <span style="color:{status_color};font-weight:bold;">{sensor.status.upper()}</span></p>
                        <p><strong>{tr('battery_level')}:</strong> <span style="color:{battery_color};">{sensor.battery_level}%</span></p>
                        <p><strong>{tr('signal_strength')}:</strong> {sensor.signal_strength}/10</p>
                        <p><strong>{tr('firmware_version')}:</strong> {sensor.firmware_version}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Action buttons for each sensor
                col1, col2, col3 = st.columns(3)
                col1.button(tr("view_data"), key=f"data_{sensor.id}")
                col2.button(tr("calibrate"), key=f"calibrate_{sensor.id}")
                col3.button(tr("restart"), key=f"restart_{sensor.id}")
    else:
        st.warning(tr("no_sensors_on_mattress"))
    
    # Patient data card (simplified, would connect to hospital API in a real system)
    st.subheader(tr("patient_information"))
    
    patient_id = selected_mattress['patient_id']
    
    # In a real application, this would be retrieved from the hospital's patient management system
    # For this demo, we'll create some placeholder data
    st.markdown(
        f"""
        <div style="border:1px solid #e0e0e0; border-radius:5px; padding:15px; margin-bottom:15px;">
            <h3 style="margin-top:0;">{tr('patient_id')}: {patient_id}</h3>
            <p><em>{tr('connect_to_hospital_system')}</em></p>
            <p>{tr('treatment')}: {tr('hemodialysis')}</p>
            <p>{tr('attending_physician')}: Dr. Smith</p>
            <p>{tr('critical_alerts')}: {tr('refer_to_hospital_system')}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Add buttons for patient data actions
    st.button(tr("connect_to_patient_records"))

# Footer
st.markdown("---")
st.caption(f"© {datetime.now().year} MediMat Monitor - {tr('version')} 1.0.0")
