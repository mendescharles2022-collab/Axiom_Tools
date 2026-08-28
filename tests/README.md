# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Estado atual

A árvore operacional completa V7/V8 ainda não foi reconciliada; portanto esta pasta ainda não representa a suíte do runtime instalado.

O repositório já possui, porém, uma suíte real para o tooling de auditoria, reconciliação, proveniência, preparação segura de migração, rollback verificável e inventário estático de segurança.

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

O inventário estático cobre:

- identificação de rotas Flask por decorators `route/get/post/put/patch/delete`;
- métodos mutantes;
- markers de autenticação configuráveis;
- detecção de `csrf.exempt` configurável;
- múltiplos decorators de rota na mesma função;
- política customizável sem assumir que o runtime usa um único decorator;
- erro de sintaxe reportado, nunca silenciado.

**Importante:** ausência de achado estático não significa autenticação/CSRF homologados. Proteções globais, wrappers dinâmicos, Flask-WTF e autorização de negócio ainda exigem teste do runtime.

## Contagem atual

- **92 testes definidos**;
- **89 testes aprovados em execuções controladas**;
- **3 testes end-to-end de reconciliação aguardando execução comprovada**.

## Execução

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Limite da suíte atual

Nenhum desses testes substitui a suíte operacional do runtime V7/V8.

Após a reconciliação, continuam obrigatórios testes de reprocessamento, Conference somente leitura, gate de saídas, universo/chamada, aplicabilidade, multi-Extrato/multi-GFD, identidade, eConsignado, retificação, invariantes V8 específicas, segurança dinâmica das rotas, banco ↔ filesystem, regressão dos 28 casos e rollback real no Windows.

## Princípio

Nenhum bloqueador V8 muda para `CORRIGIDO_HOMOLOGADO` apenas porque código ou tooling foram adicionados. A transição exige execução objetiva sobre a árvore/runtime/build correto.
