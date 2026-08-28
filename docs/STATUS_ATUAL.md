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
- contratos e protocolos para reconciliação, proveniência, migração, rollback, segurança, desempenho e regressão;
- snapshot machine-readable do estado dos 50 bloqueadores;
- nenhum bloqueador marcado como `CORRIGIDO_HOMOLOGADO` sem prova.

Estado vivo:

- `docs/auditoria/RASTREADOR_EXECUCAO_CORRECAO_V8.md`;
- `config/blocker_registry_v8.json`;
- `config/blocker_status_v8_current.json`.

## 3. CI do tooling — comprovada

O GitHub Actions executou oficialmente o workflow `V8 Audit Tooling Tests` no commit:

`651771a899a3b35de3260c802e81e67f5ae8f3b3`

Ambiente: Python 3.12.14.

Resultado:

```text
Ran 132 tests in 0.951s
OK
```

Portanto o tooling atual possui **132 testes definidos e 132 aprovados**. Os 3 testes E2E de reconciliação estão incluídos nessa aprovação.

Essa aprovação é do tooling de auditoria/homologação, não da V8 operacional.

## 4. Gate Zero — repositório ≠ runtime

B06 permanece **BLOQUEADO_POR_RUNTIME**.

O `main` ainda não espelha integralmente a implementação operacional auditada no servidor/ZIP canônico. A reconciliação deve trazer somente código, templates, assets, testes, scripts e metadata controlada.

Permanecem fora do GitHub:

- banco operacional;
- PDFs/documentos de clientes;
- certificados;
- credenciais/tokens;
- logs;
- caches;
- backups com dados reais;
- temporários.

Tooling já preparado e testado:

- `scripts/export_runtime_reconciliation.py`;
- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/audit_runtime_reconciliation.py`;
- pipeline E2E de exportação/auditoria/diferença/adulteração.

## 5. Estado machine-readable dos bloqueadores

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

## 6. Proveniência de build — B42

Tooling implementado/testado:

- `config/release_identity.toml` — atualmente `UNRELEASED`;
- `scripts/generate_build_provenance.py`;
- `scripts/verify_build_provenance.py`;
- manifesto de payload e SHA-256;
- exigência de Git limpo;
- bloqueio de payload sensível e segredo hardcoded.

Ainda falta integrar essa identidade ao runtime reconciliado, `/health`, logs, instalador e pacote final.

## 7. SQLite / migração — B05/B35

Tooling versionado:

- `scripts/audit_sqlite_baseline.py`;
- `scripts/compare_sqlite_audits.py`;
- `scripts/clone_sqlite_for_migration.py`;
- `scripts/run_sqlite_invariants.py`.

Fluxo aprovado:

1. auditar origem sem escrever;
2. criar cópia consistente via `sqlite3.Connection.backup()`;
3. migrar somente a cópia;
4. auditar pós-migração;
5. comparar pré/pós;
6. executar invariantes lógicas versionadas.

Nenhuma invariante específica foi inventada sem o schema operacional real.

## 8. Backup/rollback — B41

Tooling versionado:

- `scripts/create_rollback_bundle.py`;
- `scripts/verify_rollback_bundle.py`;
- `scripts/restore_rollback_bundle.py`;
- `docs/auditoria/GUIA_BACKUP_ROLLBACK_V8.md`.

O rollback já foi ensaiado em staging controlado, com hashes, SQLite consistente e validação posterior. O rollback físico na instalação Windows continua pendente e proibido até a reconciliação do runtime e o plano real de atualização.

## 9. Segurança — B38

Tooling estático preparado:

- `scripts/audit_route_security.py`;
- `config/route_security_policy.example.json`;
- `docs/auditoria/GUIA_AUDITORIA_SEGURANCA_ROTAS_V8.md`.

Ausência de achado estático não equivale a segurança homologada. Autenticação/CSRF globais, autorização de negócio, escopo e transações ainda dependem do runtime.

## 10. Banco ↔ filesystem / retenção / escala

Preparados:

- B49: `scripts/audit_db_filesystem_links.py`;
- B48: `scripts/plan_retention_cleanup.py` em modo estritamente dry-run;
- B45: `scripts/benchmark_sqlite_queries.py`.

As consultas, roots e políticas reais só serão definidas após reconciliação do schema/acervo/runtime.

## 11. Regressão canônica — 08/2026

Registro e validação:

- `config/regression_cases_v8_202608.json`;
- `scripts/validate_regression_results.py`;
- `tests/test_validate_regression_results.py`.

Modo final só aprova com **28/28 casos `PASS` com evidência**.

Controle adicional documental: P DA SILVA CARMO permanece como fixture contra interpretação errada de diretor/pró-labore como empregado com FGTS.

## 12. Governança dos B01–B50

Arquivos:

- `config/blocker_registry_v8.json`;
- `config/blocker_status_v8_current.json`;
- `scripts/validate_blocker_statuses.py`.

Regras:

- registry precisa conter exatamente B01–B50;
- `CORRIGIDO_TESTADO` exige prova de código + teste;
- `CORRIGIDO_HOMOLOGADO` exige também prova de runtime + homologação;
- modo final só aprova com 50/50 homologados.

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
4. B03 — gate único de saída;
5. B07/B08 — universo/chamadas;
6. B12–B20 — identidade/composição/aplicabilidade;
7. B24–B28 — eConsignado;
8. schema/migração + invariantes;
9. regressão dos 28 casos;
10. benchmark;
11. segurança;
12. build/pacote da mesma árvore testada;
13. instalação Windows + rollback comprovado.

## 15. Estado de entrega

Neste momento:

- V8 **não homologada**;
- pacote final **não autorizado**;
- migração real **não autorizada**;
- rollback físico final **não comprovado**;
- runtime **ainda não reconciliado integralmente com o GitHub**.

O `main`, o rastreador canônico e os registries machine-readable são a referência atual da auditoria até a reconciliação do runtime.
