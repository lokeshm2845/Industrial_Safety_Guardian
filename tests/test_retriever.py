import pytest
import os
import asyncio
import dotenv
from src.backend.rag.retriever import SafetyRetriever

def test_retriever_initialization_and_mock_fallback():
    # Save original dotenv load function and environment keys
    orig_load = dotenv.load_dotenv
    old_gemini_key = os.environ.pop("GEMINI_API_KEY", None)
    old_google_key = os.environ.pop("GOOGLE_API_KEY", None)
    
    # Mock load_dotenv so it doesn't load any actual key from disk during this test
    dotenv.load_dotenv = lambda *args, **kwargs: None

    try:
        retriever = SafetyRetriever()
        
        # Test basic query answering for hot work query
        res = asyncio.run(retriever.answer_safety_query("What are the guidelines for Hot Work?"))
        
        assert res["query"] == "What are the guidelines for Hot Work?"
        assert len(res["citations"]) > 0
        assert "OISD" in res["answer"] or "Factories Act" in res["answer"]
        assert "Safety Copilot Analysis" in res["answer"]
        assert "Gemini API key is not set" in res["answer"]

        # Test query answering for confined space query
        res_o2 = asyncio.run(retriever.answer_safety_query("What is the O2 deficiency threshold?"))
        assert len(res_o2["citations"]) > 0
        assert "19.5%" in res_o2["answer"] or "O2" in res_o2["answer"]

    finally:
        # Restore original functions and environment keys
        dotenv.load_dotenv = orig_load
        if old_gemini_key is not None:
            os.environ["GEMINI_API_KEY"] = old_gemini_key
        if old_google_key is not None:
            os.environ["GOOGLE_API_KEY"] = old_google_key
