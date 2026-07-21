# Incident Pattern Intelligence (RAG)

## Description
RAG-powered agent that cross-references incident reports and regulations.

## Technical Requirements
- **Vector Database**: ChromaDB
- **LLM**: Gemini via Antigravity SDK
- **Documents**: OISD guidelines, Factory Act, incident reports

## Implementation Steps
1. Create `src/backend/rag/vector_store.py` - sets up ChromaDB
2. Create `src/backend/rag/retriever.py` - retrieves relevant documents
3. Ingest sample incident reports and regulations
4. Build retrieval pipeline with Gemini

## Deliverables
- Document ingestion pipeline
- Vector store with safety documents
- RAG query endpoint
- Citation generation
