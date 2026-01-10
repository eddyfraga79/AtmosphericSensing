import time
import board
import busio
import adafruit_bme680

class BME688Sensor:
    """
    Wrapper class for the Adafruit CircuitPython BME688 driver.
    Provides temperature, humidity, pressure, gas resistance,
    and a simple Air Quality Index (0-100).
    """

    def __init__(self, measurement_interval=5, verbose=False, i2c_bus=None, address=0x77):
        """
        Initialize the BME688 sensor.
        :param measurement_interval: Minimum seconds between readings.
        :param verbose: Print debug info
        :param i2c_bus: Optional I2C bus object. Defaults to board.I2C()
        :param address: I2C address (usually 0x77 or 0x76)
        """
        self.measurement_interval = measurement_interval
        self._last_measurement = 0
        self.verbose = verbose
        self.bme688 = None
        self._baseline_gas = None  # will store initial "clean air" baseline

        try:
            self.i2c = i2c_bus if i2c_bus else board.I2C()
            self.bme688 = adafruit_bme680.Adafruit_BME680_I2C(self.i2c, address=address)
            self.bme688.sea_level_pressure = 1013.25

            # Take the first reading as a baseline for AQI
            self._baseline_gas = 100000 # Evaluated by experimentation
            if self.verbose:
                print(f"[BME688] Sensor detected. Baseline gas: {self._baseline_gas} Ω")
        except Exception as e:
            print(f"[BME688 ERROR] Sensor not detected or failed to initialize: {e}")
            self.bme688 = None

    # ───────────────────────────────
    # Reading Methods
    # ───────────────────────────────
    def read_data(self):
        """
        Read temperature (C), humidity (%RH), pressure (hPa),
        gas resistance (Ohms), and calculate a simple Air Quality Index (0-100).
        Returns None if sensor missing or data not ready.
        """
        if self.bme688 is None:
            if self.verbose:
                print("[BME688 WARNING] No sensor detected. Cannot read data.")
            return None

        current_time = time.time()
        if current_time - self._last_measurement < self.measurement_interval:
            if self.verbose:
                print("[BME688 WARNING] Measurement sample delay too short")
            return None

        try:
            gas = self.bme688.gas
            # Compute AQI: higher resistance = cleaner air
            aqi = self._calculate_aqi(gas)

            data = {
                "temperature": round(self.bme688.temperature, 2),
                "humidity": round(self.bme688.relative_humidity, 2),
                "pressure": round(self.bme688.pressure, 2),
                "gas": gas,
                "aqi": aqi    #air_quality_index
            }
            if self.verbose:
                print(data)
            self._last_measurement = current_time
            return data
        except Exception as e:
            print(f"[BME688 ERROR] Failed to read data: {e}")
            return None

    # ───────────────────────────────
    # Convenience methods for individual readings
    # ───────────────────────────────
    def get_temperature(self):
        data = self.read_data()
        return data["temperature"] if data else None

    def get_humidity(self):
        data = self.read_data()
        return data["humidity"] if data else None

    def get_pressure(self):
        data = self.read_data()
        return data["pressure"] if data else None

    def get_gas(self):
        data = self.read_data()
        return data["gas"] if data else None

    def get_aqi(self):
        data = self.read_data()
        return data["aqi"] if data else None

    # ───────────────────────────────
    # Utility Methods
    # ───────────────────────────────
    @property
    def detected(self):
        """Return True if the sensor was successfully initialized."""
        return self.bme688 is not None

    def stop_measurement(self):
        """
        Stop periodic measurement.
        BME688 is read-on-demand, so this just provides a placeholder
        for symmetry with other sensor classes like SCD4x.
        """
        if self.verbose:
            print("[BME688] Stop measurement called (sensor is read-on-demand).")
        # If you later implement background threads for measurement,
        # you could set a flag here to stop them.

    # ───────────────────────────────
    # Private helper for AQI calculation
    # ───────────────────────────────
    def _calculate_aqi(self, gas_resistance):
        """
        Simple Air Quality Index (0-100) based on gas resistance.
        Higher resistance = cleaner air (AQI closer to 100)
        """
        if self._baseline_gas is None or gas_resistance is None:
            return None

        aqi = int((gas_resistance / self._baseline_gas) * 100)
        # Clamp to 0-100
        aqi = max(0, min(100, aqi))
        return aqi
