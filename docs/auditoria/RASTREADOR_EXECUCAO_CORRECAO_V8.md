# Rastreador canônico — Execução de correção V8

Data: 28/08/2026  
Status: **RUNTIME AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

## 1. Marco canônico do tooling

GitHub Actions run `33195532631`  
Commit `b18c487f125c300964a5558b5f8cbe271c0418dc`  
Python 3.12.14

```text
Ran 161 tests in 0.999s
OK
```

Preflight da mesma run:

- `Final OK = False`;
- B homologados `0/50`;
- C PASS `0/28`;
- evidências externas `1/10`;
- release READY `False`;
- build OK `False`.

Artifact: `v8-release-preflight`, ID `9695566182`, 2.190 bytes, SHA-256 `a379a32b433722f87b179d200dde5d454eefdaff68a2e2318f8bb93b295bf4c6`.

## 2. Fontes de verdade

- `config/blocker_registry_v8.json`;
- `config/blocker_status_v8_current.json`;
- `config/regression_cases_v8_202608.json`;
- `config/release_identity.toml`;
- `config/release_gate_evidence_v8_current.json`;
- `docs/STATUS_ATUAL.md`;
- este rastreador.

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

## 4. B06 — próximo gate operacional

Não implementar B01/B02/B03 sobre a fundação reduzida da `main`.

Já pronto/testado:

- `scripts/export_runtime_reconciliation.py`;
- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/audit_runtime_reconciliation.py`;
- E2E de export/auditoria/diferença/adulteração.

Pendente:

1. exportar a instalação Windows real ou recuperar pacote canônico equivalente;
2. auditar o export;
3. reconciliar código controlado com o `main`;
4. trazer/rodar a suíte operacional original;
5. estabelecer baseline antes de alterar runtime.

## 5. B42 — proveniência

Estado `EM_CORRECAO`.

Pronto: release identity, geração/verificação de manifesto, Git limpo, SHA-256 e bloqueio de conteúdo sensível.

Pendente: integração com runtime, `/health`, logs, instalador e pacote final.

## 6. B35/B05 — banco

Pronto: baseline somente leitura, clone consistente, comparação pré/pós e invariantes parametrizáveis.

B35 `EM_CORRECAO`; B05 `BLOQUEADO_POR_RUNTIME`.

## 7. B41 — rollback

Pronto: bundle, verificador e restauração em staging.

Pendente: arquivos reais, cópia real, rollback físico Windows e smoke posterior.

## 8. B38/B45/B48/B49

- B38: auditor estático de rotas pronto; dinâmica depende do runtime;
- B45: benchmark SQLite pronto; runtime representativo pendente;
- B48: retenção estritamente dry-run;
- B49: auditor banco ↔ filesystem pronto; schema/acervo real pendentes.

## 9. C01–C28

Registro canônico e validador prontos. Esqueleto `NOT_RUN` é gerado automaticamente pelo preflight.

Modo final exige 28/28 PASS com evidência.

## 10. B01–B50

Registry/status/validador prontos. Modo final exige 50/50 `CORRIGIDO_HOMOLOGADO`, cada um com evidências de código, teste, runtime e homologação.

## 11. Gate final

Ferramentas:

- `scripts/validate_release_gate.py`;
- `scripts/build_current_preflight.py`;
- `scripts/build_evidence_index.py`;
- `docs/auditoria/GUIA_GATE_FINAL_HOMOLOGACAO_V8.md`.

O CI gera automaticamente três arquivos de preflight e publica artifact verificável.

O gate final exige 50/50 B homologados, 28/28 C PASS, release READY, build verificado e dez gates externos PASS.

## 12. Ordem após B06

1. baseline/suíte operacional original;
2. B01;
3. B02;
4. B03/B39;
5. B07/B08;
6. B09/B10/B11/B37/B40;
7. B12–B23/B29–B33;
8. B24–B28;
9. B34/B36/B38;
10. B43/B44/B46/B47/B50;
11. migração/invariantes reais;
12. C01–C28;
13. benchmark runtime;
14. build/pacote;
15. instalação Windows + rollback.

## 13. Situação final desta atualização

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**

O tooling está maduro e comprovado em CI. O próximo salto de valor depende de remover B06 e trabalhar sobre a árvore operacional real.
