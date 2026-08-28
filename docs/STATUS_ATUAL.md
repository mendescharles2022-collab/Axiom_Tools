# Axiom Tools — Status Atual

Data: 28/08/2026  
Status: **V5.6.14V7 estável em servidor / V8 em auditoria e correção / V8 NÃO HOMOLOGADA**

## 1. Referência estável

A referência operacional estável continua sendo **V5.6.14V7 — Ciclo Mensal com Fechamento Automático**, instalada em 26/08/2026 preservando banco, serviços, histórico e retificações.

Builds posteriores da família V8 não substituem essa referência sem homologação formal.

## 2. Situação atual da V8

A auditoria de 28/08/2026 consolidou:

- 50 bloqueadores canônicos (`B01`–`B50`);
- 28 casos reais da competência 08/2026 em matriz e registro machine-readable;
- snapshot machine-readable do estado dos 50 bloqueadores;
- tooling de reconciliação, proveniência, migração, rollback, segurança, desempenho e regressão;
- gate único de homologação/liberação;
- nenhum bloqueador marcado como `CORRIGIDO_HOMOLOGADO` sem prova.

## 3. CI do tooling — APROVADA

Workflow: `V8 Audit Tooling Tests`  
Run: `33194834851`  
Commit: `568f878bf8b99dc8b63466a8ab556233d7fd83b0`  
Python: `3.12.14`

Resultado:

```text
Ran 142 tests in 1.390s
OK
```

Portanto o tooling atual possui **142 testes definidos e 142 aprovados**.

Essa aprovação é do tooling de auditoria/homologação, não da V8 operacional.

## 4. Gate Zero — B06

B06 permanece **BLOQUEADO_POR_RUNTIME**.

O `main` ainda não espelha integralmente a implementação operacional auditada no servidor/ZIP canônico. A reconciliação deve trazer somente código, templates, assets, testes, scripts e metadata controlada.

Permanecem fora do GitHub banco operacional, documentos de clientes, certificados, credenciais, logs, caches, backups com dados reais e temporários.

Ferramentas já preparadas/testadas:

- `scripts/export_runtime_reconciliation.py`;
- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/audit_runtime_reconciliation.py`;
- pipeline E2E de exportação/auditoria/diferença/adulteração.

## 5. Estado B01–B50

Snapshot atual (`config/blocker_status_v8_current.json`):

- 35 `PRONTO_PARA_CORRIGIR`;
- 8 `INSPECAO_PENDENTE`;
- 3 `EM_CORRECAO`;
- 4 `BLOQUEADO_POR_RUNTIME`;
- 0 `CORRIGIDO_HOMOLOGADO`.

Em correção:

- B35 — FK/invariantes;
- B41 — backup/rollback;
- B42 — proveniência de build.

Bloqueados pelo runtime:

- B05 — migração V8;
- B06 — reconciliação fonte/runtime;
- B45 — benchmark representativo do runtime;
- B49 — consistência banco ↔ filesystem sobre schema/acervo reais.

## 6. Regressão canônica — 08/2026

Arquivos:

- `config/regression_cases_v8_202608.json`;
- `scripts/validate_regression_results.py`.

Modo final só aprova com **28/28 casos `PASS` com evidência**.

## 7. Governança dos bloqueadores

Arquivos:

- `config/blocker_registry_v8.json`;
- `config/blocker_status_v8_current.json`;
- `scripts/validate_blocker_statuses.py`.

`CORRIGIDO_TESTADO` exige prova de código + teste. `CORRIGIDO_HOMOLOGADO` exige também prova de runtime + homologação.

## 8. Gate único de homologação

Novo tooling:

- `scripts/validate_release_gate.py`;
- `config/release_gate_evidence.example.json`;
- `tests/test_validate_release_gate.py`.

O gate final exige simultaneamente:

1. 50/50 bloqueadores `CORRIGIDO_HOMOLOGADO`;
2. 28/28 casos `PASS` com evidência;
3. release canônica em `READY`;
4. build/proveniência verificados;
5. evidências `PASS` para CI, baseline runtime, integridade/FK/invariantes do banco, benchmark runtime, segurança runtime, relatório A4, instalação Windows e rollback Windows.

No estado atual o gate final **deve falhar** e permanecer bloqueado.

## 9. Proveniência de build — B42

Implementado/testado:

- `config/release_identity.toml` — atualmente `UNRELEASED`;
- `scripts/generate_build_provenance.py`;
- `scripts/verify_build_provenance.py`;
- Git limpo obrigatório;
- manifesto SHA-256;
- bloqueio de conteúdo sensível.

Ainda falta integração com runtime, `/health`, logs, instalador e pacote final.

## 10. SQLite / migração — B05/B35

Tooling versionado:

- `scripts/audit_sqlite_baseline.py`;
- `scripts/compare_sqlite_audits.py`;
- `scripts/clone_sqlite_for_migration.py`;
- `scripts/run_sqlite_invariants.py`.

Fluxo aprovado: baseline → cópia consistente → migração só na cópia → pós-auditoria → comparação → invariantes → regressão funcional.

## 11. Backup/rollback — B41

Versionado:

- `scripts/create_rollback_bundle.py`;
- `scripts/verify_rollback_bundle.py`;
- `scripts/restore_rollback_bundle.py`.

Rollback em staging está testado. Rollback físico na instalação Windows continua pendente.

## 12. Segurança / acervo / desempenho

Preparados:

- B38: `scripts/audit_route_security.py`;
- B49: `scripts/audit_db_filesystem_links.py`;
- B48: `scripts/plan_retention_cleanup.py` em modo dry-run;
- B45: `scripts/benchmark_sqlite_queries.py`.

Esses itens ainda dependem do runtime/schema/acervo reais para homologação.

## 13. Arquitetura funcional preservada

1. **Fechamento Mensal** abre competência e acompanha o ciclo.
2. **Processamento de Arquivos** produz evidências técnicas dentro da competência/chamada aberta.
3. **Central de Conferência** resolve divergências, justificativas, sem movimento, anexos e reprocessamento.
4. **Fechado** é consequência das obrigações aplicáveis e da versão vigente; não é sinônimo de `PROCESSADO`.

A Conferência deve ser somente leitura ao abrir/recarregar.

## 14. Ordem da correção após reconciliação

1. baseline e suíte operacional original;
2. B01 — reprocessamento candidato/versionado;
3. B02 — Conference GET somente leitura;
4. B03/B39 — gate único de saída;
5. B07/B08 — universo/chamadas;
6. estados/retificação/concorrência;
7. documentos/identidade/composição/aplicabilidade;
8. eConsignado;
9. cadastro/legado/segurança;
10. UX/restantes;
11. migração + invariantes reais;
12. regressão C01–C28;
13. benchmark runtime;
14. build/pacote;
15. instalação Windows + rollback.

## 15. Estado de entrega

Neste momento:

- V8 **não homologada**;
- pacote final **não autorizado**;
- migração real **não autorizada**;
- rollback físico final **não comprovado**;
- runtime **ainda não reconciliado integralmente com o GitHub**.

O `main`, o rastreador canônico e os registries machine-readable são a referência atual da auditoria.
