# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Estado atual

A árvore operacional completa V7/V8 ainda não foi reconciliada; portanto esta pasta **não substitui a suíte operacional do runtime instalado**.

O tooling de auditoria/homologação possui suíte automatizada real e execução oficial no GitHub Actions.

## Execução oficial mais recente

Workflow: `V8 Audit Tooling Tests`  
Run: `33194834851`  
Commit testado: `568f878bf8b99dc8b63466a8ab556233d7fd83b0`  
Python: `3.12.14`

Resultado oficial:

```text
Ran 142 tests in 1.390s
OK
```

**142 testes definidos / 142 testes aprovados.**

## Suítes cobertas

### Reconciliação runtime ↔ repositório

- `test_audit_runtime_reconciliation.py` — 9;
- `test_export_runtime_reconciliation.py` — 9;
- `test_reconciliation_pipeline_e2e.py` — 3.

### Proveniência de build

- `test_generate_build_provenance.py` — 12;
- `test_verify_build_provenance.py` — 9.

### SQLite / migração controlada

- `test_audit_sqlite_baseline.py` — 7;
- `test_compare_sqlite_audits.py` — 7;
- `test_clone_sqlite_for_migration.py` — 6;
- `test_run_sqlite_invariants.py` — 8.

### Backup / rollback verificável

- `test_rollback_bundle.py` — 8;
- `test_restore_rollback_bundle.py` — 6.

### Segurança estática das rotas

- `test_audit_route_security.py` — 8.

### Banco ↔ filesystem

- `test_audit_db_filesystem_links.py` — 8.

### Retenção / limpeza dry-run

- `test_plan_retention_cleanup.py` — 7.

### Benchmark SQLite

- `test_benchmark_sqlite_queries.py` — 7.

### Regressão dos 28 casos reais

- `test_validate_regression_results.py` — 8.

### Governança dos B01–B50

- `test_validate_blocker_statuses.py` — 8;
- `test_current_blocker_status.py` — 2.

### Gate único de homologação

- `test_validate_release_gate.py` — **10 aprovados**.

O gate final combina:

- 50/50 bloqueadores homologados com evidência;
- 28/28 casos `PASS` com evidência;
- release canônica em `READY`;
- build/proveniência verificados;
- manifesto de evidências externas obrigatório;
- CI, baseline runtime, banco, invariantes, benchmark, segurança, A4, instalação Windows e rollback Windows.

## Controles canônicos

Regressão de agosto:

- `config/regression_cases_v8_202608.json`;
- `scripts/validate_regression_results.py`.

Governança dos bloqueadores:

- `config/blocker_registry_v8.json`;
- `config/blocker_status_v8_current.json`;
- `scripts/validate_blocker_statuses.py`.

Gate final:

- `scripts/validate_release_gate.py`;
- `config/release_gate_evidence.example.json`.

## Limite da suíte atual

Os 142 testes aprovam o **tooling de auditoria/homologação**. Eles não significam que a V8 operacional esteja homologada.

Após a reconciliação do runtime continuam obrigatórios testes reais de reprocessamento, Conference somente leitura, gate de saídas, universo/chamada, aplicabilidade, multi-Extrato/multi-GFD, identidade, eConsignado, retificação, invariantes específicas do schema real, segurança dinâmica, banco ↔ filesystem sobre o acervo real, política real de retenção, benchmark runtime/HTTP/workers, execução dos 28 casos e rollback físico no Windows.

## Princípio

Nenhum bloqueador V8 muda para `CORRIGIDO_HOMOLOGADO` apenas porque código ou tooling foram adicionados. A transição exige prova objetiva sobre a árvore/runtime/build correto.
