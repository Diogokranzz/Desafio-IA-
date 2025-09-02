from __future__ import annotations

from typing import Dict, List

from src.agente.ferramentas import news_search

from src.governance import audit, record_decision, guardrail_check, scrub_record


def _classify_trend(rate: float) -> str:
    if rate > 0.15:
        return "alta"

    if rate < -0.10:
        return "queda"

    return "estável"


def _format_metrics(metrics: Dict) -> str:
    return (
        f"Data de referência: {metrics.get('as_of', '')}\n"
        f"Casos (últimos 7 dias): {metrics.get('last7_cases', 0)}\n"
        f"Casos (7 dias anteriores): {metrics.get('prev7_cases', 0)}\n"
        f"Variação de casos: {metrics.get('case_increase_rate', 0.0):.2%}\n"
        f"Mortalidade (30 dias): {metrics.get('mortality_rate_30d', 0.0):.2%}\n"
        f"UTI (30 dias): {metrics.get('icu_rate_30d', 0.0):.2%}\n"
        f"Vacinação (proxy nos casos): {metrics.get('vaccination_rate', 0.0):.2%}"
    )


def generate_narrative(metrics: Dict) -> str:
    audit("receive_metrics", {"metrics_keys": list(metrics.keys())})

    metrics = scrub_record(metrics)

    case_rate = float(metrics.get("case_increase_rate", 0.0))

    mort = float(metrics.get("mortality_rate_30d", 0.0))

    icu = float(metrics.get("icu_rate_30d", 0.0))

    trend = _classify_trend(case_rate)

    risco = []

    if mort >= 0.05:
        risco.append("mortalidade elevada")

    if icu >= 0.10:
        risco.append("pressão de UTI")

    news = news_search(max_results=2)

    manchetes = (
        "; ".join([n["title"] for n in news])
        if news
        else "sem manchetes recentes relevantes"
    )

    partes: List[str] = []

    partes.append(
        f"Visão geral: o volume de casos está {trend} na comparação semanal. "
        f"Na janela de 30 dias, mortalidade em {mort:.1%} e UTI em {icu:.1%}."
    )

    if risco:
        partes.append("Pontos de atenção: " + ", ".join(risco) + ".")

    partes.append(
        f"Contexto: manchetes recentes sugerem temas a acompanhar ({manchetes})."
    )

    partes.append(
        "Nota: a taxa de vacinação é um proxy dentro dos casos SRAG, não reflete cobertura populacional."
    )

    narrative = " \n".join(partes).strip()

    violations = list(guardrail_check(metrics))

    if violations:
        audit("guardrail_violations", {"violations": violations})

    record_decision(
        {
            "action": "generate_narrative",
            "trend": _classify_trend(case_rate),
            "violations": violations,
        }
    )

    return narrative
