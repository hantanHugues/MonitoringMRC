# Translation module for multi-language support

def get_languages():
    """
    Returns a dictionary of available languages
    """
    return {
        'en': 'English',
        'fr': 'Français'
    }

def get_translation(key, language='en'):
    """
    Returns the translation for a given key in the specified language
    
    Parameters:
    - key: Translation key
    - language: Language code ('en' or 'fr')
    
    Returns:
    - Translated string or the key itself if translation not found
    """
    translations = {
        # Main titles and common elements
        'main_title': {
            'en': 'Medical Mattress Monitoring System',
            'fr': 'Système de Surveillance des Matelas Médicaux'
        },
        'main_subtitle': {
            'en': 'Real-time monitoring of sensors for patients with chronic kidney disease',
            'fr': 'Surveillance en temps réel des capteurs pour patients atteints de maladie rénale chronique'
        },
        'version': {
            'en': 'Version',
            'fr': 'Version'
        },
        
        # Dashboard metrics
        'total_mattresses': {
            'en': 'Total Mattresses',
            'fr': 'Total des Matelas'
        },
        'active_sensors': {
            'en': 'Active Sensors',
            'fr': 'Capteurs Actifs'
        },
        'active_alerts': {
            'en': 'Active Alerts',
            'fr': 'Alertes Actives'
        },
        'critical_alerts': {
            'en': 'Critical Alerts',
            'fr': 'Alertes Critiques'
        },
        'alerts_help': {
            'en': 'Number of active alerts that require attention',
            'fr': 'Nombre d\'alertes actives nécessitant une attention'
        },
        'critical_alerts_help': {
            'en': 'Number of critical alerts that require immediate attention',
            'fr': 'Nombre d\'alertes critiques nécessitant une attention immédiate'
        },
        
        # Sensor statuses
        'status_active': {
            'en': 'Active',
            'fr': 'Actif'
        },
        'status_inactive': {
            'en': 'Inactive',
            'fr': 'Inactif'
        },
        'status_maintenance': {
            'en': 'Maintenance',
            'fr': 'Maintenance'
        },
        'status_error': {
            'en': 'Error',
            'fr': 'Erreur'
        },
        
        # Dashboard sections
        'sensor_status_overview': {
            'en': 'Sensor Status Overview',
            'fr': 'Aperçu du Statut des Capteurs'
        },
        'alert_summary': {
            'en': 'Alert Summary',
            'fr': 'Résumé des Alertes'
        },
        'system_health': {
            'en': 'System Health',
            'fr': 'État du Système'
        },
        'recent_activity': {
            'en': 'Recent Activity',
            'fr': 'Activité Récente'
        },
        'quick_access': {
            'en': 'Quick Access to Mattresses',
            'fr': 'Accès Rapide aux Matelas'
        },
        
        # Sample activities for dashboard
        'activity_1': {
            'en': 'Sensor SEN-201 signal weak',
            'fr': 'Signal faible du capteur SEN-201'
        },
        'activity_2': {
            'en': 'Maintenance completed on MAT-103',
            'fr': 'Maintenance terminée sur MAT-103'
        },
        'activity_3': {
            'en': 'Firmware updated for temperature sensors',
            'fr': 'Firmware mis à jour pour les capteurs de température'
        },
        'activity_4': {
            'en': 'Calibration needed for pressure sensor SEN-204',
            'fr': 'Calibration nécessaire pour le capteur de pression SEN-204'
        },
        'activity_5': {
            'en': 'New mattress MAT-105 registered',
            'fr': 'Nouveau matelas MAT-105 enregistré'
        },
        
        # System health metrics
        'power_status': {
            'en': 'Power Status',
            'fr': 'État d\'Alimentation'
        },
        'power_status_ok': {
            'en': 'Connected to power supply',
            'fr': 'Connecté à l\'alimentation'
        },
        'power_status_disconnected': {
            'en': 'Disconnected from power supply',
            'fr': 'Déconnecté de l\'alimentation'
        },
        'avg_signal_strength': {
            'en': 'Average Signal Strength',
            'fr': 'Force du Signal Moyenne'
        },
        
        # Buttons and actions
        'view_details': {
            'en': 'View Details',
            'fr': 'Voir Détails'
        },
        'refresh_data': {
            'en': 'Refresh Data',
            'fr': 'Actualiser les Données'
        },
        'last_update': {
            'en': 'Last update',
            'fr': 'Dernière mise à jour'
        },
        
        # Alerts and notifications
        'no_active_alerts': {
            'en': 'No active alerts',
            'fr': 'Aucune alerte active'
        },
        
        # Sensor Dashboard Page
        'sensor_dashboard_title': {
            'en': 'Sensor Dashboard',
            'fr': 'Tableau de Bord des Capteurs'
        },
        'sensor_dashboard_description': {
            'en': 'Overview and management of all sensors in the system',
            'fr': 'Vue d\'ensemble et gestion de tous les capteurs du système'
        },
        'filters': {
            'en': 'Filters',
            'fr': 'Filtres'
        },
        'filter_by_type': {
            'en': 'Filter by Type',
            'fr': 'Filtrer par Type'
        },
        'filter_by_status': {
            'en': 'Filter by Status',
            'fr': 'Filtrer par Statut'
        },
# Removed battery filter as sensors are plugged in, not battery-powered
        'sensor_overview': {
            'en': 'Sensor Overview',
            'fr': 'Aperçu des Capteurs'
        },
        'total_filtered_sensors': {
            'en': 'Total Filtered Sensors',
            'fr': 'Total des Capteurs Filtrés'
        },
        'error_sensors': {
            'en': 'Error Sensors',
            'fr': 'Capteurs en Erreur'
        },
        'sensors_in_error_state': {
            'en': 'Sensors currently in error state',
            'fr': 'Capteurs actuellement en état d\'erreur'
        },
        'power_status': {
            'en': 'Power Status',
            'fr': 'État d\'Alimentation'
        },
        'no_sensors_match_criteria': {
            'en': 'No sensors match the selected criteria',
            'fr': 'Aucun capteur ne correspond aux critères sélectionnés'
        },
        'sensor_types_distribution': {
            'en': 'Sensor Types Distribution',
            'fr': 'Répartition des Types de Capteurs'
        },
        'signal_strength': {
            'en': 'Signal Strength',
            'fr': 'Force du Signal'
        },
        'avg_signal_by_type': {
            'en': 'Average Signal Strength by Sensor Type',
            'fr': 'Force du Signal Moyenne par Type de Capteur'
        },
        'sensor_type': {
            'en': 'Sensor Type',
            'fr': 'Type de Capteur'
        },
        'sensors_list': {
            'en': 'Sensors List',
            'fr': 'Liste des Capteurs'
        },
        'download_csv': {
            'en': 'Download CSV',
            'fr': 'Télécharger CSV'
        },
        
        # Mattress View Page
        'mattress_view_title': {
            'en': 'Mattress View',
            'fr': 'Vue des Matelas'
        },
        'mattress_view_description': {
            'en': 'View and manage mattresses and their assigned sensors',
            'fr': 'Afficher et gérer les matelas et leurs capteurs assignés'
        },
        'select_mattress': {
            'en': 'Select Mattress',
            'fr': 'Sélectionner un Matelas'
        },
        'select_mattress_prompt': {
            'en': 'Select a mattress to view',
            'fr': 'Sélectionner un matelas à afficher'
        },
        'mattress_details': {
            'en': 'Mattress Details',
            'fr': 'Détails du Matelas'
        },
        'status': {
            'en': 'Status',
            'fr': 'Statut'
        },
        'patient_id': {
            'en': 'Patient ID',
            'fr': 'ID Patient'
        },
        'location': {
            'en': 'Location',
            'fr': 'Emplacement'
        },
        'installation_date': {
            'en': 'Installation Date',
            'fr': 'Date d\'Installation'
        },
        'last_maintenance': {
            'en': 'Last Maintenance',
            'fr': 'Dernière Maintenance'
        },
        'mattress_visualization': {
            'en': 'Mattress Visualization',
            'fr': 'Visualisation du Matelas'
        },
        'sensor_placement_on': {
            'en': 'Sensor Placement on',
            'fr': 'Placement des Capteurs sur'
        },
        'status_legend': {
            'en': 'Status Legend',
            'fr': 'Légende des Statuts'
        },
        'sensors_on_mattress': {
            'en': 'Sensors on this Mattress',
            'fr': 'Capteurs sur ce Matelas'
        },
        'power_connection': {
            'en': 'Power Connection',
            'fr': 'Connexion d\'Alimentation'
        },
        'firmware_version': {
            'en': 'Firmware Version',
            'fr': 'Version du Firmware'
        },
        'view_data': {
            'en': 'View Data',
            'fr': 'Voir les Données'
        },
        'calibrate': {
            'en': 'Calibrate',
            'fr': 'Calibrer'
        },
        'restart': {
            'en': 'Restart',
            'fr': 'Redémarrer'
        },
        'no_sensors_on_mattress': {
            'en': 'No sensors assigned to this mattress',
            'fr': 'Aucun capteur assigné à ce matelas'
        },
        'patient_information': {
            'en': 'Patient Information',
            'fr': 'Informations Patient'
        },
        'connect_to_hospital_system': {
            'en': 'Connect to Hospital Patient System for details',
            'fr': 'Connectez-vous au Système Patient de l\'Hôpital pour les détails'
        },
        'treatment': {
            'en': 'Treatment',
            'fr': 'Traitement'
        },
        'hemodialysis': {
            'en': 'Hemodialysis',
            'fr': 'Hémodialyse'
        },
        'attending_physician': {
            'en': 'Attending Physician',
            'fr': 'Médecin Traitant'
        },
        'refer_to_hospital_system': {
            'en': 'Refer to hospital system',
            'fr': 'Se référer au système hospitalier'
        },
        'connect_to_patient_records': {
            'en': 'Connect to Patient Records',
            'fr': 'Connecter aux Dossiers Patients'
        },
        
        # Sensor Details Page
        'sensor_details_title': {
            'en': 'Sensor Details',
            'fr': 'Détails du Capteur'
        },
        'sensor_details_description': {
            'en': 'Detailed view and management of individual sensors',
            'fr': 'Vue détaillée et gestion des capteurs individuels'
        },
        'select_sensor': {
            'en': 'Select Sensor',
            'fr': 'Sélectionner un Capteur'
        },
        'select_sensor_prompt': {
            'en': 'Select a sensor to view details',
            'fr': 'Sélectionner un capteur pour voir les détails'
        },
        'time_range': {
            'en': 'Time Range',
            'fr': 'Plage de Temps'
        },
        'select_time_range': {
            'en': 'Select time range for data',
            'fr': 'Sélectionner la plage de temps pour les données'
        },
        'sensor_details': {
            'en': 'Sensor Details',
            'fr': 'Détails du Capteur'
        },
        'mattress_id': {
            'en': 'Mattress ID',
            'fr': 'ID Matelas'
        },
        'historical_data': {
            'en': 'Historical Data',
            'fr': 'Données Historiques'
        },
        'historical_readings': {
            'en': 'Historical Readings',
            'fr': 'Lectures Historiques'
        },
        'statistics_for_period': {
            'en': 'Statistics for Selected Period',
            'fr': 'Statistiques pour la Période Sélectionnée'
        },
        'min_value': {
            'en': 'Minimum Value',
            'fr': 'Valeur Minimale'
        },
        'max_value': {
            'en': 'Maximum Value',
            'fr': 'Valeur Maximale'
        },
        'avg_value': {
            'en': 'Average Value',
            'fr': 'Valeur Moyenne'
        },
        'std_dev': {
            'en': 'Standard Deviation',
            'fr': 'Écart Type'
        },
        'no_historical_data_available': {
            'en': 'No historical data available for this sensor',
            'fr': 'Aucune donnée historique disponible pour ce capteur'
        },
        'current_readings': {
            'en': 'Current Readings',
            'fr': 'Lectures Actuelles'
        },
        'current': {
            'en': 'Current',
            'fr': 'Actuel'
        },
        'reading': {
            'en': 'Reading',
            'fr': 'Lecture'
        },
        'sensor_actions': {
            'en': 'Sensor Actions',
            'fr': 'Actions du Capteur'
        },
        'test_sensor': {
            'en': 'Test Sensor',
            'fr': 'Tester le Capteur'
        },
        'calibrate_sensor': {
            'en': 'Calibrate Sensor',
            'fr': 'Calibrer le Capteur'
        },
        'restart_sensor': {
            'en': 'Restart Sensor',
            'fr': 'Redémarrer le Capteur'
        },
        'update_firmware': {
            'en': 'Update Firmware',
            'fr': 'Mettre à Jour le Firmware'
        },
        'export_data': {
            'en': 'Export Data',
            'fr': 'Exporter les Données'
        },
        'maintenance_history': {
            'en': 'Maintenance History',
            'fr': 'Historique de Maintenance'
        },
        'firmware_update': {
            'en': 'Firmware Update',
            'fr': 'Mise à Jour du Firmware'
        },
        'calibration': {
            'en': 'Calibration',
            'fr': 'Calibration'
        },
        'maintenance_check': {
            'en': 'Maintenance Check',
            'fr': 'Vérification de Maintenance'
        },
        'regular_update': {
            'en': 'Regular update to latest version',
            'fr': 'Mise à jour régulière vers la dernière version'
        },
        'scheduled_calibration': {
            'en': 'Scheduled calibration procedure',
            'fr': 'Procédure de calibration planifiée'
        },
        'preventive_maintenance': {
            'en': 'Preventive maintenance',
            'fr': 'Maintenance préventive'
        },
        'date': {
            'en': 'Date',
            'fr': 'Date'
        },
        'maintenance_type': {
            'en': 'Maintenance Type',
            'fr': 'Type de Maintenance'
        },
        'technician': {
            'en': 'Technician',
            'fr': 'Technicien'
        },
        'notes': {
            'en': 'Notes',
            'fr': 'Notes'
        },
        
        # Configuration Page
        'configuration_title': {
            'en': 'Configuration',
            'fr': 'Configuration'
        },
        'configuration_description': {
            'en': 'Configure sensors, alerts, and system settings',
            'fr': 'Configurer les capteurs, les alertes et les paramètres système'
        },
        'configuration_categories': {
            'en': 'Configuration Categories',
            'fr': 'Catégories de Configuration'
        },
        'select_config_area': {
            'en': 'Select Configuration Area',
            'fr': 'Sélectionner la Zone de Configuration'
        },
        'sensor_parameters': {
            'en': 'Sensor Parameters',
            'fr': 'Paramètres des Capteurs'
        },
        'alert_thresholds': {
            'en': 'Alert Thresholds',
            'fr': 'Seuils d\'Alerte'
        },
        'mattress_sensor_assignment': {
            'en': 'Mattress-Sensor Assignment',
            'fr': 'Attribution Matelas-Capteur'
        },
        'system_settings': {
            'en': 'System Settings',
            'fr': 'Paramètres Système'
        },
        'select_sensor_type': {
            'en': 'Select Sensor Type',
            'fr': 'Sélectionner le Type de Capteur'
        },
        'configure': {
            'en': 'Configure',
            'fr': 'Configurer'
        },
        'sensors': {
            'en': 'Sensors',
            'fr': 'Capteurs'
        },
        'set_parameters_for_all': {
            'en': 'Set parameters for all',
            'fr': 'Définir les paramètres pour tous les'
        },
        'sampling_frequency': {
            'en': 'Sampling Frequency',
            'fr': 'Fréquence d\'Échantillonnage'
        },
        'seconds_between_readings': {
            'en': 'Seconds between readings',
            'fr': 'Secondes entre les lectures'
        },
        'min_pressure_threshold': {
            'en': 'Minimum Pressure Threshold',
            'fr': 'Seuil de Pression Minimum'
        },
        'minimum_pressure_mmhg': {
            'en': 'Minimum pressure in mmHg',
            'fr': 'Pression minimale en mmHg'
        },
        'max_pressure_threshold': {
            'en': 'Maximum Pressure Threshold',
            'fr': 'Seuil de Pression Maximum'
        },
        'maximum_pressure_mmhg': {
            'en': 'Maximum pressure in mmHg',
            'fr': 'Pression maximale en mmHg'
        },
        'sensitivity': {
            'en': 'Sensitivity',
            'fr': 'Sensibilité'
        },
        'sensitivity_help': {
            'en': 'Sensor sensitivity level',
            'fr': 'Niveau de sensibilité du capteur'
        },
        'min_temperature_threshold': {
            'en': 'Minimum Temperature Threshold',
            'fr': 'Seuil de Température Minimum'
        },
        'minimum_temp_celsius': {
            'en': 'Minimum temperature in °C',
            'fr': 'Température minimale en °C'
        },
        'max_temperature_threshold': {
            'en': 'Maximum Temperature Threshold',
            'fr': 'Seuil de Température Maximum'
        },
        'maximum_temp_celsius': {
            'en': 'Maximum temperature in °C',
            'fr': 'Température maximale en °C'
        },
        'min_humidity_threshold': {
            'en': 'Minimum Humidity Threshold',
            'fr': 'Seuil d\'Humidité Minimum'
        },
        'minimum_humidity_percent': {
            'en': 'Minimum humidity in %',
            'fr': 'Humidité minimale en %'
        },
        'max_humidity_threshold': {
            'en': 'Maximum Humidity Threshold',
            'fr': 'Seuil d\'Humidité Maximum'
        },
        'maximum_humidity_percent': {
            'en': 'Maximum humidity in %',
            'fr': 'Humidité maximale en %'
        },
        'movement_detection_threshold': {
            'en': 'Movement Detection Threshold',
            'fr': 'Seuil de Détection de Mouvement'
        },
        'movement_threshold_help': {
            'en': 'Minimum intensity to detect movement (1-10)',
            'fr': 'Intensité minimale pour détecter un mouvement (1-10)'
        },
        'movement_duration_threshold': {
            'en': 'Movement Duration Threshold',
            'fr': 'Seuil de Durée de Mouvement'
        },
        'movement_duration_help': {
            'en': 'Minimum duration in seconds to register movement',
            'fr': 'Durée minimale en secondes pour enregistrer un mouvement'
        },
        'power_mode': {
            'en': 'Power Mode',
            'fr': 'Mode d\'Alimentation'
        },
        'normal': {
            'en': 'Normal',
            'fr': 'Normal'
        },
        'power_saving': {
            'en': 'Power Saving',
            'fr': 'Économie d\'Énergie'
        },
        'high_precision': {
            'en': 'High Precision',
            'fr': 'Haute Précision'
        },
        'power_mode_help': {
            'en': 'Select power usage mode (affects battery life)',
            'fr': 'Sélectionner le mode d\'utilisation d\'énergie (affecte la durée de vie de la batterie)'
        },
        'apply_settings_to': {
            'en': 'Apply Settings To',
            'fr': 'Appliquer les Paramètres À'
        },
        'all_sensors_of_type': {
            'en': 'All Sensors of This Type',
            'fr': 'Tous les Capteurs de Ce Type'
        },
        'selected_sensors_only': {
            'en': 'Selected Sensors Only',
            'fr': 'Capteurs Sélectionnés Uniquement'
        },
        'select_specific_sensors': {
            'en': 'Select Specific Sensors',
            'fr': 'Sélectionner des Capteurs Spécifiques'
        },
        'apply_configuration': {
            'en': 'Apply Configuration',
            'fr': 'Appliquer la Configuration'
        },
        'configuration_applied_to': {
            'en': 'Configuration applied to',
            'fr': 'Configuration appliquée à'
        },
        'alert_priority_settings': {
            'en': 'Alert Priority Settings',
            'fr': 'Paramètres de Priorité d\'Alerte'
        },
        'battery_level_thresholds': {
            'en': 'Battery Level Thresholds',
            'fr': 'Seuils de Niveau de Batterie'
        },
        'battery_warning_threshold': {
            'en': 'Battery Warning Threshold',
            'fr': 'Seuil d\'Avertissement de Batterie'
        },
        'battery_warning_help': {
            'en': 'Battery level percentage that triggers a warning alert',
            'fr': 'Pourcentage de niveau de batterie qui déclenche une alerte d\'avertissement'
        },
        'battery_critical_threshold': {
            'en': 'Battery Critical Threshold',
            'fr': 'Seuil Critique de Batterie'
        },
        'battery_critical_help': {
            'en': 'Battery level percentage that triggers a critical alert',
            'fr': 'Pourcentage de niveau de batterie qui déclenche une alerte critique'
        },
        'signal_strength_thresholds': {
            'en': 'Signal Strength Thresholds',
            'fr': 'Seuils de Force du Signal'
        },
        'signal_warning_threshold': {
            'en': 'Signal Warning Threshold',
            'fr': 'Seuil d\'Avertissement du Signal'
        },
        'signal_warning_help': {
            'en': 'Signal strength level that triggers a warning alert (1-10)',
            'fr': 'Niveau de force du signal qui déclenche une alerte d\'avertissement (1-10)'
        },
        'signal_critical_threshold': {
            'en': 'Signal Critical Threshold',
            'fr': 'Seuil Critique du Signal'
        },
        'signal_critical_help': {
            'en': 'Signal strength level that triggers a critical alert (1-10)',
            'fr': 'Niveau de force du signal qui déclenche une alerte critique (1-10)'
        },
        'data_age_thresholds': {
            'en': 'Data Age Thresholds',
            'fr': 'Seuils d\'Âge des Données'
        },
        'data_age_warning_min': {
            'en': 'Data Age Warning (minutes)',
            'fr': 'Avertissement d\'Âge des Données (minutes)'
        },
        'data_age_warning_help': {
            'en': 'Age of data in minutes that triggers a warning alert',
            'fr': 'Âge des données en minutes qui déclenche une alerte d\'avertissement'
        },
        'data_age_critical_min': {
            'en': 'Data Age Critical (minutes)',
            'fr': 'Âge Critique des Données (minutes)'
        },
        'data_age_critical_help': {
            'en': 'Age of data in minutes that triggers a critical alert',
            'fr': 'Âge des données en minutes qui déclenche une alerte critique'
        },
        'alert_notifications': {
            'en': 'Alert Notifications',
            'fr': 'Notifications d\'Alerte'
        },
        'enable_email_alerts': {
            'en': 'Enable Email Alerts',
            'fr': 'Activer les Alertes par Email'
        },
        'email_recipients': {
            'en': 'Email Recipients',
            'fr': 'Destinataires Email'
        },
        'email_recipients_help': {
            'en': 'Comma-separated list of email addresses',
            'fr': 'Liste d\'adresses email séparées par des virgules'
        },
        'enable_sms_alerts': {
            'en': 'Enable SMS Alerts',
            'fr': 'Activer les Alertes SMS'
        },
        'sms_recipients': {
            'en': 'SMS Recipients',
            'fr': 'Destinataires SMS'
        },
        'sms_recipients_help': {
            'en': 'Comma-separated list of phone numbers',
            'fr': 'Liste de numéros de téléphone séparés par des virgules'
        },
        'save_alert_thresholds': {
            'en': 'Save Alert Thresholds',
            'fr': 'Enregistrer les Seuils d\'Alerte'
        },
        'alert_thresholds_saved': {
            'en': 'Alert thresholds have been saved successfully',
            'fr': 'Les seuils d\'alerte ont été enregistrés avec succès'
        },
        'current_sensors_on': {
            'en': 'Current Sensors on',
            'fr': 'Capteurs Actuels sur'
        },
        'battery': {
            'en': 'Battery',
            'fr': 'Batterie'
        },
        'firmware': {
            'en': 'Firmware',
            'fr': 'Firmware'
        },
        'remove': {
            'en': 'Remove',
            'fr': 'Supprimer'
        },
        'confirm_unassign': {
            'en': 'Are you sure you want to unassign',
            'fr': 'Êtes-vous sûr de vouloir désassigner'
        },
        'yes': {
            'en': 'Yes',
            'fr': 'Oui'
        },
        'no': {
            'en': 'No',
            'fr': 'Non'
        },
        'sensor_unassigned': {
            'en': 'Sensor unassigned',
            'fr': 'Capteur désassigné'
        },
        'no_sensors_assigned': {
            'en': 'No sensors are currently assigned to this mattress',
            'fr': 'Aucun capteur n\'est actuellement assigné à ce matelas'
        },
        'assign_new_sensors_to': {
            'en': 'Assign New Sensors to',
            'fr': 'Assigner de Nouveaux Capteurs à'
        },
        'select_sensors_to_assign': {
            'en': 'Select Sensors to Assign',
            'fr': 'Sélectionner les Capteurs à Assigner'
        },
        'assign_sensors': {
            'en': 'Assign Sensors',
            'fr': 'Assigner les Capteurs'
        },
        'sensors_assigned_to': {
            'en': 'sensors assigned to',
            'fr': 'capteurs assignés à'
        },
        'no_unassigned_sensors': {
            'en': 'No unassigned sensors available',
            'fr': 'Aucun capteur non assigné disponible'
        },
        'general_settings': {
            'en': 'General Settings',
            'fr': 'Paramètres Généraux'
        },
        'data_retention_days': {
            'en': 'Data Retention (days)',
            'fr': 'Conservation des Données (jours)'
        },
        'data_retention_help': {
            'en': 'Number of days to keep historical data',
            'fr': 'Nombre de jours pour conserver les données historiques'
        },
        'maintenance_reminder_days': {
            'en': 'Maintenance Reminder (days)',
            'fr': 'Rappel de Maintenance (jours)'
        },
        'maintenance_reminder_help': {
            'en': 'Days before scheduled maintenance to send reminder',
            'fr': 'Jours avant la maintenance programmée pour envoyer un rappel'
        },
        'default_language': {
            'en': 'Default Language',
            'fr': 'Langue par Défaut'
        },
        'mqtt_settings': {
            'en': 'MQTT Settings',
            'fr': 'Paramètres MQTT'
        },
        'mqtt_broker': {
            'en': 'MQTT Broker',
            'fr': 'Broker MQTT'
        },
        'mqtt_broker_help': {
            'en': 'Hostname or IP address of the MQTT broker',
            'fr': 'Nom d\'hôte ou adresse IP du broker MQTT'
        },
        'mqtt_port': {
            'en': 'MQTT Port',
            'fr': 'Port MQTT'
        },
        'mqtt_port_help': {
            'en': 'Port number for the MQTT broker (default: 1883)',
            'fr': 'Numéro de port pour le broker MQTT (par défaut: 1883)'
        },
        'mqtt_username': {
            'en': 'MQTT Username',
            'fr': 'Nom d\'Utilisateur MQTT'
        },
        'mqtt_username_help': {
            'en': 'Username for MQTT authentication (if required)',
            'fr': 'Nom d\'utilisateur pour l\'authentification MQTT (si nécessaire)'
        },
        'mqtt_password': {
            'en': 'MQTT Password',
            'fr': 'Mot de Passe MQTT'
        },
        'mqtt_password_help': {
            'en': 'Password for MQTT authentication (if required)',
            'fr': 'Mot de passe pour l\'authentification MQTT (si nécessaire)'
        },
        'mqtt_topic_prefix': {
            'en': 'MQTT Topic Prefix',
            'fr': 'Préfixe de Sujet MQTT'
        },
        'mqtt_topic_prefix_help': {
            'en': 'Prefix for all MQTT topics',
            'fr': 'Préfixe pour tous les sujets MQTT'
        },
        'save_system_settings': {
            'en': 'Save System Settings',
            'fr': 'Enregistrer les Paramètres Système'
        },
        'system_settings_saved': {
            'en': 'System settings have been saved successfully',
            'fr': 'Les paramètres système ont été enregistrés avec succès'
        },
        'configuration_history': {
            'en': 'Configuration History',
            'fr': 'Historique de Configuration'
        },
        'no_configuration_changes': {
            'en': 'No configuration changes have been made',
            'fr': 'Aucune modification de configuration n\'a été effectuée'
        },
        'timestamp': {
            'en': 'Timestamp',
            'fr': 'Horodatage'
        },
        'change_type': {
            'en': 'Change Type',
            'fr': 'Type de Changement'
        },
        'parameters': {
            'en': 'Parameters',
            'fr': 'Paramètres'
        },
        
        # Maintenance Page
        'maintenance_title': {
            'en': 'Maintenance',
            'fr': 'Maintenance'
        },
        'maintenance_description': {
            'en': 'Schedule and track maintenance activities for sensors and mattresses',
            'fr': 'Planifier et suivre les activités de maintenance pour les capteurs et les matelas'
        },
        'maintenance_categories': {
            'en': 'Maintenance Categories',
            'fr': 'Catégories de Maintenance'
        },
        'select_maintenance_area': {
            'en': 'Select Maintenance Area',
            'fr': 'Sélectionner la Zone de Maintenance'
        },
        'maintenance_schedule': {
            'en': 'Maintenance Schedule',
            'fr': 'Calendrier de Maintenance'
        },
        'firmware_updates': {
            'en': 'Firmware Updates',
            'fr': 'Mises à Jour du Firmware'
        },
        'calibration': {
            'en': 'Calibration',
            'fr': 'Calibration'
        },
        'historical_maintenance': {
            'en': 'Historical Maintenance',
            'fr': 'Maintenance Historique'
        },
        'schedule_new_maintenance': {
            'en': 'Schedule New Maintenance',
            'fr': 'Planifier une Nouvelle Maintenance'
        },
        'select_asset_type': {
            'en': 'Select Asset Type',
            'fr': 'Sélectionner le Type d\'Actif'
        },
        'sensor': {
            'en': 'Sensor',
            'fr': 'Capteur'
        },
        'mattress': {
            'en': 'Mattress',
            'fr': 'Matelas'
        },
        'select_sensor': {
            'en': 'Select Sensor',
            'fr': 'Sélectionner un Capteur'
        },
        'maintenance_type': {
            'en': 'Maintenance Type',
            'fr': 'Type de Maintenance'
        },
        'physical_inspection': {
            'en': 'Physical Inspection',
            'fr': 'Inspection Physique'
        },
        'cleaning': {
            'en': 'Cleaning',
            'fr': 'Nettoyage'
        },
        'sensor_replacement': {
            'en': 'Sensor Replacement',
            'fr': 'Remplacement de Capteur'
        },
        'scheduled_date': {
            'en': 'Scheduled Date',
            'fr': 'Date Planifiée'
        },
        'priority': {
            'en': 'Priority',
            'fr': 'Priorité'
        },
        'low': {
            'en': 'Low',
            'fr': 'Basse'
        },
        'medium': {
            'en': 'Medium',
            'fr': 'Moyenne'
        },
        'high': {
            'en': 'High',
            'fr': 'Haute'
        },
        'critical': {
            'en': 'Critical',
            'fr': 'Critique'
        },
        'assigned_technician': {
            'en': 'Assigned Technician',
            'fr': 'Technicien Assigné'
        },
        'schedule_maintenance': {
            'en': 'Schedule Maintenance',
            'fr': 'Planifier la Maintenance'
        },
        'maintenance_scheduled_for': {
            'en': 'Maintenance scheduled for',
            'fr': 'Maintenance planifiée pour'
        },
        'on': {
            'en': 'on',
            'fr': 'le'
        },
        'upcoming_maintenance': {
            'en': 'Upcoming Maintenance',
            'fr': 'Maintenance à Venir'
        },
        'scheduled': {
            'en': 'Scheduled',
            'fr': 'Planifié'
        },
        'next_30_days_schedule': {
            'en': 'Next 30 Days Schedule',
            'fr': 'Calendrier des 30 Prochains Jours'
        },
        'upcoming_tasks_list': {
            'en': 'Upcoming Tasks List',
            'fr': 'Liste des Tâches à Venir'
        },
        'complete': {
            'en': 'Complete',
            'fr': 'Terminer'
        },
        'maintenance_marked_complete': {
            'en': 'Maintenance marked as completed',
            'fr': 'Maintenance marquée comme terminée'
        },
        'no_upcoming_maintenance': {
            'en': 'No upcoming maintenance tasks scheduled',
            'fr': 'Aucune tâche de maintenance à venir planifiée'
        },
        'no_maintenance_tasks': {
            'en': 'No maintenance tasks have been created',
            'fr': 'Aucune tâche de maintenance n\'a été créée'
        },
        'current_firmware_versions': {
            'en': 'Current Firmware Versions',
            'fr': 'Versions Actuelles du Firmware'
        },
        'firmware_versions_by_sensor_type': {
            'en': 'Firmware Versions by Sensor Type',
            'fr': 'Versions du Firmware par Type de Capteur'
        },
        'number_of_sensors': {
            'en': 'Number of Sensors',
            'fr': 'Nombre de Capteurs'
        },
        'sensors_needing_updates': {
            'en': 'Sensors Needing Updates',
            'fr': 'Capteurs Nécessitant des Mises à Jour'
        },
        'current_version': {
            'en': 'Current Version',
            'fr': 'Version Actuelle'
        },
        'latest_version': {
            'en': 'Latest Version',
            'fr': 'Dernière Version'
        },
        'update': {
            'en': 'Update',
            'fr': 'Mettre à Jour'
        },
        'confirm_firmware_update': {
            'en': 'Confirm firmware update for',
            'fr': 'Confirmer la mise à jour du firmware pour'
        },
        'update_from': {
            'en': 'Update from',
            'fr': 'Mise à jour de'
        },
        'to': {
            'en': 'to',
            'fr': 'à'
        },
        'firmware_update_started_for': {
            'en': 'Firmware update started for',
            'fr': 'Mise à jour du firmware démarrée pour'
        },
        'all_sensors_up_to_date': {
            'en': 'All sensors are up to date with the latest firmware',
            'fr': 'Tous les capteurs sont à jour avec le dernier firmware'
        },
        'firmware_update_history': {
            'en': 'Firmware Update History',
            'fr': 'Historique des Mises à Jour du Firmware'
        },
        'sensor_name': {
            'en': 'Sensor Name',
            'fr': 'Nom du Capteur'
        },
        'details': {
            'en': 'Details',
            'fr': 'Détails'
        },
        'performed_by': {
            'en': 'Performed By',
            'fr': 'Effectué Par'
        },
        'no_firmware_update_history': {
            'en': 'No firmware update history available',
            'fr': 'Aucun historique de mise à jour du firmware disponible'
        },
        'no_maintenance_history': {
            'en': 'No maintenance history available',
            'fr': 'Aucun historique de maintenance disponible'
        },
        'sensor_calibration': {
            'en': 'Sensor Calibration',
            'fr': 'Calibration des Capteurs'
        },
        'calibration_status': {
            'en': 'Calibration Status',
            'fr': 'Statut de Calibration'
        },
        'due_soon': {
            'en': 'Due Soon',
            'fr': 'À Faire Bientôt'
        },
        'overdue': {
            'en': 'Overdue',
            'fr': 'En Retard'
        },
        'ok': {
            'en': 'OK',
            'fr': 'OK'
        },
        'sensor_calibration_status': {
            'en': 'Sensor Calibration Status',
            'fr': 'Statut de Calibration des Capteurs'
        },
        'sensors_needing_calibration': {
            'en': 'Sensors Needing Calibration',
            'fr': 'Capteurs Nécessitant une Calibration'
        },
        'last_calibration': {
            'en': 'Last Calibration',
            'fr': 'Dernière Calibration'
        },
        'days_since_last': {
            'en': 'Days Since Last',
            'fr': 'Jours Depuis la Dernière'
        },
        'confirm_calibration': {
            'en': 'Confirm calibration for',
            'fr': 'Confirmer la calibration pour'
        },
        'calibration_completed_for': {
            'en': 'Calibration completed for',
            'fr': 'Calibration terminée pour'
        },
        'calibration_performed': {
            'en': 'Calibration performed',
            'fr': 'Calibration effectuée'
        },
        'all_sensors_calibrated': {
            'en': 'All sensors are properly calibrated',
            'fr': 'Tous les capteurs sont correctement calibrés'
        },
        'calibration_history': {
            'en': 'Calibration History',
            'fr': 'Historique de Calibration'
        },
        'no_calibration_history': {
            'en': 'No calibration history available',
            'fr': 'Aucun historique de calibration disponible'
        },
        'filters': {
            'en': 'Filters',
            'fr': 'Filtres'
        },
        'start_date': {
            'en': 'Start Date',
            'fr': 'Date de Début'
        },
        'end_date': {
            'en': 'End Date',
            'fr': 'Date de Fin'
        },
        'asset_type': {
            'en': 'Asset Type',
            'fr': 'Type d\'Actif'
        },
        'maintenance_activities_by_type': {
            'en': 'Maintenance Activities by Type',
            'fr': 'Activités de Maintenance par Type'
        },
        'number_of_activities': {
            'en': 'Number of Activities',
            'fr': 'Nombre d\'Activités'
        },
        'maintenance_timeline': {
            'en': 'Maintenance Timeline',
            'fr': 'Chronologie de Maintenance'
        },
        'asset': {
            'en': 'Asset',
            'fr': 'Actif'
        },
        'maintenance_details': {
            'en': 'Maintenance Details',
            'fr': 'Détails de Maintenance'
        },
        'asset_name': {
            'en': 'Asset Name',
            'fr': 'Nom de l\'Actif'
        },
        'export_maintenance_history': {
            'en': 'Export Maintenance History',
            'fr': 'Exporter l\'Historique de Maintenance'
        },
        'no_maintenance_records_for_filters': {
            'en': 'No maintenance records match the selected filters',
            'fr': 'Aucun enregistrement de maintenance ne correspond aux filtres sélectionnés'
        },
        'no_completed_maintenance_tasks': {
            'en': 'No completed maintenance tasks found',
            'fr': 'Aucune tâche de maintenance terminée trouvée'
        },
        
        # Alerts & Logs Page
        'alerts_logs_title': {
            'en': 'Alerts & Logs',
            'fr': 'Alertes et Journaux'
        },
        'alerts_logs_description': {
            'en': 'View and manage system alerts and activity logs',
            'fr': 'Afficher et gérer les alertes système et les journaux d\'activité'
        },
        'categories': {
            'en': 'Categories',
            'fr': 'Catégories'
        },
        'select_view': {
            'en': 'Select View',
            'fr': 'Sélectionner la Vue'
        },
        'active_alerts': {
            'en': 'Active Alerts',
            'fr': 'Alertes Actives'
        },
        'alert_history': {
            'en': 'Alert History',
            'fr': 'Historique des Alertes'
        },
        'system_logs': {
            'en': 'System Logs',
            'fr': 'Journaux Système'
        },
        'activity_logs': {
            'en': 'Activity Logs',
            'fr': 'Journaux d\'Activité'
        },
        'filter_by_priority': {
            'en': 'Filter by Priority',
            'fr': 'Filtrer par Priorité'
        },
        'filter_by_status': {
            'en': 'Filter by Status',
            'fr': 'Filtrer par Statut'
        },
        'search_alerts': {
            'en': 'Search Alerts',
            'fr': 'Rechercher des Alertes'
        },
        'high_priority': {
            'en': 'High Priority',
            'fr': 'Priorité Haute'
        },
        'other_alerts': {
            'en': 'Other Alerts',
            'fr': 'Autres Alertes'
        },
        'description': {
            'en': 'Description',
            'fr': 'Description'
        },
        'sensor_id': {
            'en': 'Sensor ID',
            'fr': 'ID Capteur'
        },
        'acknowledge': {
            'en': 'Acknowledge',
            'fr': 'Accuser Réception'
        },
        'resolve': {
            'en': 'Resolve',
            'fr': 'Résoudre'
        },
        'alert_acknowledged': {
            'en': 'Alert acknowledged',
            'fr': 'Alerte accusée réception'
        },
        'acknowledged': {
            'en': 'Acknowledged',
            'fr': 'Accusé Réception'
        },
        'alert_resolved': {
            'en': 'Alert resolved',
            'fr': 'Alerte résolue'
        },
        'no_active_alerts': {
            'en': 'No active alerts',
            'fr': 'Aucune alerte active'
        },
        'alerts_over_time': {
            'en': 'Alerts Over Time',
            'fr': 'Alertes dans le Temps'
        },
        'number_of_alerts': {
            'en': 'Number of Alerts',
            'fr': 'Nombre d\'Alertes'
        },
        'alert_distribution_by_priority': {
            'en': 'Alert Distribution by Priority',
            'fr': 'Répartition des Alertes par Priorité'
        },
        'alert_distribution_by_status': {
            'en': 'Alert Distribution by Status',
            'fr': 'Répartition des Alertes par Statut'
        },
        'alert_history_details': {
            'en': 'Alert History Details',
            'fr': 'Détails de l\'Historique des Alertes'
        },
        'export_alert_history': {
            'en': 'Export Alert History',
            'fr': 'Exporter l\'Historique des Alertes'
        },
        'no_alerts_match_criteria': {
            'en': 'No alerts match the selected criteria',
            'fr': 'Aucune alerte ne correspond aux critères sélectionnés'
        },
        'filter_by_level': {
            'en': 'Filter by Level',
            'fr': 'Filtrer par Niveau'
        },
        'filter_by_component': {
            'en': 'Filter by Component',
            'fr': 'Filtrer par Composant'
        },
        'log_distribution_by_level': {
            'en': 'Log Distribution by Level',
            'fr': 'Répartition des Journaux par Niveau'
        },
        'logs_by_component': {
            'en': 'Logs by Component',
            'fr': 'Journaux par Composant'
        },
        'component': {
            'en': 'Component',
            'fr': 'Composant'
        },
        'number_of_logs': {
            'en': 'Number of Logs',
            'fr': 'Nombre de Journaux'
        },
        'export_system_logs': {
            'en': 'Export System Logs',
            'fr': 'Exporter les Journaux Système'
        },
        'no_logs_match_criteria': {
            'en': 'No logs match the selected criteria',
            'fr': 'Aucun journal ne correspond aux critères sélectionnés'
        },
        'filter_by_user': {
            'en': 'Filter by User',
            'fr': 'Filtrer par Utilisateur'
        },
        'filter_by_action': {
            'en': 'Filter by Action',
            'fr': 'Filtrer par Action'
        },
        'activities_by_user': {
            'en': 'Activities by User',
            'fr': 'Activités par Utilisateur'
        },
        'user': {
            'en': 'User',
            'fr': 'Utilisateur'
        },
        'activities_by_type': {
            'en': 'Activities by Type',
            'fr': 'Activités par Type'
        },
        'activity_timeline': {
            'en': 'Activity Timeline',
            'fr': 'Chronologie des Activités'
        },
        'time': {
            'en': 'Time',
            'fr': 'Temps'
        },
        'action_type': {
            'en': 'Action Type',
            'fr': 'Type d\'Action'
        },
        'activity_details': {
            'en': 'Activity Details',
            'fr': 'Détails d\'Activité'
        },
        'action': {
            'en': 'Action',
            'fr': 'Action'
        },
        'export_activity_logs': {
            'en': 'Export Activity Logs',
            'fr': 'Exporter les Journaux d\'Activité'
        },
        'no_activities_match_criteria': {
            'en': 'No activities match the selected criteria',
            'fr': 'Aucune activité ne correspond aux critères sélectionnés'
        }
    }
    
    # Return the translation or the key itself if not found
    if key in translations:
        if language in translations[key]:
            return translations[key][language]
    
    # Return the key if no translation found
    return key

def set_language(language_code):
    """
    Sets the current language in the session state
    
    Parameters:
    - language_code: Language code ('en' or 'fr')
    """
    import streamlit as st
    
    if language_code in get_languages():
        st.session_state['language'] = language_code
