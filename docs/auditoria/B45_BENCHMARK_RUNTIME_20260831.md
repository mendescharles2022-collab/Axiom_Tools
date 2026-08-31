# B45 — Benchmark representativo da árvore reconciliada

Data: 31/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## Objetivo

Provar que as consultas críticas da V8 não dependem de varreduras globais desnecessárias nem degradam de forma relevante quando a carteira cresce além do volume atual.

## Ferramenta

Foi utilizado o runner somente leitura já versionado em:

`scripts/benchmark_sqlite_queries.py`

Spec canônico:

`config/benchmark_runtime_v8_20260831.json`

O runner registra `EXPLAIN QUERY PLAN`, p50/p95/p99, contagem de linhas e threshold por cenário.

## Baseline real — 08/2026

Banco operacional recuperado:

- 845 clientes totais;
- 677 clientes ativos;
- 677 registros de fechamento em 08/2026;
- 3.369 documentos de processamento.

Resultados p95:

| Cenário | Linhas | p95 |
|---|---:|---:|
| Fechamento da competência | 677 | 0,875 ms |
| Conference / chamada atual | 30 | 0,054 ms |
| Pendências da competência | 2 | 1,844 ms |
| Monitor / últimos vigentes | 100 | 1,542 ms |
| Universo eConsignado | 30 | 0,029 ms |
| Gate de saídas FECHADA | 598 | 0,700 ms |

## Ensaio de crescimento

Foi criada cópia SQLite isolada e consistente. Nenhum dado operacional original foi alterado.

A cópia foi ampliada com registros sintéticos válidos pelo schema até:

- 1.200 clientes;
- 1.032 participações de fechamento em 08/2026;
- 6.000 documentos de processamento;
- 889 versões de fechamento;
- `PRAGMA integrity_check = ok`;
- `PRAGMA foreign_key_check = 0`.

Resultados p95:

| Cenário | Linhas | p95 |
|---|---:|---:|
| Fechamento da competência | 1.032 | 1,193 ms |
| Conference / chamada atual | 101 | 0,146 ms |
| Pendências da competência | 2 | 2,710 ms |
| Monitor / últimos vigentes | 100 | 2,447 ms |
| Universo eConsignado | 101 | 0,093 ms |
| Gate de saídas FECHADA | 882 | 1,038 ms |

Todos os cenários permaneceram muito abaixo do threshold canônico de 20 ms p95 no benchmark SQLite local.

## Query plans

Os cenários críticos utilizam índices existentes, entre eles:

- `sqlite_autoindex_fechamento_mensal_cliente_1` por competência;
- `idx_fechamento_cliente_comp` por competência/status/chamada;
- `idx_proc_repo_comp` / `idx_proc_vigente` no processamento;
- índice único de versões do fechamento;
- `ux_fech_retif_detectada` para retificação aberta;
- PK de Clientes nos joins.

Há uso de B-tree temporária para `ORDER BY`, mas sem evidência de explosão N+1 ou full scan dominante nas consultas auditadas.

## Limite da prova

Este benchmark cobre banco/query plan. Ele não substitui:

- tempo HTTP/Jinja no navegador;
- concorrência real de workers;
- latência de integrações externas;
- teste do servidor Windows;
- percepção visual/interativa.

Esses pontos pertencem à homologação final do build reconciliado.

## Estado

B45 pode ser classificado como `CORRIGIDO_TESTADO` na fase de auditoria/reconciliação.
