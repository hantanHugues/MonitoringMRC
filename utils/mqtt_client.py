import paho.mqtt.client as mqtt
import json
import time
import logging
import threading
import streamlit as st

class MQTTClient:
    """
    MQTT Client for connecting to a broker and handling sensor data
    """
    def __init__(self, client_id, host="localhost", port=1883, 
                 username=None, password=None, topic_prefix="hospital/mattress/"):
        """
        Initialize MQTT client
        
        Parameters:
        - client_id: Unique identifier for this client
        - host: MQTT broker hostname or IP
        - port: MQTT broker port
        - username: Username for broker authentication (optional)
        - password: Password for broker authentication (optional)
        - topic_prefix: Prefix for MQTT topics to subscribe to
        """
        self.client_id = client_id
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic_prefix = topic_prefix
        self.client = mqtt.Client(client_id=client_id)
        self.connected = False
        self.latest_data = {}
        self.callbacks = []
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("mqtt_client")
        
        # Set up callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Set up authentication if provided
        if username and password:
            self.client.username_pw_set(username, password)
    
    def connect(self):
        """
        Connect to the MQTT broker
        """
        try:
            self.logger.info(f"Connecting to MQTT broker {self.host}:{self.port}")
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """
        Disconnect from the MQTT broker
        """
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        self.logger.info("Disconnected from MQTT broker")
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the broker
        """
        if rc == 0:
            self.connected = True
            self.logger.info("Connected to MQTT broker")
            
            # Subscribe to all mattress/sensor topics
            self.client.subscribe(f"{self.topic_prefix}#")
            self.logger.info(f"Subscribed to {self.topic_prefix}#")
        else:
            self.connected = False
            self.logger.error(f"Connection failed with code {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """
        Callback for when the client disconnects from the broker
        """
        self.connected = False
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection, code {rc}")
        else:
            self.logger.info("Disconnected from broker")
    
    def on_message(self, client, userdata, msg):
        """
        Callback for when a message is received from the broker
        """
        try:
            # Parse the topic to extract mattress and sensor IDs
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 3:
                mattress_id = topic_parts[-2]
                sensor_id = topic_parts[-1]
                
                # Parse the message payload as JSON
                payload = json.loads(msg.payload.decode())
                
                # Store the latest data
                if mattress_id not in self.latest_data:
                    self.latest_data[mattress_id] = {}
                
                self.latest_data[mattress_id][sensor_id] = {
                    'timestamp': time.time(),
                    'data': payload
                }
                
                # Call registered callbacks
                for callback in self.callbacks:
                    callback(mattress_id, sensor_id, payload)
                
                self.logger.debug(f"Received data for mattress {mattress_id}, sensor {sensor_id}")
            
        except json.JSONDecodeError:
            self.logger.warning(f"Received invalid JSON: {msg.payload}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def publish(self, topic, payload, qos=0, retain=False):
        """
        Publish a message to the MQTT broker
        
        Parameters:
        - topic: MQTT topic to publish to
        - payload: Message payload (will be converted to JSON)
        - qos: Quality of Service level
        - retain: Whether the broker should retain the message
        """
        if not self.connected:
            self.logger.warning("Cannot publish: not connected to broker")
            return False
        
        try:
            # Convert payload to JSON
            if isinstance(payload, (dict, list)):
                json_payload = json.dumps(payload)
            else:
                json_payload = str(payload)
            
            # Publish the message
            result = self.client.publish(topic, json_payload, qos, retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published to {topic}: {json_payload}")
                return True
            else:
                self.logger.warning(f"Failed to publish to {topic}, code {result.rc}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error publishing message: {e}")
            return False
    
    def register_callback(self, callback):
        """
        Register a callback function to be called when new data is received
        
        Parameters:
        - callback: Function that takes (mattress_id, sensor_id, data) as parameters
        """
        self.callbacks.append(callback)
    
    def get_latest_data(self, mattress_id=None, sensor_id=None):
        """
        Get the latest data received from sensors
        
        Parameters:
        - mattress_id: Optional, filter by mattress ID
        - sensor_id: Optional, filter by sensor ID (requires mattress_id)
        
        Returns:
        - Dictionary of the latest data
        """
        if mattress_id is None:
            return self.latest_data
        
        if mattress_id not in self.latest_data:
            return {}
        
        if sensor_id is None:
            return self.latest_data[mattress_id]
        
        if sensor_id not in self.latest_data[mattress_id]:
            return {}
        
        return self.latest_data[mattress_id][sensor_id]
    
    def send_command(self, mattress_id, sensor_id, command, params=None):
        """
        Send a command to a specific sensor
        
        Parameters:
        - mattress_id: ID of the mattress
        - sensor_id: ID of the sensor
        - command: Command to send
        - params: Optional parameters for the command
        
        Returns:
        - True if command was sent successfully, False otherwise
        """
        if params is None:
            params = {}
        
        payload = {
            'command': command,
            'params': params,
            'timestamp': time.time()
        }
        
        topic = f"{self.topic_prefix}{mattress_id}/{sensor_id}/command"
        return self.publish(topic, payload)
