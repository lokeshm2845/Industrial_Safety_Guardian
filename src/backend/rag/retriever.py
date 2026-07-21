import os
import asyncio

# Ensure .env is loaded BEFORE importing google.antigravity to prevent import-time caching of env keys
try:
    from dotenv import load_dotenv
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    env_path = os.path.join(base_dir, ".env")
    load_dotenv(dotenv_path=env_path, override=True)
except Exception:
    pass

from google.antigravity import Agent, LocalAgentConfig
from .vector_store import SafetyVectorStore

def generate_mock_safety_response(user_query: str, citations: list) -> str:
    # Build a synthesized response based on context citations
    response_lines = [
        "### 🛡️ Safety Copilot Analysis (Local Database Synthesis)",
        "⚠️ *The Gemini API key is not set. A high-fidelity safety synthesis was generated from local regulations and incident logs.*",
        ""
    ]
    
    q = user_query.lower()
    
    # 1. Regulations matching
    matched_regs = []
    matched_incidents = []
    
    for c in citations:
        src = c["source"]
        sec = c["section"]
        excerpt = c["excerpt"]
        
        if "oisd" in src.lower():
            matched_regs.append(c)
        elif "factories act" in src.lower() or "factory" in src.lower():
            matched_regs.append(c)
        elif "incident" in src.lower() or "inc-" in str(sec).lower():
            matched_incidents.append(c)
            
    # Synthesize section based on topics
    if "hot work" in q or "welding" in q or "spark" in q or "grind" in q:
        response_lines.extend([
            "#### 1. Hot Work Regulatory Guidelines & Permit Standards",
            "According to **OISD-137 (Work Permit System)**, Hot Work includes any activity involving welding, grinding, cutting, or producing sparks/flame.",
            "- **Mandatory LEL Limit:** Gas testing must show **0.0% LEL** prior to starting work.",
            "- **Continuous Monitoring:** Required on hydrocarbon lines or manifolds where gas levels may fluctuate.",
            "- **Automatic Suspension:** All active hot work permits must be immediately suspended if LEL rises above 2% or a CO trend warning is flagged.",
            "- **Isolation/LOTO:** DBB (Double Block and Bleed) is required for hot work on hydrocarbon lines, and all electrical/process sources must be verified locked out.",
            ""
        ])
        # Add matching incidents
        inc_list = []
        for inc in matched_incidents:
            if "INC-2025-012" in str(inc["section"]):
                inc_list.append("- **INC-2025-012 (Flash Fire During Piping Modification):** A contractor crew welding under a Hot Work permit triggered a local flash fire due to trapped gas pocket escape. *Key lesson learned: Mandate portable monitors within 1 meter of welding and implement continuous local detection rather than relying on distant area sensors.*")
        if inc_list:
            response_lines.extend(["#### 2. Related Incident Precedents"] + inc_list + [""])
            
    elif "loto" in q or "lockout" in q or "tagout" in q or "isolation" in q or "transformer" in q:
        response_lines.extend([
            "#### 1. Isolation & Lockout-Tagout (LOTO) Regulations",
            "- **OISD Guidelines:** Isolation of electrical, mechanical, hydraulic, and process hazards is mandatory. Lock and Tag must be applied by authorized safety leads. For hydrocarbon lines, Double Block and Bleed (DBB) is mandatory.",
            "- **Factories Act Sec. 37:** Exclusion or effective isolation of all sources of ignition is required when handling flammable dust or gas.",
            ""
        ])
        # Check incidents
        inc_list = []
        for inc in matched_incidents:
            if "INC-2025-088" in str(inc["section"]):
                inc_list.append("- **INC-2025-088 (Toxic Gas Leak):** Pump flange was opened without verified LOTO, causing a CO gas leak and inhalation symptoms. *Lesson: Enforce active LOTO validation prior to permit signoff.*")
            elif "INC-2026-003" in str(inc["section"]):
                inc_list.append("- **INC-2026-003 (Arc Flash):** Substation maintenance caused an arc flash due to physical verification failure. *Lesson: Mandate live-line testing and physical key lock box systems.*")
        if inc_list:
            response_lines.extend(["#### 2. Related Incident Precedents"] + inc_list + [""])
            
    elif "confined" in q or "tank" in q or "oxygen" in q or "o2" in q or "deficiency" in q:
        response_lines.extend([
            "#### 1. Confined Space & Dangerous Gas Precautions (Factories Act Section 36)",
            "- **Entry Requirements:** Entry into tanks, vats, flues, or pipes is strictly prohibited unless:",
            "  1. A suitable access/manhole is provided.",
            "  2. Practical measures are taken to remove fumes and prevent gas ingress.",
            "  3. The atmosphere is certified safe (O2 must be > 19.5% and CO < 25 ppm).",
            "  4. Workers wear a safety belt/rope, and an observer is stationed outside for immediate rescue.",
            ""
        ])
        # Check incidents
        inc_list = []
        for inc in matched_incidents:
            if "INC-2025-104" in str(inc["section"]):
                inc_list.append("- **INC-2025-104 (O2 Deficiency in Tank T-102):** A worker entering a storage tank experienced lightheadedness due to 18.2% O2. *Lesson: Require continuous forced-air ventilation and secondary telemetry monitoring for all confined spaces.*")
        if inc_list:
            response_lines.extend(["#### 2. Related Incident Precedents"] + inc_list + [""])
            
    elif "gas" in q or "co" in q or "lel" in q or "h2s" in q or "detector" in q or "alarm" in q:
        response_lines.extend([
            "#### 1. Gas Detector Thresholds & Alarm Standards",
            "According to **OISD-STD-105 / OISD-137**:",
            "- **Hydrocarbons:** Pre-alarm at 10% LEL, Emergency alarm at 20% LEL.",
            "- **Carbon Monoxide (CO):** Pre-alarm at 25 ppm, Emergency alarm at 50 ppm.",
            "- **Hydrogen Sulfide (H2S):** Pre-alarm at 5 ppm, Emergency alarm at 10 ppm.",
            "- **Oxygen (O2):** Below 19.5% indicates immediate danger requiring SCBA (Self-Contained Breathing Apparatus).",
            "- **Trend Triggers:** An increase trend of >2% per minute of toxic/flammable gas concentration constitutes a critical compound risk if hot work is active.",
            ""
        ])
    else:
        # Default safety compliance synthesis
        response_lines.extend([
            "#### 1. Safety Regulations & Compliance Overview",
            "The retrieved database contains guidelines regarding work permits, isolation procedures, and gas monitoring standards.",
            "- **Work Permit & LOTO:** All hazardous work requires validation of isolation (LOTO) and active permits.",
            "- **Atmospheric Monitoring:** Mandatory testing before and during hot work or confined space entry.",
            "- **Emergency Evacuation:** Automatic triggers based on gas concentration trends or high alarm thresholds.",
            ""
        ])

    # Show retrieved sources
    response_lines.append("#### 📚 Direct Citations Used in Analysis:")
    for c in citations:
        response_lines.append(f"- **{c['source']}** ({c['section']}): *\"{c['excerpt'].strip()}\"*")
        
    response_lines.extend([
        "",
        "---",
        "💡 *To enable full Gemini AI cognitive analysis, please set your Google Gemini API key in a `.env` file (e.g. `GEMINI_API_KEY=your_key`) or as an environment variable.*"
    ])
    
    return "\n".join(response_lines)


class SafetyRetriever:
    def __init__(self, vector_store=None):
        if vector_store is None:
            self.vector_store = SafetyVectorStore()
        else:
            self.vector_store = vector_store
        
        # Trigger ingestion on startup if collection is empty
        self.initialize_store_data()

    def initialize_store_data(self):
        """
        Check if documents are already ingested. If not, run ingestion.
        """
        try:
            count = self.vector_store.collection.count()
            if count == 0:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
                oisd = os.path.join(base_dir, "regulations/oisd_guidelines.txt")
                factory = os.path.join(base_dir, "regulations/factory_act.txt")
                incidents = os.path.join(base_dir, "incidents/sample_incidents.json")
                
                self.vector_store.ingest_regulations(oisd, factory)
                self.vector_store.ingest_incidents(incidents)
                print(f"RAG Vector Store initialized. Ingested {self.vector_store.collection.count()} clauses/reports.")
        except Exception as e:
            print(f"Error during RAG ingestion: {e}")

    async def answer_safety_query(self, user_query: str) -> dict:
        """
        Retrieves top reference documents from vector database, feeds them to Gemini, and returns a cited response.
        """
        # Query ChromaDB for top 3 matching chunks
        try:
            results = self.vector_store.query(user_query, n_results=3)
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
        except Exception as e:
            documents = []
            metadatas = []
            print(f"Error querying ChromaDB: {e}")

        # Format context for the prompt
        context_str = ""
        citations = []
        for doc, meta in zip(documents, metadatas):
            source = meta.get("source", "Unknown")
            sec = meta.get("section", meta.get("incident_id", ""))
            citation_label = f"[{source} - {sec}]"
            citations.append({
                "source": source,
                "section": sec,
                "excerpt": doc[:200] + "..." if len(doc) > 200 else doc
            })
            context_str += f"\n--- SOURCE: {citation_label} ---\n{doc}\n"

        # Construct system instructions and context-rich prompt
        system_instruction = (
            "You are the RAG Safety Agent for the Industrial Safety Guardian platform.\n"
            "Your task is to answer queries from the Safety Officer using only the provided context and regulations.\n"
            "If the context does not contain the answer, say that you cannot find it in active documents.\n"
            "Always cite your sources using the format [Source Name - Section/ID] in your explanation."
        )

        prompt = (
            f"{system_instruction}\n\n"
            f"Here is the context retrieved from the safety documents database:\n"
            f"{context_str}\n"
            f"User Query: {user_query}\n\n"
            f"Please write a professional, detailed response that directly answers the query and explicitly cites the source clauses."
        )

        answer_text = ""
        # Invoke Gemini Agent via google-antigravity SDK
        try:
            # First, check if GEMINI_API_KEY is in environment. If not, try loading with dotenv
            # We also try to load if the value is the placeholder to refresh it.
            current_key = os.environ.get("GEMINI_API_KEY")
            if not current_key or current_key == "YOUR_GEMINI_API_KEY_HERE" or not os.environ.get("GOOGLE_API_KEY"):
                try:
                    from dotenv import load_dotenv
                    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
                    env_path = os.path.join(base_dir, ".env")
                    load_dotenv(dotenv_path=env_path, override=True) # Load and override
                except Exception:
                    pass

            # If still not present or is the placeholder, raise a specific error to trigger mock fallback
            resolved_key = os.environ.get("GEMINI_API_KEY")
            
            # Diagnostic log
            try:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
                env_path = os.path.join(base_dir, ".env")
                with open(r"C:\Users\Asus\AppData\Local\Temp\debug_env.log", "a") as f:
                    f.write(f"CWD: {os.getcwd()}\n")
                    f.write(f"env_path: {env_path}\n")
                    f.write(f"Exists: {os.path.exists(env_path)}\n")
                    f.write(f"KEY: {resolved_key}\n")
                    f.write(f"GOOGLE_API_KEY: {os.environ.get('GOOGLE_API_KEY')}\n")
                    f.write("-" * 40 + "\n")
            except Exception:
                pass

            if (not resolved_key or resolved_key == "YOUR_GEMINI_API_KEY_HERE") and not os.environ.get("GOOGLE_API_KEY"):
                raise ValueError("A Gemini API key is required. Set it via GEMINI_API_KEY.")

            config = LocalAgentConfig()
            async with Agent(config) as agent:
                response = await agent.chat(prompt)
                # Google Antigravity Agent returns an object. Let's retrieve its text response
                answer_text = await response.text()
        except Exception as e:
            # Check if the error is due to missing API key
            err_msg = str(e)
            is_missing_key = (
                "API key" in err_msg or 
                "GEMINI_API_KEY" in err_msg or 
                "GOOGLE_API_KEY" in err_msg or 
                "apikey" in err_msg.lower()
            )
            if is_missing_key:
                answer_text = generate_mock_safety_response(user_query, citations)
            else:
                answer_text = (
                    f"Error invoking Gemini via Antigravity SDK: {e}\n\n"
                    f"Direct Retrieval Context:\n" + 
                    "\n".join([f"• {c['source']} ({c['section']})" for c in citations])
                )

        return {
            "query": user_query,
            "answer": answer_text,
            "citations": citations
        }
