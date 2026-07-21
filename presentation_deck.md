# Hackathon Presentation: Industrial Safety Guardian
*AI-Powered Industrial Safety Intelligence for Zero-Harm Operations*

---

## Slide 1: The Problem
### Zero-Harm Operations: The Silent Threat of Compound Risks
*   **The Baseline Trap**: Industrial plants monitor safety in silos. Isolated sensors (gas levels, work permits, maintenance status) trigger alarm alerts independently.
*   **The Blind Spot**: A zone with an active **Hot Work** permit (welding), equipment undergoing maintenance, and a gas concentration rising *rapidly* (but still below the individual sensor limit) represents a critical safety risk.
*   **The Consequence**: Incidents occur because warning signs go uncoordinated. False-negative rates remain high, and safety lead-time is zero.

---

## Slide 2: The Solution
### Industrial Safety Guardian: Unified Multi-Agent Engine
*   **Multi-Agent Coordination**: Specialized agents monitor IoT gas levels (`sensor-agent`), work permits (`permit-agent`), and LOTO checklists (`maintenance-agent`).
*   **Compound Risk Detection**: The `RiskEngine` correlates these states in real-time. If it detects a welding operation combined with a rapidly rising gas trend, the risk score climbs instantly.
*   **Early Warning Action**: Evacuation notifications are dispatched **45 minutes before** gas levels breach individual sensor alarm levels.

---

## Slide 3: Core Technology Stack
*   **Real-time Correlation Backend**: Python FastAPI + Asyncio Event Loop.
*   **Geospatial Layer**: Folium Leaflet-based plant maps showing zones shaded green->yellow->orange->red, alongside worker coordinates tracked via simulated UWB.
*   **Compliance & Historical RAG**: ChromaDB Vector Store + Gemini (Google Antigravity SDK) generating regulatory summaries with citations (OISD, Factories Act).
*   **Evacuation Orchestration**: Automatic alert logs, sensor log freezing, and preliminary compliance report drafts.
*   **Control Room Portal**: Streamlit safety dashboard.

---

## Slide 4: Hackathon Metrics & Validation
*   **Compound Risk Accuracy**: 100% detection of early hazards by correlating factors that trigger no alerts on single-sensor baselines.
*   **Early warning lead time**: **45 minutes** advance notice (warning triggered at 23:35/23:45, danger threshold breached at 23:50).
*   **Evacuation Efficiency**: Immediate identification of affected personnel (such as Rajesh Kumar, Welder in Zone A) and redirection to assembly gates.
*   **Audit Preservation**: Instant preservation of sensor spools for incident reports.

---

## Slide 5: The Demo Scenario Progression
*   **00:00 - Normal State**: Clean telemetry logs. Green heatmap overlays.
*   **02:00 - Operations Begin**: Welding permit is issued in Zone A. Heatmap remains green.
*   **04:00 - Anomaly Development**: Gas sensor in Zone A registers CO climbing >2%/minute.
*   **06:00 - Compound Trigger**: Safety score climbs to 0.7 (Orange) and then 0.9 (Red).
*   **08:00 - Automated Response**: SMS alerts are dispatched, workers are redirected, sensor evidence is saved, and RAG retriever references similar historical incidents.
