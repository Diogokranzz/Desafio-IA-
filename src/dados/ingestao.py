from pathlib import Path
from typing import Optional
import glob
from src.configuracao import RAW_DIR, SRAG_CSV_PATH, PROJECT_ROOT
from src.governance import audit


def ensure_srag_csv(optional_path: Optional[str] = None) -> Path:
    """Retorna um caminho válido para o CSV de SRAG.
    Prioridade: argumento explícito -> env SRAG_CSV_PATH -> primeiro CSV em dados/brutos -> legado data/raw.
    Lança FileNotFoundError se nada for encontrado.
    """
    if optional_path:
        path = Path(optional_path)
        if path.exists():
            audit("select_csv", {"method": "argument", "path": str(path)})
            return path
        raise FileNotFoundError(
            f"CSV não encontrado no caminho informado por --csv: {path}"
        )

    if SRAG_CSV_PATH:
        env_path = Path(SRAG_CSV_PATH)
        if env_path.exists():
            audit("select_csv", {"method": "env", "path": str(env_path)})
            return env_path

    candidates = sorted(glob.glob(str(RAW_DIR / "*.csv")))
    if candidates:
        p = Path(candidates[0])
        audit("select_csv", {"method": "raw_dir_first", "path": str(p)})
        return p

    legacy_raw = PROJECT_ROOT / "data" / "raw"
    legacy_candidates = sorted(glob.glob(str(legacy_raw / "*.csv")))
    if legacy_candidates:
        p = Path(legacy_candidates[0])
        audit("select_csv", {"method": "legacy_data_raw", "path": str(p)})
        return p

    raise FileNotFoundError(
        "Nenhum CSV de SRAG encontrado. Coloque um arquivo em 'dados/brutos' (ou antigo 'data/raw') ou use --csv / SRAG_CSV_PATH."
    )
