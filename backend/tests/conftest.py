"""Pytest fixtures and LLM mocks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def audiopen_reviews() -> list[dict[str, Any]]:
    return json.loads((FIXTURES / "6502638001_reviews.json").read_text(encoding="utf-8"))


@pytest.fixture
def cookshelf_reviews() -> list[dict[str, Any]]:
    return json.loads((FIXTURES / "6743496454_reviews.json").read_text(encoding="utf-8"))


@pytest.fixture
def game_reviews() -> list[dict[str, Any]]:
    return json.loads((FIXTURES / "544007664_reviews.json").read_text(encoding="utf-8"))


@pytest.fixture
def mock_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub Claude calls with deterministic theme/takeaway payloads."""

    def fake_complete_json(
        *,
        system: str,
        user: str,
        tool_name: str,
        schema: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any] | None:
        if tool_name == "discovered_themes":
            return {
                "loves": [
                    {
                        "key": "core_feature",
                        "title": "Core feature works well",
                        "keywords": ["works", "great", "love"],
                    },
                    {
                        "key": "ease_of_use",
                        "title": "Easy to use",
                        "keywords": ["easy", "simple"],
                    },
                ],
                "pains": [
                    {
                        "key": "pricing",
                        "title": "Subscription too expensive",
                        "keywords": ["expensive", "subscription"],
                    },
                ],
            }
        if tool_name == "unified_themes":
            return {
                "themes": [
                    {
                        "key": "core_feature",
                        "title": "Core feature works well",
                        "type": "love",
                        "mention_count": 3,
                        "quotes": [
                            {
                                "author": "User1",
                                "storefront": "us",
                                "rating": 5,
                                "excerpt": "The core feature works great for my workflow.",
                            }
                        ],
                    },
                    {
                        "key": "ease_of_use",
                        "title": "Easy to use",
                        "type": "love",
                        "mention_count": 2,
                        "quotes": [
                            {
                                "author": "User3",
                                "storefront": "us",
                                "rating": 5,
                                "excerpt": "So easy and simple to use every day.",
                            }
                        ],
                    },
                    {
                        "key": "pricing",
                        "title": "Subscription too expensive",
                        "type": "pain",
                        "mention_count": 2,
                        "quotes": [
                            {
                                "author": "User2",
                                "storefront": "us",
                                "rating": 1,
                                "excerpt": "Too expensive for a subscription.",
                            }
                        ],
                    },
                ]
            }
        if tool_name == "strategic_takeaways":
            strength = {
                "title": "Highlight core feature",
                "summary": "Reviewers praise it often.",
                "points": ["Three mentions in this sample."],
                "based_on_theme": "Core feature works well",
            }
            fix = {
                "title": "Address subscription cost",
                "summary": "Several reviewers cite price.",
                "points": ["Mentioned in negative reviews."],
                "based_on_theme": "Subscription too expensive",
            }
            opp = {
                "title": "Connect praise and pricing concerns",
                "summary": "Users love the product but resist cost.",
                "points": ["Worth a focused pricing pass."],
                "based_on_theme": "Core feature works well",
            }
            return {
                "strengths": [strength, strength, strength, strength],
                "fixes": [fix, fix, fix, fix],
                "opportunities": [opp, opp, opp, opp],
            }
        if tool_name == "refined_quotes":
            return {"quotes": []}
        return None

    def fake_complete_json_many(
        requests: list[dict[str, Any]],
        *,
        max_workers: int | None = None,
    ) -> list[dict[str, Any] | None]:
        results = []
        for req in requests:
            if req.get("tool_name") == "theme_assignments":
                user = json.loads(req["user"])
                assignments = []
                for review in user.get("reviews", []):
                    assignments.append(
                        {
                            "theme_key": "core_feature",
                            "author": review.get("author"),
                            "storefront": review.get("storefront"),
                        }
                    )
                    if (review.get("rating") or 5) <= 2:
                        assignments.append(
                            {
                                "theme_key": "pricing",
                                "author": review.get("author"),
                                "storefront": review.get("storefront"),
                            }
                        )
                results.append({"assignments": assignments})
            else:
                results.append(fake_complete_json(**req))
        return results

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    targets = [
        "app.llm",
        "app.theme_discovery",
        "app.theme_unified",
        "app.theme_classifier",
        "app.takeaway_generator",
        "app.quote_refiner",
    ]
    import importlib

    for module_name in targets:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "complete_json"):
            monkeypatch.setattr(mod, "complete_json", fake_complete_json)
        if hasattr(mod, "complete_json_many"):
            monkeypatch.setattr(mod, "complete_json_many", fake_complete_json_many)
