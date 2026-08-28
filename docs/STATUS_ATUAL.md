# Axiom Tools — Status Atual

Data: 28/08/2026  
Status: **V5.6.14V7 estável / V8 em auditoria e correção / V8 NÃO HOMOLOGADA**

## 1. Marco atual

Execução canônica do tooling:

- GitHub Actions run `33196049264`;
- commit `eb695be6531c7711ac36b3f45e0d9d31eb809233`;
- Python 3.12.14;
- **165 testes executados / 165 aprovados**.

Artifact `v8-release-preflight`:

- ID `9695772154`;
- 2.288 bytes;
- SHA-256 `380162c6ed4b1d5b01b0f7c7c834f8f1d300699db54b4b050ed967b5e9181d85`.

Preflight continua corretamente bloqueado:

- `Final OK = False`;
- B homologados `0/50`;
- C PASS `0/28`;
- evidências externas `1/10`;
- release READY `False`;
- build OK `False`.

## 2. Estado B01–B50

- 35 `PRONTO_PARA_CORRIGIR`;
- 8 `INSPECAO_PENDENTE`;
- 3 `EM_CORRECAO` — B35, B41, B42;
- 4 `BLOQUEADO_POR_RUNTIME` — B05, B06, B45, B49;
- 0 `CORRIGIDO_HOMOLOGADO`.

## 3. B35 — avanço com invariantes reais

Além do executor genérico somente leitura, já existe:

- `config/sqlite_invariants_closing_confirmed_v8.json`;
- `tests/test_closing_confirmed_invariants.py`.

Regras comprovadas pelo runtime preservado:

1. `FECHADA` deve possuir ao menos uma versão em `fechamento_mensal_versao`;
2. `versao_atual`, quando preenchida, deve apontar para versão existente do mesmo cliente/competência.

As quatro regressões específicas dessas regras passaram na run canônica.

B35 continua `EM_CORRECAO` porque essas invariantes ainda não foram executadas contra uma cópia real do banco operacional.

## 4. B06 — principal gate operacional

O `main` ainda não contém integralmente a árvore V8 auditada no servidor/ZIP canônico.

Ferramentas prontas/testadas:

- exportador controlado do runtime;
- launcher PowerShell;
- auditor runtime ↔ GitHub;
- E2E de reconciliação;
- preflight automático no CI.

Pendente: exportar/reconciliar a árvore Windows real ou recuperar pacote canônico equivalente.

## 5. Achado novo de interface no runtime

O template real de Processamento preservado em logs mostra:

- eyebrow `PROCESSAMENTO DE ARQUIVOS`;
- `<h1>` ainda iniciado por `Aud...`.

O achado foi registrado em:

`docs/auditoria/ACHADO_RUNTIME_RESIDUO_AUDITORIA_NO_PROCESSAMENTO_V8.md`.

Ele reforça B37/B43/B46 e confirma resíduo semântico da arquitetura antiga na interface, sem criar novo bloqueador.

## 6. Gate final

Implementado:

- `scripts/validate_release_gate.py`;
- `scripts/build_current_preflight.py`;
- `scripts/build_evidence_index.py`;
- registries B01–B50 e C01–C28;
- evidência viva do CI;
- artifact automático de preflight.

Modo final exige 50/50 B homologados, 28/28 C PASS, release READY, build verificado e todas as evidências externas PASS.

## 7. Demais tooling preparado

- proveniência de build;
- SQLite baseline/clone/comparação/invariantes;
- backup/rollback em staging;
- segurança estática;
- banco ↔ filesystem;
- retenção dry-run;
- benchmark SQLite;
- regressão dos 28 casos;
- governança dos 50 bloqueadores.

## 8. Ordem da correção após B06

1. baseline/suíte operacional original;
2. B01 — reprocessamento candidato;
3. B02 — Conference somente leitura;
4. B03/B39 — gate de saídas;
5. B07/B08 — universo/chamadas;
6. estados/retificação/concorrência;
7. documentos/identidade/composição/aplicabilidade;
8. eConsignado;
9. cadastro/legado/segurança;
10. UX/restantes;
11. migração/invariantes reais;
12. C01–C28;
13. benchmark runtime;
14. build/pacote;
15. instalação Windows + rollback.

## 9. Estado de entrega

- V8 **não homologada**;
- pacote final **não autorizado**;
- migração real **não autorizada**;
- rollback físico **não comprovado**;
- runtime **ainda não reconciliado integralmente com o GitHub**.
