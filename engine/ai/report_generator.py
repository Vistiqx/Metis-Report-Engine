
    """AI report generation interface for Metis Report Engine.

    This module provides an integration surface for future AI-driven report
    generation workflows without coupling the renderer to any one model or
    provider.
    """

    from __future__ import annotations

    from dataclasses import dataclass
    from typing import Any, Dict, Protocol


    @dataclass
    class GenerationRequest:
        report_type: str
        instructions: str
        source_material: str
        preferred_output: str = "dsl"


    class AIProvider(Protocol):
        def generate(self, prompt: str) -> str:
            ...


    class ReportGenerator:
        """Thin orchestration wrapper around pluggable AI providers."""

        def __init__(self, provider: AIProvider) -> None:
            self.provider = provider

        def build_prompt(self, request: GenerationRequest) -> str:
            return f"""Generate a {request.report_type} report.
Preferred output: {request.preferred_output}

Instructions:
{request.instructions}

Source material:
{request.source_material}
"""

        def generate(self, request: GenerationRequest) -> Dict[str, Any]:
            prompt = self.build_prompt(request)
            output = self.provider.generate(prompt)
            return {
                "report_type": request.report_type,
                "preferred_output": request.preferred_output,
                "raw_output": output,
            }
