import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import threading
from utils.sensor_utils import get_sensor_status_color, generate_sample_data
from utils.visualization import create_time_series_chart, create_gauge_chart
from utils.translation import get_translation
from utils.data_manager import get_sensors_data, get_mattresses_data

# Configuration de la page
st.set_page_config(
    page_title="Détails des Capteurs - Monitoring Matelas Médical",
    page_icon="📊",
    layout="wide"
)

# En-tête
if 'language' not in st.session_state:
    st.session_state['language'] = 'fr'

tr = lambda key: get_translation(key, st.session_state.language)

# Conteneur principal avec style personnalisé
st.markdown("""
    <style>
    .main-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .sensor-header {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .sensor-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .metric-container {
        padding: 10px;
        border-radius: 5px;
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)

# Obtention des données
sensors_data = get_sensors_data()
mattresses_data = get_mattresses_data()

# Sidebar pour les filtres
with st.sidebar:
    st.header("🔍 Sélection du Capteur")

    # Sélection par matelas
    mattress_options = {m.id: f"{m.name} ({m.location})" for m in mattresses_data.itertuples()}
    selected_mattress_id = st.selectbox(
        "Sélectionner un matelas",
        options=list(mattress_options.keys()),
        format_func=lambda x: mattress_options[x]
    )

    # Filtrer les capteurs par matelas sélectionné
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

    # Sélection du capteur
    sensor_options = {s.id: f"{s.name} ({s.type} - {s.unit})" for s in filtered_sensors.itertuples()}
    selected_sensor_id = st.selectbox(
        "Sélectionner un capteur",
        options=list(sensor_options.keys()),
        format_func=lambda x: sensor_options[x]
    )

# Obtenir le capteur sélectionné
selected_sensor = filtered_sensors[filtered_sensors['id'] == selected_sensor_id].iloc[0]

# En-tête principal
with st.container():
    st.markdown(f"""
        <div class="sensor-header">
            <h1>📊 {selected_sensor['name']}</h1>
            <p>Monitoring en temps réel des données du capteur</p>
        </div>
    """, unsafe_allow_html=True)

# Disposition principale en trois colonnes
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    # Carte des valeurs actuelles
    st.markdown('<div class="sensor-card">', unsafe_allow_html=True)
    st.subheader("📈 Valeurs Actuelles")
    current_value_container = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

    # Graphique historique
    st.markdown('<div class="sensor-card">', unsafe_allow_html=True)
    historical_chart_container = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Statistiques et tendances
    st.markdown('<div class="sensor-card">', unsafe_allow_html=True)
    st.subheader("📊 Statistiques")
    stats_container = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

    # Tableau des dernières valeurs
    st.markdown('<div class="sensor-card">', unsafe_allow_html=True)
    st.subheader("📋 Dernières Mesures")
    table_container = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    # Informations du capteur
    st.markdown('<div class="sensor-card">', unsafe_allow_html=True)
    st.subheader("ℹ️ Informations")
    status_color = get_sensor_status_color(selected_sensor['status'])
    st.markdown(f"""
        - 🏷️ **ID:** {selected_sensor['id']}
        - 📊 **Type:** {selected_sensor['type']}
        - 📏 **Unité:** {selected_sensor['unit']}
        - 🔌 **État:** <span style='color:{status_color};font-weight:bold;'>{selected_sensor['status'].upper()}</span>
        - 🛏️ **Matelas:** {selected_sensor['mattress_id']}
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Actions rapides
    st.markdown('<div class="sensor-card">', unsafe_allow_html=True)
    st.subheader("⚡ Actions Rapides")
    if st.button("🔄 Calibrer"):
        st.info("Calibration en cours...")
    if st.button("📊 Exporter CSV"):
        st.download_button(
            "📥 Télécharger",
            data=pd.DataFrame().to_csv().encode('utf-8'),
            file_name=f'capteur_{selected_sensor["id"]}_data.csv',
            mime='text/csv',
        )
    if st.button("⚠️ Test Alarme"):
        st.warning("Test d'alarme effectué")
    st.markdown('</div>', unsafe_allow_html=True)

# Initialiser les données historiques
historical_data = generate_sample_data(
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now(),
    interval_seconds=60,
    sensor_type=selected_sensor['type']
)

# Fonction de mise à jour des données en temps réel
def update_sensor_data():
    while True:
        try:
            mqtt_data = None
            if 'mqtt_integration' in st.session_state:
                mqtt_integration = st.session_state['mqtt_integration']
                if mqtt_integration and mqtt_integration.connected:
                    mqtt_data = mqtt_integration.get_latest_data(selected_sensor_id)

            if not mqtt_data and 'direct_simulator' in st.session_state:
                direct_simulator = st.session_state['direct_simulator']
                if direct_simulator:
                    mqtt_data = direct_simulator.get_latest_data(selected_sensor_id)

            if mqtt_data:
                with current_value_container:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Valeur actuelle",
                            f"{mqtt_data.get('value', 0):.1f} {selected_sensor['unit']}",
                            delta=None
                        )
                    with col2:
                        st.metric(
                            "Dernière mise à jour",
                            datetime.now().strftime("%H:%M:%S")
                        )

                if not historical_data.empty:
                    new_data = pd.DataFrame({
                        'timestamp': [datetime.now()],
                        'value': [mqtt_data.get('value', 0)]
                    })
                    historical_data = pd.concat([historical_data, new_data]).tail(100)

                    with historical_chart_container:
                        fig = create_time_series_chart(
                            historical_data,
                            f"Évolution - {selected_sensor['name']}",
                            selected_sensor['type']
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with stats_container:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Moyenne", f"{historical_data['value'].mean():.1f} {selected_sensor['unit']}")
                        with col2:
                            st.metric("Maximum", f"{historical_data['value'].max():.1f} {selected_sensor['unit']}")
                        with col3:
                            st.metric("Minimum", f"{historical_data['value'].min():.1f} {selected_sensor['unit']}")

                    with historical_chart_container:
                        st.subheader("📈 Historique des mesures")
                        fig = px.line(
                            historical_data,
                            x='timestamp',
                            y='value',
                            title=f"Évolution des données - {selected_sensor['name']}",
                            labels={'value': f"Valeur ({selected_sensor['unit']})", 'timestamp': 'Temps'}
                        )
                        fig.update_layout(
                            xaxis=dict(rangeslider=dict(visible=True)),
                            yaxis_title=f"Valeur ({selected_sensor['unit']})",
                            height=400,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with table_container:
                        st.subheader("📋 Dernières mesures")
                        st.dataframe(
                            historical_data.tail(10).sort_values('timestamp', ascending=False),
                            use_container_width=True,
                            hide_index=True
                        )


        except Exception as e:
            st.error(f"Erreur de mise à jour: {e}")

        time.sleep(2)

# Démarrer la mise à jour automatique dans un thread séparé
if 'update_thread' not in st.session_state:
    update_thread = threading.Thread(target=update_sensor_data, daemon=True)
    update_thread.start()
    st.session_state['update_thread'] = update_thread