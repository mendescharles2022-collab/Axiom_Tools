# Auditoria canônica V8 — Etapa 60

Data: 31/08/2026  
Status: **B42 em correção / cadeia única de identidade implementada e testada / release permanece UNRELEASED / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 60 fechou a lacuna de coerência entre a identidade canônica da release, a proveniência do build, a identidade observada no runtime/health e a identidade declarada pelo instalador.

Novo script:

`scripts/validate_release_identity_chain.py`

Fluxo lógico:

`release_identity.toml → BUILD_PROVENANCE.json → runtime/health → installer`

Nenhuma dessas fontes pode declarar uma identidade diferente e ainda ser considerada coerente.

## 2. Regra de autoridade

A fonte canônica de versão/schema/plataforma é:

`config/release_identity.toml`

O arquivo canônico não inventa nem fixa antecipadamente o commit final.

A proveniência do build é quem sela a identidade canônica a um commit Git específico.

A partir daí, runtime/health e instalador precisam repetir exatamente:

- produto;
- versão da release;
- versão do schema;
- plataforma;
- commit SHA.

## 3. Estado UNRELEASED

O repositório permanece corretamente com:

`state = "UNRELEASED"`

Enquanto esse estado permanecer:

- release_version não pode ser fabricada;
- schema_version final não pode ser fabricada;
- build final continua bloqueado;
- a cadeia de identidade não pode produzir autorização de release.

O validador trata `UNRELEASED` como bloqueio esperado, não como convite para preencher valores por inferência.

## 4. Verificações implementadas

A cadeia verifica, entre outras condições:

1. identidade canônica válida;
2. hash do `release_identity.toml` usado pelo build;
3. versão do build igual à identidade canônica;
4. schema do build igual à identidade canônica;
5. plataforma do build igual à identidade canônica;
6. commit Git válido no build;
7. runtime/health repetindo versão, schema e commit do build;
8. instalador repetindo versão, schema e commit do build.

Divergências são reportadas explicitamente e bloqueiam `ok`.

## 5. Regressões adicionadas

Foram adicionados sete testes cobrindo:

1. cadeia integralmente coerente;
2. release `UNRELEASED` bloqueando a cadeia;
3. hash de identidade divergente no build;
4. versão divergente no build;
5. commit divergente no runtime;
6. schema divergente no instalador;
7. commit inválido no runtime.

## 6. Marco CI

Run:

`33440917657`

Commit:

`61a519f1f9b6db866d2a34a7a66b6918d3c77bf0`

Python:

`3.12.14`

Resultado:

```text
Ran 235 tests in 1.242s
OK
```

Preflight:

```text
Final OK: False
Bloqueadores homologados: 0/50
Casos PASS: 0/28
Mapa causal: 28/28
Evidências PASS: 1/10
Release READY: False
Build OK: False
```

Artifact:

- `v8-release-preflight`;
- ID `9776186424`;
- SHA-256 `a149a692e92d194d8c750151e0d2bb4b86c3b9cff4e1c2a2b96364543578d8ce`.

## 7. Impacto sobre B42

B42 permanece `EM_CORRECAO`.

O tooling agora consegue detectar a classe de erro em que:

- o build diz uma versão;
- `/health` diz outra;
- o instalador grava outra;
- ou um deles está em commit/schema diferente.

Ainda faltam para homologação:

1. árvore operacional integral reconciliada por B06;
2. build real final gerado a partir de release `READY`;
3. `/health` real expondo a identidade selada pelo build;
4. logs/runtime consumindo a mesma identidade;
5. instalador Windows real declarando a mesma identidade;
6. instalação física comprovando a cadeia de ponta a ponta;
7. evidência final nos gates externos.

## 8. Regra preservada

**Identidade coerente no tooling não equivale a release homologada.**

A Etapa 60 apenas impede que componentes diferentes se apresentem como a mesma V8 quando não pertencem ao mesmo build/schema/commit.

## 9. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
