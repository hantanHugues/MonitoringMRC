#!/usr/bin/env python3
"""
Script de test pour envoyer des données au broker MQTT local.
Ce script permet de simuler des capteurs qui envoient des données au broker MQTT
que notre application Streamlit peut ensuite récupérer.
"""

import paho.mqtt.client as mqtt
import random
import time
import json
import datetime
import argparse
import signal
import sys
import logging

# Configuration de la journalisation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration MQTT par défaut
DEFAULT_BROKER_HOST = "0.0.0.0"
DEFAULT_BROKER_PORT = 1883
DEFAULT_MATTRESS_ID = "MAT-101"
DEFAULT_TOPIC_PREFIX = "hospital/mattress/"

# Configuration des capteurs
SENSORS = {
    "SEN-201": {
        "type": "pressure",
        "name": "Pressure Sensor 1",
        "min_value": 0,
        "max_value": 100,
        "unit": "mmHg",
        "variation": 10
    },
    "SEN-202": {
        "type": "temperature",
        "name": "Temperature Sensor 1",
        "min_value": 35.5,
        "max_value": 37.5,
        "unit": "°C",
        "variation": 0.5
    },
    "SEN-203": {
        "type": "humidity",
        "name": "Humidity Sensor 1",
        "min_value": 40,
        "max_value": 60,
        "unit": "%",
        "variation": 5
    }
}

# Variables globales
client = None
running = True
last_values = {}

def on_connect(client, userdata, flags, rc):
    """Callback pour la connexion au broker MQTT"""
    if rc == 0:
        logging.info("Connecté au broker MQTT")
    else:
        logging.error(f"Échec de connexion au broker MQTT, code de retour: {rc}")

def on_disconnect(client, userdata, rc):
    """Callback pour la déconnexion du broker MQTT"""
    if rc != 0:
        logging.warning(f"Déconnexion inattendue du broker MQTT, code de retour: {rc}")

def on_publish(client, userdata, mid):
    """Callback pour la publication d'un message"""
    logging.debug(f"Message {mid} publié")

def generate_sensor_value(sensor_id):
    """Génère une valeur de capteur aléatoire basée sur la configuration"""
    sensor = SENSORS[sensor_id]
    
    # Si nous avons déjà une valeur précédente, utiliser une variation aléatoire
    if sensor_id in last_values:
        last_value = last_values[sensor_id]
        variation = sensor["variation"] * random.uniform(-1, 1)
        new_value = last_value + variation
        
        # S'assurer que la nouvelle valeur est dans les limites
        new_value = max(sensor["min_value"], min(sensor["max_value"], new_value))
    else:
        # Première valeur, générer un nombre aléatoire dans la plage
        new_value = random.uniform(sensor["min_value"], sensor["max_value"])
    
    # Stocker la valeur pour la prochaine itération
    last_values[sensor_id] = new_value
    
    return new_value

def create_sensor_payload(sensor_id, value):
    """Crée la charge utile à envoyer via MQTT"""
    sensor = SENSORS[sensor_id]
    
    # Formater la valeur en fonction du type de capteur
    if sensor["type"] == "temperature":
        formatted_value = f"{value:.1f} {sensor['unit']}"
    elif sensor["type"] == "humidity":
        formatted_value = f"{value:.1f} {sensor['unit']}"
    elif sensor["type"] == "pressure":
        formatted_value = f"{value:.1f} {sensor['unit']}"
    else:
        formatted_value = f"{value:.1f} {sensor['unit']}"
    
    # Créer le payload
    payload = {
        "sensor_id": sensor_id,
        "type": sensor["type"],
        "name": sensor["name"],
        "value": value,
        "formatted_value": formatted_value,
        "unit": sensor["unit"],
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "active"
    }
    
    return json.dumps(payload)

def publish_sensors(client, mattress_id):
    """Publie des données de capteurs via MQTT"""
    for sensor_id in SENSORS:
        # Générer une valeur pour ce capteur
        value = generate_sensor_value(sensor_id)
        
        # Créer la charge utile
        payload = create_sensor_payload(sensor_id, value)
        
        # Construire le topic MQTT
        topic = f"{DEFAULT_TOPIC_PREFIX}{mattress_id}/{sensor_id}"
        
        # Publier le message
        result = client.publish(topic, payload, qos=0, retain=True)
        
        # Vérifier si la publication a réussi
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            sensor_type = SENSORS[sensor_id]["type"]
            sensor_unit = SENSORS[sensor_id]["unit"]
            logging.info(f"Publié: {topic} = {value:.1f} {sensor_unit}")
        else:
            logging.error(f"Échec de publication sur {topic}, code d'erreur: {result.rc}")

def signal_handler(sig, frame):
    """Gère l'arrêt propre du script avec Ctrl+C"""
    global running
    logging.info("Arrêt du test MQTT...")
    running = False

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Testeur MQTT pour simuler des capteurs de matelas")
    parser.add_argument("-b", "--broker", type=str, default=DEFAULT_BROKER_HOST,
                        help=f"Adresse du broker MQTT (défaut: {DEFAULT_BROKER_HOST})")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_BROKER_PORT,
                        help=f"Port du broker MQTT (défaut: {DEFAULT_BROKER_PORT})")
    parser.add_argument("-m", "--mattress", type=str, default=DEFAULT_MATTRESS_ID,
                        help=f"ID du matelas (défaut: {DEFAULT_MATTRESS_ID})")
    parser.add_argument("-i", "--interval", type=float, default=5.0,
                        help="Intervalle entre les mises à jour (en secondes, défaut: 5.0)")
    args = parser.parse_args()
    
    global client
    
    # Configurer le client MQTT
    client_id = f"mqtt-test-{random.randint(0, 1000)}"
    client = mqtt.Client(client_id=client_id)
    
    # Configurer les callbacks
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    
    try:
        # Se connecter au broker
        logging.info(f"Tentative de connexion au broker MQTT à {args.broker}:{args.port}...")
        client.connect(args.broker, args.port, 60)
        
        # Démarrer le client dans un thread séparé
        client.loop_start()
        
        # Imprimer le message de démarrage
        logging.info(f"Test MQTT démarré pour le matelas {args.mattress}")
        logging.info(f"Intervalle de mise à jour: {args.interval} secondes")
        logging.info("Appuyez sur Ctrl+C pour arrêter")
        
        # Boucle principale
        while running:
            # Publier les données des capteurs
            publish_sensors(client, args.mattress)
            
            # Attendre l'intervalle spécifié
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Erreur: {e}")
    finally:
        # Arrêter proprement le client MQTT
        if client:
            client.loop_stop()
            client.disconnect()
            
        logging.info("Test MQTT terminé")

if __name__ == "__main__":
    # Configurer le gestionnaire de signal pour Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Lancer la fonction principale
    main()