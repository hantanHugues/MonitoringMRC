import paho.mqtt.client as mqtt
import json
import time
import threading
import logging
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
        # Par défaut, on écoute les topics standard pour notre système
        self.topics = topics or [
            "capteur/temperature",
            "capteur/humidite",
            "capteur/debit_urinaire",
            "capteur/poul",
            "capteur/creatine"
        ]
        
        # Map du type de capteur vers le type dans notre système
        self.sensor_type_map = {
            "temperature": "temperature",
            "humidite": "humidity",
            "debit_urinaire": "pressure",
            "poul": "movement",
            "creatine": "movement"
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
            
            # Mapper les capteurs aux IDs de notre système
            sensor_map = {
                "capteur/temperature": "SEN-202",     # Capteur de température -> SEN-202
                "capteur/humidite": "SEN-203",        # Capteur d'humidité -> SEN-203  
                "capteur/debit_urinaire": "SEN-201",  # Capteur de débit urinaire -> SEN-201 (pression)
                "capteur/poul": "SEN-204",            # Capteur de pouls -> SEN-204 (mouvement)
                "capteur/creatine": "SEN-205"         # Capteur de créatine -> SEN-205 (autre mouvement)
            }
            
            # Extraire le type de capteur du topic
            topic = msg.topic
            
            # Affecter un ID de capteur basé sur le topic
            sensor_id = sensor_map.get(topic)
            if not sensor_id:
                self.logger.warning(f"Topic non reconnu: {topic}")
                return
                
            # Tous les capteurs appartiennent au matelas 1
            mattress_id = "MAT-101"
            
            # Déterminer le type de capteur basé sur le topic
            sensor_type_from_topic = topic.split('/')[1]  # Exemple: 'capteur/temperature' -> 'temperature'
            
            try:
                # Tenter de décoder le payload JSON
                payload = json.loads(msg.payload.decode())
                value = payload.get("valeur")
                esp32_id = payload.get("esp32_id")
                timestamp = payload.get("timestamp")
            except (json.JSONDecodeError, AttributeError):
                # Si ce n'est pas du JSON, essayer de traiter comme une valeur brute
                try:
                    value = float(msg.payload.decode().strip())
                    esp32_id = None
                    timestamp = None
                except ValueError:
                    self.logger.warning(f"Impossible de parser le payload: {msg.payload}")
                    return
            
            # Mapping du type de capteur
            mapped_type = self.sensor_type_map.get(sensor_type_from_topic, sensor_type_from_topic)
            
            # Stocker les données
            if sensor_id not in self.latest_data:
                self.latest_data[sensor_id] = {}
            
            self.latest_data[sensor_id] = {
                'timestamp': timestamp or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': mapped_type,
                'value': value,
                'topic': topic,
                'mattress_id': mattress_id,
                'esp32_id': esp32_id
            }
            
            self.logger.info(f"Données mises à jour pour le capteur {sensor_id} du matelas {mattress_id}: {value} ({mapped_type})")
                
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