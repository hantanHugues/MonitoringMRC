import paho.mqtt.client as mqtt
import json
import time
import threading
import logging
import streamlit as st
from datetime import datetime

# Configuration du client MQTT pour l'intégration avec le simulateur externe
class MQTTIntegration:
    def __init__(self, 
                 host="localhost", 
                 port=1883,
                 topics=None):
        """
        Initialise le client MQTT pour l'intégration avec le simulateur externe
        
        Parameters:
        - host: Adresse du broker MQTT 
        - port: Port du broker MQTT
        - topics: Liste des topics à écouter
        """
        self.host = host
        self.port = port
        self.client_id = f"medimat_integration_{int(time.time())}"
        self.client = mqtt.Client(client_id=self.client_id)
        self.connected = False
        self.latest_data = {}
        
        # Topics MQTT pour les capteurs - format matelas/mattress_id/sensor_id
        # Pour le simulateur, on utilise les topics hospital/mattress/MAT-101/SEN-20X
        self.topics = topics or [
            "hospital/mattress/+/+"  # Subscribe à tous les topics des capteurs
        ]
        
        # Map du type de capteur vers le type dans notre système
        self.sensor_type_map = {
            "temperature": "temperature",
            "humidity": "humidity",
            "pressure": "pressure",
            "movement": "movement"
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
            self.logger.info(f"Message reçu sur le topic {msg.topic}: {msg.payload}")
            
            # Format du topic attendu: hospital/mattress/MAT-101/SEN-201
            topic_parts = msg.topic.split('/')
            if len(topic_parts) < 4:
                self.logger.warning(f"Format de topic invalide: {msg.topic}")
                return
                
            # Extraire l'ID du matelas et du capteur du topic
            mattress_id = topic_parts[2]
            sensor_id = topic_parts[3]
            
            # Parse the message payload as JSON
            payload = json.loads(msg.payload.decode())
            
            # Extraire les données du payload
            value = payload.get("value")
            sensor_type = payload.get("type")
            
            if value is not None and sensor_type is not None:
                # Conserver le type de capteur dans notre format interne
                mapped_type = self.sensor_type_map.get(sensor_type, sensor_type)
                
                # Ajouter aux données les plus récentes
                if sensor_id not in self.latest_data:
                    self.latest_data[sensor_id] = {}
                
                self.latest_data[sensor_id] = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'type': mapped_type,
                    'value': value,
                    'topic': msg.topic,
                    'mattress_id': mattress_id
                }
                
                self.logger.info(f"Données mises à jour pour le capteur {sensor_id} du matelas {mattress_id}: {value} ({mapped_type})")
            else:
                self.logger.warning(f"Données incomplètes reçues: valeur={value}, type={sensor_type}")
                
        except json.JSONDecodeError:
            self.logger.warning(f"JSON invalide reçu: {msg.payload}")
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement du message: {e}")
    
    def get_latest_data(self, sensor_id=None):
        """
        Retourne les dernières données reçues des capteurs
        
        Parameters:
        - sensor_id: Optionnel, filtre par ID du capteur
        
        Returns:
        - Dictionnaire des dernières données
        """
        if sensor_id is None:
            return self.latest_data
        
        if sensor_id not in self.latest_data:
            return {}
        
        return self.latest_data[sensor_id]

# Création d'une instance globale pour l'intégration MQTT
mqtt_integration = None

def initialize_mqtt_integration(host="localhost", port=1883):
    """
    Initialise l'intégration MQTT
    """
    global mqtt_integration
    
    if mqtt_integration is None:
        mqtt_integration = MQTTIntegration(host=host, port=port)
        success = mqtt_integration.connect()
        
        if success:
            # Stocker l'intégration dans le session state pour qu'elle soit accessible partout
            if 'mqtt_integration' not in st.session_state:
                st.session_state['mqtt_integration'] = mqtt_integration
            
            logging.info("Intégration MQTT initialisée et connectée")
            return mqtt_integration
        else:
            logging.error("Échec de l'initialisation de l'intégration MQTT")
            return None
    
    return mqtt_integration

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