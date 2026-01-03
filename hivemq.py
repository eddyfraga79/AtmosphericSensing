import paho.mqtt.client as mqtt
import ssl
import sys
import os

class HiveMQ:
    def __init__(self, broker, port=1883, username=None, password=None, client_id="HiveMQ_Client", use_tls=True, verbose=False):
        """Initialize the HiveMQ client with connection parameters."""
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.use_tls = use_tls
        self.verbose = verbose
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv5)

        # Optional TLS for secure connection
        if self.use_tls:
            self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)

        # Optional authentication
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        # Attach callbacks (for logging/debugging)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

    # ───────────────────────────────
    # MQTT Callback functions
    # ───────────────────────────────
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if self.verbose == True:
            print(f"[CONNECTED] to {self.broker}:{self.port} — reason code: {reason_code}")

    def on_disconnect(self, client, userdata, reason_code, properties=None):
        if self.verbose == True:
            print(f"[DISCONNECTED] — reason code: {reason_code}")

    def on_publish(self, client, userdata, mid, properties=None):
        if self.verbose == True:
            print(f"[PUBLISHED] message ID: {mid}")

    # ───────────────────────────────
    # Core methods
    # ───────────────────────────────
    def connect_hivemq(self):
        """Connect to the HiveMQ broker."""
        try:
            if self.verbose == True:
                print(f"Connecting to {self.broker}:{self.port} ...")
            self.client.connect(self.broker, self.port)
            self.client.loop_start()  # Start background loop for network handling
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            self.terminate(force=True)

    def disconnect_hivemq(self):
        """Disconnect from the HiveMQ broker."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            if self.verbose == True:
                print("[INFO] Disconnected cleanly.")
        except Exception as e:
            print(f"[ERROR] Failed to disconnect: {e}")

    def send_payload_hivemq(self, topic, payload, qos=0, retain=False):
        """Publish a payload to the given topic."""
        try:
            result = self.client.publish(topic, payload, qos=qos, retain=retain)
            status = result[0]
            if status == mqtt.MQTT_ERR_SUCCESS:
                if self.verbose == True:
                    print(f"[INFO] Payload sent to topic '{topic}': {payload}")
            else:
                print(f"[WARNING] Failed to send message to topic {topic}")
        except Exception as e:
            print(f"[ERROR] Publish failed: {e}")
            self.terminate(force=True)

    # ───────────────────────────────
    # Terminate method
    # ───────────────────────────────
    def terminate(self, force=False):
        """
        Safely terminate the program.
        - Closes MQTT connection
        - Stops background loops
        - Exits cleanly (or forcefully)
        """
        print("[INFO] Terminating program...")

        # Attempt a clean disconnect
        try:
            self.disconnect_hivemq()
        except Exception as e:
            print(f"[WARN] Could not disconnect cleanly: {e}")

        if force:
            print("[FORCE EXIT] Killing process immediately.")
            os._exit(1)
        else:
            print("[EXIT] Graceful shutdown.")
            sys.exit(0)

