# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Estado atual

A árvore operacional completa V7/V8 ainda não foi reconciliada; portanto esta pasta ainda não representa a suíte do runtime instalado.

O repositório já possui, porém, uma suíte real para o tooling de auditoria, reconciliação, proveniência, preparação segura de migração e rollback verificável.

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

Essas quatro suítes cobrem `integrity_check`, `foreign_key_check`, inventário/hash de schema, contagens, cópia consistente, comparação pré/pós-migração, ausência de mutação da origem e invariantes lógicas somente leitura.

### Backup / rollback verificável

- `test_rollback_bundle.py` — **8 aprovados**;
- `test_restore_rollback_bundle.py` — **6 aprovados**.

Cobertura atual:

- bundle criado apenas a partir de lista explícita de arquivos controlados;
- preservação integral das origens;
- cópia SQLite consistente via `sqlite3.Connection.backup()`;
- manifesto com tamanho e SHA-256;
- bloqueio de path traversal e destino existente;
- limpeza de `.partial` em falha;
- detecção de arquivo/manifesto adulterado e arquivo extra;
- verificação independente antes de restaurar;
- restauração somente em diretório novo de ensaio;
- nova validação de hashes, `integrity_check` e `foreign_key_check` depois da restauração;
- geração de `RESTORE_REHEARSAL.json` para prova do ensaio.

## Contagem atual

- **84 testes definidos**;
- **81 testes aprovados em execuções controladas**;
- **3 testes end-to-end de reconciliação aguardando execução comprovada**.

## Execução

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Limite da suíte atual

Nenhum desses testes substitui a suíte operacional do runtime V7/V8.

Após a reconciliação, continuam obrigatórios testes de reprocessamento, Conference somente leitura, gate de saídas, universo/chamada, aplicabilidade, multi-Extrato/multi-GFD, identidade, eConsignado, retificação, invariantes V8 específicas, segurança, banco ↔ filesystem, regressão dos 28 casos e rollback real no Windows.

## Princípio

Nenhum bloqueador V8 muda para `CORRIGIDO_HOMOLOGADO` apenas porque código ou tooling foram adicionados. A transição exige execução objetiva sobre a árvore/runtime/build correto.
