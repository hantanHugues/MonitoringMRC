#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import random
import time
import json
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration MQTT
broker = "0.0.0.0"
port = 1883

# Topics MQTT
topics = {
    "temperature": "capteur/temperature",
    "humidite": "capteur/humidite",
    "debit_urinaire": "capteur/debit_urinaire",
    "poul": "capteur/poul",
    "creatine": "capteur/creatine"
}

# ESP32 UUIDs
esp32_uuids = {
    "esp32_1": "1234567890abcdef",
    "esp32_2": "abcdef1234567890",
    "esp32_3": "0abcdef123456789"
}

def generate_data(sensor_type):
    if sensor_type == "temperature":
        return round(random.uniform(20.0, 30.0), 2)
    elif sensor_type == "humidite":
        return round(random.uniform(30.0, 60.0), 2)
    elif sensor_type == "debit_urinaire":
        return random.randint(1, 10)
    elif sensor_type == "poul":
        return random.randint(60, 100)
    elif sensor_type == "creatine":
        return round(random.uniform(0.5, 1.5), 2)
    else:
        logging.error(f"Type de capteur inconnu: {sensor_type}")
        return None

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logging.info("Connecté au broker MQTT")
    else:
        logging.error(f"Échec de connexion au broker MQTT, code de retour: {rc}")

def main():
    # Configuration du client avec ID unique et protocole v3.1.1
    client_id = f"sensor_publisher_{int(time.time())}"
    client = mqtt.Client(
        client_id=client_id,
        clean_session=True
    )
    client.on_connect = on_connect

    # Ajout de la gestion des erreurs de connexion
    client.on_disconnect = lambda client, userdata, rc: logging.error(f"Déconnexion avec code {rc}")

    try:
        # Tentatives de reconnexion automatique
        client.reconnect_delay_set(min_delay=1, max_delay=30)
        logging.info(f"Tentative de connexion au broker MQTT à {broker}:{port}...")
        client.connect(broker, port, 60)
        client.loop_start()

        while True:
            for esp32_id, uid in esp32_uuids.items():
                for sensor_type, topic in topics.items():
                    value = generate_data(sensor_type)
                    if value is not None:
                        message = {
                            "uid": uid,
                            "value": value,
                            "timestamp": time.time(),
                            "sensor_type": sensor_type
                        }

                        result = client.publish(topic, json.dumps(message), qos=0)
                        if result.rc == mqtt.MQTT_ERR_SUCCESS:
                            logging.info(f"Publié sur {topic}: {message}")
                        else:
                            logging.error(f"Échec de publication sur {topic}")

            time.sleep(2)

    except KeyboardInterrupt:
        logging.info("Arrêt du test MQTT")
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        logging.error(f"Erreur: {e}")
    finally:
        logging.info("Test MQTT terminé")

if __name__ == "__main__":
    main()