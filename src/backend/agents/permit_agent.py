import json
import os

class PermitAgent:
    def __init__(self, data_path=None):
        if data_path is None:
            data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/sample_permits.json"))
        self.data_path = data_path
        self.permits = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                self.permits = json.load(f)
        else:
            self.permits = []

    def get_active_permits(self, zone: str):
        """
        Retrieve all permits currently marked as active for a zone.
        """
        return [p for p in self.permits if p["zone"] == zone and p["status"] == "Active"]

    def has_hot_work(self, zone: str):
        """
        Check if any active permit in the zone is 'Hot Work'.
        """
        active_permits = self.get_active_permits(zone)
        for p in active_permits:
            if p["type"].lower() == "hot work":
                return True, p
        return False, None
