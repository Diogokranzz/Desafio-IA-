import argparse


from pathlib import Path


from src.dados.ingestao import ensure_srag_csv


from src.dados.limpeza import load_and_clean_srag


from src.relatorio.metricas import compute_core_metrics


from src.relatorio.graficos import generate_charts


from src.agente.orquestrador import generate_narrative


from src.relatorio.escritor import write_markdown_report


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
        help="Caminho opcional para o CSV de SRAG (se omitido, procura em dados/brutos)",
    )

    args = parser.parse_args()

    path = run_pipeline(args.csv)

    print(f"Relatório salvo em: {path}")
