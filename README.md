# Relatórios automatizados de SRAG

Este repositório reúne um pequeno pipeline para cálculo de indicadores sobre Síndrome Respiratória Aguda Grave (SRAG), geração de gráficos e montagem de um relatório em Markdown. O foco é oferecer um fluxo simples e reproduzível para acompanhamento rápido.

O que o projeto faz:
- Calcula indicadores básicos (evolução semanal de casos, taxa de mortalidade em 30 dias, proporção de UTI e um proxy de vacinação) a partir de um CSV do OpenDataSUS.
- Gera dois gráficos: casos diários (últimos 30 dias) e casos mensais (últimos 12 meses).
- Monta um arquivo Markdown com os números e um texto-resumo.
- (Opcional) Exporta um PDF com um diagrama simples da arquitetura.

Referência de dados para citação no relatório:
- OpenDataSUS – SRAG 2021 a 2025: [`https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024`](https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024)

## Requisitos
- Python 3.10+
- (Opcional) um arquivo `.env` para configurar `NEWS_QUERY`/`SRAG_CSV_PATH`.

## Instalação
```bash
python -m venv .venv
. .venv/Scripts/activate  # PowerShell no Windows
pip install -r requirements.txt
```

Crie o arquivo `.env` a partir de `ENV_TEMPLATE` (opcional) e preencha, por exemplo:
```ini
NEWS_QUERY=SRAG,"Síndrome Respiratória Aguda Grave",Influenza,COVID-19,Brasil
SRAG_CSV_PATH=
```

## Como usar
1) Baixe o CSV de SRAG do OpenDataSUS e coloque em `data/raw` (ou informe com `--csv`).
2) Execute o pipeline:
```bash
python main.py --csv "data/raw/seu_arquivo.csv"
```
3) O relatório em Markdown é salvo em `reports/`. Os gráficos em PNG são gravados no mesmo diretório.
4) (Opcional) Gere o diagrama em PDF:
```bash
python scripts/generate_architecture_pdf.py
```

## Observações sobre os dados
- A base pode conter ausências e inconsistências. O fluxo seleciona colunas relevantes, normaliza datas e indicadores (UTI, óbito, vacinação) e calcula os números de forma tolerante a nulos.
- A “taxa de vacinação” é um proxy entre os casos com registro de vacinação conhecido. Não representa cobertura populacional.

## Arquitetura (resumo)
- Módulo de cálculo de métricas (a partir de CSV).
- Módulo de coleta de manchetes públicas (RSS) para contexto.
- Módulo que organiza o relatório em Markdown e salva os gráficos.
- (Opcional) Script que desenha um diagrama simples em PDF.

## Governança e auditoria

O projeto inclui mecanismos básicos de governança para facilitar auditoria e controle:

- Logs de auditoria: `relatorios/audit.log` (eventos como seleção de CSV, leitura e limpeza).
- Registro de decisões: `relatorios/decisions.jsonl` (decisões do orquestrador e violações de guardrails).
- Scrubbing/pseudonimização: controlado por `SENSITIVE_FIELDS` e `PSEUDONYMIZE_ENABLED` (variáveis de ambiente configuráveis via `.env`).
- Retenção básica de logs: `AUDIT_MAX_LINES` controla quantas linhas manter no `audit.log`.

Variáveis relevantes (exemplo `.env`):
```ini
PSEUDONYMIZE_ENABLED=0
PSEUDONYMIZE_SALT=seu_salt_aqui
AUDIT_MAX_LINES=5000
GOVERNANCE_ENABLED=1
SENSITIVE_FIELDS=nu_idade_n,cs_sexo
S3_ARCHIVE_BUCKET=
S3_ARCHIVE_PREFIX=audit/
PSEUDONYMIZE_MODE=hash  # ou token
```

## Integração contínua (CI)

Um workflow de CI (`.github/workflows/ci.yml`) roda testes e um linter básico (ruff) em pushes/PRs contra `main`.

Pré-commit e formatação

Para manter qualidade de código localmente, o repositório inclui uma configuração de `pre-commit` que roda `ruff` e `black`.

Instalação e uso:
```powershell
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

O workflow de CI agora faz o linter (`ruff`) falhar o build quando detectar problemas.

S3 archival

Se `S3_ARCHIVE_BUCKET` for configurado, o `audit.log` será arquivado localmente e enviado para o bucket S3 configurado quando exceder `AUDIT_MAX_BYTES`.

Token service

O repositório inclui um `token_service` local (`src/token_service.py`) que implementa mapeamento token<->valor para casos de uso de pseudonimização com reidentificação controlada. Por padrão, o `PSEUDONYMIZE_MODE` está em `hash`. Para utilizar tokens:

```powershell
PSEUDONYMIZE_MODE=token
```

Observação: o `token_service` usa um arquivo local (`data/tokens.json`) e não é seguro para produção; deve ser substituído por um secret manager/token service em ambientes reais.

## Licença de dados
Os dados são do Ministério da Saúde (OpenDataSUS), sob licença aberta conforme a página do conjunto. Veja: [`https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024`](https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024)
