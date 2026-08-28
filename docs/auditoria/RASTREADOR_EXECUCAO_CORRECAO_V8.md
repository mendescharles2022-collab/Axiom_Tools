# Rastreador canônico — Execução de correção V8

Data: 28/08/2026  
Status: **RUNTIME AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

Este é o rastreador vivo da fase de correção/homologação. Os documentos `AUDITORIA_CANONICA_V8_20260828_ETAPA*.md` permanecem como histórico.

## 1. Fonte de verdade

- `config/blocker_registry_v8.json` — B01–B50;
- `config/blocker_status_v8_current.json` — estados atuais;
- `config/regression_cases_v8_202608.json` — C01–C28;
- `docs/STATUS_ATUAL.md` — estado geral;
- este arquivo — sequência operacional.

## 2. CI do tooling — APROVADA

Workflow: `V8 Audit Tooling Tests`  
Run: `33194834851`  
Commit: `568f878bf8b99dc8b63466a8ab556233d7fd83b0`  
Python: `3.12.14`

```text
Ran 142 tests in 1.390s
OK
```

**142/142 testes aprovados**.

Essa aprovação valida o tooling de auditoria/homologação, não a V8 operacional.

## 3. Snapshot B01–B50

| Estado | Quantidade |
|---|---:|
| `PRONTO_PARA_CORRIGIR` | 35 |
| `INSPECAO_PENDENTE` | 8 |
| `EM_CORRECAO` | 3 |
| `BLOQUEADO_POR_RUNTIME` | 4 |
| `CORRIGIDO_TESTADO` | 0 |
| `CORRIGIDO_HOMOLOGADO` | 0 |

Em correção: B35, B41, B42.  
Bloqueados pelo runtime: B05, B06, B45, B49.

## 4. Gate Zero — B06

B06 continua sendo o principal bloqueador da correção operacional.

Não implementar B01/B02/B03 sobre a fundação reduzida da `main` como se fosse o runtime auditado.

Tooling pronto/testado:

- `scripts/export_runtime_reconciliation.py`;
- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/audit_runtime_reconciliation.py`;
- 3 E2E de reconciliação aprovados no CI.

Pendente:

- exportar runtime no Windows;
- auditar export;
- reconciliar código controlado;
- trazer suíte operacional original.

## 5. B42 — proveniência

Estado: `EM_CORRECAO`.

Implementado/testado:

- identidade canônica `UNRELEASED`;
- geração/verificação de `BUILD_PROVENANCE.json`;
- Git limpo;
- SHA-256 do payload;
- bloqueio de conteúdo sensível.

Pendente: runtime, `/health`, logs, instalador e pacote final consumirem a mesma identidade.

## 6. B35/B05 — SQLite/migração

Tooling:

- baseline somente leitura;
- cópia consistente via `backup()`;
- comparação pré/pós;
- executor de invariantes somente leitura.

B35 = `EM_CORRECAO`.  
B05 = `BLOQUEADO_POR_RUNTIME`.

## 7. B41 — backup/rollback

Estado: `EM_CORRECAO`.

Bundle, verificador e restauração em staging estão implementados/testados.

Pendente: bundle real, ensaio com cópia real, rollback físico Windows e smoke pós-rollback.

## 8. B38/B45/B48/B49

- B38 — auditoria estática de rotas preparada; segurança dinâmica depende do runtime;
- B45 — benchmark SQLite preparado; benchmark runtime depende da árvore real;
- B48 — retenção somente dry-run; política real depende do acervo;
- B49 — banco ↔ filesystem preparado; consultas/roots reais dependem do schema/acervo.

## 9. Regressão C01–C28

O modo final exige 28/28 `PASS` com evidência e hash do registry correspondente.

Arquivos:

- `config/regression_cases_v8_202608.json`;
- `scripts/validate_regression_results.py`.

## 10. Governança B01–B50

`CORRIGIDO_TESTADO` exige prova de código + teste.  
`CORRIGIDO_HOMOLOGADO` exige também prova de runtime + homologação.

Modo final exige 50/50 homologados.

## 11. Gate único de homologação — NOVO

Arquivos:

- `scripts/validate_release_gate.py`;
- `config/release_gate_evidence.example.json`;
- `tests/test_validate_release_gate.py`.

Cobertura: **10 testes aprovados** dentro da run oficial de 142 testes.

O gate final exige simultaneamente:

1. 50/50 bloqueadores homologados;
2. 28/28 casos `PASS` com evidência;
3. release canônica `READY`;
4. build/proveniência verificados;
5. `CI_TOOLING = PASS`;
6. `RUNTIME_BASELINE = PASS`;
7. banco/integridade/FK/invariantes = `PASS`;
8. benchmark runtime = `PASS`;
9. segurança runtime = `PASS`;
10. relatório A4 = `PASS`;
11. instalação Windows = `PASS`;
12. rollback Windows = `PASS`.

No estado atual o gate final **deve falhar**. Isso é a proteção correta.

## 12. Ordem oficial da correção operacional

Assim que B06 sair do bloqueio:

1. baseline/suíte original;
2. B01;
3. B02;
4. B03/B39;
5. B07/B08;
6. B09/B10/B11/B37/B40;
7. B12–B23/B29–B33;
8. B24–B28;
9. B34/B36/B38;
10. B43/B44/B46/B47/B50;
11. migração + invariantes reais;
12. regressão C01–C28;
13. benchmark runtime;
14. build/pacote;
15. instalação Windows + rollback.

## 13. Gate final

Nenhum pacote V8 final antes de:

- [ ] runtime reconciliado;
- [ ] suíte operacional original aprovada;
- [ ] 50/50 bloqueadores homologados;
- [ ] 28/28 casos `PASS` com evidência;
- [ ] banco/invariantes aprovados;
- [ ] benchmark aprovado;
- [ ] segurança aprovada;
- [ ] A4 homologado;
- [ ] build verificável da mesma árvore testada;
- [ ] migração em cópia aprovada;
- [ ] instalação Windows aprovada;
- [ ] rollback comprovado.

Até lá: **V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO**.
