from __future__ import annotations

from pathlib import Path

from typing import Dict, List

from datetime import datetime

from jinja2 import Environment, FileSystemLoader, select_autoescape


from src.configuracao import REPORTS_DIR, TEMPLATES_DIR


def _jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=(".html", ".xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    return env


def write_markdown_report(
    metrics: Dict, narrative: str, chart_paths: List[Path]
) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    context = {
        "generated_at": datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC"),
        "metrics": metrics,
        "narrative": narrative,
        "charts": [str(p.name) for p in chart_paths],
        "data_source": "OpenDataSUS – SRAG 2021 a 2025",
        "data_url": "https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024",
    }

    template_name = "modelo_relatorio.md.j2"

    output_name = f"relatorio_srag_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"

    out_path = REPORTS_DIR / output_name

    try:
        env = _jinja_env()

        template = env.get_template(template_name)

        content = template.render(**context)

    except Exception:
        content = _fallback_markdown(**context)

    out_path.write_text(content, encoding="utf-8")

    return out_path


def _fallback_markdown(
    generated_at: str,
    metrics: Dict,
    narrative: str,
    charts: List[str],
    data_source: str,
    data_url: str,
) -> str:
    lines = []

    lines.append("# Relatório rápido de SRAG\n")

    lines.append(f"Gerado em: {generated_at}\n")

    lines.append("\n## Indicadores\n")

    lines.append(f"- Casos (últimos 7 dias): {metrics.get('last7_cases', 0)}")

    lines.append(f"- Casos (7 dias anteriores): {metrics.get('prev7_cases', 0)}")

    lines.append(f"- Variação de casos: {metrics.get('case_increase_rate', 0.0):.2%}")

    lines.append(
        f"- Mortalidade (30 dias): {metrics.get('mortality_rate_30d', 0.0):.2%}"
    )

    lines.append(f"- UTI (30 dias): {metrics.get('icu_rate_30d', 0.0):.2%}")

    lines.append(
        f"- Vacinação (proxy nos casos): {metrics.get('vaccination_rate', 0.0):.2%}\n"
    )

    lines.append("## Resumo\n")

    lines.append(narrative + "\n")

    if charts:
        lines.append("## Gráficos\n")

        for c in charts:
            lines.append(f"![Gráfico]({c})\n")

    lines.append("## Fontes\n")

    lines.append(f"- {data_source} – [{data_url}]({data_url})\n")

    return "\n".join(lines)
