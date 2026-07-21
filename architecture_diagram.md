# System Architecture Diagram

This document details the software architecture, data flow, and agent integration layers for the **Industrial Safety Guardian** platform.

```mermaid
graph TD
    %% Telemetry and Input Data Source Layer
    subgraph DataSources["Telemetry & PTW Layers"]
        A1["sample_sensor_data.json<br>(IoT Gas Telemetry)"]
        A2["sample_permits.json<br>(PTW Registry & LOTO status)"]
        A3["sample_workers.json<br>(UWB Wearable Telemetry)"]
        A4["sample_incidents.json<br>(Historical incident logs)"]
        A5["regulations/<br>(OISD guidelines & Factories Act)"]
    end

    %% Agent Intelligence Layer
    subgraph AgenticCore["Multi-Agent Risk Assessment Engine"]
        SA["SensorAgent<br>(Rate-of-Increase Trends)"]
        PA["PermitAgent<br>(Hot Work Checks)"]
        MA["MaintenanceAgent<br>(LOTO Verification)"]
        RE["RiskEngine<br>(Compound Score Correlation)"]
    end

    %% RAG Intelligence Layer
    subgraph RAGCore["Regulatory Intelligence (RAG)"]
        VS["SafetyVectorStore<br>(ChromaDB Persistent Index)"]
        RT["SafetyRetriever<br>(Google Antigravity SDK & Gemini)"]
    end

    %% Playbook Action Orchestration Layer
    subgraph PlaybookOrchestrator["Emergency Actions Orchestration"]
        EO["EmergencyResponseOrchestrator<br>(Playbook Automation)"]
        AL["SMS & WhatsApp Alerts"]
        EV["Evacuation Dispatcher"]
        ES["Evidence Preservation System"]
    end

    %% Delivery and Frontend Layer
    subgraph DeliveryAPI["FastAPI Integration Layer"]
        FA["FastAPI main.py Router"]
        WS["WebSocket Alerts Server"]
    end

    subgraph ClientDashboard["Officer Control Room Portal"]
        ST["Streamlit UI Portal"]
        FL["Folium Layout Map"]
        CH["RAG Q&A Chat UI"]
    end

    %% Logical Connectivities
    A1 --> SA
    A2 --> PA
    A2 --> MA
    SA & PA & MA --> RE
    
    A4 & A5 --> VS
    VS --> RT
    RT --> CH
    
    RE --> EO
    A3 --> EO
    A1 --> EO
    
    EO --> AL
    EO --> EV
    EO --> ES
    
    RE & A3 & A2 --> FA
    FA --> WS
    WS --> ST
    FL --> ST
    ST --> CH
    
    classDef datasource fill:#2b2d42,stroke:#8d99ae,stroke-width:2px,color:#fff;
    classDef agent fill:#1d3557,stroke:#457b9d,stroke-width:2px,color:#fff;
    classDef RAG fill:#1a1c23,stroke:#7f5af0,stroke-width:2px,color:#fff;
    classDef playbook fill:#4b1c1c,stroke:#ef4444,stroke-width:2px,color:#fff;
    classDef delivery fill:#112233,stroke:#10b981,stroke-width:2px,color:#fff;
    
    class A1,A2,A3,A4,A5 datasource;
    class SA,PA,MA,RE agent;
    class VS,RT RAG;
    class EO,AL,EV,ES playbook;
    class FA,WS,ST,FL,CH delivery;
```

## Data Flow Narrative
1. **Anomaly & Telemetry Assessment**:
   - The `SensorAgent` tracks gas readouts in real-time, focusing on percentage-based rate of increase (>2% per minute triggers anomaly flags).
   - The `PermitAgent` monitors work permits and identifies zones with active "Hot Work" permits.
   - The `MaintenanceAgent` checks lock-out tag-out (LOTO) verification fields.

2. **Risk Correlation & Prediction**:
   - The `RiskEngine` pulls inputs from the sub-agents and correlates them into a compound safety risk index score between `0.0` and `1.0`.
   - The score escalates early—alerting safety officers **45 minutes before** gas levels reach high threat thresholds, by identifying combinations of active welding and rising gas trends.

3. **Autonomous Emergency Response**:
   - If risk score exceeds `0.80`, `EmergencyResponseOrchestrator` triggers evacuation logs, drafts compliance documents based on regulation references, and preserves sensor spool evidence to JSON logs.

4. **Regulatory RAG System**:
   - Safety officers query the `SafetyRetriever` on guidelines or previous near-miss reports, which performs vector database similarity searches using ChromaDB and generates responses via the Gemini model (Google Antigravity SDK).
