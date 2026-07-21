import json
import os
import chromadb

class SafetyVectorStore:
    def __init__(self, persist_dir=None):
        if persist_dir is None:
            persist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/chroma_db"))
        self.persist_dir = persist_dir
        
        # Ensure parent folder exists
        os.makedirs(os.path.dirname(self.persist_dir), exist_ok=True)
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection_name = "safety_docs"
        
        # Get or create safety documents collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def ingest_regulations(self, oisd_path, factory_path):
        """
        Split OISD guidelines and Factory Act files into sections and add them to ChromaDB.
        """
        # 1. Ingest OISD Guidelines
        if os.path.exists(oisd_path):
            with open(oisd_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Split by markdown-like double newlines or headers
            sections = [s.strip() for s in content.split("\n\n") if s.strip()]
            documents = []
            metadatas = []
            ids = []
            
            for i, sec in enumerate(sections):
                if len(sec) < 30:  # skip headers/decorations
                    continue
                documents.append(sec)
                metadatas.append({"source": "OISD Guidelines", "section": f"Clause {i+1}"})
                ids.append(f"oisd_clause_{i}")
            
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

        # 2. Ingest Factories Act, 1948
        if os.path.exists(factory_path):
            with open(factory_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            sections = [s.strip() for s in content.split("Section ") if s.strip()]
            documents = []
            metadatas = []
            ids = []
            
            for i, sec in enumerate(sections):
                sec_text = "Section " + sec
                if len(sec_text) < 30:
                    continue
                # Extract first line as title reference
                title = sec_text.split("\n")[0].strip()
                documents.append(sec_text)
                metadatas.append({"source": "Factories Act, 1948", "section": title})
                ids.append(f"factory_sec_{i}")
                
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

    def ingest_incidents(self, incidents_path):
        """
        Ingest mock near-miss incident history items from JSON.
        """
        if os.path.exists(incidents_path):
            with open(incidents_path, "r", encoding="utf-8") as f:
                incidents = json.load(f)
                
            documents = []
            metadatas = []
            ids = []
            
            for inc in incidents:
                text_content = (
                    f"Incident Reference: {inc['incident_id']}\n"
                    f"Title: {inc['title']}\n"
                    f"Zone: {inc['zone']}\n"
                    f"Description: {inc['description']}\n"
                    f"Root Cause: {inc['root_cause']}\n"
                    f"Corrective Actions: {inc['corrective_actions']}\n"
                    f"Keywords: {', '.join(inc['tags'])}"
                )
                documents.append(text_content)
                metadatas.append({
                    "source": "Incident History",
                    "incident_id": inc["incident_id"],
                    "zone": inc["zone"],
                    "tags": ",".join(inc["tags"])
                })
                ids.append(inc["incident_id"])
                
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

    def query(self, query_text: str, n_results: int = 3):
        """
        Query the database collection for similar documents.
        """
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
