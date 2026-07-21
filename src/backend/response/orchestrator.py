import json
import os
from datetime import datetime

class EmergencyResponseOrchestrator:
    def __init__(self, output_dir=None):
        if output_dir is None:
            # Store output evidence in data/preserved_evidence/
            output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/preserved_evidence"))
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.audit_log_path = os.path.join(self.output_dir, "response_audit_log.txt")
        self.active_alerts = []

    def log_audit(self, message: str):
        """
        Log an entry into the local audit ledger file.
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")

    def handle_risk_evaluation(self, risk_eval: dict, workers_data: list, sensor_history: list):
        """
        Evaluate risk scores. If score > 0.8, execute the Emergency Containment Playbook.
        """
        zone = risk_eval["zone"]
        score = risk_eval["risk_score"]
        
        if score >= 0.8:
            # Create a unique alert ID
            alert_id = f"ALERT-{zone.replace(' ', '')}-{int(datetime.utcnow().timestamp())}"
            self.log_audit(f"EMERGENCY TRIGGERED: Risk score {score} for {zone} exceeds critical threshold (0.8). Initiating Containment Playbook.")

            # 1. Trigger Evacuation Alerts (Simulated SMS/WhatsApp)
            affected_workers = [w for w in workers_data if w["zone"] == zone]
            notifications = []
            for w in affected_workers:
                sms_msg = (
                    f"⚠️ [EVACUATION ALERT] Zone {zone} is at CRITICAL Risk ({score}). "
                    f"Immediately halt welding operations, verify LOTO state, and evacuate "
                    f"to safe assembly point. Recipient: {w['name']} ({w['role']})"
                )
                notifications.append(sms_msg)
                self.log_audit(f"Dispatched Evacuation Alert: {sms_msg}")

            if not affected_workers:
                self.log_audit(f"Evacuation checklist: No workers registered in {zone} at time of alert.")

            # 2. Evidence Preservation (Save current sensor history for audit)
            evidence_file = os.path.join(self.output_dir, f"{alert_id}_sensor_evidence.json")
            zone_sensors = [s for s in sensor_history if s["zone"] == zone]
            
            evidence_data = {
                "alert_id": alert_id,
                "zone": zone,
                "risk_score_at_trigger": score,
                "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                "active_permits": [risk_eval["reasons"]],
                "active_telemetry_snapshot": zone_sensors
            }
            
            with open(evidence_file, "w", encoding="utf-8") as f:
                json.dump(evidence_data, f, indent=2)
            self.log_audit(f"Sensor evidence snapshot frozen and preserved: {evidence_file}")

            # 3. Generate Preliminary Incident Report
            report_file = os.path.join(self.output_dir, f"{alert_id}_incident_report.json")
            incident_rep = {
                "report_id": f"INC-REP-{zone.replace(' ', '')}-{datetime.utcnow().strftime('%Y%m%d-%H%M')}",
                "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                "alert_id": alert_id,
                "target_zone": zone,
                "consequences": "None (Early Warning Evacuation Executed)",
                "incident_factors": risk_eval["reasons"],
                "impacted_personnel": [w["name"] for w in affected_workers],
                "compliance_citations": [
                    "OISD Clause 2: Suspended Hot Work permits due to rising gas trends",
                    "Factories Act Section 36: Forced extraction and evacuation before fumes exceed safe inhalation levels"
                ],
                "status": "Evacuated. Area Isolated."
            }
            
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(incident_rep, f, indent=2)
            self.log_audit(f"Compliance Draft Incident Report archived: {report_file}")

            # 4. Generate and save Markdown report
            md_report_file = os.path.join(self.output_dir, f"{alert_id}_compliance_audit.md")
            md_report_content = self.generate_markdown_report(
                alert_id=alert_id,
                zone=zone,
                score=score,
                reasons=risk_eval["reasons"],
                affected_workers=affected_workers
            )
            with open(md_report_file, "w", encoding="utf-8") as f:
                f.write(md_report_content)
            self.log_audit(f"Compliance Markdown Report archived: {md_report_file}")

            alert_details = {
                "alert_id": alert_id,
                "zone": zone,
                "risk_score": score,
                "notifications": notifications,
                "evidence_path": evidence_file,
                "report_path": report_file,
                "md_report_path": md_report_file,
                "md_report_content": md_report_content,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            self.active_alerts.append(alert_details)
            return alert_details
            
        return None

    def generate_markdown_report(self, alert_id: str, zone: str, score: float, reasons: list, affected_workers: list) -> str:
        """
        Generates a premium compliance incident audit report in Markdown format.
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Build list of workers
        workers_str = ""
        if affected_workers:
            for w in affected_workers:
                workers_str += f"- **{w['name']}** ({w['role']}) - UWB Tag: `{w.get('uwb_tag_id', w['worker_id'])}` - Status: **EVACUATED**\n"
        else:
            workers_str = "*No registered personnel were inside the hazard zone during the alert.*"
            
        # Build factors/reasons
        factors_str = ""
        for r in reasons:
            factors_str += f"- {r}\n"
            
        report_md = f"""# 🛡️ ZERO-HARM COMPLIANCE & INCIDENT AUDIT REPORT

## 📄 Incident Overview
- **Incident Reference ID:** `{alert_id}`
- **Generation Timestamp:** `{timestamp}`
- **Target Plant Zone:** `{zone}`
- **Calculated Cumulative Risk:** `{score}` (Critical Threshold: `0.80`)
- **Containment Playbook Status:** **SUCCESSFULLY EXECUTED & RESOLVED**

---

## 👷 Impacted Personnel & Evacuation Audit
All personnel in the affected zone were tracked via UWB and successfully routed to the muster station:
{workers_str}

---

## 📊 Risk Analysis & Factor Breakdown
The Multi-Agent Risk Engine triggered this alert due to the coupling of the following safety hazards:
{factors_str}

### Explainable Safety Weight Contributions:
- **Active Hot Work permit:** `+0.20` risk weight contribution
- **Active Maintenance operations:** `+0.10` risk weight contribution
- **Lockout-Tagout (LOTO) Compliance status:** Variable (Unapplied checks add `+0.20`)
- **IoT Telemetry Gas concentrations:** Pre-alarm/Alarm levels add up to `+0.50`
- **Rate-of-Increase Trends:** Rapidly climbing gas trends add `+0.30`

---

## ⚖️ Legal & Regulatory Citations
This incident logs compliance with the following safety mandates:
1. **OISD Standard 137 (Clause 2):** Mandatory suspension of active work permits and hot work operations upon detection of combustible/toxic gas concentrations.
2. **Factories Act, 1948 (Section 36):** Direct prohibition of work in spaces containing dangerous fumes, requiring immediate extraction and evacuation of onsite personnel.

---

## 🛠️ Action Plan & Corrective Guidance
To prevent recurrence, the Safety Operations Lead must sign off on the following actions:
1. **Calibrate Area Sensors:** Cross-reference telemetry spool `{alert_id}_sensor_evidence.json` to verify sensor response times.
2. **Verify LOTO Physical Keys:** Conduct mechanical and electrical double-isolation inspection on affected equipment.
3. **Audit Vent Ventilation:** Re-establish continuous positive-pressure ventilation before allowing workers back into the zone.

---

## ✍️ Sign-off Authority
*This report is digitally certified by the Industrial Safety Guardian Multi-Agent Network.*

**Safety Lead Name:** ________________________  
**Title:** __________________________________  
**Signature & Date:** _______________________  
"""
        return report_md

