import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("test/topic")

def on_message(client, userdata, msg):
    print(f"Received message on {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect("127.0.0.1", 1883, 60)
    print("Connection successful, publishing a test message")
    client.publish("test/topic", "Hello MQTT!")
    client.loop_start()
    time.sleep(5)
    client.loop_stop()
    print("Test completed")
except Exception as e:
    print(f"Error connecting to broker: {e}")