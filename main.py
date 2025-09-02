import argparse


from pathlib import Path


from src.data.ingest import ensure_srag_csv


from src.data.clean import load_and_clean_srag


from src.report.metrics import compute_core_metrics


from src.report.charts import generate_charts


from src.agent.orchestrator import generate_narrative


from src.report.writer import write_markdown_report


def run_pipeline(csv_path: str | None = None) -> Path:
    raw_csv = ensure_srag_csv(csv_path)

    df = load_and_clean_srag(raw_csv)

    metrics = compute_core_metrics(df)

    daily_png, monthly_png = generate_charts(df)

    narrative = generate_narrative(metrics)

    report_path = write_markdown_report(metrics, narrative, [daily_png, monthly_png])

    return report_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerador de relatório de SRAG")

    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Caminho opcional para o CSV de SRAG (se omitido, procura em data/raw)",
    )

    args = parser.parse_args()

    path = run_pipeline(args.csv)

    print(f"Relatório salvo em: {path}")
