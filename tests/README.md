# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Estado atual

A árvore operacional completa V7/V8 ainda não foi reconciliada; portanto esta pasta ainda não representa a suíte do runtime instalado.

O repositório já possui, porém, uma suíte real para o tooling de auditoria, reconciliação, proveniência e preparação segura de migração.

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

Essas quatro suítes cobrem:

- `integrity_check`;
- `foreign_key_check`;
- inventário/hash do schema;
- contagens de registros;
- ausência de mutação da origem;
- cópia consistente via `sqlite3.Connection.backup()`;
- proteção contra sobrescrita do destino;
- limpeza de `.partial` em falha;
- comparação pré/pós-migração;
- nova violação de FK como regressão;
- falha nova de integridade como regressão;
- remoção de objeto e queda de registros como avisos que exigem justificativa, não como conclusão automática;
- execução de invariantes lógicas por especificação versionada;
- regra `zero linhas = invariante atendida`;
- severidade `error` e `warning` separadas;
- bloqueio de SQL mutante inclusive quando disfarçado em CTE;
- bloqueio de `PRAGMA` dentro das invariantes;
- execução em conexão SQLite somente leitura.

## Contagem atual

- **70 testes definidos**;
- **67 testes aprovados em execuções controladas**;
- **3 testes end-to-end de reconciliação aguardando execução comprovada**.

## Execução

Suíte completa do tooling V8:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Limite da suíte atual

Nenhum desses testes substitui a suíte operacional do runtime V7/V8.

Após a reconciliação, continuam obrigatórios testes de:

- reprocessamento candidato/versionado;
- Conference GET somente leitura;
- gate único de Impressão/Entregas;
- universo por competência/chamada;
- 2ª chamada e concorrência lógica;
- aplicabilidade DARF/FGTS/DAE;
- multi-Extrato e multi-GFD;
- identidade CPF/CNPJ/CAEPF/matrícula;
- eConsignado contextual/idempotente;
- retificação/versionamento;
- invariantes lógicas V8 específicas do schema operacional;
- autenticação/CSRF/autorização;
- banco ↔ filesystem;
- regressão dos 28 casos reais de 08/2026.

## Princípio

Nenhum bloqueador V8 muda para `CORRIGIDO_HOMOLOGADO` apenas porque código ou tooling foram adicionados. A transição exige execução objetiva sobre a árvore/runtime/build correto.
