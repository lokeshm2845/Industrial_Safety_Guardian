# AI Team Definition: Industrial Safety Guardian

This document defines the specialized agent team roles, operational scopes, and communication protocols for the zero-harm platform.

## Agent Directory

### 1. Product Manager Agent (pm-agent)
- **Role**: Team coordination and requirements supervisor.
- **Responsibilities**:
  - Outlines technical specifications and coordinates workflow phases.
  - Ensures alignment with the hackathon metrics (lead-time improvement, accuracy).
  - Reviews and signs off on component integrations.

### 2. Sensor Intelligence Agent (sensor-agent)
- **Role**: IoT streaming analytics specialist.
- **Responsibilities**:
  - Tracks O2, CO, LEL, and H2S sensor readings.
  - Computes moving window rate-of-increase trends (>2% per minute triggers warnings).
  - Determines anomaly confidence levels.

### 3. Permit & Maintenance Agent (permit-agent)
- **Role**: Administrative safety controller.
- **Responsibilities**:
  - Reviews the Permit-to-Work database for hot and cold work authorizations.
  - Tracks Lockout-Tagout (LOTO) and active maintenance equipment statuses.

### 4. Geospatial Agent (geo-agent)
- **Role**: Layout mapping and tracking specialist.
- **Responsibilities**:
  - Generates Folium plant overlays showing risk levels.
  - Coordinates coordinates for workers based on UWB sensors.

### 5. RAG Intelligence Agent (rag-agent)
- **Role**: Regulatory knowledge search expert.
- **Responsibilities**:
  - Manages ChromaDB index for safety laws (OISD, Factory Act).
  - Answers system inquiries utilizing context-informed citations.

### 6. Emergency Response Agent (response-agent)
- **Role**: Playbook executioner.
- **Responsibilities**:
  - Triggers alerts for high-risk flags (risk > 0.8).
  - Preserves sensor evidence.
  - Audits containment playbooks.

### 7. Frontend Agent (frontend-agent)
- **Role**: Control room developer.
- **Responsibilities**:
  - Builds the Streamlit interface displaying heatmap and chats.

## Collaboration Rules
1. **pm-agent** initiates tasks and assigns work.
2. Agents must provide code review validation before integration.
3. Tests must be generated for all critical functions.
