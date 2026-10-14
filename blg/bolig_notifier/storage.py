"""Tracks which listing IDs have already been seen, so we only notify once per listing."""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_STATE_FILE = Path(__file__).resolve().parent.parent / "data" / "seen_listings.json"


def load_seen_ids(state_file: Path = DEFAULT_STATE_FILE) -> set[str]:
    if not state_file.exists():
        return set()
    return set(json.loads(state_file.read_text()))


def save_seen_ids(ids: set[str], state_file: Path = DEFAULT_STATE_FILE) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(sorted(ids), ensure_ascii=False, indent=2))
