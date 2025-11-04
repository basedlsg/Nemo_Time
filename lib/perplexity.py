"""
Lightweight Perplexity integration stub used for local testing.
Provides deterministic fallback responses when the real Perplexity
service is not available.
"""

from __future__ import annotations

from typing import Dict, Any, List

from lib.sanitize import normalize_query
from lib.composer import compose_response


def answer_with_perplexity(
    question: str,
    province: str,
    asset: str,
    *,
    lang: str = "zh-CN",
    doc_class: str = "grid"
) -> Dict[str, Any]:
    """
    Return a deterministic fallback answer that mimics the structure of the
    real Perplexity integration so tests can run without external services.
    """
    normalized_question = normalize_query(question)

    synthetic_candidates: List[Dict[str, Any]] = [
        {
            "title": f"{province.upper()}省{asset}项目{doc_class}并网指南",
            "content": (
                f"针对{province}地区的{asset}项目，{doc_class}并网流程一般包括备案申请、"
                f"技术评估、并网验收等关键步骤，建议提前准备完整的资料清单。"
            ),
            "url": f"https://example.com/{province}/{asset}/{doc_class}/guide",
            "province": province,
            "asset": asset,
            "doc_class": doc_class,
            "effective_date": "2024-01-01",
        }
    ]

    response = compose_response(synthetic_candidates, normalized_question, lang)

    if not response.get("answer_zh"):
        response["answer_zh"] = (
            f"{normalized_question}需关注备案申请、技术评估、并网验收等要点，以保证顺利接入电网。"
        )

    if not response.get("citations"):
        response["citations"] = [
            {
                "title": synthetic_candidates[0]["title"],
                "url": synthetic_candidates[0]["url"],
                "effective_date": synthetic_candidates[0]["effective_date"],
            }
        ]

    return response


__all__ = ["answer_with_perplexity"]
