# Guia — Gate final de homologação V8

Data: 28/08/2026  
Status: **gate implementado / V8 ainda bloqueada**

## Objetivo

Impedir que um pacote seja chamado de V8 final com alguma camada incompleta.

Ferramenta:

- `scripts/validate_release_gate.py`

Arquivos canônicos relacionados:

- `config/blocker_registry_v8.json`;
- `config/blocker_status_v8_current.json`;
- `config/regression_cases_v8_202608.json`;
- `config/release_identity.toml`;
- `config/release_gate_evidence_v8_current.json`;
- `config/release_gate_evidence.example.json`.

## Modos

### Preflight

O preflight pode ser executado antes da homologação para mostrar objetivamente o que ainda falta.

Ele não transforma pendência em erro operacional do sistema; apenas informa que a liberação final ainda não é permitida.

### Final

Com `--final`, qualquer camada incompleta bloqueia a liberação.

O modo final exige também `--payload-root` e `--repo-root` para verificar o build e sua proveniência.

## Condições obrigatórias

### Bloqueadores

- exatamente B01–B50;
- 50/50 em `CORRIGIDO_HOMOLOGADO`;
- cada homologado com evidências de código, teste, runtime e homologação.

### Regressão

- exatamente C01–C28;
- 28/28 `PASS`;
- cada `PASS` com evidência;
- resultados vinculados ao hash do registry canônico.

### Release/build

- `config/release_identity.toml` em `READY`;
- versão/schema preenchidos;
- Git limpo;
- `BUILD_PROVENANCE.json` válido;
- payload idêntico ao manifesto;
- commit do build idêntico à fonte verificada.

### Evidências externas

Todos os gates abaixo precisam estar `PASS` com evidência:

1. `CI_TOOLING`;
2. `RUNTIME_BASELINE`;
3. `DATABASE_INTEGRITY`;
4. `DATABASE_FOREIGN_KEYS`;
5. `DATABASE_INVARIANTS`;
6. `BENCHMARK_RUNTIME`;
7. `SECURITY_RUNTIME`;
8. `REPORT_A4`;
9. `WINDOWS_INSTALLATION`;
10. `ROLLBACK_WINDOWS`.

## Estado atual

`config/release_gate_evidence_v8_current.json` registra apenas:

- `CI_TOOLING = PASS` — GitHub Actions run `33194834851`, 142 testes aprovados;
- demais gates = `NOT_RUN`.

Além disso:

- B01–B50 ainda possuem 0 homologados;
- C01–C28 ainda não foram executados no runtime reconciliado;
- release continua `UNRELEASED`;
- build final ainda não existe.

Portanto o gate final deve falhar no estado atual.

## Exemplo de execução final

```bash
python scripts/validate_release_gate.py \
  --blocker-registry config/blocker_registry_v8.json \
  --blocker-status <status-final.json> \
  --regression-registry config/regression_cases_v8_202608.json \
  --regression-results <resultados-28-casos.json> \
  --release-identity config/release_identity.toml \
  --evidence-manifest <evidencias-finais.json> \
  --payload-root <payload-do-build> \
  --repo-root . \
  --final \
  --output V8_RELEASE_GATE.json
```

## Regra de governança

`V8_RELEASE_GATE.json` com `final_ok=true` é condição necessária para liberação, mas não substitui a responsabilidade de executar os testes reais corretamente.

O gate valida consistência e completude das evidências; ele não autoriza inventar evidência.

Enquanto `final_ok=false`, nenhum ZIP deve ser chamado de V8 final/homologado.
