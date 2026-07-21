# Compound Risk Detection Engine

## Description
Detects dangerous combinations of conditions that no single sensor would flag alone. This is the core innovation of the platform.

## Technical Requirements
- **Framework**: Python with asyncio for concurrent monitoring
- **Multi-Agent Coordination**: Each agent monitors one data source
- **Detection Logic**:
  - Sensor Agent: Detect gas concentration rising >2% per minute
  - Permit Agent: Check if "Hot Work" permit is active in same zone
  - Maintenance Agent: Verify if equipment is in maintenance mode
  - **COMPOUND RISK** = Gas_Rising + Hot_Work_Active + Maintenance_Active

## Implementation Steps
1. Create `src/backend/agents/sensor_agent.py` - monitors gas levels with simulated data
2. Create `src/backend/agents/permit_agent.py` - tracks active permits from JSON
3. Create `src/backend/agents/maintenance_agent.py` - checks equipment status
4. Create `src/backend/agents/risk_engine.py` - correlates all three and computes risk score
5. Use WebSocket for real-time risk updates

## Deliverables
- Working compound risk detection engine
- Unit tests for each agent
- API endpoint for risk scores
- WebSocket for real-time alerts
