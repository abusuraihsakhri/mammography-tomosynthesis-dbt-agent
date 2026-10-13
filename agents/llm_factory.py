"""
Deterministic mock response adapter. External language-model providers are not implemented.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Mammography Tomosynthesis Dbt Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} Demo]: No language model or clinical verification is running. Received: '{prompt[:60]}...'"


class LLMFactory:
    """Creates configured LLM client instances with zero-PHI protection."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Mammography Tomosynthesis Dbt Agent"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError("Unsupported model provider: only the deterministic mock is implemented.")
