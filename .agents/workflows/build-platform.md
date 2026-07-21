# /build-safety-platform

## Description
Orchestrates the complete build of the Industrial Safety Guardian platform.

## Workflow Steps

### Phase 1: Planning
1. **pm-agent** analyzes the problem statement
2. **pm-agent** creates technical specification
3. **All agents** review and provide input
4. **USER** approves the plan

### Phase 2: Backend Development
1. **sensor-agent** builds `src/backend/agents/sensor_agent.py`
2. **permit-agent** builds `src/backend/agents/permit_agent.py`
3. **geo-agent** builds `src/backend/geospatial/heatmap.py`
4. **rag-agent** builds `src/backend/rag/retriever.py`
5. **response-agent** builds `src/backend/response/orchestrator.py`

### Phase 3: Integration
1. **pm-agent** integrates all backend components
2. **All agents** review integration points
3. Run tests

### Phase 4: Frontend Development
1. **frontend-agent** builds the dashboard using Streamlit
2. **frontend-agent** integrates with backend APIs

### Phase 5: Demo Preparation
1. Create sample data for demonstration
2. Build the demo script
3. Prepare presentation deck
4. Record demo video

## Success Criteria
- [ ] Compound risk detection working
- [ ] Geospatial heatmap visible
- [ ] RAG agent responds to queries
- [ ] Emergency response triggers alerts
- [ ] Demo video shows end-to-end flow
