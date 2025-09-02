from __future__ import annotations

import json

import datetime

# pathlib.Path não é usado aqui

from typing import Any, Dict, Iterable

from src.configuracao import (
    AUDIT_LOG_PATH,
    DECISIONS_PATH,
    GOVERNANCE_ENABLED,
    SENSITIVE_FIELDS,
)

from src.configuracao import (
    PSEUDONYMIZE_ENABLED,
    PSEUDONYMIZE_SALT,
    AUDIT_MAX_LINES,
    ARCHIVE_DIR,
)

import hashlib

from src.configuracao import AUDIT_MAX_BYTES

import shutil

from src.configuracao import PSEUDONYMIZE_MODE

from src.token_service import tokenize

from src.configuracao import S3_ARCHIVE_BUCKET, S3_ARCHIVE_PREFIX

import boto3

from botocore.exceptions import BotoCoreError, ClientError


def _ensure_paths():
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    DECISIONS_PATH.parent.mkdir(parents=True, exist_ok=True)


def audit(event: str, details: Dict[str, Any] | None = None) -> None:
    """Grava um evento de auditoria simples em formato texto (timestamped).



    Uso: audit('load_csv', {'path': 'data/raw/file.csv', 'rows': 123})

    """

    if not GOVERNANCE_ENABLED:
        return

    _ensure_paths()

    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "event": event,
        "details": details or {},
    }

    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    try:
        if AUDIT_MAX_LINES and AUDIT_MAX_LINES > 0:
            lines = AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()

            if len(lines) > AUDIT_MAX_LINES:
                AUDIT_LOG_PATH.write_text(
                    "\n".join(lines[-AUDIT_MAX_LINES:]), encoding="utf-8"
                )

    except Exception:
        pass

    try:
        if AUDIT_MAX_BYTES and AUDIT_MAX_BYTES > 0 and AUDIT_LOG_PATH.exists():
            if AUDIT_LOG_PATH.stat().st_size > AUDIT_MAX_BYTES:
                ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

                target = ARCHIVE_DIR / f"audit.{ts}.log"

                shutil.move(str(AUDIT_LOG_PATH), str(target))

                if S3_ARCHIVE_BUCKET:
                    client = boto3.client("s3")

                    key = f"{S3_ARCHIVE_PREFIX}audit.{ts}.log"

                    try:
                        client.upload_file(str(target), S3_ARCHIVE_BUCKET, key)

                        with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
                            f.write(
                                json.dumps(
                                    {
                                        "ts": datetime.datetime.utcnow().isoformat()
                                        + "Z",
                                        "event": "rotated_uploaded",
                                        "details": {
                                            "archived_to": str(target),
                                            "s3_key": key,
                                        },
                                    }
                                )
                                + "\n"
                            )

                    except (BotoCoreError, ClientError):
                        with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
                            f.write(
                                json.dumps(
                                    {
                                        "ts": datetime.datetime.utcnow().isoformat()
                                        + "Z",
                                        "event": "rotated_local_only",
                                        "details": {"archived_to": str(target)},
                                    }
                                )
                                + "\n"
                            )

                else:
                    with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
                        f.write(
                            json.dumps(
                                {
                                    "ts": datetime.datetime.utcnow().isoformat() + "Z",
                                    "event": "rotated",
                                    "details": {"archived_to": str(target)},
                                }
                            )
                            + "\n"
                        )

    except Exception:
        pass


def record_decision(decision: Dict[str, Any]) -> None:
    """Registra decisões dos agentes em JSONL (uma decisão por linha)."""

    if not GOVERNANCE_ENABLED:
        return

    _ensure_paths()

    decision_out = {"ts": datetime.datetime.utcnow().isoformat() + "Z", **decision}

    with open(DECISIONS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(decision_out, ensure_ascii=False) + "\n")


def scrub_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Remove ou anonimiza campos sensíveis de um registro.



    Atualmente substitui o valor por None para os campos listados em SENSITIVE_FIELDS.

    """

    if not record:
        return record

    out = dict(record)

    for f in SENSITIVE_FIELDS:
        if f in out:
            if PSEUDONYMIZE_ENABLED:
                v = str(out.get(f, ""))

                if PSEUDONYMIZE_MODE == "hash":
                    h = hashlib.sha256(
                        (PSEUDONYMIZE_SALT + v).encode("utf-8")
                    ).hexdigest()

                    out[f] = f"pseud_{h}"

                elif PSEUDONYMIZE_MODE == "token":
                    t = tokenize(f, v)

                    out[f] = f"tok_{t}"

                else:
                    out[f] = None

            else:
                out[f] = None

    return out


def guardrail_check(metrics: Dict[str, Any]) -> Iterable[str]:
    """Verificações simples de guardrail para métricas.



    Retorna uma lista de mensagens de violação (vazia se ok).

    Exemplos: valores percentuais fora de 0-1, contagens negativas.

    """

    violations = []

    for k in (
        "mortality_rate_30d",
        "icu_rate_30d",
        "vaccination_rate",
        "case_increase_rate",
    ):
        v = metrics.get(k)

        if v is None:
            continue

        try:
            fv = float(v)

        except Exception:
            violations.append(f"campo {k} não é numérico: {v}")

            continue

        if not (-1.0 <= fv <= 1.0):
            violations.append(f"campo {k} fora do intervalo esperado [-1, 1]: {fv}")

    for k in ("last7_cases", "prev7_cases"):
        v = metrics.get(k)

        if v is None:
            continue

        try:
            iv = int(v)

        except Exception:
            violations.append(f"campo {k} não é inteiro: {v}")

            continue

        if iv < 0:
            violations.append(f"campo {k} tem valor negativo: {iv}")

    return violations
