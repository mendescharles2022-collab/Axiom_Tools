# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Estado atual

A árvore operacional completa V7/V8 ainda não foi reconciliada; esta suíte valida o **tooling de auditoria/homologação**, não substitui a suíte operacional do runtime.

## Execução oficial canônica

Workflow: `V8 Audit Tooling Tests`  
Run: `33195532631`  
Commit: `b18c487f125c300964a5558b5f8cbe271c0418dc`  
Python: `3.12.14`

```text
Ran 161 tests in 0.999s
OK
```

**161 testes definidos / 161 aprovados.**

A mesma run também:

- gerou o preflight atual da V8;
- confirmou `0/50` bloqueadores homologados;
- confirmou `0/28` casos PASS;
- confirmou `1/10` evidências externas PASS;
- confirmou `Release READY = False`;
- confirmou `Build OK = False`;
- publicou o artifact `v8-release-preflight`, ID `9695566182`, 2.190 bytes;
- artifact SHA-256: `a379a32b433722f87b179d200dde5d454eefdaff68a2e2318f8bb93b295bf4c6`.

## Famílias cobertas

- reconciliação runtime ↔ repositório, inclusive 3 E2E;
- proveniência/verificação de build;
- SQLite baseline, comparação pré/pós, clone e invariantes;
- backup/rollback e restauração em staging;
- segurança estática das rotas;
- banco ↔ filesystem;
- retenção dry-run;
- benchmark SQLite;
- regressão C01–C28;
- governança B01–B50;
- gate único de homologação;
- preflight atual;
- índice SHA-256 de evidências.

## Controles canônicos

- `config/blocker_registry_v8.json`;
- `config/blocker_status_v8_current.json`;
- `config/regression_cases_v8_202608.json`;
- `config/release_identity.toml`;
- `config/release_gate_evidence_v8_current.json`;
- `scripts/validate_release_gate.py`;
- `scripts/build_current_preflight.py`;
- `scripts/build_evidence_index.py`.

## Limite da suíte atual

Os 161 testes aprovam o tooling. A V8 operacional continua dependente da reconciliação do runtime e dos testes reais de reprocessamento, Conference, saídas, chamadas, documentos, eConsignado, migração, segurança dinâmica, benchmark runtime, C01–C28 e rollback Windows.

## Princípio

Nenhum item muda para `CORRIGIDO_HOMOLOGADO` por documentação ou tooling. É obrigatória prova sobre a árvore/runtime/build correto.
