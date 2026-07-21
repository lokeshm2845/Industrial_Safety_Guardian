import pytest
import os
from src.backend.agents.sensor_agent import SensorAgent
from src.backend.agents.permit_agent import PermitAgent
from src.backend.agents.maintenance_agent import MaintenanceAgent
from src.backend.agents.risk_engine import RiskEngine

def test_sensor_agent_trend():
    agent = SensorAgent()
    # Override readings with a clear rapid rising trend
    agent.readings = [
        {"timestamp": "2026-07-16T23:00:00Z", "zone": "Zone A", "gas": "CO", "value": 2.0, "unit": "ppm"},
        {"timestamp": "2026-07-16T23:05:00Z", "zone": "Zone A", "gas": "CO", "value": 2.2, "unit": "ppm"},
        {"timestamp": "2026-07-16T23:10:00Z", "zone": "Zone A", "gas": "CO", "value": 10.0, "unit": "ppm"}
    ]
    trend = agent.evaluate_trend("Zone A", "CO", window_size=3)
    assert trend["is_rising_rapidly"] is True
    # (10.0 - 2.0)/2.0 * 100 / 10 minutes = 40% per minute increase
    assert trend["rate_of_increase_pct_per_min"] > 2.0

def test_permit_agent_hot_work():
    agent = PermitAgent()
    agent.permits = [
        {"permit_id": "P-101", "zone": "Zone A", "type": "Hot Work", "status": "Active"},
        {"permit_id": "P-102", "zone": "Zone B", "type": "Cold Work", "status": "Active"},
        {"permit_id": "P-103", "zone": "Zone A", "type": "Cold Work", "status": "Pending"}
    ]
    has_hot, permit = agent.has_hot_work("Zone A")
    assert has_hot is True
    assert permit["permit_id"] == "P-101"

    has_hot, permit = agent.has_hot_work("Zone B")
    assert has_hot is False

def test_maintenance_loto_compliance():
    agent = MaintenanceAgent()
    agent.permits = [
        {"permit_id": "P-101", "zone": "Zone A", "equipment_id": "EQ-01", "status": "Active", "loto_status": "Applied"},
        {"permit_id": "P-102", "zone": "Zone B", "equipment_id": "EQ-02", "status": "Active", "loto_status": "Not Applied"}
    ]
    in_maint, permits = agent.is_equipment_in_maintenance("Zone A")
    assert in_maint is True

    loto_ok, missing_loto = agent.verify_loto_applied("Zone A")
    assert loto_ok is True

    loto_ok, missing_loto = agent.verify_loto_applied("Zone B")
    assert loto_ok is False
    assert len(missing_loto) == 1

def test_risk_engine_calculation():
    engine = RiskEngine()
    
    # Setup mock active states
    engine.permit_agent.permits = [
        {"permit_id": "P-101", "zone": "Zone A", "type": "Hot Work", "status": "Active", "equipment_id": "EQ-01", "loto_status": "Applied", "description": "Welding pipe spool"}
    ]
    # Synchronize permits lists across tests
    engine.maintenance_agent.permits = engine.permit_agent.permits
    
    engine.sensor_agent.readings = [
        {"timestamp": "2026-07-16T23:00:00Z", "zone": "Zone A", "gas": "CO", "value": 2.0, "unit": "ppm"},
        {"timestamp": "2026-07-16T23:05:00Z", "zone": "Zone A", "gas": "CO", "value": 2.0, "unit": "ppm"},
        {"timestamp": "2026-07-16T23:10:00Z", "zone": "Zone A", "gas": "CO", "value": 2.0, "unit": "ppm"}
    ]
    
    # 1. Normal state evaluate
    eval_res = engine.evaluate_risk("Zone A")
    # Hot Work (0.2) + Active Maintenance (0.1) + Gas levels normal (no penalty/trend) = 0.30 risk
    assert eval_res["risk_score"] == 0.3
    
    # 2. Escalation evaluate (rising trend and value threshold > 10)
    engine.sensor_agent.readings.append(
        {"timestamp": "2026-07-16T23:15:00Z", "zone": "Zone A", "gas": "CO", "value": 11.5, "unit": "ppm"}
    )
    eval_res2 = engine.evaluate_risk("Zone A")
    # Hot Work (0.2) + Active Maint (0.1) + CO level > 10 (0.1) + Rapid rise trend (0.3) = 0.70 risk
    assert eval_res2["risk_score"] == 0.7
