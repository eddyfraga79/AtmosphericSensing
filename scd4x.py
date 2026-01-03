import time
import board
import adafruit_scd4x

class SCD40Sensor:
    """
    Wrapper class for the Adafruit CircuitPython SCD4X driver.
    Supports SCD40 and SCD41 sensors.
    """

    def __init__(self, measurement_interval=5, verbose=False):
        """
        Initialize the SCD40 sensor.
        :param measurement_interval: Minimum seconds between readings.
        """
        self.i2c = board.I2C()  # Uses default I2C pins
        print(self.i2c)
        self.scd4x = adafruit_scd4x.SCD4X(self.i2c)
        self.measurement_interval = measurement_interval
        self._last_measurement = 0
        self.verbose = verbose

        # Start measurement mode
        self.scd4x.start_periodic_measurement()
        print("[SCD40] Sensor initialized and measuring...")

    # ───────────────────────────────
    # Reading Methods
    # ───────────────────────────────
    def read_data(self):
        """
        Read CO2, temperature, and humidity from the sensor.
        Returns a dict like:
        {
            "co2": 415.2,
            "temperature": 22.6,
            "humidity": 44.3
        }
        Returns None if data not ready or on error.
        """
        current_time = time.time()
        if current_time - self._last_measurement < self.measurement_interval:
            print(f"[SCD40 WARNING] Measurement sample delay too short")
            # Avoid reading too frequently
            return None

        if not self.scd4x.data_ready:
            print(f"[SCD40 WARNING] Sensor measurement not ready")
            return None

        try:
            data = {
                "co2": round(self.scd4x.CO2, 2),
                "temperature": round(self.scd4x.temperature, 2),
                "humidity": round(self.scd4x.relative_humidity, 2)
            }
            if self.verbose == True:
                print(data)
            self._last_measurement = current_time
            return data
        except Exception as e:
            print(f"[SCD40 ERROR] Failed to read data: {e}")
            return None

    def get_co2(self):
        """Return only the CO2 value (ppm)."""
        data = self.read_data()
        return data["co2"] if data else None

    def get_temperature(self):
        """Return only the temperature (°C)."""
        data = self.read_data()
        return data["temperature"] if data else None

    def get_humidity(self):
        """Return only the humidity (%RH)."""
        data = self.read_data()
        return data["humidity"] if data else None

    # ───────────────────────────────
    # Utility Methods
    # ───────────────────────────────
    def stop_measurement(self):
        """Stop periodic measurement."""
        try:
            self.scd4x.stop_periodic_measurement()
            print("[SCD40] Measurement stopped.")
        except Exception as e:
            print(f"[SCD40 ERROR] Could not stop measurement: {e}")