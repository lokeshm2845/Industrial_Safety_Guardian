import json
import os

class MaintenanceAgent:
    def __init__(self, permits_data_path=None):
        if permits_data_path is None:
            permits_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/sample_permits.json"))
        self.permits_data_path = permits_data_path
        self.permits = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.permits_data_path):
            with open(self.permits_data_path, "r") as f:
                self.permits = json.load(f)
        else:
            self.permits = []

    def is_equipment_in_maintenance(self, zone: str, equipment_id: str = None):
        """
        Check if any equipment in the zone is undergoing active maintenance.
        """
        active_permits = [p for p in self.permits if p["zone"] == zone and p["status"] == "Active"]
        if equipment_id:
            active_permits = [p for p in active_permits if p["equipment_id"] == equipment_id]
        
        return len(active_permits) > 0, active_permits

    def verify_loto_applied(self, zone: str, equipment_id: str = None):
        """
        Verify if Lockout-Tagout (LOTO) is applied for equipment undergoing active maintenance.
        Returns a tuple: (bool_status, details_list)
        """
        in_maint, permits = self.is_equipment_in_maintenance(zone, equipment_id)
        if not in_maint:
            return True, []

        missing_loto = []
        applied_loto = []
        for p in permits:
            if p.get("loto_status") == "Applied":
                applied_loto.append(p)
            else:
                missing_loto.append(p)
        
        if len(missing_loto) > 0:
            return False, missing_loto
        return True, applied_loto
