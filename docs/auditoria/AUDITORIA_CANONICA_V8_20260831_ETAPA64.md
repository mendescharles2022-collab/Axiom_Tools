# Auditoria canônica V8 — Etapa 64

Data: 31/08/2026  
Status: **B28 em correção / auditor idempotência+retry implementado e testado / schema/job real ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 64 criou auditoria read-only para o contrato de idempotência e retry de jobs SQLite.

Novo script:

`scripts/audit_sqlite_idempotency_retry.py`

## 2. Contrato auditado

A política descreve:

- tabela de jobs;
- chave primária;
- componentes da chave idempotente;
- status;
- contador de tentativas;
- próxima tentativa, quando existente;
- limite máximo de tentativas;
- estados terminais;
- estados retryable.

## 3. Proteções

O auditor verifica:

1. índice `UNIQUE` real cobrindo a chave idempotente;
2. duplicidades já existentes;
3. componentes nulos quando proibidos;
4. contador de tentativas inválido;
5. estado retryable no limite ou acima do limite;
6. job terminal ainda agendado para nova tentativa;
7. presença das colunas exigidas;
8. abertura do SQLite em modo somente leitura.

## 4. Achados

Entre os códigos possíveis:

- `MISSING_UNIQUE_IDEMPOTENCY_INDEX`;
- `DUPLICATE_IDEMPOTENCY_KEY`;
- `NULL_IDEMPOTENCY_KEY`;
- `INVALID_ATTEMPT_COUNTER`;
- `RETRYABLE_STATUS_AT_OR_ABOVE_LIMIT`;
- `TERMINAL_JOB_STILL_SCHEDULED`.

## 5. Regressões

Foram adicionados nove testes específicos, incluindo prova de não mutação do SQLite.

## 6. Marco CI combinado

Run:

`33444141491`

Commit:

`09f331ea07c222388b3911ba8e43587e495284c2`

Python:

`3.12.14`

Resultado combinado B28+B04:

```text
Ran 280 tests in 1.211s
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

- ID `9777371725`;
- SHA-256 `e1b7dc55a87fb80cc7755f7ceefa18b90a74c326e697aed5afe223a43302ad6d`.

## 7. Impacto sobre B28

B28 pode avançar de `INSPECAO_PENDENTE` para `EM_CORRECAO`.

Ainda faltam:

1. schema/job real reconciliado;
2. definição da chave idempotente por job;
3. índices reais;
4. política real de retry/backoff;
5. execução do auditor contra cópia do banco;
6. teste de replay da mesma entrada;
7. teste de falha parcial + retry;
8. prova de que duplicação não duplica efeito econômico/operacional.

## 8. Limite

**Índice e invariantes verdes em fixture não homologam o job real.**

## 9. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
