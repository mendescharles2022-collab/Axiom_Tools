# Auditoria canônica V8 — Etapa 58

Data: 31/08/2026  
Status: **B35 em correção / preflight consolidado implementado e testado / execução real pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 58 consolidou em uma única execução read-only as verificações de banco que já existiam separadamente no repositório.

Novo script:

`scripts/build_database_homologation_preflight.py`

Objetivo:

executar sobre a **mesma fotografia SQLite**:

1. `PRAGMA integrity_check`;
2. `PRAGMA foreign_key_check`;
3. inventário/schema/contagens opcionais;
4. invariantes lógicas V8 confirmadas;
5. opcionalmente auditoria bidirecional banco ↔ filesystem do B49.

Nenhuma migração, correção ou saneamento é executado.

## 2. Identidade da fotografia auditada

O preflight registra antes e depois:

- nome do banco;
- tamanho;
- `mtime_ns`;
- SHA-256.

O resultado só pode ficar `all_ok=true` quando a fotografia permanecer idêntica durante a auditoria.

Isso evita combinar, em um único relatório, resultados obtidos sobre estados diferentes do SQLite.

## 3. Integridade estrutural

O preflight reutiliza `audit_sqlite_baseline.py` e preserva separadamente:

- `integrity_ok`;
- `foreign_keys_ok`;
- `structural_ok`.

Não declara “banco íntegro” somente por `integrity_check=ok`.

## 4. Invariantes lógicas

O runner reutiliza `run_sqlite_invariants.py`.

As invariantes confirmadas atualmente permanecem:

1. `CLOSING_FECHADA_WITHOUT_VERSION`;
2. `CLOSING_CURRENT_VERSION_MUST_EXIST`.

Spec canônica:

`config/sqlite_invariants_closing_confirmed_v8.json`

Nenhuma nova invariante foi inventada sem prova do schema/runtime.

## 5. Integração opcional com B49

Quando `forward_spec`, `reverse_spec` e roots autorizadas forem fornecidos, o mesmo preflight também executa:

`scripts/audit_db_filesystem_bidirectional.py`

Assim, a fotografia de banco usada para invariantes pode ser a mesma usada para detectar:

- referência para arquivo ausente;
- tamanho/SHA divergentes;
- arquivo físico não indexado (`UNINDEXED_FILE`).

Achado de acervo bloqueia `all_ok`.

## 6. Proteções

- SQLite aberto em read-only/query-only;
- invariantes não aceitam SQL mutável;
- auditoria de acervo bloqueia SQL de escrita;
- relatório não executa migration;
- relatório não remove órfãos;
- relatório não altera arquivo físico;
- mudança do banco durante a auditoria invalida a fotografia.

## 7. Regressões adicionadas

Foram adicionados sete testes cobrindo:

1. snapshot íntegro + duas invariantes válidas;
2. violação lógica bloqueando o preflight mesmo com estrutura íntegra;
3. prova de não mutação do SQLite;
4. erro quando apenas metade das specs de acervo é fornecida;
5. B49 integrado e coerente no mesmo snapshot;
6. `UNINDEXED_FILE` bloqueando o preflight integrado;
7. spec de invariantes inválida recusada.

## 8. Marco CI

Run:

`33440483913`

Commit:

`4ece56c4612151305f5042ac7809d925a73d88bf`

Python:

`3.12.14`

Resultado:

```text
Ran 222 tests in 1.047s
OK
```

Preflight de release:

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
- ID `9776031310`;
- SHA-256 `9a993013b764a242216774e495e71e1c09f2a4a4215d7be8cb1b6665d76c8ddd`.

## 9. Impacto sobre B35

B35 permanece `EM_CORRECAO`.

A pendência de tooling genérico está substancialmente reduzida: existe agora um único relatório capaz de provar integridade física, referencial, invariantes lógicas confirmadas e coerência com acervo na mesma fotografia.

Ainda faltam para homologação:

1. recuperar/reconciliar o schema runtime real via B06;
2. executar o preflight contra cópia real do banco;
3. acrescentar novas invariantes somente quando comprovadas pelo schema;
4. repetir antes/depois de migração;
5. repetir após instalação Windows;
6. arquivar evidências no gate final.

## 10. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
