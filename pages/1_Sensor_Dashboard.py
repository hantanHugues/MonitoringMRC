import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from utils.sensor_utils import get_sensor_status_color, get_battery_level_color
from utils.visualization import create_status_distribution_chart, create_battery_distribution_chart
from utils.translation import get_translation
from utils.data_manager import get_sensors_data, get_sensor_types

# Page configuration
st.set_page_config(
    page_title="Sensor Dashboard - Medical Mattress Monitoring",
    page_icon="🔌",
    layout="wide"
)

# Header
tr = lambda key: get_translation(key, st.session_state.language)
st.title(tr("sensor_dashboard_title"))
st.markdown(tr("sensor_dashboard_description"))

# Get sensors data
sensors_data = get_sensors_data()
sensor_types = get_sensor_types()

# Filter controls
st.sidebar.header(tr("filters"))

# Filter by sensor type
selected_types = st.sidebar.multiselect(
    tr("filter_by_type"),
    options=sensor_types,
    default=sensor_types
)

# Filter by status
status_options = ['active', 'inactive', 'maintenance', 'error']
selected_statuses = st.sidebar.multiselect(
    tr("filter_by_status"),
    options=status_options,
    default=['active', 'error']
)

# Filter by battery level
min_battery, max_battery = st.sidebar.slider(
    tr("filter_by_battery"),
    0, 100, (0, 100)
)

# Apply filters
filtered_sensors = sensors_data[
    (sensors_data['type'].isin(selected_types)) &
    (sensors_data['status'].isin(selected_statuses)) &
    (sensors_data['battery_level'] >= min_battery) &
    (sensors_data['battery_level'] <= max_battery)
]

# Refresh button
if st.sidebar.button(tr("refresh_data")):
    st.rerun()

# Show last update time
st.sidebar.info(f"{tr('last_update')}: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

# Main dashboard content in two columns
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader(tr("sensor_overview"))
    
    # Show key metrics
    total_sensors = len(filtered_sensors)
    active_sensors = filtered_sensors[filtered_sensors['status'] == 'active'].shape[0]
    error_sensors = filtered_sensors[filtered_sensors['status'] == 'error'].shape[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric(tr("total_filtered_sensors"), total_sensors)
    col2.metric(tr("active_sensors"), active_sensors, f"{round(active_sensors/total_sensors*100)}%" if total_sensors > 0 else "N/A")
    col3.metric(tr("error_sensors"), error_sensors, help=tr("sensors_in_error_state"))
    
    # Status distribution chart
    if not filtered_sensors.empty:
        status_counts = filtered_sensors['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        fig = create_status_distribution_chart(status_counts)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(tr("no_sensors_match_criteria"))
    
    # Battery level distribution
    if not filtered_sensors.empty:
        st.subheader(tr("battery_levels"))
        
        fig = create_battery_distribution_chart(filtered_sensors)
        st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader(tr("sensor_types_distribution"))
    
    # Sensor types pie chart
    if not filtered_sensors.empty:
        type_counts = filtered_sensors['type'].value_counts().reset_index()
        type_counts.columns = ['type', 'count']
        
        fig = px.pie(
            type_counts, 
            values='count', 
            names='type',
            title=tr("sensor_types_distribution"),
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Signal strength overview
    st.subheader(tr("signal_strength"))
    
    if not filtered_sensors.empty:
        # Create a horizontal bar chart for signal strength by sensor type
        avg_signal = filtered_sensors.groupby('type')['signal_strength'].mean().reset_index()
        
        fig = px.bar(
            avg_signal,
            x='signal_strength',
            y='type',
            orientation='h',
            labels={
                'signal_strength': tr('avg_signal_strength'),
                'type': tr('sensor_type')
            },
            title=tr('avg_signal_by_type'),
            color='signal_strength',
            color_continuous_scale='blues',
            range_color=[0, 10]
        )
        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        
        st.plotly_chart(fig, use_container_width=True)

# Display the sensor table
st.subheader(tr("sensors_list"))

if not filtered_sensors.empty:
    # Add colored status indicator to the dataframe
    def format_status(status):
        color = get_sensor_status_color(status)
        return f'<span style="color:{color};font-weight:bold;">{status.upper()}</span>'
    
    def format_battery(battery):
        color = get_battery_level_color(battery)
        return f'<span style="color:{color};">{battery}%</span>'
    
    # Format the dataframe for display
    display_df = filtered_sensors.copy()
    display_df['formatted_status'] = display_df['status'].apply(format_status)
    display_df['formatted_battery'] = display_df['battery_level'].apply(format_battery)
    
    # Select columns to display
    display_cols = ['id', 'name', 'type', 'formatted_status', 'formatted_battery', 'signal_strength', 'last_maintenance']
    
    # Display as HTML to show colored status
    st.write(
        display_df[display_cols].to_html(
            escape=False, 
            index=False,
            columns=['id', 'name', 'type', 'formatted_status', 'formatted_battery', 'signal_strength', 'last_maintenance'],
            col_space=100
        ),
        unsafe_allow_html=True
    )
    
    # Add a download button for the filtered data
    csv = filtered_sensors.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=tr("download_csv"),
        data=csv,
        file_name=f"sensors_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
else:
    st.warning(tr("no_sensors_match_criteria"))

# Footer
st.markdown("---")
st.caption(f"© {datetime.now().year} MediMat Monitor - {tr('version')} 1.0.0")
