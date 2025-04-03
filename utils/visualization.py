import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_gauge_chart(value, title, suffix="", min_value=0, max_value=100):
    """
    Creates a gauge chart for sensor readings
    
    Parameters:
    - value: The value to display on the gauge
    - title: Title of the gauge
    - suffix: Units to display after the value (e.g., "%", "°C")
    - min_value: Minimum value on the gauge
    - max_value: Maximum value on the gauge
    
    Returns:
    - Plotly figure object
    """
    # Define color thresholds
    if max_value - min_value <= 10:  # For small ranges like 0-10
        threshold_low = min_value + (max_value - min_value) * 0.3
        threshold_high = min_value + (max_value - min_value) * 0.7
    else:
        threshold_low = min_value + (max_value - min_value) * 0.25
        threshold_high = min_value + (max_value - min_value) * 0.75
    
    # Set the color based on value
    if value < threshold_low:
        color = "red"
    elif value > threshold_high:
        color = "green"
    else:
        color = "orange"
    
    # Create the gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [min_value, max_value]},
            'bar': {'color': color},
            'steps': [
                {'range': [min_value, threshold_low], 'color': "lightcoral"},
                {'range': [threshold_low, threshold_high], 'color': "lightyellow"},
                {'range': [threshold_high, max_value], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        },
        number={'suffix': suffix}
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(size=12)
    )
    
    return fig

def create_status_distribution_chart(status_counts):
    """
    Creates a bar chart showing the distribution of sensor statuses
    
    Parameters:
    - status_counts: DataFrame with columns 'status' and 'count'
    
    Returns:
    - Plotly figure object
    """
    # Define colors for each status
    status_colors = {
        'active': '#28a745',      # Green
        'inactive': '#6c757d',    # Gray
        'error': '#dc3545',       # Red
        'maintenance': '#ffc107', # Yellow/Orange
        'calibrating': '#17a2b8'  # Cyan
    }
    
    # Map colors to statuses in the DataFrame
    colors = [status_colors.get(status, '#6c757d') for status in status_counts['status']]
    
    # Create the bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=status_counts['status'],
            y=status_counts['count'],
            marker_color=colors,
            text=status_counts['count'],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title='Sensor Status Distribution',
        xaxis_title='Status',
        yaxis_title='Count',
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

# Battery distribution chart function removed as sensors are now plugged in, not battery-powered

def create_time_series_chart(data, title, sensor_type):
    """
    Creates a time series chart for sensor readings
    
    Parameters:
    - data: DataFrame with columns 'timestamp' and 'value'
    - title: Title of the chart
    - sensor_type: Type of sensor (affects y-axis label and line color)
    
    Returns:
    - Plotly figure object
    """
    # Define y-axis label based on sensor type
    if sensor_type == 'pressure':
        y_label = 'Pressure (mmHg)'
        color = '#1f77b4'  # Blue
    elif sensor_type == 'temperature':
        y_label = 'Temperature (°C)'
        color = '#ff7f0e'  # Orange
    elif sensor_type == 'humidity':
        y_label = 'Humidity (%)'
        color = '#2ca02c'  # Green
    elif sensor_type == 'movement':
        y_label = 'Movement (intensity)'
        color = '#d62728'  # Red
    else:
        y_label = 'Value'
        color = '#1f77b4'  # Blue
    
    # Create the time series chart
    fig = px.line(
        data,
        x='timestamp',
        y='value',
        title=title,
        labels={'timestamp': 'Time', 'value': y_label}
    )
    
    # Update the line style
    fig.update_traces(line=dict(color=color, width=2))
    
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type='date'
        ),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig
