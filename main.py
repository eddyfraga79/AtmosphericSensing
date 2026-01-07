import time
import os
import uuid
from dotenv import load_dotenv
from hivemq import HiveMQ
from scd4x import SCD40Sensor
from database import SensorDatabase

SENSOR_SAMPLE_TIME = 10
DEVICE_MQTT_HEARTBEAT = 10

def updateDisplayData(temperature, humidity, co2):
  display.setColorOrange()
  
  display.set_cursor(0,0)
  display.print(f"H: {int(humidity)}%")

  display.print(f"T: {int(temperature)}C");
  display.set_cursor(9, 0)

  display.print(f"CO2: {int(temperature)}PPM");
  display.set_cursor(2, 1)

def generate_device_id():
    mac = uuid.getnode()
    mac_addr = ''.join(f'{(mac >> ele) & 0xff:02x}' for ele in range(40, -1, -8))
    return str(os.getenv("HIVEMQ_TOPIC_DEVICES")) + mac_addr + "/status"

def main():

    # Load the environment file (.env)
    load_dotenv()

    # Create a new or open database
    db = SensorDatabase()

    # Create a display instance
    # display = LCD1602RGB()

    # Create a sensor instance
    sensor = SCD40Sensor(measurement_interval=SENSOR_SAMPLE_TIME, verbose=False)

    # Create a client instance
    hivemq_client = HiveMQ(
        str(os.getenv("HIVEMQ_URL")), 
        int(os.getenv("HIVEMQ_PORT")), 
        str(os.getenv("HIVEMQ_USERNAME")), 
        str(os.getenv("HIVEMQ_PASSWORD")), 
        use_tls=True, 
        lwt_topic=generate_device_id(),
        heartbeat_interval=DEVICE_MQTT_HEARTBEAT,
        verbose=False
        )

    # Connect to MQTT broker
    hivemq_client.connect_hivemq()

    #Simulate sensor data
    try:
        while True:
            time.sleep(SENSOR_SAMPLE_TIME)
            data = sensor.read_data()
            if data != None :
                # Send data to MQTT broker
                hivemq_client.send_payload_hivemq(str(os.getenv("HIVEMQ_TOPIC_TEMPERATURE")), data['temperature'], qos=0)
                hivemq_client.send_payload_hivemq(str(os.getenv("HIVEMQ_TOPIC_HUMIDITY")), data['humidity'], qos=0)
                hivemq_client.send_payload_hivemq(str(os.getenv("HIVEMQ_TOPIC_CO2")), data['co2'], qos=0)
                
                # Write new sensor data
                db.write_reading(temperature=data['temperature'], humidity=data['humidity'], co2=data['co2'])

                # Update display data
                # updateDisplayData(data['temperature'], data['humidity'], data['co2'])

    except KeyboardInterrupt:
            print("Disconnecting gracefully...")
            hivemq_client.disconnect_hivemq()
            sensor.stop_measurement()
            print("Disconnected")

if __name__ == "__main__":
    main()
