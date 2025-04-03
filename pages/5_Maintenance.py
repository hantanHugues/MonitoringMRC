import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.sensor_utils import get_sensor_status_color, get_battery_level_color
from utils.translation import get_translation
from utils.data_manager import get_sensors_data, get_mattresses_data

# Page configuration
st.set_page_config(
    page_title="Maintenance - Medical Mattress Monitoring",
    page_icon="🔧",
    layout="wide"
)

# Header
tr = lambda key: get_translation(key, st.session_state.language)
st.title(tr("maintenance_title"))
st.markdown(tr("maintenance_description"))

# Initialize session state variables for maintenance if not present
if 'maintenance_tasks' not in st.session_state:
    st.session_state['maintenance_tasks'] = []

# Get data
sensors_data = get_sensors_data()
mattresses_data = get_mattresses_data()

# Sidebar with maintenance categories
st.sidebar.header(tr("maintenance_categories"))
maintenance_option = st.sidebar.radio(
    tr("select_maintenance_area"),
    options=[
        tr("maintenance_schedule"),
        tr("firmware_updates"),
        tr("calibration"),
        tr("historical_maintenance")
    ]
)

# Main maintenance area
if maintenance_option == tr("maintenance_schedule"):
    st.header(tr("maintenance_schedule"))
    
    # Schedule new maintenance
    st.subheader(tr("schedule_new_maintenance"))
    
    with st.form(key="maintenance_schedule_form"):
        # Select asset type
        asset_type = st.radio(
            tr("select_asset_type"),
            options=[tr("sensor"), tr("mattress")],
            horizontal=True
        )
        
        # Select specific asset
        if asset_type == tr("sensor"):
            asset_options = sensors_data
            asset_id = st.selectbox(
                tr("select_sensor"),
                options=asset_options['id'].tolist(),
                format_func=lambda x: f"{asset_options[asset_options['id'] == x].iloc[0]['name']} ({asset_options[asset_options['id'] == x].iloc[0]['type']})"
            )
            asset_name = asset_options[asset_options['id'] == asset_id].iloc[0]['name']
        else:
            asset_options = mattresses_data
            asset_id = st.selectbox(
                tr("select_mattress"),
                options=asset_options['id'].tolist(),
                format_func=lambda x: f"{asset_options[asset_options['id'] == x].iloc[0]['name']} (Patient: {asset_options[asset_options['id'] == x].iloc[0]['patient_id']})"
            )
            asset_name = asset_options[asset_options['id'] == asset_id].iloc[0]['name']
        
        # Select maintenance type
        if asset_type == tr("sensor"):
            maintenance_types = [tr("calibration"), tr("battery_replacement"), tr("firmware_update"), tr("physical_inspection")]
        else:
            maintenance_types = [tr("cleaning"), tr("sensor_replacement"), tr("physical_inspection")]
        
        maintenance_type = st.selectbox(
            tr("maintenance_type"),
            options=maintenance_types
        )
        
        # Schedule date
        schedule_date = st.date_input(
            tr("scheduled_date"),
            value=datetime.now().date() + timedelta(days=7),
            min_value=datetime.now().date(),
            max_value=datetime.now().date() + timedelta(days=365)
        )
        
        # Priority
        priority = st.select_slider(
            tr("priority"),
            options=[tr("low"), tr("medium"), tr("high"), tr("critical")],
            value=tr("medium")
        )
        
        # Notes
        notes = st.text_area(
            tr("notes"),
            height=100
        )
        
        # Assigned technician
        technician = st.text_input(
            tr("assigned_technician"),
            value="Tech1"
        )
        
        submit_button = st.form_submit_button(tr("schedule_maintenance"))
        
        if submit_button:
            # In a real application, this would add the maintenance task to the database
            # For this demo, we'll add it to the session state
            
            st.session_state['maintenance_tasks'].append({
                'id': len(st.session_state['maintenance_tasks']) + 1,
                'asset_type': asset_type,
                'asset_id': asset_id,
                'asset_name': asset_name,
                'maintenance_type': maintenance_type,
                'schedule_date': schedule_date,
                'priority': priority,
                'status': tr("scheduled"),
                'notes': notes,
                'technician': technician,
                'created_at': datetime.now()
            })
            
            st.success(f"{tr('maintenance_scheduled_for')} {asset_name} {tr('on')} {schedule_date}")
    
    # Upcoming maintenance tasks
    st.subheader(tr("upcoming_maintenance"))
    
    if st.session_state['maintenance_tasks']:
        # Create a DataFrame from the maintenance tasks
        tasks_df = pd.DataFrame(st.session_state['maintenance_tasks'])
        
        # Filter for upcoming tasks
        upcoming_tasks = tasks_df[
            (tasks_df['status'] == tr("scheduled")) & 
            (pd.to_datetime(tasks_df['schedule_date']) >= datetime.now())
        ]
        
        if not upcoming_tasks.empty:
            # Sort by scheduled date
            upcoming_tasks = upcoming_tasks.sort_values('schedule_date')
            
            # Display as a calendar view for the next 30 days
            st.markdown(f"#### {tr('next_30_days_schedule')}")
            
            # Get date range
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=30)
            date_range = pd.date_range(start=start_date, end=end_date)
            
            # Create a calendar-like grid with 7 days per row
            for week_start in range(0, len(date_range), 7):
                week_dates = date_range[week_start:week_start + 7]
                cols = st.columns(7)
                
                for i, date in enumerate(week_dates):
                    # Format the date
                    date_str = date.strftime("%d %b")
                    day_name = date.strftime("%a")
                    
                    # Check if there are tasks scheduled for this date
                    day_tasks = upcoming_tasks[pd.to_datetime(upcoming_tasks['schedule_date']).dt.date == date.date()]
                    
                    with cols[i]:
                        # Date header
                        if date.date() == datetime.now().date():
                            st.markdown(f"**{date_str}** ({day_name}) 📌")
                        else:
                            st.markdown(f"**{date_str}** ({day_name})")
                        
                        # Tasks for this day
                        if not day_tasks.empty:
                            for _, task in day_tasks.iterrows():
                                # Color based on priority
                                if task['priority'] == tr("critical"):
                                    color = "#ff4b4b"
                                elif task['priority'] == tr("high"):
                                    color = "#ff9d00"
                                elif task['priority'] == tr("medium"):
                                    color = "#00cc96"
                                else:
                                    color = "#636efa"
                                
                                st.markdown(
                                    f"""
                                    <div style="border-left:3px solid {color}; padding-left:5px; margin-bottom:5px; font-size:0.9em;">
                                    <strong>{task['asset_name']}</strong><br>
                                    {task['maintenance_type']}<br>
                                    <span style="font-size:0.8em;">{task['technician']}</span>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
            
            # List view of upcoming tasks
            st.markdown(f"#### {tr('upcoming_tasks_list')}")
            
            for _, task in upcoming_tasks.iterrows():
                # Determine color based on priority
                if task['priority'] == tr("critical"):
                    color = "#ff4b4b"
                elif task['priority'] == tr("high"):
                    color = "#ff9d00"
                elif task['priority'] == tr("medium"):
                    color = "#00cc96"
                else:
                    color = "#636efa"
                
                # Create a container for each task
                with st.container():
                    cols = st.columns([1, 3, 2, 2, 2, 1])
                    
                    cols[0].markdown(f"**{task['schedule_date']}**")
                    cols[1].markdown(f"**{task['asset_name']}** ({task['asset_type']})")
                    cols[2].markdown(task['maintenance_type'])
                    cols[3].markdown(f"{tr('priority')}: <span style='color:{color};font-weight:bold;'>{task['priority'].upper()}</span>", unsafe_allow_html=True)
                    cols[4].markdown(f"{tr('technician')}: {task['technician']}")
                    
                    if cols[5].button(tr("complete"), key=f"complete_{task['id']}"):
                        # Mark the task as completed
                        for i, t in enumerate(st.session_state['maintenance_tasks']):
                            if t['id'] == task['id']:
                                st.session_state['maintenance_tasks'][i]['status'] = tr("completed")
                                st.session_state['maintenance_tasks'][i]['completion_date'] = datetime.now().date()
                                break
                        
                        st.success(f"{tr('maintenance_marked_complete')}: {task['asset_name']} - {task['maintenance_type']}")
                        st.rerun()
        else:
            st.info(tr("no_upcoming_maintenance"))
    else:
        st.info(tr("no_maintenance_tasks"))

elif maintenance_option == tr("firmware_updates"):
    st.header(tr("firmware_updates"))
    
    # Current firmware versions
    st.subheader(tr("current_firmware_versions"))
    
    # Group sensors by type and show firmware versions
    if not sensors_data.empty:
        # Group by type and firmware version
        firmware_versions = sensors_data.groupby(['type', 'firmware_version']).size().reset_index(name='count')
        
        # Create a bar chart of firmware versions by sensor type
        fig = px.bar(
            firmware_versions,
            x='type',
            y='count',
            color='firmware_version',
            title=tr("firmware_versions_by_sensor_type"),
            labels={
                'type': tr('sensor_type'),
                'count': tr('number_of_sensors'),
                'firmware_version': tr('firmware_version')
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # List of sensors that need firmware updates
        # For demo purposes, we'll consider sensors with firmware versions below 2.0 as needing updates
        needs_update = sensors_data[sensors_data['firmware_version'].apply(lambda x: float(x.split('v')[1]) < 2.0)]
        
        if not needs_update.empty:
            st.subheader(tr("sensors_needing_updates"))
            
            for sensor in needs_update.itertuples():
                with st.container():
                    cols = st.columns([3, 2, 2, 2, 1])
                    
                    cols[0].markdown(f"**{sensor.name}** ({sensor.type})")
                    cols[1].markdown(f"{tr('current_version')}: {sensor.firmware_version}")
                    cols[2].markdown(f"{tr('latest_version')}: v2.1")
                    cols[3].markdown(f"{tr('mattress')}: {sensor.mattress_id}")
                    
                    if cols[4].button(tr("update"), key=f"update_{sensor.id}"):
                        st.warning(f"{tr('confirm_firmware_update')} {sensor.name}?")
                        
                        confirm_cols = st.columns([3, 1, 1])
                        
                        if confirm_cols[1].button(tr("yes"), key=f"confirm_update_{sensor.id}"):
                            # In a real application, this would trigger the firmware update process
                            # For this demo, we'll just show a success message
                            
                            # Add a new maintenance task for the firmware update
                            st.session_state['maintenance_tasks'].append({
                                'id': len(st.session_state['maintenance_tasks']) + 1,
                                'asset_type': tr("sensor"),
                                'asset_id': sensor.id,
                                'asset_name': sensor.name,
                                'maintenance_type': tr("firmware_update"),
                                'schedule_date': datetime.now().date(),
                                'priority': tr("high"),
                                'status': tr("in_progress"),
                                'notes': f"{tr('update_from')} {sensor.firmware_version} {tr('to')} v2.1",
                                'technician': "System",
                                'created_at': datetime.now()
                            })
                            
                            st.success(f"{tr('firmware_update_started_for')} {sensor.name}")
                            st.rerun()
                        
                        if confirm_cols[2].button(tr("no"), key=f"cancel_update_{sensor.id}"):
                            st.rerun()
        else:
            st.success(tr("all_sensors_up_to_date"))
    
    # Firmware update history
    st.subheader(tr("firmware_update_history"))
    
    if st.session_state['maintenance_tasks']:
        # Filter for firmware update tasks
        update_history = pd.DataFrame([
            task for task in st.session_state['maintenance_tasks'] 
            if task['maintenance_type'] == tr("firmware_update") and task['status'] != tr("scheduled")
        ])
        
        if not update_history.empty:
            # Sort by created_at (newest first)
            update_history = update_history.sort_values('created_at', ascending=False)
            
            st.dataframe(
                update_history,
                column_config={
                    'asset_name': tr("sensor_name"),
                    'schedule_date': st.column_config.DateColumn(tr("date"), format="DD/MM/YYYY"),
                    'status': tr("status"),
                    'notes': tr("details"),
                    'technician': tr("performed_by")
                },
                hide_index=True,
                column_order=['asset_name', 'schedule_date', 'status', 'notes', 'technician']
            )
        else:
            st.info(tr("no_firmware_update_history"))
    else:
        st.info(tr("no_maintenance_history"))

elif maintenance_option == tr("calibration"):
    st.header(tr("sensor_calibration"))
    
    # Calibration status overview
    st.subheader(tr("calibration_status"))
    
    # For demo purposes, we'll consider last_maintenance date as last calibration date
    # In a real application, this would be a separate field
    
    # Calculate days since last maintenance
    sensors_data['days_since_maintenance'] = sensors_data['last_maintenance'].apply(
        lambda x: (datetime.now().date() - datetime.strptime(x, '%Y-%m-%d').date()).days if isinstance(x, str) else 999
    )
    
    # Determine calibration status
    sensors_data['calibration_status'] = sensors_data['days_since_maintenance'].apply(
        lambda days: tr("due_soon") if days > 60 and days <= 90 else tr("overdue") if days > 90 else tr("ok")
    )
    
    # Count sensors by calibration status
    calibration_status = sensors_data['calibration_status'].value_counts().reset_index()
    calibration_status.columns = ['status', 'count']
    
    # Create a pie chart of calibration status
    fig = px.pie(
        calibration_status,
        values='count',
        names='status',
        title=tr("sensor_calibration_status"),
        color='status',
        color_discrete_map={
            tr("ok"): "#00cc96",
            tr("due_soon"): "#ffa15a",
            tr("overdue"): "#ef553b"
        }
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Sensors needing calibration
    needs_calibration = sensors_data[sensors_data['calibration_status'] != tr("ok")]
    
    if not needs_calibration.empty:
        st.subheader(tr("sensors_needing_calibration"))
        
        # Sort by days since maintenance (descending)
        needs_calibration = needs_calibration.sort_values('days_since_maintenance', ascending=False)
        
        for sensor in needs_calibration.itertuples():
            # Determine color based on calibration status
            if sensor.calibration_status == tr("overdue"):
                color = "#ef553b"
            else:  # due_soon
                color = "#ffa15a"
            
            with st.container():
                cols = st.columns([3, 2, 2, 2, 1])
                
                cols[0].markdown(f"**{sensor.name}** ({sensor.type})")
                cols[1].markdown(f"{tr('last_calibration')}: {sensor.last_maintenance}")
                cols[2].markdown(f"{tr('status')}: <span style='color:{color};font-weight:bold;'>{sensor.calibration_status.upper()}</span>", unsafe_allow_html=True)
                cols[3].markdown(f"{tr('days_since_last')}: {sensor.days_since_maintenance}")
                
                if cols[4].button(tr("calibrate"), key=f"calibrate_{sensor.id}"):
                    st.warning(f"{tr('confirm_calibration')} {sensor.name}?")
                    
                    confirm_cols = st.columns([3, 1, 1])
                    
                    if confirm_cols[1].button(tr("yes"), key=f"confirm_calibrate_{sensor.id}"):
                        # In a real application, this would trigger the calibration process
                        # For this demo, we'll just show a success message
                        
                        # Add a new maintenance task for the calibration
                        st.session_state['maintenance_tasks'].append({
                            'id': len(st.session_state['maintenance_tasks']) + 1,
                            'asset_type': tr("sensor"),
                            'asset_id': sensor.id,
                            'asset_name': sensor.name,
                            'maintenance_type': tr("calibration"),
                            'schedule_date': datetime.now().date(),
                            'priority': tr("high") if sensor.calibration_status == tr("overdue") else tr("medium"),
                            'status': tr("completed"),
                            'completion_date': datetime.now().date(),
                            'notes': f"{tr('calibration_performed')} - {tr('days_since_last')}: {sensor.days_since_maintenance}",
                            'technician': "Tech1",
                            'created_at': datetime.now()
                        })
                        
                        st.success(f"{tr('calibration_completed_for')} {sensor.name}")
                        st.rerun()
                    
                    if confirm_cols[2].button(tr("no"), key=f"cancel_calibrate_{sensor.id}"):
                        st.rerun()
    else:
        st.success(tr("all_sensors_calibrated"))
    
    # Calibration history
    st.subheader(tr("calibration_history"))
    
    if st.session_state['maintenance_tasks']:
        # Filter for calibration tasks
        calibration_history = pd.DataFrame([
            task for task in st.session_state['maintenance_tasks'] 
            if task['maintenance_type'] == tr("calibration") and task['status'] == tr("completed")
        ])
        
        if not calibration_history.empty:
            # Sort by created_at (newest first)
            calibration_history = calibration_history.sort_values('created_at', ascending=False)
            
            st.dataframe(
                calibration_history,
                column_config={
                    'asset_name': tr("sensor_name"),
                    'schedule_date': st.column_config.DateColumn(tr("date"), format="DD/MM/YYYY"),
                    'notes': tr("details"),
                    'technician': tr("performed_by")
                },
                hide_index=True,
                column_order=['asset_name', 'schedule_date', 'notes', 'technician']
            )
        else:
            st.info(tr("no_calibration_history"))
    else:
        st.info(tr("no_maintenance_history"))

elif maintenance_option == tr("historical_maintenance"):
    st.header(tr("historical_maintenance"))
    
    # Filter controls
    st.sidebar.subheader(tr("filters"))
    
    # Filter by date range
    start_date = st.sidebar.date_input(
        tr("start_date"),
        value=datetime.now().date() - timedelta(days=30),
        max_value=datetime.now().date()
    )
    
    end_date = st.sidebar.date_input(
        tr("end_date"),
        value=datetime.now().date(),
        min_value=start_date,
        max_value=datetime.now().date()
    )
    
    # Filter by asset type
    asset_type_filter = st.sidebar.multiselect(
        tr("asset_type"),
        options=[tr("sensor"), tr("mattress")],
        default=[tr("sensor"), tr("mattress")]
    )
    
    # Filter by maintenance type
    maintenance_type_filter = st.sidebar.multiselect(
        tr("maintenance_type"),
        options=[tr("calibration"), tr("battery_replacement"), tr("firmware_update"), tr("physical_inspection"), tr("cleaning"), tr("sensor_replacement")],
        default=[tr("calibration"), tr("battery_replacement"), tr("firmware_update")]
    )
    
    if st.session_state['maintenance_tasks']:
        # Convert to DataFrame
        maintenance_history = pd.DataFrame(st.session_state['maintenance_tasks'])
        
        # Filter by completion status
        maintenance_history = maintenance_history[maintenance_history['status'] == tr("completed")]
        
        if not maintenance_history.empty:
            # Apply filters
            filtered_history = maintenance_history[
                (pd.to_datetime(maintenance_history['schedule_date']).dt.date >= start_date) &
                (pd.to_datetime(maintenance_history['schedule_date']).dt.date <= end_date) &
                (maintenance_history['asset_type'].isin(asset_type_filter)) &
                (maintenance_history['maintenance_type'].isin(maintenance_type_filter))
            ]
            
            if not filtered_history.empty:
                # Sort by schedule_date (newest first)
                filtered_history = filtered_history.sort_values('schedule_date', ascending=False)
                
                # Group by maintenance type
                maintenance_counts = filtered_history['maintenance_type'].value_counts().reset_index()
                maintenance_counts.columns = ['type', 'count']
                
                # Create a bar chart of maintenance types
                fig = px.bar(
                    maintenance_counts,
                    x='type',
                    y='count',
                    title=tr("maintenance_activities_by_type"),
                    labels={
                        'type': tr('maintenance_type'),
                        'count': tr('number_of_activities')
                    },
                    color='type'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Timeline of maintenance activities
                st.subheader(tr("maintenance_timeline"))
                
                # Format the timeline data
                timeline_data = filtered_history.copy()
                timeline_data['formatted_date'] = pd.to_datetime(timeline_data['schedule_date'])
                
                fig = px.timeline(
                    timeline_data,
                    x_start='formatted_date',
                    x_end='formatted_date',
                    y='asset_name',
                    color='maintenance_type',
                    hover_name='asset_name',
                    hover_data=['maintenance_type', 'technician', 'notes'],
                    title=tr("maintenance_timeline")
                )
                fig.update_yaxes(title=tr('asset'))
                fig.update_xaxes(title=tr('date'))
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed list
                st.subheader(tr("maintenance_details"))
                
                st.dataframe(
                    filtered_history,
                    column_config={
                        'asset_name': tr("asset_name"),
                        'asset_type': tr("asset_type"),
                        'maintenance_type': tr("maintenance_type"),
                        'schedule_date': st.column_config.DateColumn(tr("date"), format="DD/MM/YYYY"),
                        'notes': tr("details"),
                        'technician': tr("performed_by")
                    },
                    hide_index=True,
                    column_order=['schedule_date', 'asset_name', 'asset_type', 'maintenance_type', 'notes', 'technician']
                )
                
                # Export as CSV
                csv = filtered_history.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=tr("export_maintenance_history"),
                    data=csv,
                    file_name=f"maintenance_history_{start_date}_to_{end_date}.csv",
                    mime="text/csv",
                )
            else:
                st.info(tr("no_maintenance_records_for_filters"))
        else:
            st.info(tr("no_completed_maintenance_tasks"))
    else:
        st.info(tr("no_maintenance_history"))

# Footer
st.markdown("---")
st.caption(f"© {datetime.now().year} MediMat Monitor - {tr('version')} 1.0.0")
