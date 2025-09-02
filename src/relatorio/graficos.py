from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

from src.configuracao import REPORTS_DIR


def _ensure_reports_dir() -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR


def generate_charts(df: pd.DataFrame) -> tuple[Path, Path]:
    out_dir = _ensure_reports_dir()

    now = pd.Timestamp(datetime.utcnow().date())
    start_30 = now - timedelta(days=30)
    df_30 = df[(df["case_date"] >= start_30) & (df["case_date"] < now)].copy()
    daily = df_30.groupby(df_30["case_date"].dt.date).size().reset_index(name="cases")

    plt.figure(figsize=(10, 4))
    sns.lineplot(data=daily, x="case_date", y="cases", marker="o")
    plt.title("Casos diários de SRAG (últimos 30 dias)")
    plt.xlabel("Data")
    plt.ylabel("Casos")
    plt.xticks(rotation=45)
    plt.tight_layout()
    daily_path = out_dir / "casos_diarios_ultimos_30d.png"
    plt.savefig(daily_path, dpi=150)
    plt.close()

    start_12m = now - timedelta(days=365)
    df_12m = df[(df["case_date"] >= start_12m) & (df["case_date"] < now)].copy()
    df_12m["month"] = df_12m["case_date"].dt.to_period("M").dt.to_timestamp()
    monthly = df_12m.groupby("month").size().reset_index(name="cases")

    plt.figure(figsize=(10, 4))
    sns.barplot(data=monthly, x="month", y="cases", color="#4C78A8")
    plt.title("Casos mensais de SRAG (últimos 12 meses)")
    plt.xlabel("Mês")
    plt.ylabel("Casos")
    plt.xticks(rotation=45)
    plt.tight_layout()
    monthly_path = out_dir / "casos_mensais_ultimos_12m.png"
    plt.savefig(monthly_path, dpi=150)
    plt.close()

    return daily_path, monthly_path
