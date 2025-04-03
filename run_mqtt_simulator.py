"""
Script pour lancer le simulateur MQTT
Ce script lance le simulateur de capteurs MQTT en tâche de fond
"""

import subprocess
import sys
import time
import signal
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_simulator():
    """
    Lance le simulateur MQTT en arrière-plan
    """
    try:
        # Lance le simulateur dans un processus séparé
        logger.info("Démarrage du simulateur MQTT...")
        process = subprocess.Popen([sys.executable, "mqtt_sensor_simulator.py"], 
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        
        logger.info(f"Simulateur MQTT démarré avec PID {process.pid}")
        
        # Stocke le PID pour pouvoir arrêter le simulateur plus tard
        with open(".mqtt_simulator_pid", "w") as f:
            f.write(str(process.pid))
        
        # Affiche un message d'aide
        print("\n")
        print("=" * 80)
        print("Simulateur MQTT démarré avec succès!")
        print("Il envoie des données pour les capteurs du matelas MAT-101")
        print("Pour l'arrêter, utilisez Ctrl+C ou exécutez 'python stop_mqtt_simulator.py'")
        print("=" * 80)
        print("\n")
        
        # Boucle pour garder le script en vie et afficher les logs du simulateur
        while True:
            # Récupère la sortie du processus
            output = process.stdout.readline()
            if output:
                print(output.decode().strip())
            
            # Vérifie si le processus est toujours en vie
            if process.poll() is not None:
                logger.error("Le simulateur s'est arrêté de façon inattendue")
                break
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        logger.info("Arrêt du simulateur demandé par l'utilisateur...")
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        logger.info("Simulateur MQTT arrêté")
    
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du simulateur: {e}")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            process.wait(timeout=5)

def signal_handler(sig, frame):
    """Gère l'arrêt propre du script avec Ctrl+C"""
    logger.info("Signal d'arrêt reçu...")
    # Arrête le simulateur s'il est en cours d'exécution
    try:
        with open(".mqtt_simulator_pid", "r") as f:
            pid = int(f.read().strip())
        
        logger.info(f"Arrêt du simulateur (PID: {pid})...")
        os.kill(pid, signal.SIGTERM)
        logger.info("Simulateur MQTT arrêté")
    except FileNotFoundError:
        logger.warning("Impossible de trouver le PID du simulateur")
    except ProcessLookupError:
        logger.warning("Le processus du simulateur n'existe plus")
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt du simulateur: {e}")
    
    sys.exit(0)

if __name__ == "__main__":
    # Enregistre le gestionnaire de signal pour Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    run_simulator()