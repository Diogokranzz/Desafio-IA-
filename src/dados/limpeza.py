from __future__ import annotations

from pathlib import Path

from typing import List

import pandas as pd

import numpy as np


from src.configuracao import RELEVANT_COLUMNS, SENSITIVE_FIELDS

from src.governance import audit


def _normalize_columns(columns: List[str]) -> List[str]:
    return [c.strip().lower() for c in columns]


def _parse_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", dayfirst=False, format=None)


def load_and_clean_srag(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, dtype=str, low_memory=False)

    audit("load_csv", {"path": str(csv_path), "rows_read": int(len(df))})

    df.columns = _normalize_columns(df.columns.tolist())

    present = [c for c in RELEVANT_COLUMNS if c in df.columns]

    if present:
        df = df[present].copy()

    for date_col in ["dt_sin_pri", "dt_notific", "dt_interna"]:
        if date_col in df.columns:
            df[date_col] = _parse_date(df[date_col])

    df["case_date"] = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")

    for date_col in ["dt_sin_pri", "dt_notific", "dt_interna"]:
        if date_col in df.columns:
            df["case_date"] = df["case_date"].combine_first(df[date_col])

    if "uti" in df.columns:
        df["icu_flag"] = (
            df["uti"]
            .astype(str)
            .str.strip()
            .str.upper()
            .isin(["1", "SIM", "YES", "Y", "TRUE"])
        )

    else:
        df["icu_flag"] = False

    death_predicates = [
        lambda s: s.astype(str).str.strip() == "2",
        lambda s: s.astype(str).str.upper().str.contains("OBITO", na=False),
        lambda s: s.astype(str).str.upper().str.contains("ÓBITO", na=False),
        lambda s: s.astype(str).str.upper().str.contains("DEATH", na=False),
    ]

    if "evolucao" in df.columns:
        death_series = pd.Series(False, index=df.index)

        for pred in death_predicates:
            death_series = death_series | pred(df["evolucao"])

        df["death_flag"] = death_series

    else:
        df["death_flag"] = False

    vac_sources = [c for c in ["vacina_cov", "vacina"] if c in df.columns]

    if vac_sources:
        vac = None

        for c in vac_sources:
            col = df[c].astype(str).str.strip().str.upper()

            flag = col.isin(["1", "SIM", "YES", "Y", "TRUE"])

            vac = flag if vac is None else (vac | flag)

        df["vaccinated_flag"] = vac.fillna(False)

    else:
        df["vaccinated_flag"] = np.nan

    if "case_date" in df.columns:
        df = df[~df["case_date"].isna()].copy()

        df["case_date"] = pd.to_datetime(df["case_date"], errors="coerce")

        df = df[~df["case_date"].isna()].copy()

    for f in SENSITIVE_FIELDS:
        if f in df.columns:
            df[f] = None

    audit(
        "clean_csv",
        {
            "path": str(csv_path),
            "rows_after_clean": int(len(df)),
            "sensitive_cleared": SENSITIVE_FIELDS,
        },
    )

    return df
