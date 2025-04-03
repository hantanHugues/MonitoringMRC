#!/usr/bin/env python
"""
Simulateur de capteurs pour envoyer des données via MQTT
Ce script simule des capteurs de matelas médicaux et envoie les données via MQTT
"""

import paho.mqtt.client as mqtt
import random
import time
import json
import argparse
import logging
import signal
import sys
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration MQTT
broker = "127.0.0.1"
port = 1883
client_id = f"sensor-simulator-{random.randint(0, 1000)}"
keep_alive = 60

# Paramètres des capteurs
mattress_id = "MAT-101"  # Matelas 1 (celui qui recevra les données MQTT)
sensor_types = {
    "SEN-201": {
        "type": "pressure",
        "min_value": 0,
        "max_value": 100,
        "unit": "mmHg",
        "frequency": 5,  # secondes entre les mesures
    },
    "SEN-202": {
        "type": "temperature",
        "min_value": 34,
        "max_value": 40,
        "unit": "°C",
        "frequency": 10,
    },
    "SEN-203": {
        "type": "humidity",
        "min_value": 30,
        "max_value": 70,
        "unit": "%",
        "frequency": 15,
    }
}

# Gestion de l'arrêt propre du script
running = True

def signal_handler(sig, frame):
    """Gère l'arrêt propre du script avec Ctrl+C"""
    global running
    logger.info("Arrêt du simulateur...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

# Fonctions MQTT
def on_connect(client, userdata, flags, rc):
    """Callback appelé lors de la connexion au broker MQTT"""
    if rc == 0:
        logger.info("Connecté au broker MQTT")
    else:
        logger.error(f"Échec de connexion au broker, code retour: {rc}")

def on_disconnect(client, userdata, rc):
    """Callback appelé lors de la déconnexion du broker MQTT"""
    if rc != 0:
        logger.warning(f"Déconnexion inattendue, code retour: {rc}")
    else:
        logger.info("Déconnexion du broker MQTT")

def on_publish(client, userdata, mid):
    """Callback appelé lorsqu'un message est publié"""
    pass  # Peut être utilisé pour le débogage

def generate_sensor_value(sensor_id):
    """Génère une valeur de capteur aléatoire basée sur la configuration du capteur"""
    sensor_config = sensor_types[sensor_id]
    
    if sensor_config["type"] == "pressure":
        # Pression: variations plus importantes
        base_value = random.uniform(sensor_config["min_value"], sensor_config["max_value"])
        noise = random.uniform(-5, 5)
        value = max(sensor_config["min_value"], min(base_value + noise, sensor_config["max_value"]))
    
    elif sensor_config["type"] == "temperature":
        # Température: faibles variations
        base_value = 36.5  # Température normale
        noise = random.uniform(-0.5, 0.5)
        value = max(sensor_config["min_value"], min(base_value + noise, sensor_config["max_value"]))
    
    elif sensor_config["type"] == "humidity":
        # Humidité: variations moyennes
        base_value = 50  # Humidité médiane
        noise = random.uniform(-3, 3)
        value = max(sensor_config["min_value"], min(base_value + noise, sensor_config["max_value"]))
    
    else:
        # Type de capteur inconnu
        value = random.uniform(sensor_config["min_value"], sensor_config["max_value"])
    
    return round(value, 1)

def create_sensor_payload(sensor_id, value):
    """Crée la charge utile à envoyer via MQTT"""
    sensor_config = sensor_types[sensor_id]
    
    return {
        "mattress_id": mattress_id,
        "sensor_id": sensor_id,
        "type": sensor_config["type"],
        "value": value,
        "unit": sensor_config["unit"],
        "timestamp": datetime.now().isoformat()
    }

def simulate_sensors(client):
    """Simule les capteurs et publie les données"""
    logger.info(f"Démarrage de la simulation pour {len(sensor_types)} capteurs sur le matelas {mattress_id}")
    
    last_update = {sensor_id: 0 for sensor_id in sensor_types}
    
    try:
        while running:
            current_time = time.time()
            
            for sensor_id, sensor_config in sensor_types.items():
                # Vérifier si c'est le moment de mettre à jour ce capteur
                if current_time - last_update[sensor_id] >= sensor_config["frequency"]:
                    # Générer et publier une nouvelle valeur
                    value = generate_sensor_value(sensor_id)
                    payload = create_sensor_payload(sensor_id, value)
                    
                    # Construire le topic MQTT
                    topic = f"hospital/mattress/{mattress_id}/{sensor_id}"
                    
                    # Publier le message
                    client.publish(topic, json.dumps(payload), qos=0)
                    logger.info(f"Publié: {topic} = {payload['value']} {payload['unit']}")
                    
                    # Mettre à jour le timestamp
                    last_update[sensor_id] = current_time
            
            # Attendre un peu pour ne pas surcharger le système
            time.sleep(1)
            
    except Exception as e:
        logger.error(f"Erreur lors de la simulation: {e}")
    finally:
        client.disconnect()
        logger.info("Simulation terminée")

def main():
    """Fonction principale"""
    
    # Configuration à partir des arguments en ligne de commande
    parser = argparse.ArgumentParser(description="Simulateur de capteurs MQTT")
    parser.add_argument("--broker", type=str, default="127.0.0.1", 
                        help="Adresse du broker MQTT (défaut: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=1883, 
                        help="Port du broker MQTT (défaut: 1883)")
    args = parser.parse_args()
    
    # Utiliser les arguments de ligne de commande
    global broker, port
    broker = args.broker
    port = args.port
    
    # Créer le client MQTT
    client = mqtt.Client(client_id=client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    
    try:
        # Se connecter au broker
        logger.info(f"Connexion au broker MQTT à {broker}:{port}")
        client.connect(broker, port, keep_alive)
        
        # Démarrer le thread de réseau MQTT
        client.loop_start()
        
        # Simuler les capteurs
        simulate_sensors(client)
        
    except KeyboardInterrupt:
        logger.info("Interruption par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur: {e}")
    finally:
        # S'assurer que le client est déconnecté proprement
        client.loop_stop()
        if client.is_connected():
            client.disconnect()
        logger.info("Programme terminé")

if __name__ == "__main__":
    main()