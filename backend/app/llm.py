"""Anthropic Claude API helpers."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_MAX_PARALLEL = 4

CLASSIFICATION_BATCH_SIZE = 40
QUOTE_BATCH_SIZE = 10


def llm_configured() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY"))


def llm_model() -> str:
    return os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)


def max_parallel_calls() -> int:
    raw = os.getenv("ANTHROPIC_MAX_PARALLEL", str(DEFAULT_MAX_PARALLEL))
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_MAX_PARALLEL


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


def complete_json_many(
    requests: list[dict[str, Any]],
    *,
    max_workers: int | None = None,
) -> list[dict[str, Any] | None]:
    """Run multiple structured Claude calls in parallel."""
    if not requests:
        return []

    workers = max_workers or max_parallel_calls()
    if len(requests) == 1:
        req = requests[0]
        return [
            complete_json(
                system=req["system"],
                user=req["user"],
                tool_name=req["tool_name"],
                schema=req["schema"],
            )
        ]

    results: list[dict[str, Any] | None] = [None] * len(requests)
    with ThreadPoolExecutor(max_workers=min(workers, len(requests))) as pool:
        future_to_idx = {
            pool.submit(
                complete_json,
                system=req["system"],
                user=req["user"],
                tool_name=req["tool_name"],
                schema=req["schema"],
            ): idx
            for idx, req in enumerate(requests)
        }
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except Exception:
                results[idx] = None

    return results
