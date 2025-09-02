from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import secrets


STORE_PATH = Path(__file__).resolve().parents[1] / "data" / "tokens.json"
STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_store() -> dict:
    if not STORE_PATH.exists():
        return {}
    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_store(store: dict) -> None:
    STORE_PATH.write_text(
        json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def tokenize(field: str, value: str) -> str:
    """Return a stable token for (field, value)."""
    store = _load_store()
    key = f"{field}:{value}"
    if key in store:
        return store[key]
    token = secrets.token_urlsafe(24)
    store[key] = token
    _save_store(store)
    return token


def detokenize(field: str, token: str) -> Optional[str]:
    """Return the original value for a token if present.

    NOTE: This simple store is not secure and intended for demo/testing only.
    """
    store = _load_store()

    for k, v in store.items():
        if v == token:
            parts = k.split(":", 1)
            if len(parts) == 2:
                return parts[1]
    return None
