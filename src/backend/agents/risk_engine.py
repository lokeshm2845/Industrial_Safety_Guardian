import os
from .sensor_agent import SensorAgent
from .permit_agent import PermitAgent
from .maintenance_agent import MaintenanceAgent

class RiskEngine:
    def __init__(self, sensor_data_path=None, permits_data_path=None):
        self.sensor_agent = SensorAgent(data_path=sensor_data_path)
        self.permit_agent = PermitAgent(data_path=permits_data_path)
        self.maintenance_agent = MaintenanceAgent(permits_data_path=permits_data_path)

    def evaluate_risk(self, zone: str, up_to_time: str = None, overrides: dict = None):
        """
        Evaluate and calculate compound safety risk score (0.0 to 1.0) for a zone.
        Formula factors:
        - Active Hot Work Permit: +0.2
        - Active Maintenance Mode: +0.1
        - Missing Lockout-Tagout (LOTO) while in maintenance: +0.2
        - Gas level absolute limits (pre-alarm or alarm thresholds): up to +0.5
        - Rapidly rising gas concentration (>2% per minute): +0.3
        
        Supports simulated overrides for testing custom scenarios.
        """
        score = 0.0
        reasons = []

        if overrides is not None:
            # Simulation override mode
            has_hot = overrides.get("has_hot_work", False)
            hot_permit_id = "SIM-PERMIT-HOT"
            hot_desc = "Simulated Hot Work permit"
            
            in_maint = overrides.get("in_maintenance", False)
            maint_equip_ids = ["SIM-EQUIP-1"]
            
            loto_ok = overrides.get("loto_compliant", True)
            
            co_val = overrides.get("co_level", 0.0)
            co_rising = overrides.get("co_rising", False)
            co_rate = overrides.get("co_rate", 0.0)
            
            lel_val = overrides.get("lel_level", 0.0)
            lel_rising = overrides.get("lel_rising", False)
            lel_rate = overrides.get("lel_rate", 0.0)
            
            h2s_val = overrides.get("h2s_level", 0.0)
            h2s_rising = overrides.get("h2s_rising", False)
            h2s_rate = overrides.get("h2s_rate", 0.0)
            
            o2_val = overrides.get("o2_level", 20.9)
            o2_falling = overrides.get("o2_falling", False)
            o2_rate = overrides.get("o2_rate", 0.0)
        else:
            # Live evaluation mode
            # 1. Hot Work permit check
            has_hot, hot_permit = self.permit_agent.has_hot_work(zone)
            hot_permit_id = hot_permit["permit_id"] if has_hot else None
            hot_desc = hot_permit.get("description", "No description") if has_hot else ""

            # 2. Maintenance and LOTO check
            in_maint, maint_permits = self.maintenance_agent.is_equipment_in_maintenance(zone)
            maint_equip_ids = [p['equipment_id'] for p in maint_permits] if in_maint else []
            
            loto_ok = True
            if in_maint:
                loto_status_ok, missing_loto = self.maintenance_agent.verify_loto_applied(zone)
                if not loto_status_ok:
                    loto_ok = False

            # 3. Gas sensor telemetry analysis
            co_trend = self.sensor_agent.evaluate_trend(zone, "CO", up_to_time=up_to_time)
            lel_trend = self.sensor_agent.evaluate_trend(zone, "LEL", up_to_time=up_to_time)
            h2s_trend = self.sensor_agent.evaluate_trend(zone, "H2S", up_to_time=up_to_time)
            o2_trend = self.sensor_agent.evaluate_trend(zone, "O2", up_to_time=up_to_time)

            co_val = co_trend["latest_value"]
            co_rising = co_trend["is_rising_rapidly"]
            co_rate = co_trend["rate_of_increase_pct_per_min"]
            
            lel_val = lel_trend["latest_value"]
            lel_rising = lel_trend["is_rising_rapidly"]
            lel_rate = lel_trend["rate_of_increase_pct_per_min"]
            
            h2s_val = h2s_trend["latest_value"]
            h2s_rising = h2s_trend["is_rising_rapidly"]
            h2s_rate = h2s_trend["rate_of_increase_pct_per_min"]
            
            o2_val = o2_trend["latest_value"] if o2_trend["latest_value"] > 0.0 else 20.9
            # O2 drops rapidly if rate of change is negative and significant
            o2_falling = o2_trend["rate_of_increase_pct_per_min"] < -0.5
            o2_rate = o2_trend["rate_of_increase_pct_per_min"]

        # Calculate contributions
        # 1. Hot Work permit
        if has_hot:
            score += 0.2
            reasons.append(f"Active Hot Work permit ({hot_permit_id}: {hot_desc})")

        # 2. Maintenance and LOTO
        if in_maint:
            score += 0.1
            reasons.append(f"Equipment under active maintenance ({', '.join(maint_equip_ids)})")
            
            if not loto_ok:
                score += 0.2
                reasons.append(f"WARNING: Lockout-Tagout (LOTO) not applied for equipment under maintenance!")

        # 3. Gas Level contribution
        gas_contrib = 0.0
        
        # Check emergency thresholds
        if co_val >= 50.0 or lel_val >= 20.0 or h2s_val >= 10.0 or o2_val <= 19.5:
            gas_contrib = 0.5
            breaches = []
            if co_val >= 50.0: breaches.append(f"CO: {co_val} ppm")
            if lel_val >= 20.0: breaches.append(f"LEL: {lel_val}%")
            if h2s_val >= 10.0: breaches.append(f"H2S: {h2s_val} ppm")
            if o2_val <= 19.5: breaches.append(f"O2 Deficiency: {o2_val}%")
            reasons.append(f"CRITICAL: Gas alarm threshold breached ({', '.join(breaches)})")
        
        # Check pre-alarm thresholds
        elif co_val >= 25.0 or lel_val >= 10.0 or h2s_val >= 5.0 or o2_val <= 20.0:
            gas_contrib = 0.3
            warnings = []
            if co_val >= 25.0: warnings.append(f"CO: {co_val} ppm")
            if lel_val >= 10.0: warnings.append(f"LEL: {lel_val}%")
            if h2s_val >= 5.0: warnings.append(f"H2S: {h2s_val} ppm")
            if o2_val <= 20.0: warnings.append(f"O2 Low: {o2_val}%")
            reasons.append(f"WARNING: Gas pre-alarm threshold reached ({', '.join(warnings)})")
        
        # Check minor presence
        elif co_val > 10.0 or lel_val > 5.0 or h2s_val > 2.0 or o2_val < 20.8:
            gas_contrib = 0.1
            elevations = []
            if co_val > 10.0: elevations.append(f"CO: {co_val} ppm")
            if lel_val > 5.0: elevations.append(f"LEL: {lel_val}%")
            if h2s_val > 2.0: elevations.append(f"H2S: {h2s_val} ppm")
            if o2_val < 20.8: elevations.append(f"O2: {o2_val}%")
            reasons.append(f"ELEVATED: Minor gas presence detected ({', '.join(elevations)})")

        score += gas_contrib

        # Gas Rate-of-Increase trend contribution (or O2 falling)
        has_rapid_trend = co_rising or lel_rising or h2s_rising or o2_falling
        if has_rapid_trend:
            score += 0.3
            trends = []
            if co_rising:
                trends.append(f"CO rising at {co_rate}%/min")
            if lel_rising:
                trends.append(f"LEL rising at {lel_rate}%/min")
            if h2s_rising:
                trends.append(f"H2S rising at {h2s_rate}%/min")
            if o2_falling:
                trends.append(f"O2 falling at {abs(o2_rate)}%/min")
            reasons.append(f"ALERT: Rapidly rising gas trend: {', '.join(trends)}")

        # Cap safety risk score at 1.0
        final_score = round(min(1.0, score), 2)

        return {
            "zone": zone,
            "risk_score": final_score,
            "reasons": reasons,
            "breakdown": {
                "hot_work": 0.2 if has_hot else 0.0,
                "maintenance": 0.1 if in_maint else 0.0,
                "loto_breach": 0.2 if (in_maint and not loto_ok) else 0.0,
                "gas_threshold": gas_contrib,
                "gas_trend": 0.3 if has_rapid_trend else 0.0
            },
            "metrics": {
                "co_level": co_val,
                "co_rate_pct": co_rate,
                "lel_level": lel_val,
                "lel_rate_pct": lel_rate,
                "h2s_level": h2s_val,
                "h2s_rate_pct": h2s_rate,
                "o2_level": o2_val,
                "o2_rate_pct": o2_rate,
                "has_hot_work": has_hot,
                "in_maintenance": in_maint,
                "loto_compliant": loto_ok if in_maint else True
            }
        }

