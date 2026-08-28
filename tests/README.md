# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Estado atual

A árvore operacional completa V7/V8 ainda não foi reconciliada; esta suíte valida o **tooling de auditoria/homologação**, não substitui a suíte operacional do runtime.

## Execução oficial canônica

Workflow: `V8 Audit Tooling Tests`  
Run: `33196049264`  
Commit: `eb695be6531c7711ac36b3f45e0d9d31eb809233`  
Python: `3.12.14`

```text
Ran 165 tests in 1.115s
OK
```

**165 testes definidos / 165 aprovados.**

A mesma run:

- gerou o preflight atual da V8;
- confirmou `0/50` bloqueadores homologados;
- confirmou `0/28` casos PASS;
- confirmou `1/10` evidências externas PASS;
- confirmou `Release READY = False`;
- confirmou `Build OK = False`;
- publicou `v8-release-preflight`, ID `9695772154`, 2.288 bytes;
- artifact SHA-256: `380162c6ed4b1d5b01b0f7c7c834f8f1d300699db54b4b050ed967b5e9181d85`.

## Famílias cobertas

- reconciliação runtime ↔ repositório, inclusive E2E;
- proveniência/verificação de build;
- SQLite baseline, comparação pré/pós, clone e invariantes;
- invariantes confirmadas do Fechamento;
- backup/rollback e restauração em staging;
- segurança estática;
- banco ↔ filesystem;
- retenção dry-run;
- benchmark SQLite;
- regressão C01–C28;
- governança B01–B50;
- gate único de homologação;
- preflight atual;
- índice SHA-256 de evidências.

## Invariantes reais já cobertas

`config/sqlite_invariants_closing_confirmed_v8.json` contém somente regras comprovadas pelo runtime preservado:

1. `FECHADA` sem qualquer `fechamento_mensal_versao` é inválido;
2. `versao_atual` preenchida precisa apontar para versão existente do mesmo cliente/competência.

`tests/test_closing_confirmed_invariants.py` possui 4 regressões específicas, todas aprovadas na run canônica.

## Controles canônicos

- `config/blocker_registry_v8.json`;
- `config/blocker_status_v8_current.json`;
- `config/regression_cases_v8_202608.json`;
- `config/release_identity.toml`;
- `config/release_gate_evidence_v8_current.json`;
- `scripts/validate_release_gate.py`;
- `scripts/build_current_preflight.py`;
- `scripts/build_evidence_index.py`.

## Limite

Os 165 testes aprovam o tooling. A V8 operacional continua dependente da reconciliação do runtime e dos testes reais de processamento, Conferência, saídas, chamadas, documentos, eConsignado, migração, segurança dinâmica, benchmark runtime, C01–C28 e rollback Windows.

## Princípio

Nenhum item muda para `CORRIGIDO_HOMOLOGADO` por documentação ou tooling. É obrigatória prova sobre a árvore/runtime/build correto.
