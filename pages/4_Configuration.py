import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.sensor_utils import get_sensor_status_color
from utils.translation import get_translation
from utils.data_manager import get_sensors_data, get_mattresses_data, get_sensor_types

# Page configuration
st.set_page_config(
    page_title="Configuration - Medical Mattress Monitoring",
    page_icon="⚙️",
    layout="wide"
)

# Header
tr = lambda key: get_translation(key, st.session_state.language)
st.title(tr("configuration_title"))
st.markdown(tr("configuration_description"))

# Initialize session state variables for configurations if not present
if 'config_changes' not in st.session_state:
    st.session_state['config_changes'] = []

# Get data
sensors_data = get_sensors_data()
mattresses_data = get_mattresses_data()
sensor_types = get_sensor_types()

# Sidebar with configuration categories
st.sidebar.header(tr("configuration_categories"))
config_option = st.sidebar.radio(
    tr("select_config_area"),
    options=[
        tr("sensor_parameters"),
        tr("alert_thresholds"),
        tr("mattress_sensor_assignment"),
        tr("system_settings")
    ]
)

# Main configuration area
if config_option == tr("sensor_parameters"):
    st.header(tr("sensor_parameters"))
    
    # Select sensor type to configure
    selected_type = st.selectbox(
        tr("select_sensor_type"),
        options=sensor_types
    )
    
    # Filter sensors by type
    type_sensors = sensors_data[sensors_data['type'] == selected_type]
    
    st.markdown(f"### {tr('configure')} {selected_type} {tr('sensors')}")
    
    with st.form(key=f"sensor_params_form_{selected_type}"):
        st.markdown(f"{tr('set_parameters_for_all')} {selected_type} {tr('sensors')}")
        
        # Different parameters based on sensor type
        if selected_type == 'pressure':
            sampling_rate = st.slider(
                tr("sampling_frequency"),
                min_value=1,
                max_value=60,
                value=10,
                step=1,
                help=tr("seconds_between_readings")
            )
            
            pressure_min = st.number_input(
                tr("min_pressure_threshold"),
                min_value=0,
                max_value=100,
                value=10,
                help=tr("minimum_pressure_mmhg")
            )
            
            pressure_max = st.number_input(
                tr("max_pressure_threshold"),
                min_value=pressure_min + 1,
                max_value=200,
                value=100,
                help=tr("maximum_pressure_mmhg")
            )
            
            sensitivity = st.select_slider(
                tr("sensitivity"),
                options=["Low", "Medium", "High"],
                value="Medium",
                help=tr("sensitivity_help")
            )
            
        elif selected_type == 'temperature':
            sampling_rate = st.slider(
                tr("sampling_frequency"),
                min_value=10,
                max_value=300,
                value=60,
                step=10,
                help=tr("seconds_between_readings")
            )
            
            temp_min = st.number_input(
                tr("min_temperature_threshold"),
                min_value=30.0,
                max_value=37.0,
                value=35.0,
                step=0.1,
                help=tr("minimum_temp_celsius")
            )
            
            temp_max = st.number_input(
                tr("max_temperature_threshold"),
                min_value=temp_min + 0.1,
                max_value=45.0,
                value=38.0,
                step=0.1,
                help=tr("maximum_temp_celsius")
            )
            
        elif selected_type == 'humidity':
            sampling_rate = st.slider(
                tr("sampling_frequency"),
                min_value=60,
                max_value=900,
                value=300,
                step=60,
                help=tr("seconds_between_readings")
            )
            
            humidity_min = st.number_input(
                tr("min_humidity_threshold"),
                min_value=0,
                max_value=50,
                value=20,
                help=tr("minimum_humidity_percent")
            )
            
            humidity_max = st.number_input(
                tr("max_humidity_threshold"),
                min_value=humidity_min + 1,
                max_value=100,
                value=80,
                help=tr("maximum_humidity_percent")
            )
            
        elif selected_type == 'movement':
            sampling_rate = st.slider(
                tr("sampling_frequency"),
                min_value=1,
                max_value=60,
                value=5,
                step=1,
                help=tr("seconds_between_readings")
            )
            
            movement_threshold = st.number_input(
                tr("movement_detection_threshold"),
                min_value=1,
                max_value=10,
                value=3,
                help=tr("movement_threshold_help")
            )
            
            movement_duration = st.number_input(
                tr("movement_duration_threshold"),
                min_value=1,
                max_value=60,
                value=10,
                help=tr("movement_duration_help")
            )
        
        # Power mode settings common to all sensor types
        power_mode = st.radio(
            tr("power_mode"),
            options=[tr("normal"), tr("power_saving"), tr("high_precision")],
            horizontal=True,
            help=tr("power_mode_help")
        )
        
        # Apply to specific sensors or all sensors of this type
        apply_to = st.radio(
            tr("apply_settings_to"),
            options=[tr("all_sensors_of_type"), tr("selected_sensors_only")],
            horizontal=True
        )
        
        if apply_to == tr("selected_sensors_only"):
            selected_sensors = st.multiselect(
                tr("select_specific_sensors"),
                options=type_sensors['id'].tolist(),
                format_func=lambda x: sensors_data[sensors_data['id'] == x].iloc[0]['name']
            )
        
        submit_button = st.form_submit_button(tr("apply_configuration"))
        
        if submit_button:
            # In a real application, this would update the database or send commands to the sensors
            # For this demo, we'll just show a success message and record the change
            if apply_to == tr("all_sensors_of_type"):
                sensors_affected = len(type_sensors)
                sensor_list = "All " + selected_type + " sensors"
            else:
                sensors_affected = len(selected_sensors)
                sensor_list = ", ".join([sensors_data[sensors_data['id'] == s].iloc[0]['name'] for s in selected_sensors])
            
            # Add to configuration change log
            st.session_state['config_changes'].append({
                'timestamp': datetime.now(),
                'type': 'sensor_parameters',
                'sensors_affected': sensors_affected,
                'sensor_list': sensor_list,
                'parameters': f"Sampling Rate: {sampling_rate}s, Power Mode: {power_mode}"
            })
            
            st.success(f"{tr('configuration_applied_to')} {sensors_affected} {tr('sensors')}")

elif config_option == tr("alert_thresholds"):
    st.header(tr("alert_thresholds"))
    
    # Alert priority settings
    st.subheader(tr("alert_priority_settings"))
    
    with st.form(key="alert_thresholds_form"):
        # Power connection thresholds
        st.markdown(f"### {tr('power_connection_thresholds')}")
        
        connection_check = st.slider(
            tr("power_check_frequency"),
            min_value=1,
            max_value=30,
            value=5,
            step=1,
            help=tr("power_check_frequency_help")
        )
        
        # Signal strength thresholds
        st.markdown(f"### {tr('signal_strength_thresholds')}")
        
        signal_warning = st.slider(
            tr("signal_warning_threshold"),
            min_value=3,
            max_value=7,
            value=5,
            step=1,
            help=tr("signal_warning_help")
        )
        
        signal_critical = st.slider(
            tr("signal_critical_threshold"),
            min_value=1,
            max_value=signal_warning - 1,
            value=3,
            step=1,
            help=tr("signal_critical_help")
        )
        
        # Data age thresholds
        st.markdown(f"### {tr('data_age_thresholds')}")
        
        data_age_warning = st.slider(
            tr("data_age_warning_min"),
            min_value=5,
            max_value=60,
            value=15,
            step=5,
            help=tr("data_age_warning_help")
        )
        
        data_age_critical = st.slider(
            tr("data_age_critical_min"),
            min_value=data_age_warning + 5,
            max_value=120,
            value=30,
            step=5,
            help=tr("data_age_critical_help")
        )
        
        # Alert notifications
        st.markdown(f"### {tr('alert_notifications')}")
        
        enable_email = st.checkbox(tr("enable_email_alerts"), value=True)
        
        if enable_email:
            email_recipients = st.text_input(
                tr("email_recipients"),
                value="technician@hospital.com",
                help=tr("email_recipients_help")
            )
        
        enable_sms = st.checkbox(tr("enable_sms_alerts"), value=False)
        
        if enable_sms:
            sms_recipients = st.text_input(
                tr("sms_recipients"),
                value="+1234567890",
                help=tr("sms_recipients_help")
            )
        
        submit_button = st.form_submit_button(tr("save_alert_thresholds"))
        
        if submit_button:
            # In a real application, this would update the alert thresholds in the database
            # For this demo, we'll just show a success message and record the change
            
            # Add to configuration change log
            st.session_state['config_changes'].append({
                'timestamp': datetime.now(),
                'type': 'alert_thresholds',
                'parameters': f"Power Check: {connection_check}min, Signal: {signal_warning}/{signal_critical}, Data Age: {data_age_warning}min/{data_age_critical}min"
            })
            
            st.success(tr("alert_thresholds_saved"))

elif config_option == tr("mattress_sensor_assignment"):
    st.header(tr("mattress_sensor_assignment"))
    
    # Select mattress
    selected_mattress_id = st.selectbox(
        tr("select_mattress"),
        options=mattresses_data['id'].tolist(),
        format_func=lambda x: f"{mattresses_data[mattresses_data['id'] == x].iloc[0]['name']} (Patient: {mattresses_data[mattresses_data['id'] == x].iloc[0]['patient_id']})"
    )
    
    selected_mattress = mattresses_data[mattresses_data['id'] == selected_mattress_id].iloc[0]
    
    # Get sensors currently assigned to this mattress
    current_sensors = sensors_data[sensors_data['mattress_id'] == selected_mattress_id]
    
    st.markdown(f"### {tr('current_sensors_on')} {selected_mattress['name']}")
    
    if not current_sensors.empty:
        # Display currently assigned sensors
        for sensor in current_sensors.itertuples():
            status_color = get_sensor_status_color(sensor.status)
            
            with st.container():
                cols = st.columns([3, 2, 2, 2, 1])
                cols[0].markdown(f"**{sensor.name}** ({sensor.type})")
                cols[1].markdown(f"{tr('status')}: <span style='color:{status_color};font-weight:bold;'>{sensor.status.upper()}</span>", unsafe_allow_html=True)
                cols[2].markdown(f"{tr('power_connection')}: {'Connected' if sensor.power_connection else 'Disconnected'}")
                cols[3].markdown(f"{tr('firmware')}: {sensor.firmware_version}")
                if cols[4].button(tr("remove"), key=f"remove_{sensor.id}"):
                    # In a real application, this would update the database to unassign the sensor
                    st.warning(f"{tr('confirm_unassign')} {sensor.name}?")
                    confirm_cols = st.columns([3, 1, 1])
                    if confirm_cols[1].button(tr("yes"), key=f"confirm_{sensor.id}"):
                        # Add to configuration change log
                        st.session_state['config_changes'].append({
                            'timestamp': datetime.now(),
                            'type': 'sensor_unassigned',
                            'sensor': sensor.name,
                            'mattress': selected_mattress['name']
                        })
                        st.success(f"{tr('sensor_unassigned')}: {sensor.name}")
                        st.rerun()
                    if confirm_cols[2].button(tr("no"), key=f"cancel_{sensor.id}"):
                        st.rerun()
    else:
        st.info(tr("no_sensors_assigned"))
    
    # Assign new sensors
    st.markdown(f"### {tr('assign_new_sensors_to')} {selected_mattress['name']}")
    
    # Get unassigned sensors
    unassigned_sensors = sensors_data[sensors_data['mattress_id'].isna() | (sensors_data['mattress_id'] == '')]
    
    if not unassigned_sensors.empty:
        with st.form(key="assign_sensor_form"):
            selected_sensor_ids = st.multiselect(
                tr("select_sensors_to_assign"),
                options=unassigned_sensors['id'].tolist(),
                format_func=lambda x: f"{unassigned_sensors[unassigned_sensors['id'] == x].iloc[0]['name']} ({unassigned_sensors[unassigned_sensors['id'] == x].iloc[0]['type']})"
            )
            
            submit_button = st.form_submit_button(tr("assign_sensors"))
            
            if submit_button and selected_sensor_ids:
                # In a real application, this would update the database to assign the sensors
                for sensor_id in selected_sensor_ids:
                    sensor_name = unassigned_sensors[unassigned_sensors['id'] == sensor_id].iloc[0]['name']
                    # Add to configuration change log
                    st.session_state['config_changes'].append({
                        'timestamp': datetime.now(),
                        'type': 'sensor_assigned',
                        'sensor': sensor_name,
                        'mattress': selected_mattress['name']
                    })
                
                st.success(f"{len(selected_sensor_ids)} {tr('sensors_assigned_to')} {selected_mattress['name']}")
    else:
        st.info(tr("no_unassigned_sensors"))

elif config_option == tr("system_settings"):
    st.header(tr("system_settings"))
    
    # General system settings
    with st.form(key="system_settings_form"):
        st.markdown(f"### {tr('general_settings')}")
        
        data_retention = st.slider(
            tr("data_retention_days"),
            min_value=30,
            max_value=365,
            value=90,
            step=30,
            help=tr("data_retention_help")
        )
        
        maintenance_reminder = st.slider(
            tr("maintenance_reminder_days"),
            min_value=30,
            max_value=180,
            value=90,
            step=30,
            help=tr("maintenance_reminder_help")
        )
        
        default_language = st.selectbox(
            tr("default_language"),
            options=["English", "Français"],
            index=0 if st.session_state.language == 'en' else 1
        )
        
        # MQTT settings
        st.markdown(f"### {tr('mqtt_settings')}")
        
        mqtt_broker = st.text_input(
            tr("mqtt_broker"),
            value="mqtt.hospital.local",
            help=tr("mqtt_broker_help")
        )
        
        mqtt_port = st.number_input(
            tr("mqtt_port"),
            min_value=1,
            max_value=65535,
            value=1883,
            help=tr("mqtt_port_help")
        )
        
        mqtt_username = st.text_input(
            tr("mqtt_username"),
            value="medimat_monitor",
            help=tr("mqtt_username_help")
        )
        
        mqtt_password = st.text_input(
            tr("mqtt_password"),
            type="password",
            value="",
            help=tr("mqtt_password_help")
        )
        
        mqtt_topic_prefix = st.text_input(
            tr("mqtt_topic_prefix"),
            value="hospital/ward1/mattress/",
            help=tr("mqtt_topic_prefix_help")
        )
        
        submit_button = st.form_submit_button(tr("save_system_settings"))
        
        if submit_button:
            # In a real application, this would update the system settings
            # For this demo, we'll just show a success message and record the change
            
            # Add to configuration change log
            st.session_state['config_changes'].append({
                'timestamp': datetime.now(),
                'type': 'system_settings',
                'parameters': f"Data Retention: {data_retention} days, Maintenance Reminder: {maintenance_reminder} days, MQTT: {mqtt_broker}:{mqtt_port}"
            })
            
            st.success(tr("system_settings_saved"))

# Configuration change history
st.markdown("---")
st.header(tr("configuration_history"))

if st.session_state['config_changes']:
    # Create a DataFrame from the configuration changes
    changes_df = pd.DataFrame(st.session_state['config_changes'])
    
    # Sort by timestamp (newest first)
    changes_df = changes_df.sort_values('timestamp', ascending=False)
    
    st.dataframe(
        changes_df,
        column_config={
            'timestamp': st.column_config.DatetimeColumn(tr("timestamp"), format="DD/MM/YYYY HH:mm:ss"),
            'type': tr("change_type"),
            'parameters': tr("parameters")
        },
        hide_index=True
    )
else:
    st.info(tr("no_configuration_changes"))

# Footer
st.markdown("---")
st.caption(f"© {datetime.now().year} MediMat Monitor - {tr('version')} 1.0.0")
