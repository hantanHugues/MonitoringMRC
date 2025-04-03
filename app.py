import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
from utils.mqtt_client import MQTTClient
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
    
    # MQTT Connection (placeholder for future implementation)
    st.markdown("### MQTT Connection")
    if not st.session_state.connected:
        if st.button("Connect to MQTT Broker"):
            # This would be replaced with actual MQTT connection code later
            st.session_state.connected = True
            st.session_state.mqtt_client = MQTTClient(client_id="medimat_monitor", host="localhost", port=1883)
            st.success("Connected to MQTT broker")
            time.sleep(1)
            st.rerun()
    else:
        if st.button("Disconnect"):
            st.session_state.connected = False
            st.session_state.mqtt_client = None
            st.info("Disconnected from MQTT broker")
            time.sleep(1)
            st.rerun()
        
        st.success("✅ Connected to MQTT broker")
    
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
