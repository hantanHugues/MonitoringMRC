
# MediMat Monitor - Système de Monitoring de Matelas Médicaux

## 📋 Description

MediMat Monitor est une application web sophistiquée de surveillance en temps réel pour matelas médicaux intelligents. Développée avec Streamlit et Python, elle offre une interface intuitive pour le monitoring de patients en milieu hospitalier, particulièrement adaptée aux services de néphrologie.

### 🎯 Fonctionnalités Principales

- **Surveillance Multi-Capteurs en Temps Réel**
  - Température corporelle
  - Humidité
  - Débit urinaire
  - Pouls
  - Niveau de créatine
  
- **Interface Multi-Vues**
  - Dashboard principal
  - Vue par matelas
  - Détails des capteurs
  - Configuration système
  - Maintenance
  - Journaux et alertes

- **Gestion Avancée des Données**
  - Visualisation en temps réel
  - Historique des mesures
  - Analyse des tendances
  - Export de données

## 🛠 Architecture Technique

### Technologies Utilisées
- **Backend**: Python
- **Frontend**: Streamlit
- **Communication**: MQTT
- **Visualisation**: Plotly
- **Base de données**: Intégration flexible avec systèmes externes

### Composants Clés
- **Simulateur Direct**: Génération de données de test réalistes
- **Client MQTT**: Communication bidirectionnelle avec les capteurs
- **Système d'Alertes**: Monitoring proactif des anomalies
- **Internationalisation**: Support multilingue (FR/EN)

## 🚀 Installation et Démarrage

1. **Prérequis**
```bash
Python 3.11+
Streamlit
Paho-MQTT
Plotly
Pandas
```

2. **Installation des dépendances**
```bash
pip install streamlit paho-mqtt plotly pandas
```

3. **Démarrage de l'application**
```bash
streamlit run app.py
```

## 📊 Structure du Projet

```
├── app.py                 # Point d'entrée principal
├── pages/                 # Vues de l'application
│   ├── Sensor_Dashboard.py
│   ├── Mattress_View.py
│   ├── Sensor_Details.py
│   ├── Configuration.py
│   ├── Maintenance.py
│   └── Alerts_Logs.py
└── utils/                 # Utilitaires et services
    ├── mqtt_client.py
    ├── direct_simulator.py
    ├── data_manager.py
    └── visualization.py
```

## 🔧 Configuration

L'application supporte deux modes de fonctionnement :

1. **Mode Simulateur Direct**
   - Génération de données de test en local
   - Parfait pour le développement et les démonstrations

2. **Mode MQTT**
   - Connection à un broker MQTT externe
   - Configuration via l'interface utilisateur
   - Support des credentials sécurisés

## 📱 Fonctionnalités Détaillées

### Dashboard Principal
- Vue d'ensemble des capteurs
- Statistiques en temps réel
- Distribution des statuts
- Filtres dynamiques

### Vue Matelas
- Visualisation 3D des emplacements des capteurs
- Données en temps réel par capteur
- État du patient
- Historique des mesures

### Maintenance
- Planification des interventions
- Historique des maintenances
- Calibration des capteurs
- Mises à jour firmware

### Alertes et Logs
- Système d'alertes temps réel
- Historique des événements
- Configuration des seuils
- Notifications paramétrables

## 🔐 Sécurité

- Support SSL/TLS pour MQTT
- Authentification sécurisée
- Validation des données
- Logging sécurisé

## 🌐 Internationalisation

Support complet de :
- Français
- Anglais

## 📈 Performance

- Interface réactive
- Mise à jour en temps réel
- Optimisation des requêtes
- Cache intelligent

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 License

Copyright © 2024 MediMat Monitor

## 👥 Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur le dépôt.
