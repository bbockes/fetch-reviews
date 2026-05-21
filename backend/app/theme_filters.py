"""Filters for generic vs feature-specific theme titles."""

from __future__ import annotations

import re

GENERIC_LOVE_TITLE_RE = re.compile(
    r"enthusiasm|game.?changer|generic praise|what delighted|overall love|"
    r"amazing app|best app|love this app|users love|strong praise",
    re.I,
)

GENERIC_PAIN_TITLE_RE = re.compile(
    r"common complaint|generic|overall hate|terrible app|hate this app|"
    r"worst app|users hate|strong complaint|overall frustration|what hurts",
    re.I,
)


def is_feature_love_theme(title: str) -> bool:
    return not GENERIC_LOVE_TITLE_RE.search(title)


def is_feature_pain_theme(title: str) -> bool:
    return not GENERIC_PAIN_TITLE_RE.search(title)
