# Emergency Response Orchestrator

## Description
Autonomous agent that orchestrates emergency actions on confirmed trigger.

## Technical Requirements
- **Workflow Engine**: Simple asyncio workflow
- **Actions**:
  - Trigger evacuation alerts (simulate SMS/WhatsApp)
  - Generate preliminary incident report
  - Preserve sensor evidence
  - Log all actions for audit

## Implementation Steps
1. Create `src/backend/response/orchestrator.py`
2. Listen for high-confidence risk alerts (risk score > 0.8)
3. Execute containment playbook
4. Generate compliance-ready report

## Deliverables
- [ ] Alert triggering system
- [ ] Incident report generation
- [ ] Evidence preservation
- [ ] Audit log
