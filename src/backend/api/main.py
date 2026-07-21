import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from ..agents.risk_engine import RiskEngine
from ..rag.retriever import SafetyRetriever
from ..response.orchestrator import EmergencyResponseOrchestrator

app = FastAPI(title="Industrial Safety Guardian API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core safety components
risk_engine = RiskEngine()
retriever = SafetyRetriever()
orchestrator = EmergencyResponseOrchestrator()

# Helper utilities to reload files
def get_workers():
    workers_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/sample_workers.json"))
    if os.path.exists(workers_path):
        with open(workers_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_sensor_data():
    sensor_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/sample_sensor_data.json"))
    if os.path.exists(sensor_path):
        with open(sensor_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_permits():
    permits_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/sample_permits.json"))
    if os.path.exists(permits_path):
        with open(permits_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

class QueryRequest(BaseModel):
    question: str

@app.get("/api/status")
def read_status():
    return {
        "status": "Operational",
        "active_agents": ["pm-agent", "sensor-agent", "permit-agent", "geo-agent", "rag-agent", "response-agent"]
    }

@app.get("/api/zones")
def get_zones_risk(up_to_time: str = Query(None, description="ISO timestamp limit to slice telemetry")):
    zones = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E"]
    results = {}
    
    workers = get_workers()
    sensors = get_sensor_data()
    
    for z in zones:
        eval_res = risk_engine.evaluate_risk(z, up_to_time=up_to_time)
        results[z] = eval_res
        
        # Trigger orchestrator response playbook if risk exceeds critical 0.8
        alert_res = orchestrator.handle_risk_evaluation(eval_res, workers, sensors)
        if alert_res:
            results[z]["alert_triggered"] = True
            results[z]["alert_details"] = alert_res
        else:
            results[z]["alert_triggered"] = False
            
    return results

@app.get("/api/workers")
def read_workers():
    return get_workers()

@app.get("/api/permits")
def read_permits():
    return get_permits()

@app.get("/api/alerts")
def read_active_alerts():
    return {
        "active_alerts": orchestrator.active_alerts,
        "audit_log_path": orchestrator.audit_log_path
    }

@app.post("/api/query")
async def query_rag(request: QueryRequest):
    response = await retriever.answer_safety_query(request.question)
    return response

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Poll risk states and stream updates down to the websocket client
            zones = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E"]
            results = {}
            workers = get_workers()
            sensors = get_sensor_data()
            
            for z in zones:
                eval_res = risk_engine.evaluate_risk(z)
                results[z] = eval_res
                alert_res = orchestrator.handle_risk_evaluation(eval_res, workers, sensors)
                if alert_res:
                    results[z]["alert_triggered"] = True
                    results[z]["alert_details"] = alert_res
            
            await websocket.send_json(results)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
