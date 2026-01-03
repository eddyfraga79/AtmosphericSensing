import time
import os
from hivemq import HiveMQ
from scd4x import SCD40Sensor
from dotenv import load_dotenv

SENSOR_SAMPLE_TIME = 5

def updateDisplayData(temperature, humidity, co2):
  display.setColorOrange()
  
  display.set_cursor(0,0)
  display.print(f"H: {int(humidity)}%")

  display.print(f"T: {int(temperature)}C");
  display.set_cursor(9, 0)

  display.print(f"CO2: {int(temperature)}PPM");
  display.set_cursor(2, 1)

def main():

    # Load the environment file (.env)
    load_dotenv()

    # Create a display instance
    # display = LCD1602RGB()

    # Create a sensor instance
    sensor = SCD40Sensor(measurement_interval=SENSOR_SAMPLE_TIME, verbose=False)

    # Create a client instance
    hivemq_client = HiveMQ(str(os.getenv("HIVEMQ_URL")), int(os.getenv("HIVEMQ_PORT")), str(os.getenv("HIVEMQ_USERNAME")), str(os.getenv("HIVEMQ_PASSWORD")), use_tls=True, verbose=False)

    # Connect to MQTT broker
    hivemq_client.connect_hivemq()

    #Simulate sensor data
    while True:
        data = sensor.read_data()
        if data != None :
            hivemq_client.send_payload_hivemq(str(os.getenv("HIVEMQ_TOPIC_TEMPERATURE")), data['temperature'], qos=1)
            hivemq_client.send_payload_hivemq(str(os.getenv("HIVEMQ_TOPIC_HUMIDITY")), data['humidity'], qos=1)
            hivemq_client.send_payload_hivemq(str(os.getenv("HIVEMQ_TOPIC_CO2")), data['co2'], qos=1)
            # updateDisplayData(data['temperature'], data['humidity'], data['co2'])

        time.sleep(SENSOR_SAMPLE_TIME)

    hivemq_client.disconnect_hivemq()
    sensor.stop_measurement()

if __name__ == "__main__":
    main()
