"""Configurações do projeto.

Arquivo limpo e validado para evitar erros de sintaxe introduzidos por
edições automáticas anteriores.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "dados"
RAW_DIR = DATA_DIR / "brutos"
PROCESSED_DIR = DATA_DIR / "processados"
REPORTS_DIR = PROJECT_ROOT / "relatorios"
ASSETS_DIR = PROJECT_ROOT / "recursos"
TEMPLATES_DIR = PROJECT_ROOT / "modelos"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Data source defaults
NEWS_QUERY = os.getenv(
    "NEWS_QUERY",
    'SRAG,"Síndrome Respiratória Aguda Grave",Influenza,COVID-19,Brasil',
)

SRAG_CSV_PATH = os.getenv("SRAG_CSV_PATH", "").strip()
SRAG_CSV_URL = os.getenv(
    "SRAG_CSV_URL",
    "https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024",
).strip()

# Audit / governance paths
AUDIT_LOG_PATH = REPORTS_DIR / "audit.log"
DECISIONS_PATH = REPORTS_DIR / "decisions.jsonl"

# Feature flags
GOVERNANCE_ENABLED = os.getenv("GOVERNANCE_ENABLED", "1") == "1"

# Sensitive fields (comma separated env var)
SENSITIVE_FIELDS = [
    f.strip()
    for f in os.getenv("SENSITIVE_FIELDS", "nu_idade_n,cs_sexo").split(",")
    if f.strip()
]

# Pseudonymization settings
PSEUDONYMIZE_ENABLED = os.getenv("PSEUDONYMIZE_ENABLED", "0") == "1"
PSEUDONYMIZE_SALT = os.getenv("PSEUDONYMIZE_SALT", "")
PSEUDONYMIZE_MODE = os.getenv("PSEUDONYMIZE_MODE", "hash")

# Audit rotation and archival defaults
try:
    AUDIT_MAX_LINES = int(os.getenv("AUDIT_MAX_LINES", "5000"))
    try:
        AUDIT_MAX_BYTES = int(os.getenv("AUDIT_MAX_BYTES", str(5 * 1024 * 1024)))
    except Exception:
        AUDIT_MAX_BYTES = 5 * 1024 * 1024

    ARCHIVE_DIR = REPORTS_DIR / "archive"
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    S3_ARCHIVE_BUCKET = os.getenv("S3_ARCHIVE_BUCKET", "")
    S3_ARCHIVE_PREFIX = os.getenv("S3_ARCHIVE_PREFIX", "audit/")
except Exception:
    AUDIT_MAX_LINES = 5000


RELEVANT_COLUMNS = [
    "dt_sin_pri",
    "dt_notific",
    "dt_interna",
    "dt_evoluca",
    "evolucao",
    "uti",
    "cs_sexo",
    "nu_idade_n",
    "classi_fin",
    "vacina_cov",
    "vacina",
]
