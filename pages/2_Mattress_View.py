import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import random
from utils.sensor_utils import get_sensor_status_color
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

# MQTT Connection for selected mattress
st.sidebar.markdown("---")
st.sidebar.subheader("Configuration MQTT")

with st.sidebar.expander(f"Configuration MQTT pour {selected_mattress['name']}", expanded=False):
        # Formulaire pour la connexion MQTT
        with st.form("mqtt_config_form"):
            mqtt_host = st.text_input("Adresse du broker MQTT", value="localhost")
            mqtt_port = st.number_input("Port MQTT", value=1883, min_value=1, max_value=65535)
            mqtt_username = st.text_input("Nom d'utilisateur (optionnel)")
            mqtt_password = st.text_input("Mot de passe (optionnel)", type="password")
            
            # List of topics to subscribe to
            st.markdown("Topics MQTT par défaut:")
            st.code("""capteur/temperature
capteur/humidite
capteur/debit_urinaire
capteur/poul
capteur/creatine""")
            
            # Form submission
            submit_button = st.form_submit_button("Connecter au Broker MQTT")
            
            if submit_button:
                from utils.mqtt_integration import initialize_mqtt_integration
                
                # Tenter de se connecter au broker MQTT
                with st.spinner("Connexion au broker MQTT..."):
                    mqtt_integration = initialize_mqtt_integration(
                        host=mqtt_host,
                        port=int(mqtt_port),
                        username=mqtt_username if mqtt_username else None,
                        password=mqtt_password if mqtt_password else None
                    )
                    
                    if mqtt_integration and mqtt_integration.connected:
                        st.success(f"Connecté au broker MQTT à {mqtt_host}:{mqtt_port}")
                        
                        # Stocker les informations de connexion pour les réutiliser
                        st.session_state['mqtt_broker_info'] = {
                            'host': mqtt_host,
                            'port': mqtt_port,
                            'username': mqtt_username,
                            'password': mqtt_password
                        }
                        
                        # Mettre à jour le timestamp de dernière mise à jour
                        st.session_state.last_update = datetime.now()
                    else:
                        st.error(f"Échec de connexion au broker MQTT à {mqtt_host}:{mqtt_port}")

    # Afficher un indicateur si connecté au broker MQTT
    if 'mqtt_integration' in st.session_state and st.session_state.get('mqtt_integration').connected:
        broker_info = st.session_state.get('mqtt_broker_info', {})
        st.sidebar.success(f"✅ Connecté au broker MQTT à {broker_info.get('host', 'localhost')}:{broker_info.get('port', 1883)}")
        
        if st.sidebar.button("Déconnecter du Broker MQTT"):
            if 'mqtt_integration' in st.session_state:
                mqtt_integration = st.session_state['mqtt_integration']
                mqtt_integration.disconnect()
                st.session_state['mqtt_integration'] = None
                st.sidebar.info("Déconnecté du broker MQTT")
                st.rerun()

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
    
    # Configuration améliorée de la visualisation
    # Using 3D representation for better visualization
    fig = go.Figure()

    # Define mattress dimensions and 3D properties
    mattress_length = 200  # cm
    mattress_width = 90    # cm
    mattress_height = 20   # cm
    
    # Create 3D mattress surface
    X = [0, mattress_length, mattress_length, 0, 0]
    Y = [0, 0, mattress_width, mattress_width, 0]
    Z = [0, 0, 0, 0, 0]
    
    # Add mattress base
    fig.add_trace(go.Mesh3d(
        x=[0, mattress_length, mattress_length, 0, 0],
        y=[0, 0, mattress_width, mattress_width, 0],
        z=[0, 0, 0, 0, 0],
        color='lightblue',
        opacity=0.6,
        name='Mattress Base'
    ))
    
    # Add mattress top surface
    fig.add_trace(go.Mesh3d(
        x=[0, mattress_length, mattress_length, 0, 0],
        y=[0, 0, mattress_width, mattress_width, 0],
        z=[mattress_height, mattress_height, mattress_height, mattress_height, mattress_height],
        color='lightblue',
        opacity=0.6,
        name='Mattress Top'
    ))
    
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
        
        # Add sensor as 3D marker with real-time data
        mqtt_value = None
        if selected_mattress_id == "MAT-101" and 'mqtt_integration' in st.session_state:
            mqtt_integration = st.session_state['mqtt_integration']
            if mqtt_integration and mqtt_integration.connected:
                mqtt_data = mqtt_integration.get_latest_data(sensor.id)
                if mqtt_data:
                    mqtt_value = mqtt_data.get('value')

        # Dynamic size based on sensor value
        marker_size = 15
        if mqtt_value is not None:
            marker_size = 15 + min(mqtt_value/10, 15)  # Scale marker size with value

        fig.add_trace(go.Scatter3d(
            x=[pos[0]], 
            y=[pos[1]],
            z=[mattress_height + 5],  # Place slightly above mattress
            mode='markers+text',
            marker=dict(
                size=marker_size,
                color=color,
                symbol='circle',
                line=dict(
                    color='white',
                    width=1
                )
            ),
            text=[f"{sensor.name}"],
            textposition="top center",
            hovertext=f"{sensor.name} ({sensor.type})<br>Status: {sensor.status.upper()}<br>Value: {mqtt_value if mqtt_value is not None else 'N/A'}",
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
            
            # Vérifier si nous avons des données MQTT pour ce capteur
            mqtt_data = None
            mqtt_value = None
            
            if selected_mattress_id == "MAT-101" and 'mqtt_integration' in st.session_state:
                mqtt_integration = st.session_state['mqtt_integration']
                if mqtt_integration and mqtt_integration.connected:
                    mqtt_data = mqtt_integration.get_latest_data(sensor.id)
                    if mqtt_data:
                        mqtt_value = mqtt_data.get('value')
            
            with st.container():
                # Ajouter un badge "Données en direct" pour les capteurs avec données MQTT
                live_badge = ""
                if mqtt_data:
                    live_badge = '<span style="background-color:#28a745; color:white; padding:3px 8px; border-radius:10px; font-size:0.8em; margin-left:10px;">LIVE</span>'
                
                # Formatter la valeur et l'unité en fonction du type de capteur
                value_display = ""
                if mqtt_value is not None:
                    if sensor.type == 'temperature':
                        value_display = f"<strong>Valeur actuelle:</strong> <span style='font-size:1.2em;'>{mqtt_value:.1f} °C</span>"
                    elif sensor.type == 'humidity':
                        value_display = f"<strong>Valeur actuelle:</strong> <span style='font-size:1.2em;'>{mqtt_value:.1f} %</span>"
                    elif sensor.type == 'pressure':
                        value_display = f"<strong>Valeur actuelle:</strong> <span style='font-size:1.2em;'>{mqtt_value:.1f} mmHg</span>"
                    elif sensor.type == 'movement':
                        value_display = f"<strong>Valeur actuelle:</strong> <span style='font-size:1.2em;'>{mqtt_value:.1f} unités</span>"
                    else:
                        value_display = f"<strong>Valeur actuelle:</strong> <span style='font-size:1.2em;'>{mqtt_value:.1f}</span>"
                
                timestamp = ""
                if mqtt_data and mqtt_data.get('timestamp'):
                    timestamp = f"<br><small>Dernière mise à jour: {mqtt_data.get('timestamp')}</small>"
                
                st.markdown(
                    f"""
                    <div style="border:1px solid #e0e0e0; border-radius:5px; padding:10px; margin-bottom:10px;">
                        <h4 style="margin-top:0;">{sensor.name} ({sensor.type}) {live_badge}</h4>
                        <p><strong>{tr('status')}:</strong> <span style="color:{status_color};font-weight:bold;">{sensor.status.upper()}</span></p>
                        <p><strong>{tr('power_status')}:</strong> <span style="color:green;">Connected</span></p>
                        <p><strong>{tr('signal_strength')}:</strong> {sensor.signal_strength}/10</p>
                        <p><strong>{tr('firmware_version')}:</strong> {sensor.firmware_version}</p>
                        {f"<p>{value_display}{timestamp}</p>" if value_display else ""}
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
