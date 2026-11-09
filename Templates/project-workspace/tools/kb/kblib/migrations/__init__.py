"""Numbered, idempotent workspace data migrations, applied in order by `kb upgrade`.

Each module defines: ID (str), needs(ws) -> bool, questions(ws) -> List[Question],
apply(ws, answers: dict, journal) -> List[str] (lines to print).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Question:
    id: str
    text: str
    candidates: List[str] = field(default_factory=list)
    how: str = ""


def all_migrations():
    from . import m001_initial, m002_agents_skills
    return [m001_initial, m002_agents_skills]
