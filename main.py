import time
import os
import uuid
from dotenv import load_dotenv
from hivemq import HiveMQ
from scd4x import SCD40Sensor
from bme688 import BME688Sensor
from database import SensorDatabase

SYSTEM_HEARTBEAT = 10

def initialize_sensor(SYSTEM_HEARTBEAT):
    """
    Try to initialize SCD40 first, then BME688 if SCD40 is not detected.
    Returns a sensor object that was successfully detected.
    Exits the program if no sensor is found.
    """
    # Try SCD40 first
    sensor = SCD40Sensor(measurement_interval=SYSTEM_HEARTBEAT, verbose=False)
    if sensor.detected:
        print("SCD4x sensor detected and ready.")
        return sensor

    # Try BME688 next
    sensor = BME688Sensor(measurement_interval=SYSTEM_HEARTBEAT, verbose=False)
    if sensor.detected:
        print("BME688 sensor detected and ready.")
        return sensor

    # No sensor detected
    print("No supported sensors detected! Exiting...")
    exit(1)


def publish_sensor_data(hivemq_client, sensor_data):
    """
    Send sensor readings to MQTT broker if the data exists.
    Supports temperature, humidity, CO2, and AQI.
    """
    if sensor_data is None:
        return  # nothing to do

    # Temperature
    temp = sensor_data.get("temperature")
    if temp is not None:
        hivemq_client.send_payload_hivemq(str(os.getenv("HIVEMQ_TOPIC_TEMPERATURE")), temp, qos=0)

    # Humidity
    humidity = sensor_data.get("humidity")
    if humidity is not None:
        hivemq_client.send_payload_hivemq(str(os.getenv("HIVEMQ_TOPIC_HUMIDITY")), humidity, qos=0)

    # CO2 (may not exist on all sensors)
    co2 = sensor_data.get("co2")
    if co2 is not None:
        hivemq_client.send_payload_hivemq(str(os.getenv("HIVEMQ_TOPIC_CO2")), co2, qos=0)

    # AQI (may not exist on all sensors)
    aqi = sensor_data.get("aqi")
    if aqi is not None:
        hivemq_client.send_payload_hivemq(str(os.getenv("HIVEMQ_TOPIC_AQI")), aqi, qos=0)

def process_sensor_data(sensor, hivemq_client, db):
    """
    Read sensor data, send to MQTT, and write to database.
    """
    data = sensor.read_data()
    if data is None:
        return  # nothing to do

    # --- MQTT publishing ---
    publish_sensor_data(hivemq_client, data)

    # --- Database writing ---
    db.write_reading(
        temperature=data.get('temperature'),
        humidity=data.get('humidity'),
        co2=data.get('co2'),
        aqi=data.get('aqi')
    )

def main():

    # Load the environment file (.env)
    load_dotenv()

    # Create a new or open database
    db = SensorDatabase()

    # Initialize available sensor
    sensor = initialize_sensor(SYSTEM_HEARTBEAT)

    # Create a client instance
    hivemq_client = HiveMQ(
        broker=str(os.getenv("HIVEMQ_URL")), 
        port=int(os.getenv("HIVEMQ_PORT")), 
        username=str(os.getenv("HIVEMQ_USERNAME")), 
        password=str(os.getenv("HIVEMQ_PASSWORD")), 
        client_id=str(os.getenv("IOT_DEVICE_NAME")),
        use_tls=True, 
        lwt_topic=str(os.getenv("HIVEMQ_TOPIC_DEVICES")) + str(os.getenv("IOT_DEVICE_NAME")) + "/status",
        heartbeat_interval=SYSTEM_HEARTBEAT,
        verbose=False
        )

    # Connect to MQTT broker
    hivemq_client.connect_hivemq()

    #Process sensor data
    try:
        while True:
            time.sleep(SYSTEM_HEARTBEAT)
            process_sensor_data(sensor, hivemq_client, db)
    except KeyboardInterrupt:
            print("Disconnecting gracefully...")
            hivemq_client.disconnect_hivemq()
            sensor.stop_measurement()
            print("Disconnected")

if __name__ == "__main__":
    main()

