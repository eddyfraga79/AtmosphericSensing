import paho.mqtt.client as mqtt
import ssl
import sys
import os
import json
import threading
import time

class HiveMQ:
    def __init__(
        self,
        broker,
        port=1883,
        username=None,
        password=None,
        client_id="HiveMQ_Client",
        use_tls=True,
        lwt_topic=None,
        lwt_payload="offline",
        lwt_qos=1,
        lwt_retain=True,
        heartbeat_interval=60,
        verbose=False
    ):
        """Initialize the HiveMQ client with connection parameters."""
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.use_tls = use_tls
        self.verbose = verbose
        self.heartbeat_interval = heartbeat_interval
        self.stop_heartbeat = threading.Event()
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv5)

        # Optional TLS for secure connection
        if self.use_tls:
            self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)

        # Optional authentication
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)

        # ──────────────── LWT Setup ────────────────
        if lwt_topic:
            self.lwt_topic = lwt_topic
            self.lwt_payload = lwt_payload
            self.client.will_set(
                topic=self.lwt_topic,
                payload=self.lwt_payload,
                qos=lwt_qos,
                retain=lwt_retain
            )
            if self.verbose:
                print(f"[LWT SET] Will publish '{lwt_payload}' to '{lwt_topic}' if connection lost.")
        else:
            self.lwt_topic = None

        # Attach callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish

    # ───────────────────────────────
    # MQTT Callback functions
    # ───────────────────────────────
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if self.verbose:
            print(f"[CONNECTED] to {self.broker}:{self.port} — reason code: {reason_code}")
        # Publish online status
        if self.lwt_topic:
            self.client.publish(self.lwt_topic, "online", qos=1, retain=True)
        # Start heartbeat thread
        if self.heartbeat_interval > 0 and self.lwt_topic:
            self._start_heartbeat()

    def on_disconnect(self, client, userdata, reason_code, properties=None):
        if self.verbose:
            print(f"[DISCONNECTED] — reason code: {reason_code}")
        # Stop heartbeat
        self.stop_heartbeat.set()

    def on_publish(self, client, userdata, mid, properties=None):
        if self.verbose:
            print(f"[PUBLISHED] message ID: {mid}")

    # ───────────────────────────────
    # Heartbeat mechanism
    # ───────────────────────────────
    def _start_heartbeat(self):
        """Start a background thread that periodically publishes 'alive' messages."""
        def heartbeat_loop():
            if self.verbose:
                print(f"[HEARTBEAT] Started (every {self.heartbeat_interval}s)")
            while not self.stop_heartbeat.is_set():
                try:
                    msg = json.dumps({"status": "alive", "timestamp": time.time()})
                    self.client.publish(self.lwt_topic, msg, qos=0, retain=False)
                    if self.verbose:
                        print(f"[HEARTBEAT] Sent: {msg}")
                except Exception as e:
                    print(f"[HEARTBEAT ERROR] {e}")
                self.stop_heartbeat.wait(self.heartbeat_interval)
            if self.verbose:
                print("[HEARTBEAT] Stopped.")

        self.stop_heartbeat.clear()
        t = threading.Thread(target=heartbeat_loop, daemon=True)
        t.start()

    # ───────────────────────────────
    # Core methods
    # ───────────────────────────────
    def connect_hivemq(self):
        """Connect to the HiveMQ broker."""
        try:
            if self.verbose:
                print(f"Connecting to {self.broker}:{self.port} ...")
            self.client.connect(self.broker, self.port)
            self.client.loop_start()  # Start background loop for network handling
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            self.terminate(force=True)

    def disconnect_hivemq(self):
        """Disconnect from the HiveMQ broker."""
        try:
            # Stop heartbeat first
            self.stop_heartbeat.set()
            # Publish offline before clean disconnect
            if self.lwt_topic:
                self.client.publish(self.lwt_topic, "offline", qos=1, retain=True)
            self.client.loop_stop()
            self.client.disconnect()
            if self.verbose:
                print("[INFO] Disconnected cleanly.")
        except Exception as e:
            print(f"[ERROR] Failed to disconnect: {e}")

    def send_payload_hivemq(self, topic, payload, qos=0, retain=False):
        """Publish a payload to the given topic."""
        try:
            result = self.client.publish(topic, payload, qos=qos, retain=retain)
            status = result[0]
            if status == mqtt.MQTT_ERR_SUCCESS:
                if self.verbose:
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
        """Safely terminate the program."""
        print("[INFO] Terminating program...")
        self.stop_heartbeat.set()
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