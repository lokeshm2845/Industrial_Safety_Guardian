import streamlit as st
import os
import sys
import json
import asyncio
import threading
import time
from datetime import datetime
import streamlit.components.v1 as components

# Add project root to sys.path to resolve src.* imports on cloud platforms like Streamlit Cloud
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Load environment variables on startup
try:
    from dotenv import load_dotenv
    env_path = os.path.join(base_dir, ".env")
    load_dotenv(dotenv_path=env_path, override=True)
except Exception:
    pass

# Configure page setup
st.set_page_config(
    page_title="Industrial Safety Guardian - Control Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS styling for modern rich aesthetics (dark mode, glassmorphism, Outfit font)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Core Styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .reportview-container {
        background: #090d16;
    }
    
    /* Premium Gauge Card */
    .safety-score-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        text-align: center;
        margin-bottom: 20px;
    }
    
    .safety-score-value {
        font-size: 44px;
        font-weight: 800;
        background: linear-gradient(to right, #10b981, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
    }
    
    .safety-score-label {
        font-size: 13px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Glassmorphism Metric Cards */
    .metric-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 16px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
    }
    
    .alert-card-critical {
        background-color: #1e1b4b;
        border: 1px solid #312e81;
        border-radius: 10px;
        padding: 16px;
        border-left: 5px solid #ef4444;
        color: white;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.15);
    }
    
    .alert-card-normal {
        background-color: #064e3b;
        border: 1px solid #065f46;
        border-radius: 10px;
        padding: 16px;
        border-left: 5px solid #10b981;
        color: white;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15);
    }
    
    /* Agent Dialogues styling */
    .agent-bubble {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 12px;
        border: 1px solid #334155;
    }
    .agent-header {
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .agent-text {
        font-size: 13px;
        color: #cbd5e1;
        font-family: 'Inter', sans-serif;
    }
    
    /* Worker ID styling */
    .worker-badge-card {
        background: radial-gradient(circle at top left, #1e293b, #0f172a);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        margin-bottom: 15px;
        position: relative;
        overflow: hidden;
    }
    .worker-badge-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #00bcd4);
    }
    .worker-status-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: bold;
        text-transform: uppercase;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to run async tasks safely in Streamlit thread contexts
def run_async_safe(coro):
    res_list = []
    exc_list = []
    def runner():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(coro)
            res_list.append(res)
        except Exception as e:
            exc_list.append(e)
        finally:
            loop.close()
    
    thread = threading.Thread(target=runner)
    thread.start()
    thread.join()
    if exc_list:
        raise exc_list[0]
    return res_list[0]

# Import backend components directly
from src.backend.agents.risk_engine import RiskEngine
from src.backend.geospatial.heatmap import generate_heatmap_html
from src.backend.rag.retriever import SafetyRetriever
from src.backend.response.orchestrator import EmergencyResponseOrchestrator

# Initialize controllers
@st.cache_resource
def get_controllers():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sensor_path = os.path.join(base_dir, "data/sample_sensor_data.json")
    permits_path = os.path.join(base_dir, "data/sample_permits.json")
    
    engine = RiskEngine(sensor_data_path=sensor_path, permits_data_path=permits_path)
    orchestrator = EmergencyResponseOrchestrator()
    retriever = SafetyRetriever(vector_store=None) # automatically builds or loads ChromaDB
    
    return engine, orchestrator, retriever

try:
    risk_engine, orchestrator, safety_retriever = get_controllers()
except Exception as e:
    st.error(f"Error loading system agents: {e}")
    st.stop()

# Data loaders
def load_workers():
    workers_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/sample_workers.json"))
    if os.path.exists(workers_path):
        with open(workers_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_permits():
    permits_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/sample_permits.json"))
    if os.path.exists(permits_path):
        with open(permits_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_sensor_history():
    sensor_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/sample_sensor_data.json"))
    if os.path.exists(sensor_path):
        with open(sensor_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

workers = load_workers()
permits = load_permits()
sensor_data = load_sensor_history()

# Header layout
st.title("🛡️ Industrial Safety Guardian - Control Center")
st.markdown("### AI-Powered Multi-Agent Refinery Risk Intelligence Dashboard")

# Timeline milestones mapping for scrubbing
milestones = [
    ("23:00:00Z (Normal Ops)", "2026-07-16T23:00:00Z"),
    ("23:15:00Z (Hot Work Started)", "2026-07-16T23:15:00Z"),
    ("23:25:00Z (Gas Levels Creeping)", "2026-07-16T23:25:00Z"),
    ("23:35:00Z (Anomalous Gas Trend)", "2026-07-16T23:35:00Z"),
    ("23:45:00Z (CRITICAL Alert - 0.90 Risk)", "2026-07-16T23:45:00Z"),
    ("23:50:00Z (Extreme Danger - 42ppm CO)", "2026-07-16T23:50:00Z")
]

# State management for auto-play timeline playback
if "timeline_index" not in st.session_state:
    st.session_state.timeline_index = 0

milestone_labels = [m[0] for m in milestones]
milestone_dict = dict(milestones)

# Sidebar controls
st.sidebar.header("🕹️ Simulation Controls")
play_sim = st.sidebar.toggle("▶️ Auto-Play Timeline", value=False, help="Animate and advance safety timeline minute-by-minute")

if play_sim:
    # Use index from session state
    selected_label = st.sidebar.select_slider(
        "Telemetry Timeline Scrubbing",
        options=milestone_labels,
        value=milestone_labels[st.session_state.timeline_index]
    )
else:
    selected_label = st.sidebar.select_slider(
        "Telemetry Timeline Scrubbing",
        options=milestone_labels,
        value=milestone_labels[st.session_state.timeline_index]
    )
    # Sync index back
    st.session_state.timeline_index = milestone_labels.index(selected_label)

# Extract timestamp safely
up_to_time = milestone_dict.get(selected_label)
st.sidebar.info(f"Visualizing telemetry up to: `{up_to_time}`")

# 1. Run live risk engine assessments
zones = ["Zone A", "Zone B", "Zone C", "Zone D", "Zone E"]
zone_risks = {}
alert_triggered = False
triggered_alert_data = None

# Evaluate risk for each zone up to current scrubbing timestamp
orchestrator.active_alerts = [] # reset for visual scrubbing sandbox view
for z in zones:
    res = risk_engine.evaluate_risk(z, up_to_time=up_to_time)
    zone_risks[z] = res
    
    # Process emergency trigger check
    alert_info = orchestrator.handle_risk_evaluation(res, workers, sensor_data)
    if alert_info:
        alert_triggered = True
        triggered_alert_data = alert_info

# 2. Calculate Factory Safety Score
total_active_permits = len([p for p in permits if p["status"] == "Active"])
avg_zone_risk = sum(z["risk_score"] for z in zone_risks.values()) / len(zone_risks)
unapplied_loto_count = len([p for p in permits if p["status"] == "Active" and p.get("loto_status") != "Applied" and p["type"] in ["Hot Work", "Electrical Work", "Confined Space Entry"]])

# Base score starting at 100
factory_score = 100 - (avg_zone_risk * 45) - (unapplied_loto_count * 10)
if any(z["metrics"]["co_level"] >= 50.0 or z["metrics"]["lel_level"] >= 20.0 for z in zone_risks.values()):
    factory_score -= 20 # additional penalty for critical limits breached
factory_score = max(0, min(100, round(factory_score)))

# Save history of safety score across steps
if "score_history" not in st.session_state:
    st.session_state.score_history = []
st.session_state.score_history.append(factory_score)
if len(st.session_state.score_history) > 30:
    st.session_state.score_history.pop(0)

# Dashboard Global KPI metric row
st.markdown("---")
col_g1, col_g2, col_g3, col_g4 = st.columns([1, 1, 1, 1])

with col_g1:
    # Circular Gauge safety card
    glow_color = "#10b981" if factory_score >= 80 else "#f59e0b" if factory_score >= 50 else "#ef4444"
    st.markdown(f"""
    <div class="safety-score-card">
        <div class="safety-score-label">Global Safety Score</div>
        <div class="safety-score-value" style="background: linear-gradient(to right, {glow_color}, #3b82f6); -webkit-background-clip: text;">{factory_score}%</div>
    </div>
    """, unsafe_allow_html=True)

with col_g2:
    if alert_triggered:
        st.error("🚨 Plant Risk: CRITICAL")
    elif any(z["risk_score"] > 0.4 for z in zone_risks.values()):
        st.warning("⚠️ Plant Risk: ELEVATED")
    else:
        st.success("✅ Plant Risk: NORMAL")
    st.metric("Early Warning Lead Time", "45 mins" if alert_triggered else "N/A", delta="vs. 0 min baseline" if alert_triggered else "Monitoring trends")

with col_g3:
    st.metric("Active Work Permits", total_active_permits, delta=f"{unapplied_loto_count} Unapplied LOTO", delta_color="inverse")
    st.metric("Active Personnel Onsite", len(workers))

with col_g4:
    # One-click report download
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if alert_triggered and triggered_alert_data:
        st.download_button(
            label="📄 Download Incident Report (One-Click)",
            data=triggered_alert_data["md_report_content"],
            file_name=f"{triggered_alert_data['alert_id']}_compliance_report.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        # Generate generic safety status report
        from src.backend.response.orchestrator import datetime as ord_datetime
        
        # simple helper
        permits_str = ""
        for p in permits:
            if p["status"] == "Active":
                permits_str += f"- **{p['permit_id']}**: {p['type']} in {p['zone']} ({p['description']}) - LOTO: {p['loto_status']}\n"
        workers_str = ""
        for w in workers:
            workers_str += f"- **{w['name']}** ({w['role']}) - Zone: {w['zone']} (Tag: {w.get('uwb_tag_id', w['worker_id'])})\n"
        zones_str = ""
        for z_name, z_val in zone_risks.items():
            zones_str += f"### {z_name}\n"
            zones_str += f"- **Risk Score:** `{z_val['risk_score']}`\n"
            for r in z_val["reasons"]:
                zones_str += f"  - {r}\n"
                
        gen_report = f"""# 🛡️ SYSTEM SHIFT SAFETY & COMPLIANCE REPORT

## 🗓️ Report Overview
- **Generation Timestamp:** `{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}`
- **Global Factory Safety Score:** `{factory_score}/100`
- **Active Permits:** {total_active_permits}
- **Personnel Onsite:** {len(workers)}

---

## 📈 Zone Risk Summaries
{zones_str}

---

## 📄 Active Work Permits
{permits_str}

---

## 👷 Onsite Personnel Directory
{workers_str}

---

## ⚖️ General Regulations Checklist
1. **OISD Standard 137 / 105:** All hot work areas verified below 0.0% LEL prior to shift start.
2. **Factories Act, 1948 (Section 36/37):** Lockout-Tagout protocols checked and verified on active equipment.

**Authorized Inspector Signature:** ________________________  
"""
        st.download_button(
            label="📄 Export Shift Safety Report (One-Click)",
            data=gen_report,
            file_name=f"refinery_safety_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=True
        )

# Dashboard layout tabs
tab_control, tab_sim, tab_workers, tab_agents, tab_copilot = st.tabs([
    "🗺️ Control Room & Routing", 
    "🔮 Simulation Studio", 
    "👷 Worker Digital IDs", 
    "🤖 Agent Collaboration Feed",
    "💬 AI Safety Copilot"
])

# ================= TAB 1: CONTROL ROOM =================
with tab_control:
    col_map, col_alerts = st.columns([2, 1])
    
    with col_map:
        st.markdown("#### 🗺️ Live Geospatial Risk Map & Evacuation Routing")
        # Evacuate Zone A workers if alert triggered
        current_workers = []
        for w in workers:
            if alert_triggered and w["zone"] == "Zone A":
                w_evac = w.copy()
                w_evac["lat"] = 22.4750
                w_evac["lon"] = 70.0750
                w_evac["role"] = f"{w['role']} (Evacuated)"
                current_workers.append(w_evac)
            else:
                current_workers.append(w)
                
        # Generate Heatmap HTML
        html_map = generate_heatmap_html(zone_risks, current_workers, permits)
        components.html(html_map, height=520, scrolling=True)
        
    with col_alerts:
        st.markdown("#### ⚖️ Explainable AI (\"Why is this risky?\")")
        # Let's inspect the most critical zone
        critical_zone = max(zone_risks.keys(), key=lambda z: zone_risks[z]["risk_score"])
        crit_detail = zone_risks[critical_zone]
        
        st.markdown(f"**Selected High-Risk Assessment: {critical_zone}**")
        st.markdown(f"**Safety Score:** `{crit_detail['risk_score']}`")
        
        # Risk factor weights visualization
        breakdown = crit_detail.get("breakdown", {})
        if breakdown:
            st.write("Contributing Risk Factors:")
            for factor, val in breakdown.items():
                if val > 0:
                    st.write(f"- {factor.replace('_', ' ').capitalize()}: `+{val}`")
                    st.progress(val / 0.5)  # normalize to 1.0 progress bar
                    
        if crit_detail["reasons"]:
            st.warning("\n".join([f"• {r}" for r in crit_detail["reasons"]]))
        else:
            st.success("All metrics conform to refinery safety standards.")
            
        st.markdown("---")
        st.markdown("#### 🚨 Real-time Alerts & Playbook Logs")
        if alert_triggered and triggered_alert_data:
            st.error(f"**CRITICAL BREACH TRIGGERED**")
            st.markdown(f"**Alert ID**: `{triggered_alert_data['alert_id']}`")
            st.markdown(f"**Trigger Zone**: `{triggered_alert_data['zone']}`")
            st.markdown("**Containment Actions Executed:**")
            for log in triggered_alert_data["notifications"]:
                st.warning(log)
        else:
            st.success("Operations normal. Standing by...")

# ================= TAB 2: SIMULATION STUDIO =================
with tab_sim:
    st.markdown("#### 🔮 Predictive Risk Simulation Studio")
    st.write("Inject arbitrary gas concentrations, active permits, and LOTO compliance status to predict the compound safety risk score.")
    
    col_s1, col_s2 = st.columns([1, 1])
    
    with col_s1:
        sim_zone = st.selectbox("Select Target Zone to Simulate", zones)
        sim_co = st.slider("Carbon Monoxide (CO) concentration (ppm)", 0.0, 100.0, 2.0)
        sim_lel = st.slider("Lower Explosive Limit (LEL) (%)", 0.0, 50.0, 0.0)
        sim_h2s = st.slider("Hydrogen Sulfide (H2S) concentration (ppm)", 0.0, 20.0, 0.0)
        sim_o2 = st.slider("Oxygen (O2) concentration (%)", 15.0, 22.0, 20.9)
        
        sim_hot = st.checkbox("Active Hot Work Permit", value=False)
        sim_maint = st.checkbox("Active Maintenance Operations", value=False)
        sim_loto = st.checkbox("Verify Lockout-Tagout (LOTO) Applied", value=True)
        
        sim_trend_rising = st.checkbox("Simulate Rapid Rising Gas Trend (>2%/min)", value=False)
        
    with col_s2:
        st.markdown("##### 📈 Predictive Risk Assessment")
        
        # Construct overrides
        overrides = {
            "has_hot_work": sim_hot,
            "in_maintenance": sim_maint,
            "loto_compliant": sim_loto,
            "co_level": sim_co,
            "co_rising": sim_trend_rising,
            "co_rate": 24.0 if sim_trend_rising else 0.0,
            "lel_level": sim_lel,
            "lel_rising": sim_trend_rising,
            "lel_rate": 15.0 if sim_trend_rising else 0.0,
            "h2s_level": sim_h2s,
            "h2s_rising": sim_trend_rising,
            "h2s_rate": 5.0 if sim_trend_rising else 0.0,
            "o2_level": sim_o2,
            "o2_falling": sim_o2 < 19.5,
            "o2_rate": -1.0 if sim_o2 < 19.5 else 0.0
        }
        
        sim_res = risk_engine.evaluate_risk(sim_zone, overrides=overrides)
        sim_score = sim_res["risk_score"]
        
        # Color coding score
        sim_color = "#2ecc71" if sim_score < 0.4 else "#f1c40f" if sim_score < 0.7 else "#e74c3c"
        
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 8px; background-color: #1e293b; text-align: center; border-left: 5px solid {sim_color};">
            <h4 style="margin: 0; color: #94a3b8;">Predicted Zone Safety Score</h4>
            <h1 style="margin: 5px 0; color: {sim_color};">{sim_score}</h1>
            <p style="margin: 0; font-size: 13px;">Threshold warning level triggers at <b>0.80</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("##### 🔍 Contributing Risk Weights (Explainable AI)")
        sim_breakdown = sim_res["breakdown"]
        for f, v in sim_breakdown.items():
            st.write(f"- {f.replace('_', ' ').capitalize()}: `+{v}`")
            st.progress(v / 0.5)
            
        st.markdown("##### 🚨 Expected Playbook Dispatches")
        if sim_score >= 0.8:
            st.error("⚠️ Containment Action Plan: EVACUATION ORDER DISPATCHED")
            st.write("- SMS sent to all registered workers in zone.")
            st.write("- Active hot work permits suspended.")
            st.write("- Frozen sensor evidence captured to spool.")
        else:
            st.success("✅ Standard Operating Tolerances: Permitted to Work.")

# ================= TAB 3: WORKER DIGITAL IDS =================
with tab_workers:
    st.markdown("#### 👷 Onsite Worker Registry & UWB Digital ID Badges")
    st.write("Browse digital IDs, training credentials, and real-time physical statuses of the field crew.")
    
    col_w_filter, = st.columns(1)
    # Search or filter workers
    worker_search = st.text_input("🔍 Search Worker by Name or Role", "")
    
    filtered_workers = [w for w in workers if worker_search.lower() in w["name"].lower() or worker_search.lower() in w["role"].lower()]
    
    w_cols = st.columns(3)
    for i, w in enumerate(filtered_workers):
        col_idx = i % 3
        with w_cols[col_idx]:
            # Determine safety status
            zone_risk = zone_risks.get(w["zone"], {}).get("risk_score", 0.0)
            is_critical = any(zr.get("risk_score", 0.0) >= 0.8 for zr in zone_risks.values())
            
            w_status = "Safe"
            w_badge_color = "#10b981"
            
            if is_critical and w["zone"] == "Zone A":
                w_status = "Evacuated"
                w_badge_color = "#3b82f6"
            elif zone_risk >= 0.8:
                w_status = "Danger Area"
                w_badge_color = "#ef4444"
            elif zone_risk >= 0.5:
                w_status = "Elevated Risk"
                w_badge_color = "#f59e0b"
                
            certs_str = ", ".join(w.get("certifications", ["HSE Awareness"]))
            
            st.markdown(f"""
            <div class="worker-badge-card">
                <div style="font-size: 10px; color: #94a3b8; font-weight: bold; letter-spacing: 0.5px; text-transform: uppercase;">Zero-Harm Operations Badge</div>
                <h4 style="margin: 4px 0 2px 0; color: white;">{w['name']}</h4>
                <div style="font-size: 12px; color: #60a5fa; font-weight: 500;">{w['role']}</div>
                <hr style="border: 0; border-top: 1px solid #334155; margin: 8px 0;" />
                <div style="font-size: 11px; color: #cbd5e1; line-height: 1.5;">
                    <b>UWB Tag:</b> <code>{w.get('uwb_tag_id', w['worker_id'])}</code><br>
                    <b>Current Zone:</b> {w['zone']}<br>
                    <b>Medical Class:</b> {w.get('medical_clearance', 'FIT - Class A')}<br>
                    <b>Blood Group:</b> {w.get('blood_group', 'O+')}<br>
                    <b>Certs:</b> <i>{certs_str}</i>
                </div>
                <div class="worker-status-badge" style="background-color: {w_badge_color}; color: white;">
                    {w_status}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ================= TAB 4: AGENT COLLABORATION TOWER =================
with tab_agents:
    st.markdown("#### 🤖 Multi-Agent AI Orchestration Feed")
    st.write("Audit the background dialogue, thought processes, and correlation decisions of the safety team agents.")
    
    # Retrieve agent logs based on selected timestamp
    agent_logs = None
    from src.backend.agents.sensor_agent import SensorAgent
    
    # Standard matching
    milestone_time = up_to_time
    
    # Define fallback or mapped logs
    AGENT_FEED = {
        "2026-07-16T23:00:00Z": [
            ("pm-agent", "Initializing safety patrol scan. Current status: Normal Operations. Coordinating telemetry analysis."),
            ("sensor-agent", "IoT streaming sensors check completed. Carbon Monoxide: 2.0 ppm, LEL: 0%. Normal thresholds."),
            ("permit-agent", "Scanning Permit-to-Work registry. No active Hot Work or hazardous work permits detected."),
            ("maintenance-agent", "Lockout-Tagout status: N/A. No equipment in active maintenance."),
            ("geo-agent", "Rendering geospatial plant layout map. All zones colored green. Active coordinates of 20 workers mapped."),
            ("response-agent", "Emergency playbook standby. Safety alerts: CLEAR.")
        ],
        "2026-07-16T23:15:00Z": [
            ("pm-agent", "Detecting active work permit for Zone A. Directing PermitAgent and MaintenanceAgent to verify compliance."),
            ("permit-agent", "Active Hot Work Permit found in Zone A: PERMIT-A-409. Description: 'Welding and pipe cutting on main hydrocarbon line'."),
            ("maintenance-agent", "Equipment EQ-PUMP-101A is under maintenance. Lockout-Tagout status verified: APPLIED (LOTO compliant)."),
            ("sensor-agent", "Sensors in Zone A show normal levels (CO: 2.1 ppm, LEL: 0%). No rate increase detected."),
            ("geo-agent", "Map updated. Zone A is green. Permit marker active at EQ-PUMP-101A center."),
            ("response-agent", "Containment checks passed. Operations permitted to proceed.")
        ],
        "2026-07-16T23:25:00Z": [
            ("pm-agent", "System telemetry scanning. Detecting minor gas presence in Zone A. SensorAgent, update rate trend calculation."),
            ("sensor-agent", "Zone A sensor SN-A-CO-01 logs minor CO presence. Level: 5.0 ppm. Rate of increase: 4.5% per minute (Elevated)."),
            ("permit-agent", "Confirming Hot Work is still active in Zone A under PERMIT-A-409."),
            ("risk-engine", "Recalculating Zone A compound risk score: 0.30 -> 0.40 (Elevated)."),
            ("geo-agent", "Updating Zone A overlay to Yellow. Worker coordinates track Rajesh Kumar and crew at safe distance from manifold."),
            ("response-agent", "Safety warning queued. Standard parameters checked.")
        ],
        "2026-07-16T23:35:00Z": [
            ("pm-agent", "🚨 ALERT: Gas concentrations escalating in Zone A. Directing immediate multi-agent hazard correlation!"),
            ("sensor-agent", "WARNING: Carbon Monoxide trend rising rapidly at 24.0% per minute in Zone A. Current value: 11.5 ppm."),
            ("permit-agent", "CRITICAL WARNING: Hot Work welding is actively taking place at the manifold! High risk of ignition!"),
            ("maintenance-agent", "Equipment isolation verify: LOTO is applied, but gaseous escape is occurring around the flange seal."),
            ("risk-engine", "CRITICAL CORRELATION: Hot Work permit coupled with a 24%/min gas rise trend. Escalating Zone A risk score to 0.70 (Orange)!"),
            ("geo-agent", "Map updated: Zone A changed to Orange. Broadcast warning to Safety Inspector Vikram Singh UWB tag."),
            ("response-agent", "Pre-alert issued. Preparing emergency containment playbook.")
        ],
        "2026-07-16T23:45:00Z": [
            ("pm-agent", "🚨 EMERGENCY SYSTEM BREACH: Zone A risk score hits 0.90! Executing emergency shutdown and muster routing!"),
            ("sensor-agent", "CRITICAL: CO level at 24.5 ppm with rapid 24%/min rise. Flammable threshold risk is imminent."),
            ("risk-engine", "RISK SCORE: 0.90 (Zone A). Standard thresholds not yet breached, but compound risk model confirms high fire probability."),
            ("response-agent", "CONTAINMENT PLAYBOOK DISPATCHED: 1. Sent evacuation alerts to Rajesh Kumar and crew. 2. Spooled telemetry to 'preserved_evidence/ALERT-ZoneA-..._sensor_evidence.json'. 3. Drafting compliance report."),
            ("geo-agent", "Evacuation routing activated. Directing Rajesh Kumar, Amit Sharma, Vikram Singh and Sunita Patel to Muster Gate 2. Rendering dynamic path bypass corridors on map. Re-routing coordinates."),
            ("permit-agent", "Permit PERMIT-A-409: SUSPENDED.")
        ],
        "2026-07-16T23:50:00Z": [
            ("pm-agent", "Muster status verification. Zone A evacuation complete. Area isolated."),
            ("sensor-agent", "CRITICAL BASELINE ALARM: CO concentration hits 42.0 ppm. Single-sensor systems now triggering alarms."),
            ("response-agent", "Muster audit: Rajesh Kumar, Amit Sharma, Sunita Patel, Vikram Singh verified safe at Muster Gate 2 (evacuation complete). Evidence locked."),
            ("geo-agent", "All Zone A personnel coordinates logged at Muster Gate 2 coordinates [22.4750, 70.0750]. Map shows Zone A Red (Risk 1.00, Evacuated)."),
            ("pm-agent", "Platform report: Multi-Agent Early Warning saved lives by providing a 45-minute head-start warning lead time.")
        ]
    }
    
    logs = AGENT_FEED.get(up_to_time, [
        ("pm-agent", "Refinery scan completed. Safety status conforms to baseline standard."),
        ("sensor-agent", "Telemetry registers nominal gas trends. Ambient CO/LEL concentrations stable."),
        ("permit-agent", "Permit registry matches work statuses with physical telemetry."),
        ("geo-agent", "Geospatial layers updated with active worker tag logs.")
    ])
    
    # Avatar and styled output mapping
    avatar_map = {
        "pm-agent": ("📋 Product Manager", "#3b82f6"),
        "sensor-agent": ("📡 Sensor Intelligence", "#10b981"),
        "permit-agent": ("📄 Permit Safety Controller", "#a855f7"),
        "maintenance-agent": ("🛠️ LOTO Specialist", "#f59e0b"),
        "geo-agent": ("🗺️ Geospatial Tracker", "#00bcd4"),
        "response-agent": ("🚨 Containment Orchestrator", "#ef4444"),
        "risk-engine": ("⚙️ Compound Risk Aggregator", "#e67e22")
    }
    
    for agent_id, msg in logs:
        label, color = avatar_map.get(agent_id, ("🤖 Safety Agent", "#6b7280"))
        st.markdown(f"""
        <div class="agent-bubble">
            <div class="agent-header" style="color: {color};">
                <span>{label}</span>
                <span style="font-size: 10px; padding: 2px 5px; border-radius: 3px; background: rgba(255,255,255,0.08); color: #94a3b8;">Active</span>
            </div>
            <div class="agent-text">{msg}</div>
        </div>
        """, unsafe_allow_html=True)

# ================= TAB 5: AI SAFETY COPILOT =================
with tab_copilot:
    st.markdown("#### 🧠 AI Safety Copilot (Proactive Assistant & RAG)")
    st.write("Leverage regulatory frameworks (OISD, Factories Act) and current live telemetry to identify risks and suggest precautions.")
    
    col_c1, col_c2 = st.columns([1, 1])
    
    with col_c1:
        st.markdown("##### 🛡️ Real-Time Safety Analysis (Proactive Copilot)")
        
        # Provide proactive alerts based on the current timeline scrubbing step
        st.info("💡 **Copilot Analysis of Active Refinery State:**")
        if up_to_time == "2026-07-16T23:00:00Z":
            st.success("All systems green. Shift starting protocols are verified compliant.")
        elif up_to_time == "2026-07-16T23:15:00Z":
            st.info("Active Hot Work permit is running in Zone A. LOTO is verified Applied. Copilot advises continuous local testing at PUMP-101A manifold.")
        elif up_to_time == "2026-07-16T23:25:00Z":
            st.warning("Minor gas presence (5ppm CO) registered in Zone A. Rate of increase is 4.5%/min. Copilot advises increasing positive ventilation flow.")
        elif up_to_time == "2026-07-16T23:35:00Z":
            st.warning("⚠️ CRITICAL THREAT WARNING: Zone A risk is Elevated (0.70) due to 24%/min CO trend coupling with active welding permit. Suspend permit PERMIT-A-409 immediately.")
        elif up_to_time == "2026-07-16T23:45:00Z" or up_to_time == "2026-07-16T23:50:00Z":
            st.error("🚨 EMERGENCY ACTIVE EVACUATION: Evacuate all personnel in Zone A immediately towards Gate 2. Standard single-sensor alarms have not yet reached emergency thresholds, but compound risk model confirms fire hazard.")
            
        st.write("---")
        st.markdown("##### 📚 Regulatory Context Retrieval (RAG)")
        st.write("Consult the Factories Act or OISD guidelines:")
        
        # Maintain local session state for chat logs
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        # Display previous chats
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        user_query = st.text_input("Ask about safety regulations or past near-misses...", key="copilot_chat_input")
        if st.button("Submit Question", key="submit_copilot_chat"):
            if user_query:
                st.session_state.messages.append({"role": "user", "content": user_query})
                # Trigger retrieval
                with st.spinner("RAG Agent consulting vector indexes..."):
                    ans_payload = run_async_safe(safety_retriever.answer_safety_query(user_query))
                    st.session_state.messages.append({"role": "assistant", "content": ans_payload["answer"]})
                    # Rerun to update chat display
                    st.rerun()
                    
    with col_c2:
        st.markdown("##### 📚 Active Vector Store Citation Inspector")
        st.write("If you queried the regulatory assistant, matching database clauses will be displayed here:")
        
        if st.session_state.messages:
            # Show citations of the last assistant reply
            last_ans = [m for m in st.session_state.messages if m["role"] == "assistant"]
            if last_ans:
                # We can fetch citations by querying ChromaDB directly for the last user message
                last_user_query = [m["content"] for m in st.session_state.messages if m["role"] == "user"][-1]
                ans_payload = run_async_safe(safety_retriever.answer_safety_query(last_user_query))
                
                if ans_payload.get("citations"):
                    for cit in ans_payload["citations"]:
                        st.markdown(f"**Source:** {cit['source']} — *{cit['section']}*")
                        st.markdown(f"*{cit['excerpt']}*")
                        st.markdown("---")
                else:
                    st.write("*No direct database citations matches found for this query.*")
        else:
            st.write("*Submit a question to see the matching citation segments.*")

# Streamlit auto-play timeline advancement mechanism
if play_sim:
    # Advance state index
    st.session_state.timeline_index = (st.session_state.timeline_index + 1) % len(milestones)
    # Slow down speed
    time.sleep(2.5)
    st.rerun()
