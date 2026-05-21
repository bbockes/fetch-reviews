"""Anthropic Claude API helpers."""

from __future__ import annotations

import os
from typing import Any

DEFAULT_MODEL = "claude-haiku-4-5-20251001"


def llm_configured() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def llm_model() -> str:
    return os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)


def complete_json(
    *,
    system: str,
    user: str,
    tool_name: str,
    schema: dict[str, Any],
) -> dict[str, Any] | None:
    """Call Claude with a forced tool-use response matching schema."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic
    except ImportError:
        return None

    client = anthropic.Anthropic(api_key=api_key)
    try:
        message = client.messages.create(
            model=llm_model(),
            max_tokens=8192,
            system=system,
            tools=[
                {
                    "name": tool_name,
                    "description": f"Structured response: {tool_name}.",
                    "input_schema": schema,
                }
            ],
            tool_choice={"type": "tool", "name": tool_name},
            messages=[{"role": "user", "content": user}],
        )
    except Exception:
        return None

    for block in message.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input

    return None
