import paho.mqtt.client as mqtt
import json
import time
import threading
import logging
from datetime import datetime
import streamlit as st
from datetime import datetime

# Configuration du client MQTT pour l'intégration avec le broker externe
class MQTTIntegration:
    def __init__(self, 
                 host="localhost", 
                 port=1883,
                 username=None,
                 password=None,
                 topics=None):
        """
        Initialise le client MQTT pour l'intégration avec le broker externe

        Parameters:
        - host: Adresse du broker MQTT 
        - port: Port du broker MQTT
        - username: Nom d'utilisateur pour l'authentification (optionnel)
        - password: Mot de passe pour l'authentification (optionnel)
        - topics: Liste des topics à écouter
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = f"medimat_integration_{int(time.time())}"
        self.client = mqtt.Client(client_id=self.client_id)
        self.connected = False
        self.latest_data = {}

        # Configurer l'authentification si nécessaire
        if username and password:
            self.client.username_pw_set(username, password)

        # Topics MQTT pour les capteurs
        self.topics = topics or [
            "capteur/temperature",
            "capteur/humidite",
            "capteur/debit_urinaire", 
            "capteur/poul",
            "capteur/creatine"
        ]

        # Map des topics vers les types de capteurs
        self.topic_type_map = {
            "capteur/temperature": "temperature",
            "capteur/humidite": "humidity",
            "capteur/debit_urinaire": "debit",
            "capteur/poul": "poul",
            "capteur/creatine": "creatine"
        }

        # Map des types de capteurs pour la compatibilité
        self.sensor_type_map = {
            "temperature": "temperature",
            "humidity": "humidity",
            "debit": "flow",
            "poul": "pulse",
            "creatine": "creatinine"
        }

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("mqtt_integration")

        # Set up callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def connect(self):
        """
        Se connecte au broker MQTT
        """
        try:
            self.logger.info(f"Connexion au broker MQTT {self.host}:{self.port}")
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            self.logger.error(f"Échec de connexion au broker MQTT: {e}")
            return False

    def disconnect(self):
        """
        Se déconnecte du broker MQTT
        """
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        self.logger.info("Déconnecté du broker MQTT")

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback appelé lors de la connexion au broker
        """
        if rc == 0:
            self.connected = True
            self.logger.info("Connecté au broker MQTT")

            # Souscrire à tous les topics
            for topic in self.topics:
                self.client.subscribe(topic)
                self.logger.info(f"Souscrit au topic {topic}")
        else:
            self.connected = False
            self.logger.error(f"Échec de connexion avec code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback appelé lors de la déconnexion du broker
        """
        self.connected = False
        if rc != 0:
            self.logger.warning(f"Déconnexion inattendue, code {rc}")
        else:
            self.logger.info("Déconnecté du broker")

    def on_message(self, client, userdata, msg):
        """
        Callback appelé lorsqu'un message est reçu du broker
        """
        try:
            # Afficher le message reçu pour le débogage
            self.logger.info(f"Message reçu sur le topic {msg.topic}")

            # Pour les nouveaux topics comme capteur/temperature
            topic = msg.topic
            if topic not in self.topic_type_map:
                self.logger.warning(f"Topic non reconnu: {topic}")
                return

            sensor_type = self.topic_type_map[topic]

            # Map des types de capteurs aux IDs par matelas
            def get_sensor_id(sensor_type, mattress_id):
                base_ids = {
                    "temperature": lambda mat_num: 202 + ((mat_num - 101) * 10),
                    "humidity": lambda mat_num: 203 + ((mat_num - 101) * 10),
                    "debit": lambda mat_num: 204 + ((mat_num - 101) * 10),
                    "poul": lambda mat_num: 205 + ((mat_num - 101) * 10),
                    "creatine": lambda mat_num: 206 + ((mat_num - 101) * 10)
                }
                try:
                    mat_num = int(mattress_id.split('-')[1])
                    return base_ids[sensor_type] + (mat_num - 101) * 10
                except (ValueError, KeyError, IndexError):
                    self.logger.error(f"Error getting sensor ID for mattress {mattress_id}, sensor {sensor_type}")
                    return None

            # Extraire l'ID du matelas depuis l'UUID
            mattress_map = {
                "1234567890abcdef": "MAT-101",
                "abcdef1234567890": "MAT-102", 
                "0abcdef123456789": "MAT-103",
                "def0123456789abc": "MAT-104",
                "789abcdef012345": "MAT-105"
            }
            mattress_id = mattress_map.get(uid)
            if not mattress_id:
                self.logger.warning(f"UUID non reconnu: {uid}")
                return

            sensor_id = get_sensor_id(sensor_type, mattress_id)
            if sensor_id is None:
              return

            try:
                # Tenter de décoder le payload JSON
                payload = json.loads(msg.payload.decode())

                # Format du payload selon le code fourni
                value = payload.get("value")
                uid = payload.get("uid")
                timestamp = datetime.fromtimestamp(payload.get("timestamp", time.time())).strftime("%Y-%m-%d %H:%M:%S")

                if value is None:
                    self.logger.warning(f"Payload incomplet: {payload}")
                    return

                # Définir les unités selon le type de capteur
                units = {
                    "temperature": "°C",
                    "humidity": "%",
                    "debit": "L/h",
                    "poul": "bpm",
                    "creatine": "mg/dL"
                }
                unit = units.get(sensor_type, "")
                status = "active"
                sensor_name = f"Capteur {sensor_type.capitalize()}"

            except (json.JSONDecodeError, AttributeError) as e:
                self.logger.warning(f"Impossible de parser le payload JSON: {e}")
                return

            # Mapping du type de capteur si nécessaire
            mapped_type = self.sensor_type_map.get(sensor_type, sensor_type)

            # Stocker les données actuelles
            current_data = {
                'id': sensor_id,
                'name': sensor_name or f"Capteur {sensor_id}",
                'type': mapped_type,
                'value': value,
                'unit': unit,
                'timestamp': timestamp,
                'topic': msg.topic,
                'mattress_id': mattress_id,
                'status': status
            }

            # Créer ou mettre à jour l'historique des données pour ce capteur
            if sensor_id not in self.latest_data:
                self.latest_data[sensor_id] = {
                    'current': current_data,
                    'history': [current_data]
                }
            else:
                # Mettre à jour les données courantes
                self.latest_data[sensor_id]['current'] = current_data

                # Ajouter à l'historique (limité à 20 entrées)
                history = self.latest_data[sensor_id]['history']
                history.append(current_data)

                # Garder seulement les 20 dernières entrées
                if len(history) > 20:
                    self.latest_data[sensor_id]['history'] = history[-20:]

            self.logger.info(f"Données mises à jour pour le capteur {sensor_id} du matelas {mattress_id}: {value} {unit}")

        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du message: {e}")

    def get_latest_data(self, sensor_id=None, history=False):
        """
        Retourne les dernières données reçues des capteurs

        Parameters:
        - sensor_id: Optionnel, filtre par ID du capteur
        - history: Si True, renvoie l'historique des données, sinon uniquement les données actuelles

        Returns:
        - Dictionnaire des dernières données ou liste de l'historique
        """
        if sensor_id is None:
            # Si on veut l'historique pour tous les capteurs
            if history:
                result = {}
                for sensor_id, data in self.latest_data.items():
                    result[sensor_id] = data.get('history', [])
                return result
            else:
                # Sinon, retourne seulement les données actuelles pour tous les capteurs
                result = {}
                for sensor_id, data in self.latest_data.items():
                    result[sensor_id] = data.get('current', {})
                return result

        # Si le capteur n'existe pas
        if sensor_id not in self.latest_data:
            return {}

        # Si on veut l'historique pour un capteur spécifique
        if history:
            return self.latest_data[sensor_id].get('history', [])
        else:
            return self.latest_data[sensor_id].get('current', {})

# Création d'une instance globale pour l'intégration MQTT
mqtt_integration = None

def initialize_mqtt_integration(host="localhost", port=1883, username=None, password=None, topics=None):
    """
    Initialise l'intégration MQTT

    Parameters:
    - host: Adresse du broker MQTT
    - port: Port du broker MQTT
    - username: Nom d'utilisateur pour l'authentification (optionnel)
    - password: Mot de passe pour l'authentification (optionnel)
    - topics: Liste des topics à écouter (optionnel)
    """
    global mqtt_integration

    # Si l'intégration existe déjà, la déconnecter d'abord
    if mqtt_integration is not None:
        try:
            mqtt_integration.disconnect()
        except:
            pass
        mqtt_integration = None

    # Créer une nouvelle instance
    mqtt_integration = MQTTIntegration(
        host=host, 
        port=port, 
        username=username, 
        password=password,
        topics=topics
    )

    # Se connecter
    success = mqtt_integration.connect()

    if success:
        # Stocker l'intégration dans le session state pour qu'elle soit accessible partout
        st.session_state['mqtt_integration'] = mqtt_integration

        logging.info(f"Intégration MQTT initialisée et connectée à {host}:{port}")
        return mqtt_integration
    else:
        logging.error(f"Échec de l'initialisation de l'intégration MQTT avec {host}:{port}")
        return None

def get_mqtt_integration():
    """
    Retourne l'instance d'intégration MQTT
    """
    global mqtt_integration

    # Si déjà dans session_state, utiliser celle-là
    if 'mqtt_integration' in st.session_state:
        return st.session_state['mqtt_integration']

    # Sinon, initialiser une nouvelle instance
    return initialize_mqtt_integration()