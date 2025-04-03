import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
from utils.sensor_utils import get_sensor_status_color
from utils.translation import get_translation
from utils.data_manager import get_alerts_data, get_sensors_data, get_mattresses_data

# Page configuration
st.set_page_config(
    page_title="Alerts & Logs - Medical Mattress Monitoring",
    page_icon="🚨",
    layout="wide"
)

# Header
tr = lambda key: get_translation(key, st.session_state.language)
st.title(tr("alerts_logs_title"))
st.markdown(tr("alerts_logs_description"))

# Initialize session state
if 'acknowledged_alerts' not in st.session_state:
    st.session_state['acknowledged_alerts'] = set()
if 'resolved_alerts' not in st.session_state:
    st.session_state['resolved_alerts'] = set()

# Get data
alerts_data = get_alerts_data()
sensors_data = get_sensors_data()
mattresses_data = get_mattresses_data()

# Sidebar with alerts/logs categories
st.sidebar.header(tr("categories"))
view_option = st.sidebar.radio(
    tr("select_view"),
    options=[
        tr("active_alerts"),
        tr("alert_history"),
        tr("system_logs"),
        tr("activity_logs")
    ]
)

# Filter controls
st.sidebar.header(tr("filters"))

# Time range filter
time_range = st.sidebar.radio(
    tr("time_range"),
    options=["24 hours", "7 days", "30 days", "All"],
    index=0
)

# Map time range to actual delta
if time_range == "24 hours":
    time_delta = timedelta(days=1)
elif time_range == "7 days":
    time_delta = timedelta(days=7)
elif time_range == "30 days":
    time_delta = timedelta(days=30)
else:
    time_delta = timedelta(days=3650)  # ~10 years, effectively "All"

filter_date = datetime.now() - time_delta

# Apply time filter to alerts data
filtered_alerts = alerts_data[pd.to_datetime(alerts_data['timestamp']) >= filter_date]

# Priority filter
priority_options = ['critical', 'high', 'medium', 'low']
selected_priorities = st.sidebar.multiselect(
    tr("filter_by_priority"),
    options=priority_options,
    default=['critical', 'high']
)

# Apply priority filter
if selected_priorities:
    filtered_alerts = filtered_alerts[filtered_alerts['priority'].isin(selected_priorities)]

# Status filter (for alert history)
if view_option == tr("alert_history"):
    status_options = ['active', 'acknowledged', 'resolved']
    selected_statuses = st.sidebar.multiselect(
        tr("filter_by_status"),
        options=status_options,
        default=status_options
    )
    
    # Apply status filter
    if selected_statuses:
        filtered_alerts = filtered_alerts[filtered_alerts['status'].isin(selected_statuses)]

# Search by mattress ID or description
search_query = st.sidebar.text_input(tr("search_alerts"))

if search_query:
    filtered_alerts = filtered_alerts[
        filtered_alerts['mattress_id'].str.contains(search_query, case=False, na=False) |
        filtered_alerts['description'].str.contains(search_query, case=False, na=False) |
        filtered_alerts['title'].str.contains(search_query, case=False, na=False)
    ]

# Display last refresh time
st.sidebar.info(f"{tr('last_update')}: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

# Refresh button
if st.sidebar.button(tr("refresh_data")):
    st.rerun()

# Main content area based on selected view
if view_option == tr("active_alerts"):
    st.header(tr("active_alerts"))
    
    # Filter only active alerts
    active_alerts = filtered_alerts[filtered_alerts['status'] == 'active']
    
    # Active Alerts Summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        critical_count = active_alerts[active_alerts['priority'] == 'critical'].shape[0]
        st.metric(
            label=tr("critical_alerts"),
            value=critical_count,
            delta=None
        )
    
    with col2:
        high_count = active_alerts[active_alerts['priority'] == 'high'].shape[0]
        st.metric(
            label=tr("high_priority"),
            value=high_count,
            delta=None
        )
    
    with col3:
        other_count = active_alerts[(active_alerts['priority'] == 'medium') | (active_alerts['priority'] == 'low')].shape[0]
        st.metric(
            label=tr("other_alerts"),
            value=other_count,
            delta=None
        )
    
    # Display active alerts
    if not active_alerts.empty:
        # Sort by priority (highest first) and then by timestamp (newest first)
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_alerts = active_alerts.sort_values(
            by=['priority', 'timestamp'],
            key=lambda x: x.map(priority_order) if x.name == 'priority' else x,
            ascending=[True, False]
        )
        
        for _, alert in sorted_alerts.iterrows():
            # Determine color based on priority
            if alert['priority'] == 'critical':
                color = "#ff4b4b"
            elif alert['priority'] == 'high':
                color = "#ff9d00"
            elif alert['priority'] == 'medium':
                color = "#00cc96"
            else:  # low
                color = "#636efa"
            
            with st.container():
                st.markdown(
                    f"""
                    <div style="border-left:5px solid {color}; padding:10px; margin-bottom:10px; background-color:#f8f9fa; border-radius:5px;">
                    <h3 style="margin-top:0;">{alert['title']}</h3>
                    <p><strong>{tr('timestamp')}:</strong> {alert['timestamp']}</p>
                    <p><strong>{tr('description')}:</strong> {alert['description']}</p>
                    <p><strong>{tr('mattress_id')}:</strong> {alert['mattress_id']} | <strong>{tr('sensor_id')}:</strong> {alert['sensor_id']}</p>
                    <p><strong>{tr('priority')}:</strong> <span style="color:{color};font-weight:bold;">{alert['priority'].upper()}</span></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Action buttons
                col1, col2 = st.columns(2)
                
                if alert['id'] not in st.session_state['acknowledged_alerts']:
                    if col1.button(tr("acknowledge"), key=f"ack_{alert['id']}"):
                        # In a real application, this would update the alert status in the database
                        st.session_state['acknowledged_alerts'].add(alert['id'])
                        st.success(f"{tr('alert_acknowledged')}: {alert['title']}")
                        time.sleep(1)
                        st.rerun()
                else:
                    col1.success(tr("acknowledged"))
                
                if col2.button(tr("resolve"), key=f"resolve_{alert['id']}"):
                    # In a real application, this would update the alert status in the database
                    st.session_state['resolved_alerts'].add(alert['id'])
                    
                    if alert['id'] in st.session_state['acknowledged_alerts']:
                        st.session_state['acknowledged_alerts'].remove(alert['id'])
                    
                    st.success(f"{tr('alert_resolved')}: {alert['title']}")
                    time.sleep(1)
                    st.rerun()
    else:
        st.success(tr("no_active_alerts"))

elif view_option == tr("alert_history"):
    st.header(tr("alert_history"))
    
    # Exclude alerts that were resolved in this session
    history_alerts = filtered_alerts[~filtered_alerts['id'].isin(st.session_state['resolved_alerts'])]
    
    # Mark alerts that were acknowledged in this session as 'acknowledged'
    history_alerts.loc[history_alerts['id'].isin(st.session_state['acknowledged_alerts']), 'status'] = 'acknowledged'
    
    if not history_alerts.empty:
        # Create a chart of alerts over time by priority
        alerts_by_day = history_alerts.copy()
        alerts_by_day['date'] = pd.to_datetime(alerts_by_day['timestamp']).dt.date
        alerts_by_day = alerts_by_day.groupby(['date', 'priority']).size().reset_index(name='count')
        
        fig = px.bar(
            alerts_by_day,
            x='date',
            y='count',
            color='priority',
            title=tr("alerts_over_time"),
            labels={
                'date': tr('date'),
                'count': tr('number_of_alerts'),
                'priority': tr('priority')
            },
            color_discrete_map={
                'critical': '#ff4b4b',
                'high': '#ff9d00',
                'medium': '#00cc96',
                'low': '#636efa'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Alert distribution by priority pie chart
        priority_counts = history_alerts['priority'].value_counts().reset_index()
        priority_counts.columns = ['priority', 'count']
        
        fig = px.pie(
            priority_counts,
            values='count',
            names='priority',
            title=tr("alert_distribution_by_priority"),
            color='priority',
            color_discrete_map={
                'critical': '#ff4b4b',
                'high': '#ff9d00',
                'medium': '#00cc96',
                'low': '#636efa'
            }
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig, use_container_width=True)
        
        # Alert distribution by status pie chart
        status_counts = history_alerts['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        fig = px.pie(
            status_counts,
            values='count',
            names='status',
            title=tr("alert_distribution_by_status"),
            color='status',
            color_discrete_map={
                'active': '#ff4b4b',
                'acknowledged': '#ffa15a',
                'resolved': '#00cc96'
            }
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        col2.plotly_chart(fig, use_container_width=True)
        
        # Alert history data table
        st.subheader(tr("alert_history_details"))
        
        # Sort by timestamp (newest first)
        sorted_history = history_alerts.sort_values('timestamp', ascending=False)
        
        def format_priority(priority):
            if priority == 'critical':
                return f'<span style="color:#ff4b4b;font-weight:bold;">{priority.upper()}</span>'
            elif priority == 'high':
                return f'<span style="color:#ff9d00;font-weight:bold;">{priority.upper()}</span>'
            elif priority == 'medium':
                return f'<span style="color:#00cc96;font-weight:bold;">{priority.upper()}</span>'
            else:  # low
                return f'<span style="color:#636efa;font-weight:bold;">{priority.upper()}</span>'
        
        def format_status(status):
            if status == 'active':
                return f'<span style="color:#ff4b4b;font-weight:bold;">{status.upper()}</span>'
            elif status == 'acknowledged':
                return f'<span style="color:#ffa15a;font-weight:bold;">{status.upper()}</span>'
            else:  # resolved
                return f'<span style="color:#00cc96;font-weight:bold;">{status.upper()}</span>'
        
        # Format the data for display
        display_df = sorted_history.copy()
        display_df['formatted_priority'] = display_df['priority'].apply(format_priority)
        display_df['formatted_status'] = display_df['status'].apply(format_status)
        
        # Display as HTML to show colored status
        st.write(
            display_df[['timestamp', 'title', 'mattress_id', 'sensor_id', 'formatted_priority', 'formatted_status']].to_html(
                escape=False,
                index=False
            ),
            unsafe_allow_html=True
        )
        
        # Export as CSV
        csv = sorted_history.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=tr("export_alert_history"),
            data=csv,
            file_name=f"alert_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.info(tr("no_alerts_match_criteria"))

elif view_option == tr("system_logs"):
    st.header(tr("system_logs"))
    
    # In a real application, this would fetch system logs from a database or log files
    # For this demo, we'll create some sample system logs
    
    # Generate sample system logs
    sample_logs = []
    
    # System startup
    sample_logs.append({
        'timestamp': (datetime.now() - timedelta(days=1, hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S'),
        'level': 'INFO',
        'component': 'System',
        'message': 'System started successfully'
    })
    
    # MQTT connection
    sample_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 12))).strftime('%Y-%m-%d %H:%M:%S'),
        'level': 'INFO',
        'component': 'MQTT',
        'message': 'Connected to MQTT broker successfully'
    })
    
    # Sensor connections
    for i in range(5):
        sample_logs.append({
            'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S'),
            'level': 'INFO',
            'component': 'Sensor',
            'message': f'Sensor SEN-{200 + i} connected'
        })
    
    # Database operations
    sample_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
        'level': 'INFO',
        'component': 'Database',
        'message': 'Sensor data successfully archived'
    })
    
    # Some warning/error logs
    sample_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
        'level': 'WARNING',
        'component': 'MQTT',
        'message': 'Temporary connection loss to MQTT broker, reconnecting...'
    })
    
    sample_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=8, minutes=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'level': 'INFO',
        'component': 'MQTT',
        'message': 'Successfully reconnected to MQTT broker'
    })
    
    sample_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S'),
        'level': 'ERROR',
        'component': 'Sensor',
        'message': 'Failed to update firmware for sensor SEN-203, timeout error'
    })
    
    # Authentication logs
    sample_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
        'level': 'INFO',
        'component': 'Auth',
        'message': 'User login: technician1'
    })
    
    sample_logs.append({
        'timestamp': (datetime.now() - timedelta(days=1, hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
        'level': 'WARNING',
        'component': 'Auth',
        'message': 'Failed login attempt for user: admin'
    })
    
    # Convert to DataFrame
    logs_df = pd.DataFrame(sample_logs)
    
    # Sort by timestamp (newest first)
    logs_df = logs_df.sort_values('timestamp', ascending=False)
    
    # Filter logs by time range
    logs_df['datetime'] = pd.to_datetime(logs_df['timestamp'])
    filtered_logs = logs_df[logs_df['datetime'] >= filter_date]
    
    # Level filter
    level_options = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    selected_levels = st.sidebar.multiselect(
        tr("filter_by_level"),
        options=level_options,
        default=level_options
    )
    
    if selected_levels:
        filtered_logs = filtered_logs[filtered_logs['level'].isin(selected_levels)]
    
    # Component filter
    component_options = filtered_logs['component'].unique().tolist()
    selected_components = st.sidebar.multiselect(
        tr("filter_by_component"),
        options=component_options,
        default=component_options
    )
    
    if selected_components:
        filtered_logs = filtered_logs[filtered_logs['component'].isin(selected_components)]
    
    # Display logs
    if not filtered_logs.empty:
        # Log level distribution
        level_counts = filtered_logs['level'].value_counts().reset_index()
        level_counts.columns = ['level', 'count']
        
        fig = px.pie(
            level_counts,
            values='count',
            names='level',
            title=tr("log_distribution_by_level"),
            color='level',
            color_discrete_map={
                'INFO': '#00cc96',
                'WARNING': '#ffa15a',
                'ERROR': '#ff4b4b',
                'CRITICAL': '#7b2cbf'
            }
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig, use_container_width=True)
        
        # Component distribution
        component_counts = filtered_logs['component'].value_counts().reset_index()
        component_counts.columns = ['component', 'count']
        
        fig = px.bar(
            component_counts,
            x='component',
            y='count',
            title=tr("logs_by_component"),
            labels={
                'component': tr('component'),
                'count': tr('number_of_logs')
            },
            color='component'
        )
        
        col2.plotly_chart(fig, use_container_width=True)
        
        # Format the logs for display
        def format_level(level):
            if level == 'INFO':
                return f'<span style="color:#00cc96;font-weight:bold;">{level}</span>'
            elif level == 'WARNING':
                return f'<span style="color:#ffa15a;font-weight:bold;">{level}</span>'
            elif level == 'ERROR':
                return f'<span style="color:#ff4b4b;font-weight:bold;">{level}</span>'
            else:  # CRITICAL
                return f'<span style="color:#7b2cbf;font-weight:bold;">{level}</span>'
        
        display_logs = filtered_logs.copy()
        display_logs['formatted_level'] = display_logs['level'].apply(format_level)
        
        # Display logs as a table
        st.subheader(tr("system_logs"))
        
        st.write(
            display_logs[['timestamp', 'component', 'formatted_level', 'message']].to_html(
                escape=False,
                index=False
            ),
            unsafe_allow_html=True
        )
        
        # Export as CSV
        csv = filtered_logs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=tr("export_system_logs"),
            data=csv,
            file_name=f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.info(tr("no_logs_match_criteria"))

elif view_option == tr("activity_logs"):
    st.header(tr("activity_logs"))
    
    # In a real application, this would fetch user activity logs from a database
    # For this demo, we'll create some sample activity logs
    
    # Generate sample activity logs
    activity_logs = []
    
    # User logins
    activity_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'user': 'technician1',
        'action': 'login',
        'details': 'Successful login from 192.168.1.100'
    })
    
    activity_logs.append({
        'timestamp': (datetime.now() - timedelta(days=1, hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
        'user': 'admin',
        'action': 'login',
        'details': 'Successful login from 192.168.1.101'
    })
    
    # Configuration changes
    activity_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'),
        'user': 'technician1',
        'action': 'configuration_update',
        'details': 'Updated threshold settings for temperature sensors'
    })
    
    activity_logs.append({
        'timestamp': (datetime.now() - timedelta(days=1, hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
        'user': 'admin',
        'action': 'configuration_update',
        'details': 'Changed MQTT broker settings'
    })
    
    # Sensor management
    activity_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S'),
        'user': 'technician1',
        'action': 'sensor_calibration',
        'details': 'Calibrated pressure sensor SEN-201'
    })
    
    activity_logs.append({
        'timestamp': (datetime.now() - timedelta(days=1, hours=8)).strftime('%Y-%m-%d %H:%M:%S'),
        'user': 'technician2',
        'action': 'firmware_update',
        'details': 'Updated firmware for humidity sensors'
    })
    
    # Alert management
    activity_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
        'user': 'technician1',
        'action': 'alert_acknowledgment',
        'details': 'Acknowledged low battery alert for sensor SEN-202'
    })
    
    activity_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S'),
        'user': 'technician1',
        'action': 'alert_resolution',
        'details': 'Resolved connectivity issue for mattress MAT-101'
    })
    
    # Report generation
    activity_logs.append({
        'timestamp': (datetime.now() - timedelta(days=1, hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'user': 'admin',
        'action': 'report_generation',
        'details': 'Generated monthly maintenance report'
    })
    
    activity_logs.append({
        'timestamp': (datetime.now() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'),
        'user': 'technician2',
        'action': 'data_export',
        'details': 'Exported sensor data for mattress MAT-102'
    })
    
    # Convert to DataFrame
    activity_df = pd.DataFrame(activity_logs)
    
    # Sort by timestamp (newest first)
    activity_df = activity_df.sort_values('timestamp', ascending=False)
    
    # Filter logs by time range
    activity_df['datetime'] = pd.to_datetime(activity_df['timestamp'])
    filtered_activities = activity_df[activity_df['datetime'] >= filter_date]
    
    # User filter
    user_options = filtered_activities['user'].unique().tolist()
    selected_users = st.sidebar.multiselect(
        tr("filter_by_user"),
        options=user_options,
        default=user_options
    )
    
    if selected_users:
        filtered_activities = filtered_activities[filtered_activities['user'].isin(selected_users)]
    
    # Action filter
    action_options = filtered_activities['action'].unique().tolist()
    selected_actions = st.sidebar.multiselect(
        tr("filter_by_action"),
        options=action_options,
        default=action_options
    )
    
    if selected_actions:
        filtered_activities = filtered_activities[filtered_activities['action'].isin(selected_actions)]
    
    # Display activity logs
    if not filtered_activities.empty:
        # Activity by user
        user_counts = filtered_activities['user'].value_counts().reset_index()
        user_counts.columns = ['user', 'count']
        
        fig = px.bar(
            user_counts,
            x='user',
            y='count',
            title=tr("activities_by_user"),
            labels={
                'user': tr('user'),
                'count': tr('number_of_activities')
            },
            color='user'
        )
        
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig, use_container_width=True)
        
        # Activity by action type
        action_counts = filtered_activities['action'].value_counts().reset_index()
        action_counts.columns = ['action', 'count']
        
        fig = px.pie(
            action_counts,
            values='count',
            names='action',
            title=tr("activities_by_type"),
            color='action'
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        col2.plotly_chart(fig, use_container_width=True)
        
        # Activity timeline
        activities_by_hour = filtered_activities.copy()
        activities_by_hour['hour'] = activities_by_hour['datetime'].dt.floor('H')
        activities_by_hour = activities_by_hour.groupby(['hour', 'action']).size().reset_index(name='count')
        
        fig = px.line(
            activities_by_hour,
            x='hour',
            y='count',
            color='action',
            title=tr("activity_timeline"),
            labels={
                'hour': tr('time'),
                'count': tr('number_of_activities'),
                'action': tr('action_type')
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display activities as a table
        st.subheader(tr("activity_details"))
        
        st.dataframe(
            filtered_activities,
            column_config={
                'timestamp': st.column_config.DatetimeColumn(tr("timestamp"), format="DD/MM/YYYY HH:mm:ss"),
                'user': tr("user"),
                'action': tr("action"),
                'details': tr("details")
            },
            hide_index=True
        )
        
        # Export as CSV
        csv = filtered_activities.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=tr("export_activity_logs"),
            data=csv,
            file_name=f"activity_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.info(tr("no_activities_match_criteria"))

# Footer
st.markdown("---")
st.caption(f"© {datetime.now().year} MediMat Monitor - {tr('version')} 1.0.0")
