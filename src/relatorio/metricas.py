from __future__ import annotations
import pandas as pd
from datetime import datetime, timedelta


def _safe_div(n: float, d: float) -> float:
    return float(n) / float(d) if float(d) != 0 else 0.0


def compute_core_metrics(df: pd.DataFrame) -> dict:
    now = pd.Timestamp(datetime.utcnow().date())

    if "case_date" not in df.columns:
        raise ValueError("DataFrame sem coluna 'case_date' após limpeza")

    last7_start = now - timedelta(days=7)
    prev7_start = now - timedelta(days=14)

    mask_last7 = (df["case_date"] >= last7_start) & (df["case_date"] < now)
    mask_prev7 = (df["case_date"] >= prev7_start) & (df["case_date"] < last7_start)

    last7_cases = int(mask_last7.sum())
    prev7_cases = int(mask_prev7.sum())

    case_increase_rate = _safe_div(
        last7_cases - prev7_cases, prev7_cases if prev7_cases else 1
    )

    last30_start = now - timedelta(days=30)
    mask_30 = (df["case_date"] >= last30_start) & (df["case_date"] < now)
    df_30 = df.loc[mask_30]
    deaths_30 = int(df_30.get("death_flag", pd.Series(False, index=df_30.index)).sum())
    cases_30 = int(len(df_30))
    mortality_rate_30d = _safe_div(deaths_30, cases_30)

    icu_30 = int(df_30.get("icu_flag", pd.Series(False, index=df_30.index)).sum())
    icu_rate_30d = _safe_div(icu_30, cases_30)

    last12m_start = now - timedelta(days=365)
    df_12m = df[(df["case_date"] >= last12m_start) & (df["case_date"] < now)]
    if "vaccinated_flag" in df_12m.columns:
        known = df_12m[~df_12m["vaccinated_flag"].isna()]
        vaccinated = int(known["vaccinated_flag"].fillna(False).sum())
        denom = int(len(known)) if len(known) else int(len(df_12m))
    else:
        vaccinated = 0
        denom = int(len(df_12m)) if len(df_12m) else 1
    vaccination_rate = _safe_div(vaccinated, denom)

    return {
        "last7_cases": last7_cases,
        "prev7_cases": prev7_cases,
        "case_increase_rate": case_increase_rate,
        "mortality_rate_30d": mortality_rate_30d,
        "icu_rate_30d": icu_rate_30d,
        "vaccination_rate": vaccination_rate,
        "as_of": str(now.date()),
    }
