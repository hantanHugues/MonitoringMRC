"""
Simulateur direct pour générer des données de capteurs sans passer par MQTT
Ce module simule des données de capteurs en temps réel directement dans l'application Streamlit
"""

import random
import time
import json
import logging
import threading
from datetime import datetime
import streamlit as st

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectSimulator:
    """
    Simulateur direct de capteurs sans passer par MQTT
    Cette classe simule des capteurs de matelas médicaux et génère des données
    comme si elles venaient d'un broker MQTT
    """
    def __init__(self):
        """Initialise le simulateur de capteurs direct"""
        self.mattress_id = "MAT-101"  # Matelas 1 (celui qui simule les données MQTT)
        self.latest_data = {}
        self.running = False
        self.thread = None
        
        # Paramètres des capteurs
        self.sensor_types = {
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
        
        logger.info("Simulateur direct initialisé")
    
    def generate_sensor_value(self, sensor_id):
        """Génère une valeur de capteur aléatoire basée sur la configuration du capteur"""
        sensor_config = self.sensor_types[sensor_id]
        
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
    
    def create_sensor_payload(self, sensor_id, value):
        """Crée la charge utile comme si elle venait de MQTT"""
        sensor_config = self.sensor_types[sensor_id]
        
        return {
            "mattress_id": self.mattress_id,
            "sensor_id": sensor_id,
            "type": sensor_config["type"],
            "value": value,
            "unit": sensor_config["unit"],
            "timestamp": datetime.now().isoformat()
        }
    
    def simulate_sensors(self):
        """Simule les capteurs et stocke les données"""
        logger.info(f"Démarrage de la simulation pour {len(self.sensor_types)} capteurs sur le matelas {self.mattress_id}")
        
        last_update = {sensor_id: 0 for sensor_id in self.sensor_types}
        
        try:
            while self.running:
                current_time = time.time()
                
                for sensor_id, sensor_config in self.sensor_types.items():
                    # Vérifier si c'est le moment de mettre à jour ce capteur
                    if current_time - last_update[sensor_id] >= sensor_config["frequency"]:
                        # Générer et stocker une nouvelle valeur
                        value = self.generate_sensor_value(sensor_id)
                        payload = self.create_sensor_payload(sensor_id, value)
                        
                        # Construire le topic MQTT comme si ça venait d'un broker
                        topic = f"hospital/mattress/{self.mattress_id}/{sensor_id}"
                        
                        # Stocker les données
                        if sensor_id not in self.latest_data:
                            self.latest_data[sensor_id] = {}
                        
                        self.latest_data[sensor_id] = {
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'type': sensor_config["type"],
                            'value': value,
                            'topic': topic,
                            'mattress_id': self.mattress_id
                        }
                        
                        logger.info(f"Simulé: {topic} = {value} {sensor_config['unit']}")
                        
                        # Mettre à jour le timestamp
                        last_update[sensor_id] = current_time
                
                # Attendre un peu pour ne pas surcharger le système
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Erreur lors de la simulation: {e}")
        finally:
            logger.info("Simulation terminée")
    
    def start(self):
        """Démarre la simulation dans un thread séparé"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.simulate_sensors)
            self.thread.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête
            self.thread.start()
            logger.info("Thread de simulation démarré")
    
    def stop(self):
        """Arrête la simulation"""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=2)
            logger.info("Simulation arrêtée")
    
    def get_latest_data(self, sensor_id=None):
        """
        Retourne les dernières données simulées
        
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

# Création d'une instance globale pour le simulateur
direct_simulator = None

def initialize_direct_simulator():
    """
    Initialise le simulateur direct
    """
    global direct_simulator
    
    if direct_simulator is None:
        direct_simulator = DirectSimulator()
        direct_simulator.start()
        
        # Stocker le simulateur dans le session state pour qu'il soit accessible partout
        if 'direct_simulator' not in st.session_state:
            st.session_state['direct_simulator'] = direct_simulator
        
        logger.info("Simulateur direct initialisé et démarré")
        return direct_simulator
    
    return direct_simulator

def get_direct_simulator():
    """
    Retourne l'instance du simulateur direct
    """
    global direct_simulator
    
    # Si déjà dans session_state, utiliser celle-là
    if 'direct_simulator' in st.session_state:
        return st.session_state['direct_simulator']
    
    # Sinon, initialiser une nouvelle instance
    return initialize_direct_simulator()