"""
AI Package to Run Agent Pipelines

AI package provides functionality that runs the agent pipeline to detect
texts in a receipt, analyze them and translate into preferred language.
"""

from backend.ai.servicer import run_pipeline

__all__ = [
    "run_pipeline",
]
