# Demo Video Script: Industrial Safety Guardian Prototype

This script guides the narrator and operator during the demonstration video recording.

---

## Part 1: Introduction & Dashboard Overview (0:00 - 1:00)
*   **Visual**: Show the Streamlit dashboard on screen. Scrubbing slider is set to **`23:00:00Z (Normal Ops)`**.
*   **Action**: Hover over the dashboard metrics (Active Permits, Workers Onsite, Safety Lead Time). Show that the heatmap is green for all five plant zones.
*   **Narrator Voiceover**:
    > "Welcome to the demonstration of the Industrial Safety Guardian, a multi-agent intelligence platform designed to eliminate catastrophic industrial accidents by detecting compound risks early. 
    > As we look at the dashboard at 23:00, all operations are normal. All 5 zones on our interactive plant layout map are highlighted in green. Our telemetry monitors indicate gas levels are near zero, and no hazardous tasks are active."

---

## Part 2: Operations Development - The Welding Permit (1:00 - 2:00)
*   **Visual**: Move the scrubbing slider to **`23:15:00Z (Hot Work Started)`**.
*   **Action**: Point out the "Active Work Permits" counter has ticked up. Zoom in on Zone A on the map. Click on the marker to reveal the popup details: `PERMIT-A-409 - Hot Work - Welding and pipe cutting on main hydrocarbon line`.
*   **Narrator Voiceover**:
    > "Let's fast-forward to 23:15. A maintenance team has checked out equipment `EQ-PUMP-101A` and initiated a Hot Work welding operation under Permit `PERMIT-A-409`. 
    > While hot work is inherently hazardous, our risk engine scores the zone at 0.30 because gas levels are normal and lockout-tagout is applied. The heatmap remains green."

---

## Part 3: The Creeping Threat (2:00 - 3:30)
*   **Visual**: Move the scrubbing slider to **`23:35:00Z (Anomalous Gas Trend)`**.
*   **Action**: Observe the heatmap for Zone A has turned **Orange**. Hover over Zone A to show the risk score is `0.70` and the reasons listed: `Active Hot Work permit`, `Equipment under active maintenance`, and `ALERT: Rapidly rising gas trend: CO rising at 24.0%/min`. Note that the CO level is only `11.5 ppm`, which is well below the standard danger alarm threshold of `50.0 ppm`.
*   **Narrator Voiceover**:
    > "At 23:35, we see our compound risk engine's core innovation. The CO level has risen to 11.5 ppm. Under standard baseline systems, this would trigger no alarms since the limit is 50 ppm. 
    > However, our `SensorAgent` calculates that the gas level is rising rapidly at 24% per minute. The `RiskEngine` correlates this trend with the active Hot Work permit, immediately raising the risk score to 0.70, turning the zone Orange on the control room heatmap."

---

## Part 4: Critical Trigger & Automated Playbook (3:30 - 5:00)
*   **Visual**: Move the scrubbing slider to **`23:45:00Z (CRITICAL Alert - 0.90 Risk)`**.
*   **Action**: Observe the heatmap for Zone A has turned **Red**. Points out the emergency console on the right: `🚨 CRITICAL RISK ALERT IN ZONE A`. Highlight the list of dispatched evacuation SMS messages. Note that the worker dots for Zone A have moved to the safe assembly coordinates `[22.4750, 70.0750]` outside Zone A. Point out the early warning lead time metric shows **`45 mins`**.
*   **Narrator Voiceover**:
    > "At 23:45, the risk score breaches the critical threshold of 0.8, hitting 0.9. The heatmap turns Red, and the `EmergencyResponseOrchestrator` launches our containment playbook. 
    > It automatically sends evacuation notifications to the UWB-tracked workers in Zone A. Rajesh Kumar and the welding crew immediately evacuate.
    > The system also freezes the sensor telemetry data and generates a compliant incident draft. Under standard single-sensor setups, alarms wouldn't go off until 23:50, meaning our multi-agent model saved lives by providing a 45-minute early warning."

---

## Part 5: Compliance RAG Q&A Demo (5:00 - 6:00)
*   **Visual**: Scroll down to the Chat interface.
*   **Action**: Type the question: `What are the OISD guidelines for hot work permits and gas leaks?` Press enter. Wait for Gemini to answer. Expand the document citations showing the exact source text matching `OISD Guidelines - Clause 2` and `Factories Act - Section 36`.
*   **Narrator Voiceover**:
    > "Finally, let's look at the safety officer's interactive compliance assistant. By querying our built-in RAG chatbot, safety officers can ask about safety codes or search similar historical incidents. 
    > The agent references our ChromaDB database and leverages Gemini to produce clear, structured answers with citations. 
    > This completes the demo of the Industrial Safety Guardian—turning reactive operations into proactive zero-harm safety."
