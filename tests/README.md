# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Estado atual

A árvore operacional completa V7/V8 ainda não foi reconciliada; portanto esta pasta ainda não representa a suíte do runtime instalado.

O repositório já possui, porém, uma suíte real para o tooling de auditoria, reconciliação, proveniência, preparação segura de migração, rollback verificável, segurança estática, consistência banco ↔ filesystem, retenção dry-run, benchmark SQLite, regressão de agosto e governança dos bloqueadores.

## Suítes aprovadas

### Reconciliação runtime ↔ repositório

- `test_audit_runtime_reconciliation.py` — **9 aprovados**;
- `test_export_runtime_reconciliation.py` — **9 aprovados**;
- `test_reconciliation_pipeline_e2e.py` — **3 versionados, execução ainda não comprovada**.

### Proveniência de build

- `test_generate_build_provenance.py` — **12 aprovados**;
- `test_verify_build_provenance.py` — **9 aprovados**.

### SQLite / migração controlada

- `test_audit_sqlite_baseline.py` — **7 aprovados**;
- `test_compare_sqlite_audits.py` — **7 aprovados**;
- `test_clone_sqlite_for_migration.py` — **6 aprovados**;
- `test_run_sqlite_invariants.py` — **8 aprovados**.

### Backup / rollback verificável

- `test_rollback_bundle.py` — **8 aprovados**;
- `test_restore_rollback_bundle.py` — **6 aprovados**.

### Segurança estática das rotas

- `test_audit_route_security.py` — **8 aprovados**.

### Banco ↔ filesystem

- `test_audit_db_filesystem_links.py` — **8 aprovados**.

### Retenção / limpeza dry-run

- `test_plan_retention_cleanup.py` — **7 aprovados**.

### Benchmark SQLite

- `test_benchmark_sqlite_queries.py` — **7 aprovados**.

### Regressão dos 28 casos reais

- `test_validate_regression_results.py` — **8 aprovados**.

A regressão machine-readable usa `config/regression_cases_v8_202608.json` e exige 28 casos completos. `PASS` sem evidência é inválido e o modo final só aceita 28 `PASS` com evidência.

### Governança dos B01–B50

- `test_validate_blocker_statuses.py` — **8 aprovados**;
- `test_current_blocker_status.py` — **2 aprovados**.

A governança machine-readable usa:

- `config/blocker_registry_v8.json` — identidade imutável B01–B50, tema e cobertura;
- `config/blocker_status_v8_current.json` — snapshot vivo do estado atual;
- `scripts/validate_blocker_statuses.py` — valida todos os estados e evidências.

Regras principais:

- registry deve conter exatamente B01–B50 em ordem e sem duplicidade;
- arquivo de status precisa estar amarrado ao SHA-256 do registry;
- `CORRIGIDO_TESTADO` exige evidência de código e teste;
- `CORRIGIDO_HOMOLOGADO` exige, além disso, evidência de runtime e homologação;
- modo final só aprova com 50/50 `CORRIGIDO_HOMOLOGADO`;
- snapshot atual possui 0 bloqueadores homologados, evitando falsa conclusão da V8.

## Contagem atual

- **132 testes definidos**;
- **129 testes aprovados em execuções controladas**;
- **3 testes end-to-end de reconciliação aguardando execução comprovada**.

## Execução

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Limite da suíte atual

Nenhum desses testes substitui a suíte operacional do runtime V7/V8.

Após a reconciliação, continuam obrigatórios testes reais de reprocessamento, Conference somente leitura, gate de saídas, universo/chamada, aplicabilidade, multi-Extrato/multi-GFD, identidade, eConsignado, retificação, invariantes V8 específicas, segurança dinâmica das rotas, consistência banco ↔ filesystem sobre o acervo real, política real de retenção, benchmark com queries/runtime reais, execução dos 28 casos e rollback real no Windows.

## Princípio

Nenhum bloqueador V8 muda para `CORRIGIDO_HOMOLOGADO` apenas porque código ou tooling foram adicionados. A transição exige execução objetiva sobre a árvore/runtime/build correto.
