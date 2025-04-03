"""
Script pour arrêter le simulateur MQTT
Ce script arrête le simulateur de capteurs MQTT lancé en tâche de fond
"""

import os
import signal
import logging
import sys

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def stop_simulator():
    """
    Arrête le simulateur MQTT en cours d'exécution
    """
    try:
        # Vérifie si le fichier PID existe
        if not os.path.exists(".mqtt_simulator_pid"):
            logger.error("Impossible de trouver le fichier PID du simulateur")
            print("Le simulateur MQTT ne semble pas être en cours d'exécution.")
            return False
        
        # Lit le PID du fichier
        with open(".mqtt_simulator_pid", "r") as f:
            pid = int(f.read().strip())
        
        # Envoie un signal SIGTERM au processus
        logger.info(f"Arrêt du simulateur (PID: {pid})...")
        os.kill(pid, signal.SIGTERM)
        
        # Supprime le fichier PID
        os.remove(".mqtt_simulator_pid")
        
        logger.info("Simulateur MQTT arrêté avec succès")
        print("Simulateur MQTT arrêté avec succès!")
        return True
    
    except FileNotFoundError:
        logger.error("Impossible de trouver le fichier PID du simulateur")
        print("Le simulateur MQTT ne semble pas être en cours d'exécution.")
        return False
    
    except ProcessLookupError:
        logger.warning("Le processus du simulateur n'existe plus")
        # Supprime le fichier PID s'il existe encore
        if os.path.exists(".mqtt_simulator_pid"):
            os.remove(".mqtt_simulator_pid")
        print("Le simulateur MQTT n'était plus en cours d'exécution.")
        return False
    
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt du simulateur: {e}")
        print(f"Erreur lors de l'arrêt du simulateur: {e}")
        return False

if __name__ == "__main__":
    stop_simulator()