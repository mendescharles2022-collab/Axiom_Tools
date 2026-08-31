# Auditoria canônica V8 — Etapa 72

Data: 31/08/2026  
Status: **launcher B06 executado em smoke real PowerShell no CI / runtime físico ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 72 removeu a última lacuna entre revisão estática do launcher PowerShell e sua execução efetiva.

O workflow:

`.github/workflows/reconciliation-tests.yml`

passa a executar o launcher:

`scripts/BUILD_RUNTIME_HANDOFF_V8.ps1`

em um runtime descartável criado no próprio runner.

## 2. Smoke executado

O job cria:

- árvore mínima `app/src`;
- SQLite real dentro de `data/operational.sqlite3`;
- diretório de saída externo ao runtime.

Em seguida executa o launcher sem `-Database`, usando a autodiscovery conservadora da Etapa 71.

O smoke exige:

- geração do handoff completo;
- `database_selection = AUTO_DISCOVERED_SINGLE`;
- `source_mutation_performed = false`;
- `database_in_code_zip = false`;
- manifesto presente;
- término com `POWERSHELL_B06_SMOKE_OK`.

## 3. Resultado observado

O log do run registrou:

```text
Banco: autodiscovery conservadora; só prossegue se houver exatamente um SQLite válido.
RUNTIME_HANDOFF_OK
Origem alterada: NÃO
V8 homologada: NÃO
RUNTIME_HANDOFF_WINDOWS_OK
Banco selecionado: operational.sqlite3 [AUTO_DISCOVERED_SINGLE]
Origem alterada: NÃO
V8 homologada: NÃO
POWERSHELL_B06_SMOKE_OK
```

Isso prova que o launcher chama o orquestrador Python, produz ZIP de código/configuração, clona o SQLite separadamente e valida o manifesto em uma execução PowerShell real.

## 4. Workflow protegido

O workflow agora também observa alterações em:

`scripts/*.ps1`

Assim modificações futuras no launcher PowerShell disparam novamente o CI.

A suíte possui regressões que exigem a existência do smoke e do trigger para `.ps1`.

## 5. Marco CI

Run `33446425395`  
Commit `49b9093fcd3060f020dd3dfbb7eee58d2913a7bf`

Smoke:

```text
POWERSHELL_B06_SMOKE_OK
```

Suíte:

```text
Ran 338 tests in 1.491s
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

- ID `9778186417`;
- SHA-256 `3e7d358b201025096378ba505b35fbd237c38c76f52f8c0cf69a921e6d9a7d42`.

## 6. Limite da evidência

O smoke foi executado por `pwsh` em runner Ubuntu hospedado pelo GitHub Actions.

Ele comprova:

- sintaxe/execução do launcher PowerShell;
- integração PowerShell → Python;
- autodiscovery de SQLite real;
- geração/validação do handoff;
- proteções lógicas do fluxo.

Ele **não** comprova:

- caminhos/ACLs/serviços específicos do Windows operacional do escritório;
- conteúdo da instalação física;
- banco real;
- runtime real;
- instalação/rollback físico.

Portanto `RUNTIME_BASELINE` permanece `NOT_RUN`.

## 7. Impacto em B06

B06 continua:

`BLOQUEADO_POR_RUNTIME`

A diferença é que o tooling necessário para a coleta física agora passou também por execução PowerShell end-to-end em CI.

O próximo passo tecnicamente material é executar o mesmo launcher na instalação Windows real.

## 8. Estado geral

- `PRONTO_PARA_CORRIGIR`: 34;
- `INSPECAO_PENDENTE`: 0;
- `EM_CORRECAO`: 12;
- `BLOQUEADO_POR_RUNTIME`: 4;
- `CORRIGIDO_TESTADO`: 0;
- `CORRIGIDO_HOMOLOGADO`: 0.

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
