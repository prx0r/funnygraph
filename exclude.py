"""Shared exclusion guard. Import + call in every pipeline script.

    from exclude import EXCLUDED, is_out, filter_ids

Owner-prerogative exclusions live in excluded.json (see EXCLUSIONS.md).
"""
from __future__ import annotations

import json
from pathlib import Path


def _load() -> set:
    try:
        here = Path(__file__).parent
        ex = json.loads((here / "excluded.json").read_text())
        return set(ex.get("excluded", []))
    except Exception:
        return set()


EXCLUDED: set = _load()


def is_out(cid: str) -> bool:
    return cid in EXCLUDED


def filter_ids(ids):
    return [i for i in ids if i not in EXCLUDED]
