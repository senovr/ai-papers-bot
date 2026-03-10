"""ZAI provider client for LLM operations."""

"""ZAI provider client for LLM operations."""

import json
from typing import Any, Optional

import json
from typing import Any, Optional

from src.core.config import settings
from src.llm.base_client import BaseLLMClient


from src.llm.base_client import BaseLLMClient


from src.core.config import settings


from src.llm.base_client import BaseLLMClient


class ZaiClient(BaseLLMClient):
    """Client for ZAI LLM provider (Claude/Gemini via zai)."""

    def __init__(self, api_key: Optional[str] = None, model: str = "glm-5"):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model
        # TODO: Initialize actual ZAI client when API is available
        self._client = None

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> str:
        """Generate completion using ZAI provider."""
        # TODO: Implement actual ZAI API call
        # For now, return stub response
        return await self._stub_complete(prompt, system_prompt, style="detailed")

    async def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        **kwargs: Any,
    ) -> dict:
        """Generate JSON completion using ZAI provider."""
        response = await self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=0.0,  # More deterministic for JSON
        )

        # Try to extract JSON from response
        try:
            # Find JSON in response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > 0:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            return json.loads(response)
        except json.JSONDecodeError:
            # Return default structure if parsing fails
            return {
                "rating": 50,
                "is_relevant": True,
                "error": "Failed to parse JSON",
            }

    async def is_relevant(self, abstract: str) -> bool:
        """Fast relevance check using ZAI."""
        prompt = f"""Analyze this paper abstract and determine if it's relevant for PRACTICAL LLM usage (not research/development).

Abstract: {abstract}

Is this paper relevant for users who want to APPLY LLM techniques in practice?
Consider relevant:
- Prompt engineering techniques
- Reasoning methods (CoT, ToT, etc.)
- RAG and retrieval methods
- LLM evaluation and benchmarks
- Practical LLM applications

Consider NOT relevant:
- Model training/finetuning papers
- Purely theoretical research
- Infrastructure optimization
- Computer vision only papers
- ML architecture improvements

Return ONLY: true or false"""

        response = await self.complete(
            prompt=prompt,
            max_tokens=10,
            temperature=0.0,
        )

        return "true" in response.lower()

    async def score_paper(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
    ) -> dict:
        """Deep scoring for paper quality and relevance."""
        content = f"""Analyze this research paper for PRACTICAL LLM applications:

Title: {title}
Abstract: {abstract}
"""

        if full_text:
            content += f"\nFull Text (excerpt):\n{full_text[:5000]}\n"

        content += """
Evaluate on these criteria:
1. **Practical Score** (0-40): Can users apply this in chat interfaces?
2. **Novelty Score** (0-30): New methods vs. incremental improvements
3. **Quality Score** (0-30): Rigorous testing, clear results, reproducible

Return JSON format:
{
    "rating": <total 0-100>,
    "practical_score": <0-40>,
    "novelty_score": <0-30>,
    "quality_score": <0-30>,
    "is_relevant": <true/false>,
    "summary": "<2-3 sentences>"
}"""

        return await self.complete_json(prompt=content, max_tokens=500)

    async def generate_summary(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
        style: str = "digest",
    ) -> str:
        """Generate summary in specified style."""
        style_prompts = {
            "digest": """Create a concise digest summary in Russian:

Title: {title}
Abstract: {abstract}

Format:
## 🎯 Суть (2-3 предложения)
<core findings>

## 💡 Как применять
<practical application>

## ⚠️ Ограничения
<limitations>""",
            "simple": """Explain this paper in simple terms (Russian):

Title: {title}
Abstract: {abstract}

Write as if explaining to a non-technical person:
- Avoid jargon
- Use analogies
- Focus on practical value
- Keep it under 200 words""",
            "concepts": """Extract atomic concepts from this paper:

Title: {title}
Abstract: {abstract}

For each concept, provide:
## Проблема
<what problem does this solve?>

## Тезис
<main claim or insight>

## Метод
<how does it work?>

## Когда применять
<specific use cases>

## Пример
<concrete example>""",
        }

        prompt = style_prompts.get(style, style_prompts["digest"])
        prompt = prompt.format(title=title, abstract=abstract)

        if full_text and style != "simple":
            prompt += f"\n\nFull Text Context:\n{full_text[:3000]}"

        return await self.complete(prompt=prompt, max_tokens=1500)

    async def extract_concepts(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
    ) -> list[dict]:
        """Extract atomic concepts from paper."""
        content = f"""Extract atomic concepts from this research paper:

Title: {title}
Abstract: {abstract}
"""

        if full_text:
            content += f"\nFull Text (excerpt):\n{full_text[:3000]}\n"

        content += """
For each concept, identify:
1. Type: "problem", "thesis", or "method"
2. Title: Short descriptive title (5-10 words)
3. Explanation: Clear explanation (1-2 sentences)
4. Example: Concrete usage example (optional)

Return JSON array:
[
    {
        "type": "problem",
        "title": "Limitation of context windows",
        "explanation": "LLMs struggle with long documents due to fixed context size",
        "example": "Processing 100-page reports requires chunking strategies"
    },
    {
        "type": "thesis",
        "title": "Hierarchical summarization improves recall",
        "explanation": "Multi-level summaries preserve more information than single-pass",
        "example": null
    }
]"""

        response = await self.complete_json(prompt=content, max_tokens=2000)

        if isinstance(response, list):
            return response
        if isinstance(response, dict) and "concepts" in response:
            return response["concepts"]
        return []

    async def _stub_complete(
        self, prompt: str, system_prompt: Optional[str] = None, style: str = "detailed"
    ) -> str:
        """Stub response for testing without API access."""
        # This is a fallback when ZAI API is not available
        return json.dumps(
            {
                "rating": 75,
                "practical_score": 30,
                "novelty_score": 25,
                "quality_score": 20,
                "is_relevant": True,
                "summary": "This paper presents interesting techniques for LLM optimization. Practical applications include improved context handling and efficiency gains.",
            },
            ensure_ascii=False,
        )
