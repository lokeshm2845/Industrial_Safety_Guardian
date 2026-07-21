import json
import os
from datetime import datetime

class SensorAgent:
    def __init__(self, data_path=None):
        if data_path is None:
            # Walk up to workspace root from src/backend/agents/
            data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/sample_sensor_data.json"))
        self.data_path = data_path
        self.readings = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                self.readings = json.load(f)
        else:
            self.readings = []

    def get_zone_readings(self, zone: str, gas_type: str = "CO"):
        """
        Returns sorted readings by timestamp for a specific zone and gas type.
        """
        zone_data = [r for r in self.readings if r["zone"] == zone and r["gas"] == gas_type]
        return sorted(zone_data, key=lambda x: x["timestamp"])

    def evaluate_trend(self, zone: str, gas_type: str = "CO", up_to_time: str = None, window_size: int = 3):
        """
        Evaluate if gas concentration is rising >2% per minute.
        If up_to_time is provided, only evaluate readings up to that ISO timestamp.
        """
        zone_data = self.get_zone_readings(zone, gas_type)
        
        if up_to_time:
            zone_data = [r for r in zone_data if r["timestamp"] <= up_to_time]
            
        if len(zone_data) < 2:
            latest_val = zone_data[-1]["value"] if len(zone_data) > 0 else 0.0
            unit = zone_data[-1]["unit"] if len(zone_data) > 0 else "ppm"
            return {
                "rate_of_increase_pct_per_min": 0.0,
                "is_rising_rapidly": False,
                "latest_value": latest_val,
                "unit": unit
            }

        latest_readings = zone_data[-window_size:]
        latest = latest_readings[-1]
        earliest = latest_readings[0]

        # Parse timestamps
        t_latest = datetime.fromisoformat(latest["timestamp"].replace("Z", "+00:00"))
        t_earliest = datetime.fromisoformat(earliest["timestamp"].replace("Z", "+00:00"))
        
        duration_minutes = (t_latest - t_earliest).total_seconds() / 60.0
        if duration_minutes <= 0:
            return {
                "rate_of_increase_pct_per_min": 0.0,
                "is_rising_rapidly": False,
                "latest_value": latest["value"],
                "unit": latest["unit"]
            }

        # Percentage increase calculation
        val_earliest = earliest["value"]
        val_latest = latest["value"]
        
        if val_earliest <= 0:
            increase_pct_per_min = (val_latest - val_earliest) * 100.0 / duration_minutes
        else:
            increase_pct = ((val_latest - val_earliest) / val_earliest) * 100.0
            increase_pct_per_min = increase_pct / duration_minutes

        # Trigger if rising trend is positive and exceeds 2% per minute
        is_rising_rapidly = increase_pct_per_min > 2.0
        
        return {
            "rate_of_increase_pct_per_min": round(increase_pct_per_min, 2),
            "is_rising_rapidly": is_rising_rapidly,
            "latest_value": latest["value"],
            "unit": latest["unit"]
        }
