"""Strip comments and emojis from Python files and create backups.

Usage:
    python scripts/strip_comments_and_emojis.py

This script is careful with string prefixes and multi-line strings. It uses
tokenize to preserve code structure and only removes comment tokens and
emoji characters inside strings and other tokens.
"""

from __future__ import annotations

import io
import shutil
import tokenize
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
BACKUP_DIR = ROOT / "scripts" / "backup_before_strip"


EMOJI_PATTERN = re.compile(
    r"[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF]+",
    flags=re.UNICODE,
)


def _remove_emojis_from_string_literal(s: str) -> str:
    """Remove emojis from a Python string literal content (not including quotes).

    s is the inner content; return the cleaned inner content.
    """
    return EMOJI_PATTERN.sub("", s)


def strip_file(path: Path) -> bool:
    try:
        src = path.read_bytes()
    except Exception:
        return False

    try:
        tokens = list(tokenize.tokenize(io.BytesIO(src).readline))
    except Exception:
        return False

    new_tokens = []

    for tok in tokens:
        ttype = tok.type
        tstr = tok.string

        # drop comments entirely
        if ttype == tokenize.COMMENT:
            continue

        # handle string literals: remove emojis inside the quotes
        if ttype == tokenize.STRING and len(tstr) >= 2:
            # detect prefix and quote type
            m = re.match(
                r"(?i)([rubf]*)(['\"]{1,3})(.*)(['\"]{1,3})$", tstr, flags=re.DOTALL
            )
            if m:
                prefix = m.group(1)
                start_quote = m.group(2)
                inner = m.group(3)
                end_quote = m.group(4)
                # clean inner
                clean_inner = _remove_emojis_from_string_literal(inner)
                tstr = f"{prefix}{start_quote}{clean_inner}{end_quote}"
            else:
                # fallback: remove emojis anywhere in the token
                tstr = EMOJI_PATTERN.sub("", tstr)
        else:
            # remove emojis from other token types (e.g., NAME/OP) defensively
            if isinstance(tstr, str) and EMOJI_PATTERN.search(tstr):
                tstr = EMOJI_PATTERN.sub("", tstr)

        new_tokens.append(tokenize.TokenInfo(ttype, tstr, tok.start, tok.end, tok.line))

    try:
        new_src = tokenize.untokenize(new_tokens)
    except Exception:
        return False

    if isinstance(new_src, (bytes, bytearray)):
        try:
            new_src = new_src.decode("utf-8")
        except Exception:
            new_src = new_src.decode("utf-8", errors="replace")

    rel = path.relative_to(ROOT)
    bak_path = BACKUP_DIR / rel
    bak_path.parent.mkdir(parents=True, exist_ok=True)

    # don't process files inside the backup dir
    if BACKUP_DIR in path.parents:
        return False

    shutil.copy2(path, bak_path)
    path.write_text(new_src, encoding="utf-8")
    return True


def iter_py_files():
    for p in ROOT.rglob("*.py"):
        if ".venv" in p.parts or "__pycache__" in p.parts:
            continue
        if BACKUP_DIR in p.parents:
            continue
        yield p


def main() -> int:
    changed = 0
    total = 0
    for p in iter_py_files():
        total += 1
        ok = strip_file(p)
        if ok:
            changed += 1
    print(
        f"Processed {total} python files, modified {changed} files. Backups in {BACKUP_DIR}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
