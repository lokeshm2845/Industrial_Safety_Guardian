# Industrial Safety Guardian 🛡️
*AI-Powered Industrial Safety Intelligence for Zero-Harm Operations*

This is a working prototype for a hackathon submission, implementing real-time compound risk assessment, worker tracking, emergency response orchestration, and regulatory RAG search.

---

## 📁 Workspace Directory Structure

```text
industrial-safety-guardian/
├── .agents/
│   ├── agents.md               # AI team definitions and collaboration rules
│   ├── skills/
│   │   ├── risk-detection.md       # Compound risk engine specifications
│   │   ├── geospatial-heatmap.md   # Map layer rules
│   │   ├── rag-intelligence.md     # Vector retrieval details
│   │   └── emergency-response.md   # Playbook automation guidelines
│   └── workflows/
│       └── build-platform.md       # Platform orchestrator instructions
├── src/
│   ├── backend/
│   │   ├── agents/
│   │   │   ├── sensor_agent.py      # Telemetry rate analysis
│   │   │   ├── permit_agent.py      # PTW active check
│   │   │   ├── maintenance_agent.py # LOTO status check
│   │   │   └── risk_engine.py       # Multi-agent risk aggregator
│   │   ├── geospatial/
│   │   │   └── heatmap.py           # Folium HTML generator
│   │   ├── rag/
│   │   │   ├── vector_store.py      # ChromaDB database client
│   │   │   └── retriever.py         # Google Antigravity & Gemini RAG
│   │   ├── response/
│   │   │   └── orchestrator.py      # SMS logs & evidence freezing
│   │   └── api/
│   │       └── main.py              # FastAPI server router
│   └── frontend/
│       └── dashboard.py             # Streamlit control room portal
├── data/
│   ├── sample_sensor_data.json      # IoT gas readings
│   ├── sample_permits.json          # PTW registry
│   ├── sample_workers.json          # UWB worker telemetry
│   ├── incidents/
│   │   └── sample_incidents.json    # Near-miss logs
│   └── regulations/
│       ├── oisd_guidelines.txt      # Oil Industry Safety Directorate guidelines
│       └── factory_act.txt          # Factories Act, 1948 provisions
├── tests/
│   └── test_risk_engine.py          # Pytest suite
├── architecture_diagram.md          # Mermaid flow chart
├── presentation_deck.md             # Markdown slides
├── demo_video_script.md             # Narrated demo timeline
├── requirements.txt                 # Dependencies
└── README.md                        # Project guide (this file)
```

---

## 🚀 Setup & Launch Instructions

### 1. Install Dependencies
Make sure you have python 3.10+ installed. In your terminal run:
```bash
pip install -r requirements.txt
```

### 2. Configure Gemini API Key
Configure your key as an environment variable:
- **Windows (PowerShell)**:
  ```powershell
  $env:GEMINI_API_KEY="your-api-key-here"
  ```
- **Linux/macOS**:
  ```bash
  export GEMINI_API_KEY="your-api-key-here"
  ```

### 3. Run Automated Tests
Execute `pytest` to verify risk assessments:
```bash
pytest tests/test_risk_engine.py
```

### 4. Run the Streamlit Dashboard
Launch the Streamlit dashboard in a local server:
```bash
streamlit run src/frontend/dashboard.py
```

### 5. Run the FastAPI Server (Optional)
If you want to run the REST API and WebSocket channels:
```bash
uvicorn src.backend.api.main:app --port 8000
```

---

## 🛡️ Compound Risk Detection Scenario
Use the **Timeline Scrubbing Slider** in the sidebar of the dashboard to walk through the zero-harm progression:
1. **23:00 (Normal Ops)**: All zones green. Gas levels low, no permits.
2. **23:15 (Welding Started)**: Hot work permit active in Zone A, but gas levels are clean (0.30 score).
3. **23:25 (Gas Creeping)**: CO starts escaping.
4. **23:35 (Anomalous Trend)**: CO rises at 24%/min to 11.5 ppm. The engine catches the trend and escalates the risk to `0.70` (Orange) before gas levels reach baseline thresholds.
5. **23:45 (CRITICAL Alert)**: Safety score hits `0.90` (Red). Containment playbook fires:
   - SMS notifications are dispatched to Rajesh Kumar (Welder) and Zone A crew.
   - UWB tracking shows workers moving to the assembly gate safely.
   - Sensor spools are frozen to local JSON.
   - Legal compliance draft is created.
6. **23:50 (High Danger Threshold)**: CO hits 42 ppm. Traditional sensors only trigger alarms *now*, giving a **45-minute advance warning lead time** using the multi-agent system.
