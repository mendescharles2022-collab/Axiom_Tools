# Rastreador canônico — Execução de correção V8

Data: 28/08/2026  
Status: **RUNTIME AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

Este é o rastreador vivo da fase de correção/homologação. Os documentos `AUDITORIA_CANONICA_V8_20260828_ETAPA*.md` permanecem como histórico da investigação.

## 1. Fonte de verdade operacional da auditoria

Arquivos canônicos:

- `config/blocker_registry_v8.json` — identidade B01–B50;
- `config/blocker_status_v8_current.json` — estado vivo dos bloqueadores;
- `config/regression_cases_v8_202608.json` — C01–C28;
- `docs/STATUS_ATUAL.md` — estado geral;
- este arquivo — sequência operacional da correção.

A documentação humana nunca pode contradizer os registries machine-readable.

## 2. CI do tooling — APROVADA

Workflow oficial: `V8 Audit Tooling Tests`  
Run: `33193366593`  
Commit: `651771a899a3b35de3260c802e81e67f5ae8f3b3`  
Python: `3.12.14`

Resultado:

```text
Ran 132 tests in 0.951s
OK
```

**132/132 testes do tooling aprovados**, incluindo os 3 E2E de reconciliação.

Essa aprovação não homologa a V8 operacional.

## 3. Snapshot B01–B50

Distribuição atual:

| Estado | Quantidade |
|---|---:|
| `PRONTO_PARA_CORRIGIR` | 35 |
| `INSPECAO_PENDENTE` | 8 |
| `EM_CORRECAO` | 3 |
| `BLOQUEADO_POR_RUNTIME` | 4 |
| `CORRIGIDO_TESTADO` | 0 |
| `CORRIGIDO_HOMOLOGADO` | 0 |

### Em correção

- B35 — FK/invariantes;
- B41 — backup/rollback;
- B42 — proveniência de build.

### Bloqueados pelo runtime

- B05 — migração V8;
- B06 — `main` ≠ runtime;
- B45 — benchmark representativo do runtime;
- B49 — banco ↔ filesystem sobre schema/acervo reais.

## 4. Gate Zero — B06

B06 permanece o principal bloqueador da fase de correção operacional.

O `main` ainda não contém integralmente a árvore V8 auditada. Não será feita correção de runtime sobre a fundação reduzida fingindo que ela é o produto instalado.

Ferramentas já prontas/testadas:

- `scripts/export_runtime_reconciliation.py`;
- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/audit_runtime_reconciliation.py`;
- 3 testes E2E de exportação/auditoria/diferença/adulteração — **aprovados no CI**.

Pendente:

- executar o launcher/exportação no Windows real;
- auditar o pacote exportado;
- reconciliar a árvore controlada com o `main`;
- trazer a suíte operacional original.

## 5. B42 — proveniência de build

Estado: `EM_CORRECAO`.

Implementado/testado:

- `config/release_identity.toml` — atualmente `UNRELEASED`;
- `scripts/generate_build_provenance.py`;
- `scripts/verify_build_provenance.py`;
- Git limpo obrigatório;
- manifesto SHA-256;
- bloqueio de conteúdo sensível;
- verificação de commit/ref/identidade.

Pendente:

- runtime consumir a identidade;
- `/health` expor versão/build/schema;
- logs de inicialização usarem a mesma identidade;
- instalador/backup/rollback consumirem o mesmo manifesto;
- pacote final nascer da mesma árvore testada.

## 6. B35/B05 — SQLite e migração

Tooling aprovado:

- `scripts/audit_sqlite_baseline.py`;
- `scripts/compare_sqlite_audits.py`;
- `scripts/clone_sqlite_for_migration.py`;
- `scripts/run_sqlite_invariants.py`.

Fluxo quando a base real controlada estiver disponível:

1. baseline somente leitura;
2. cópia consistente via `sqlite3.Connection.backup()`;
3. migração somente na cópia;
4. baseline pós-migração;
5. comparação pré/pós;
6. invariantes lógicas versionadas;
7. regressão funcional.

B35 está `EM_CORRECAO`; B05 continua `BLOQUEADO_POR_RUNTIME`.

## 7. B41 — backup/rollback

Estado: `EM_CORRECAO`.

Implementado/testado:

- `scripts/create_rollback_bundle.py`;
- `scripts/verify_rollback_bundle.py`;
- `scripts/restore_rollback_bundle.py`;
- bundle com manifesto/hash;
- SQLite consistente;
- ensaio de restauração somente em staging novo;
- validação pós-restauração.

Pendente:

- plano real de arquivos da instalação;
- bundle da instalação real;
- ensaio com cópia real;
- rollback físico Windows;
- smoke pós-rollback.

## 8. B38 — segurança

Estado: `INSPECAO_PENDENTE`.

Preparado:

- `scripts/audit_route_security.py`;
- `config/route_security_policy.example.json`.

O inventário estático é apenas evidência auxiliar. Segurança dinâmica, CSRF global, autorização de negócio, escopo e transações dependem do runtime reconciliado.

## 9. B45/B48/B49 — escala e acervo

Preparado:

- B45 — `scripts/benchmark_sqlite_queries.py`;
- B48 — `scripts/plan_retention_cleanup.py`, somente dry-run;
- B49 — `scripts/audit_db_filesystem_links.py`.

B45 e B49 continuam bloqueados pelo runtime. B48 segue em inspeção pendente até conhecer política/acervo reais.

## 10. Regressão C01–C28

Registro:

- `config/regression_cases_v8_202608.json`;
- `scripts/validate_regression_results.py`.

Modo final exige:

- 28/28 casos presentes;
- 28 `PASS`;
- evidência para cada `PASS`;
- registry hash correspondente.

O controle adicional P DA SILVA CARMO permanece fixture complementar e não substitui C01–C28.

## 11. Ordem oficial da correção operacional

Assim que B06 for removido:

1. rodar baseline/suíte operacional original;
2. B01 — reprocessamento candidato/versionado;
3. B02 — Conference GET somente leitura;
4. B03/B39 — gate único de saídas e IDs manuais;
5. B07/B08 — universo/chamadas;
6. B09/B10/B11/B37/B40 — estados, retificação e concorrência;
7. B12–B23/B29–B33 — documentos, identidade, composição e aplicabilidade;
8. B24–B28 — eConsignado;
9. B34/B36/B38 — cadastro, legado e segurança;
10. B43/B44/B46/B47/B50 — UX/saídas/deduplicação restantes;
11. migração + invariantes reais;
12. regressão C01–C28;
13. benchmark runtime;
14. build/pacote;
15. instalação Windows + rollback.

## 12. Gate final

Nenhum pacote final V8 antes de:

- [ ] runtime reconciliado;
- [ ] suíte operacional original aprovada;
- [ ] 50/50 bloqueadores `CORRIGIDO_HOMOLOGADO`;
- [ ] 28/28 casos `PASS` com evidência;
- [ ] `integrity_check` aprovado;
- [ ] `foreign_key_check` aprovado;
- [ ] invariantes lógicas aprovadas;
- [ ] benchmark aprovado;
- [ ] segurança aprovada;
- [ ] A4 homologado;
- [ ] build proveniente da mesma árvore testada;
- [ ] migração em cópia aprovada;
- [ ] instalação Windows aprovada;
- [ ] rollback código + banco + configuração comprovado.

## 13. Próximo avanço real

Sem o runtime, não criar implementação fictícia para B01/B02/B03.

O próximo trabalho útil no repositório é fortalecer o **gate de release/homologação**, fazendo uma ferramenta única verificar automaticamente:

- status dos 50 bloqueadores;
- resultado dos 28 casos;
- identidade `READY`;
- proveniência do build;
- evidência de CI;
- relatórios de banco/benchmark/segurança/rollback.

Até esse gate passar, a V8 permanece **NÃO HOMOLOGADA**.
