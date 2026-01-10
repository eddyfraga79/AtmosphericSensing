import sqlite3
from datetime import datetime
from typing import List, Tuple

class SensorDatabase:
    def __init__(self, db_name: str = "sensor_data.db"):
        """Initialize the database connection and ensure the table exists."""
        self.db_name = db_name
        self._create_table()

    def _connect(self):
        """Connect to the SQLite database."""
        return sqlite3.connect(self.db_name)

    def _create_table(self):
        """Create the readings table if it doesn’t already exist."""
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL,
                    co2 REAL,
                    aqi REAL
                );
            """)
            conn.commit()

    def write_reading(self, temperature: float, humidity: float, co2: float = None, aqi: float = None):
        """Insert a new sensor reading into the database."""
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO readings (timestamp, temperature, humidity, co2, aqi) VALUES (?, ?, ?, ?, ?)",
                (timestamp, temperature, humidity, co2, aqi)
            )
            conn.commit()

    def read_all(self) -> List[Tuple]:
        """Return all records from the database."""
        with self._connect() as conn:
            cursor = conn.execute("SELECT * FROM readings ORDER BY timestamp ASC;")
            return cursor.fetchall()

    def read_latest(self, limit: int = 10) -> List[Tuple]:
        """Return the most recent N records."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM readings ORDER BY timestamp DESC LIMIT ?;", 
                (limit,)
            )
            return cursor.fetchall()

    def erase_database(self):
        """Erase all sensor readings from the database."""
        with self._connect() as conn:
            conn.execute("DELETE FROM readings;")
            conn.commit()

    def count_records(self) -> int:
        """Return how many readings are stored."""
        with self._connect() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM readings;")
            (count,) = cursor.fetchone()
            return count
