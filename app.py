import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
import logging
from utils.mqtt_client import MQTTClient
from utils.direct_simulator import initialize_direct_simulator, get_direct_simulator
from utils.sensor_utils import get_sensor_status_color, generate_sample_data
from utils.visualization import create_gauge_chart, create_status_distribution_chart
from utils.translation import get_translation, get_languages, set_language
from utils.data_manager import get_sensors_data, get_mattresses_data, get_alerts_data

# Page configuration
st.set_page_config(
    page_title="Medical Mattress Monitoring System", 
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state['language'] = 'en'
if 'connected' not in st.session_state:
    st.session_state['connected'] = False
if 'mqtt_client' not in st.session_state:
    st.session_state['mqtt_client'] = None
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now()

# Initialize direct simulator for simulating sensor data
# This will be used to get sensor data for mattress 1 (MAT-101)
if 'direct_simulator' not in st.session_state:
    try:
        logging.info("Initializing direct simulator...")
        direct_simulator = initialize_direct_simulator()
        st.session_state['direct_simulator'] = direct_simulator
        logging.info("Direct simulator initialized successfully")
    except Exception as e:
        logging.error(f"Failed to initialize direct simulator: {e}")
        st.session_state['direct_simulator'] = None

# Sidebar with hospital information and settings
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b", width=300)
    st.title("MediMat Monitor")
    
    st.markdown("### Hospital Information")
    st.text("Hospital: Central Renal Care")
    st.text("Department: Nephrology")
    st.text(f"Last update: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Language selector
    st.markdown("### Language / Langue")
    languages = get_languages()
    cols = st.columns(len(languages))
    for i, (code, name) in enumerate(languages.items()):
        if cols[i].button(name, key=f"lang_{code}"):
            set_language(code)
            st.rerun()
    
    # MQTT & Sensor Simulator
    st.markdown("### Données des capteurs")
    
    if 'simulator_type' not in st.session_state:
        st.session_state['simulator_type'] = 'direct'
    
    if not st.session_state.connected:
        with st.expander("Options de connexion", expanded=True):
            # Option 1: Direct Simulator (local)
            st.markdown("##### Option 1: Simulateur intégré")
            if st.button("Démarrer le simulateur intégré", key="start_direct"):
                # Start the direct simulator
                st.session_state.connected = True
                st.session_state.simulator_type = "direct"
                if 'direct_simulator' in st.session_state and st.session_state.direct_simulator:
                    st.session_state.direct_simulator.start()
                    st.success("Simulateur intégré démarré")
                else:
                    st.warning("Échec du démarrage du simulateur. Essayez de rafraîchir la page.")
                time.sleep(1)
                st.rerun()
            
            st.markdown("---")
            # Option 2: External MQTT Broker
            st.markdown("##### Option 2: Broker MQTT externe")
            
            with st.form("mqtt_config_form_sidebar"):
                mqtt_host = st.text_input("Adresse du broker MQTT", value="localhost")
                mqtt_port = st.number_input("Port MQTT", value=1883, min_value=1, max_value=65535)
                mqtt_username = st.text_input("Nom d'utilisateur (optionnel)")
                mqtt_password = st.text_input("Mot de passe (optionnel)", type="password")
                
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
                            st.session_state.connected = True
                            st.session_state.simulator_type = "mqtt"
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
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Échec de connexion au broker MQTT à {mqtt_host}:{mqtt_port}")
    else:
        # Afficher l'état actuel et le bouton pour arrêter
        simulator_type = st.session_state.get('simulator_type', 'direct')
        
        if simulator_type == "direct":
            st.success("✅ Simulateur intégré en cours d'exécution")
            if st.button("Arrêter le simulateur"):
                st.session_state.connected = False
                if 'direct_simulator' in st.session_state and st.session_state.direct_simulator:
                    st.session_state.direct_simulator.stop()
                st.info("Simulateur arrêté")
                time.sleep(1)
                st.rerun()
        else:  # MQTT
            broker_info = st.session_state.get('mqtt_broker_info', {})
            st.success(f"✅ Connecté au broker MQTT à {broker_info.get('host', 'localhost')}:{broker_info.get('port', 1883)}")
            
            if st.button("Déconnecter du broker MQTT"):
                st.session_state.connected = False
                if 'mqtt_integration' in st.session_state:
                    mqtt_integration = st.session_state['mqtt_integration']
                    mqtt_integration.disconnect()
                    st.session_state['mqtt_integration'] = None
                st.info("Déconnecté du broker MQTT")
                time.sleep(1)
                st.rerun()
    
    st.markdown("---")
    st.markdown("👨‍💻 User: Medical Technician")
    st.markdown("📅 " + datetime.now().strftime("%Y-%m-%d"))

# Main content
tr = lambda key: get_translation(key, st.session_state.language)

st.title(tr("main_title"))
st.markdown(tr("main_subtitle"))

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

# We will replace this with real data from MQTT later
sensors_data = get_sensors_data()
mattresses_data = get_mattresses_data()
alerts_data = get_alerts_data()

total_mattresses = len(mattresses_data)
active_sensors = sensors_data[sensors_data['status'] == 'active'].shape[0]
total_sensors = len(sensors_data)
active_alerts = alerts_data[alerts_data['status'] == 'active'].shape[0]
critical_alerts = alerts_data[(alerts_data['status'] == 'active') & (alerts_data['priority'] == 'critical')].shape[0]

with col1:
    st.metric(
        label=tr("total_mattresses"),
        value=total_mattresses,
        delta=None
    )

with col2:
    st.metric(
        label=tr("active_sensors"),
        value=f"{active_sensors}/{total_sensors}",
        delta=f"{round(active_sensors/total_sensors*100)}%" if total_sensors > 0 else "N/A",
        delta_color="normal"
    )

with col3:
    st.metric(
        label=tr("active_alerts"),
        value=active_alerts,
        delta=None,
        help=tr("alerts_help")
    )

with col4:
    st.metric(
        label=tr("critical_alerts"),
        value=critical_alerts,
        delta=None,
        help=tr("critical_alerts_help")
    )

# Main dashboard content in two columns
left_col, right_col = st.columns([2, 1])

with left_col:
    # Sensor Status Overview
    st.subheader(tr("sensor_status_overview"))
    
    # Distribution of sensor statuses
    status_counts = sensors_data['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    
    fig = create_status_distribution_chart(status_counts)
    st.plotly_chart(fig, use_container_width=True)

    # Recent activity
    st.subheader(tr("recent_activity"))
    
    # Simulate some recent activities
    activities = pd.DataFrame({
        'timestamp': [datetime.now() - timedelta(minutes=i*7) for i in range(5)],
        'event': [
            tr("activity_1"),
            tr("activity_2"),
            tr("activity_3"),
            tr("activity_4"),
            tr("activity_5")
        ],
        'mattress_id': ['MAT-' + str(101 + i) for i in range(5)],
        'sensor_id': ['SEN-' + str(201 + i) for i in range(5)]
    })
    
    for i, activity in activities.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div style='border-left: 3px solid #0066cc; padding-left: 10px; margin-bottom: 10px;'>
                <small>{activity['timestamp'].strftime('%H:%M:%S')}</small><br>
                <b>{activity['event']}</b><br>
                <small>Mattress: {activity['mattress_id']} | Sensor: {activity['sensor_id']}</small>
                </div>
                """, 
                unsafe_allow_html=True
            )

with right_col:
    # Alert Summary
    st.subheader(tr("alert_summary"))
    
    # Display top alerts
    if not alerts_data.empty:
        alerts_to_show = alerts_data[alerts_data['status'] == 'active'].sort_values('priority', ascending=False).head(5)
        
        for _, alert in alerts_to_show.iterrows():
            priority_color = "#ff4b4b" if alert['priority'] == 'critical' else "#ff9d00"
            with st.container():
                st.markdown(
                    f"""
                    <div style='border-left: 3px solid {priority_color}; padding-left: 10px; margin-bottom: 10px;'>
                    <b>{alert['title']}</b><br>
                    <small>{alert['description']}</small><br>
                    <small>Mattress: {alert['mattress_id']} | Priority: {alert['priority'].upper()}</small>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    else:
        st.info(tr("no_active_alerts"))
    
    # System health
    st.subheader(tr("system_health"))
    
    # Power status (replaces battery level since devices are plugged in)
    st.success(tr("power_status_ok"))
    
    # Connection quality
    signal_levels = sensors_data['signal_strength'].dropna()
    avg_signal = signal_levels.mean() if not signal_levels.empty else 0
    
    fig = create_gauge_chart(
        value=avg_signal,
        title=tr("avg_signal_strength"),
        suffix="/10"
    )
    st.plotly_chart(fig, use_container_width=True)

# Quick links to mattress monitoring
st.subheader(tr("quick_access"))

mattress_cols = st.columns(4)
for i, mattress in enumerate(mattresses_data.head(4).itertuples()):
    with mattress_cols[i]:
        status = mattress.status
        color = get_sensor_status_color(status)
        
        with st.container():
            st.markdown(
                f"""
                <div style='border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; text-align: center;'>
                <h3 style='margin-top: 0;'>{mattress.name}</h3>
                <p style='color: {color}; font-weight: bold;'>{status.upper()}</p>
                <p>Patient ID: {mattress.patient_id}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            st.button(tr("view_details"), key=f"view_{mattress.id}")

# Footer
st.markdown("---")
st.caption(f"© {datetime.now().year} MediMat Monitor - {tr('version')} 1.0.0")
