import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils.sensor_utils import generate_sample_data
from utils.data_manager import get_sensors_data, get_mattresses_data

# Configuration de la page
st.set_page_config(page_title="Détails des Capteurs", page_icon="📊", layout="wide")

# Obtention des données
sensors_data = get_sensors_data()
mattresses_data = get_mattresses_data()

# Sidebar pour la sélection
with st.sidebar:
    st.header("🔍 Sélection du Capteur")

    # Sélection par matelas
    mattress_options = {m.id: f"{m.name} ({m.location})" for m in mattresses_data.itertuples()}
    selected_mattress_id = st.selectbox(
        "Sélectionner un matelas",
        options=list(mattress_options.keys()),
        format_func=lambda x: mattress_options[x]
    )

    # Liste des capteurs pour le matelas sélectionné
    filtered_sensors = []
    for sensor_type, name, unit in [
        ('temperature', 'Capteur de température', '°C'),
        ('humidity', 'Capteur d\'humidité', '%'),
        ('debit_urinaire', 'Débit urinaire', 'ml/h'),
        ('poul', 'Pouls', 'bpm'),
        ('creatine', 'Créatinine', 'mg/dL')
    ]:
        filtered_sensors.append({
            'id': f"SEN-{201 + len(filtered_sensors)}",
            'name': name,
            'type': sensor_type,
            'unit': unit,
            'mattress_id': selected_mattress_id
        })

    filtered_sensors = pd.DataFrame(filtered_sensors)
    sensor_options = {s.id: f"{s.name}" for s in filtered_sensors.itertuples()}
    selected_sensor_id = st.selectbox(
        "Sélectionner un capteur",
        options=list(sensor_options.keys()),
        format_func=lambda x: sensor_options[x]
    )

# Obtenir le capteur sélectionné
selected_sensor = filtered_sensors[filtered_sensors['id'] == selected_sensor_id].iloc[0]

# En-tête
st.title(f"📊 {selected_sensor['name']}")
st.markdown("Monitoring en temps réel des données du capteur")

# Génération des données exemple
historical_data = generate_sample_data(
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now(),
    interval_seconds=60,
    sensor_type=selected_sensor['type']
)

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    # Graphique
    st.subheader("📈 Historique des mesures")
    fig = px.line(
        historical_data,
        x='timestamp',
        y='value',
        title=f"Évolution - {selected_sensor['name']}",
    )
    fig.update_layout(
        xaxis_title="Temps",
        yaxis_title=f"Valeur ({selected_sensor['unit']})",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tableau des dernières mesures
    st.subheader("📋 Dernières mesures")
    st.dataframe(
        historical_data.tail(10).sort_values('timestamp', ascending=False),
        use_container_width=True,
        hide_index=True
    )

with col2:
    # Statistiques actuelles
    st.subheader("📊 Statistiques")
    current_value = historical_data['value'].iloc[-1]
    avg_value = historical_data['value'].mean()
    max_value = historical_data['value'].max()
    min_value = historical_data['value'].min()

    st.metric("Valeur actuelle", f"{current_value:.1f} {selected_sensor['unit']}")
    st.metric("Moyenne", f"{avg_value:.1f} {selected_sensor['unit']}")
    st.metric("Maximum", f"{max_value:.1f} {selected_sensor['unit']}")
    st.metric("Minimum", f"{min_value:.1f} {selected_sensor['unit']}")