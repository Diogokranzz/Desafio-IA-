# Arquitetura (resumo)

Este documento resume a arquitetura do projeto e como os módulos principais se relacionam.

Componentes principais
- `src/dados` — funções de ingestão e limpeza (`ensure_srag_csv`, `load_and_clean_srag`).
- `src/agent` e `src/agente` — orquestradores que geram narrativas a partir das métricas.
- `src/governance.py` — mecanismo de auditoria, registro de decisões, guardrails e scrubbing/pseudonimização.
- `relatorios/` — saída de relatórios, gráficos e logs de auditoria (`audit.log`, `decisions.jsonl`).

Fluxo (resumido)
1. `ensure_srag_csv()` seleciona o CSV (argumento/ENV/dados/brutos) — evento `select_csv`.
2. `load_and_clean_srag()` lê o CSV, normaliza colunas e aplica scrubbing/pseudonimização — eventos `load_csv` e `clean_csv`.
3. Orquestrador gera narrativa e métricas; chama `guardrail_check()` e registra decisões com `record_decision()`.
4. Logs de auditoria e decisões são gravados em `relatorios/`.

Governança e segurança
- Pseudonimização controlável via `PSEUDONYMIZE_ENABLED` e `PSEUDONYMIZE_SALT` em variáveis de ambiente.
- Retenção básica de audit.log controlada por `AUDIT_MAX_LINES`.
