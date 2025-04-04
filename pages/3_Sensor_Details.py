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
# Initialiser la langue si elle n'existe pas dans la session
if 'language' not in st.session_state:
    st.session_state['language'] = 'en'

# Initialiser la date de dernière mise à jour
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now()

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
        
        for tab, sensor_type in zip(tabs, sensor_types):
            with tab:
                # Filtrer les capteurs par type
                type_sensors = filtered_sensors[filtered_sensors['type'] == sensor_type]
                
                for sensor in type_sensors.itertuples():
                    with st.container():
                        st.subheader(f"{sensor.name} ({sensor.type})")
                        
                        # Afficher les données MQTT en temps réel pour ce capteur
                        if 'mqtt_integration' in st.session_state and st.session_state['mqtt_integration'].connected:
                            mqtt_data = st.session_state['mqtt_integration'].get_latest_data(sensor.id)
                            if mqtt_data:
                                st.metric(
                                    "Valeur actuelle",
                                    f"{mqtt_data.get('value')} {mqtt_data.get('unit', '')}"
                                )
                        
                        # Créer un graphique pour ce capteur
                        historical_data = get_sensor_readings(
                            sensor_id=sensor.id,
                            sensor_type=sensor.type,
                            timeframe=timeframe
                        )
                        
                        if not historical_data.empty:
                            fig = create_time_series_chart(
                                historical_data,
                                title=f"{sensor.name} - {tr('historical_readings')}",
                                sensor_type=sensor.type
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("---")
    else:
        st.sidebar.warning(f"No sensors assigned to this mattress.")
        st.stop()

# On ne sélectionne plus un seul capteur puisqu'on les affiche tous

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

# Get time range for the data
end_time = datetime.now()
start_time = end_time - selected_delta

# For Matelas 1, use the real MQTT data when available
from utils.data_manager import get_sensor_readings

# Get historical data using the data manager - it will use MQTT data when available
time_map = {
    "1 hour": "hour",
    "24 hours": "day",
    "7 days": "week",
    "30 days": "month"
}
timeframe = time_map.get(time_range, "day")
# Récupérer les informations du capteur sélectionné
selected_sensor = sensors_data[sensors_data['id'] == selected_sensor_id].iloc[0]

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

    # Création de containers pour les données en temps réel
    mqtt_live_container = st.empty()
    history_container = st.empty()
    info_container = st.empty()

    # Containers pour les graphiques
    historical_chart_container = st.empty()
    stats_container = st.empty()

    # Créer un conteneur vide pour la jauge (défini ici pour éviter l'erreur)
    gauge_container = st.empty()

    # Fonction pour mettre à jour les données MQTT en temps réel
    def update_mqtt_data():
        live_data_found = False
        mqtt_value = None

        if selected_sensor['mattress_id'] == "MAT-101" and 'mqtt_integration' in st.session_state:
            mqtt_integration = st.session_state['mqtt_integration']
            if mqtt_integration and mqtt_integration.connected:
                with mqtt_live_container.container():
                    st.subheader("Dernières valeurs MQTT (Temps réel)")

                    # Obtenir toutes les données MQTT pour ce matelas
                    all_mqtt_data = mqtt_integration.get_latest_data()

                    # Vérifier si les données sont disponibles
                    if all_mqtt_data:
                        # Créer un DataFrame à partir des données MQTT
                        mqtt_rows = []
                        for sensor_id, data in all_mqtt_data.items():
                            if data and isinstance(data, dict):
                                mqtt_rows.append({
                                    "Capteur": data.get('name', sensor_id),
                                    "Type": data.get('type', ''),
                                    "Valeur": data.get('value', 0),
                                    "Unité": data.get('unit', ''),
                                    "Horodatage": data.get('timestamp', '')
                                })

                                # On récupère la valeur du capteur sélectionné
                                if sensor_id == selected_sensor_id:
                                    mqtt_value = data.get('value', 0)

                        if mqtt_rows:
                            live_data_found = True
                            mqtt_df = pd.DataFrame(mqtt_rows)
                            st.dataframe(mqtt_df, use_container_width=True)

                # Afficher l'historique des données pour le capteur sélectionné
                with history_container.container():
                    if live_data_found:
                        st.subheader(f"Historique des données pour {selected_sensor['name']}")

                        # Obtenir l'historique des données pour ce capteur
                        sensor_history = mqtt_integration.get_latest_data(selected_sensor_id, history=True)

                        if sensor_history and isinstance(sensor_history, list):
                            # Créer un DataFrame à partir de l'historique
                            history_rows = []
                            for data in reversed(sensor_history):  # Afficher les plus récentes en premier
                                if data and isinstance(data, dict):
                                    history_rows.append({
                                        "Horodatage": data.get('timestamp', ''),
                                        "Valeur": data.get('value', 0),
                                        "Unité": data.get('unit', '')
                                    })

                            if history_rows:
                                history_df = pd.DataFrame(history_rows)
                                st.dataframe(history_df, use_container_width=True)

                                # Mettre à jour également les données historiques pour le graphique
                                if 'timestamp' in history_df.columns and 'Valeur' in history_df.columns:
                                    try:
                                        # Préparer les données pour le graphique
                                        updated_historical_data = pd.DataFrame({
                                            'timestamp': pd.to_datetime(history_df['Horodatage']),
                                            'value': history_df['Valeur']
                                        })

                                        # Mettre à jour le graphique si nous avons des données
                                        if not updated_historical_data.empty:
                                            with historical_chart_container.container():
                                                st.subheader(f"{tr('historical_data')} - Temps réel")
                                                fig = create_time_series_chart(
                                                    updated_historical_data,
                                                    title=f"{selected_sensor['name']} - {tr('historical_readings')} (LIVE)",
                                                    sensor_type=selected_sensor['type']
                                                )
                                                st.plotly_chart(fig, use_container_width=True, key=f"historical_live_chart_{datetime.now().timestamp()}")

                                            # Mettre à jour les statistiques
                                            with stats_container.container():
                                                if 'value' in updated_historical_data.columns:
                                                    st.subheader(tr("statistics_for_period"))

                                                    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                                                    stats_col1.metric(tr("min_value"), f"{updated_historical_data['value'].min():.2f}")
                                                    stats_col2.metric(tr("max_value"), f"{updated_historical_data['value'].max():.2f}")
                                                    stats_col3.metric(tr("avg_value"), f"{updated_historical_data['value'].mean():.2f}")
                                                    stats_col4.metric(tr("std_dev"), f"{updated_historical_data['value'].std():.2f}")
                                    except Exception as e:
                                        st.error(f"Erreur lors de la mise à jour du graphique: {str(e)}")
                        else:
                            st.warning(f"Aucun historique disponible pour le capteur {selected_sensor['name']}")

                # Information sur la mise à jour automatique
                with info_container.container():
                    if live_data_found:
                        st.info(f"Les données sont mises à jour en temps réel. L'historique conserve les 20 dernières valeurs.")
                    else:
                        st.warning("Aucune donnée MQTT en temps réel disponible pour ce matelas.")

        # Mettre à jour la dernière mise à jour
        st.session_state.last_update = datetime.now()

        return live_data_found, mqtt_value

    # Function to update the gauge with real-time data
    def update_gauge(mqtt_value=None):
        # Check if we have live MQTT data for this sensor
        is_live_data = False

        if mqtt_value is None and selected_sensor['mattress_id'] == "MAT-101" and 'mqtt_integration' in st.session_state:
            mqtt_integration = st.session_state['mqtt_integration']
            if mqtt_integration and mqtt_integration.connected:
                mqtt_data = mqtt_integration.get_latest_data(selected_sensor_id)
                if mqtt_data:
                    mqtt_value = mqtt_data.get('value')
                    is_live_data = True
        elif mqtt_value is not None:
            is_live_data = True

        # Get the latest value
        latest_value = mqtt_value if is_live_data else (historical_data['value'].iloc[-1] if not historical_data.empty else 0)

        # Create a gauge chart for the current reading
        gauge_title = f"{tr('current')} {selected_sensor['type']} {tr('reading')}" + (" (LIVE)" if is_live_data else "")

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

        # Create the gauge chart
        fig = create_gauge_chart(
            value=latest_value,
            title=gauge_title,
            suffix=unit,
            min_value=min_val,
            max_value=max_val
        )

        # Update the container with the new chart
        with gauge_container.container():
            if is_live_data:
                # Add a live data indicator
                st.markdown(
                    '<div style="display:flex; align-items:center; margin-bottom:10px;">'
                    '<div style="width:10px; height:10px; border-radius:50%; background-color:#28a745; margin-right:5px;"></div>'
                    '<span>Données en direct</span>'
                    '</div>',
                    unsafe_allow_html=True
                )
            st.plotly_chart(fig, use_container_width=True, key=f"gauge_chart_{datetime.now().timestamp()}")

        return is_live_data, latest_value

    # Option de mise à jour automatique pour la page des détails du capteur
    auto_refresh = st.sidebar.checkbox("Mise à jour automatique", value=True)
    refresh_interval = st.sidebar.slider("Intervalle de rafraîchissement (secondes)", min_value=1, max_value=10, value=2)

    # Appel initial pour afficher les données MQTT
    live_data_found, mqtt_value_initial = update_mqtt_data()

    # Initial gauge update
    is_live_data, latest_value = update_gauge(mqtt_value_initial)

    # Si l'auto-refresh est activé, on démarre la boucle d'actualisation
    if auto_refresh and 'mqtt_integration' in st.session_state:
        # Créer un placeholder pour les mises à jour en temps réel
        update_time_placeholder = st.sidebar.empty()

        # Boucle de rafraîchissement pour données MQTT
        while True:
            # Attendre l'intervalle spécifié
            time.sleep(refresh_interval)

            # Mettre à jour les données MQTT
            live_data_found, mqtt_value = update_mqtt_data()

            # Mettre à jour la jauge en temps réel
            update_gauge(mqtt_value)

            # Afficher l'heure de la dernière mise à jour
            update_time_placeholder.info(f"{tr('last_update')}: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

    # Affichage initial du graphique historique pour les données non MQTT
    # Ce graphique sera remplacé par les données en temps réel pour MAT-101
    if not historical_data.empty and not (live_data_found and selected_sensor['mattress_id'] == "MAT-101"):
        with historical_chart_container.container():
            st.subheader(f"{tr('historical_data')} - Temps réel")
            
            # Create real-time line chart
            fig = go.Figure()
            
            # Get MQTT data if available
            mqtt_data = None
            if 'mqtt_integration' in st.session_state:
                mqtt_integration = st.session_state['mqtt_integration']
                if mqtt_integration and mqtt_integration.connected:
                    mqtt_data = mqtt_integration.get_latest_data(selected_sensor_id, history=True)
            
            if mqtt_data and isinstance(mqtt_data, list):
                # Convert MQTT timestamps to datetime
                x_data = [datetime.strptime(d['timestamp'], "%Y-%m-%d %H:%M:%S") for d in mqtt_data]
                y_data = [d['value'] for d in mqtt_data]
                
                # Add the real-time data trace
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='lines+markers',
                    name='Valeurs en temps réel',
                    line=dict(
                        color='#2E86C1',
                        width=2,
                        shape='linear'
                    ),
                    marker=dict(
                        size=8,
                        symbol='circle',
                        color='#2E86C1',
                        line=dict(
                            color='#FFFFFF',
                            width=1
                        )
                    )
                ))
                
                # Update layout with proper axes labels and grid
                fig.update_layout(
                    title=f"{selected_sensor['name']} - Mesures en temps réel",
                    xaxis=dict(
                        title='Temps',
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='#E5E5E5',
                        tickformat='%H:%M:%S'
                    ),
                    yaxis=dict(
                        title=f"Valeur ({selected_sensor['type']})",
                        showgrid=True,
                        gridwidth=1,
                        gridcolor='#E5E5E5'
                    ),
                    plot_bgcolor='white',
                    hovermode='x unified',
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True, key=f"live_chart_{datetime.now().timestamp()}")
            else:
                # Fallback to historical data if no MQTT data
                fig.add_trace(go.Scatter(
                    x=historical_data.index,
                    y=historical_data['value'],
                    mode='lines+markers',
                    name='Valeurs historiques',
                    line=dict(color='#2E86C1', width=2),
                    marker=dict(size=8, color='#2E86C1', symbol='circle')
                ))
                
                fig.update_layout(
                    title=f"{selected_sensor['name']} - Mesures historiques",
                    xaxis_title='Temps',
                    yaxis_title=f"Valeur ({selected_sensor['type']})",
                    plot_bgcolor='white',
                    hovermode='x unified',
                    height=500,
                    showlegend=True,
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#E5E5E5'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
                )
                
                st.plotly_chart(fig, use_container_width=True, key=f"historical_chart_{datetime.now().timestamp()}")

        # Statistics for the selected time period
        with stats_container.container():
            if 'value' in historical_data.columns:
                st.subheader(tr("statistics_for_period"))

                stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
                stats_col1.metric(tr("min_value"), f"{historical_data['value'].min():.2f}")
                stats_col2.metric(tr("max_value"), f"{historical_data['value'].max():.2f}")
                stats_col3.metric(tr("avg_value"), f"{historical_data['value'].mean():.2f}")
                stats_col4.metric(tr("std_dev"), f"{historical_data['value'].std():.2f}")
    elif not live_data_found or selected_sensor['mattress_id'] != "MAT-101":
        with historical_chart_container.container():
            st.warning(tr("no_historical_data_available"))

with col2:
    # Current readings
    st.subheader(tr("current_readings"))

    # Initial gauge update (using the function defined earlier)
    is_live_data, latest_value = update_gauge(mqtt_value_initial)

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
    st.plotly_chart(signal_fig, use_container_width=True, key=f"signal_chart_{datetime.now().timestamp()}")

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