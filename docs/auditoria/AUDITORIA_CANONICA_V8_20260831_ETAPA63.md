# Auditoria canônica V8 — Etapa 63

Data: 31/08/2026  
Status: **B40 em correção / auditor compare-and-set implementado e testado / concorrência real ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 63 criou tooling estático para localizar transições SQLite suscetíveis a `lost update`.

Novo script:

`scripts/audit_sqlite_cas_contract.py`

O auditor é somente leitura e não modifica código nem banco.

## 2. Contrato CAS

Para tabelas de estado protegidas pela política, cada `UPDATE` precisa demonstrar:

1. chave de negócio completa no `WHERE`;
2. ao menos um guard de concorrência no `WHERE`, como estado/chamada/revisão/token previamente lido;
3. verificação de `rowcount` após a tentativa de atualização.

Um `UPDATE` filtrado apenas por `competencia + cliente_id`, por exemplo, não é tratado como compare-and-set.

## 3. Achados

O auditor pode produzir:

- `MISSING_KEY_COLUMNS`;
- `MISSING_CAS_GUARD`;
- `ROWCOUNT_NOT_CHECKED`;
- `UNRESOLVED_EXECUTE_SQL` quando a política real exigir bloqueio de SQL dinâmico não resolvido.

## 4. Cobertura estática

São reconhecidos:

- `execute`;
- `executemany`;
- SQL literal;
- SQL multiline;
- SQL guardado em constante string simples;
- maiúsculas/minúsculas SQL.

SQL/ORM construído dinamicamente permanece explicitamente fora da prova automática e deve ser auditado no runtime/árvore reconciliada.

## 5. Regressões

Foram adicionados oito testes cobrindo:

1. atualização apenas pela chave bloqueada;
2. CAS com guard + rowcount válido;
3. guard sem rowcount bloqueado;
4. chave incompleta bloqueada;
5. tabela fora da política ignorada;
6. SQL multiline/lowercase;
7. SQL em constante resolvido;
8. SQL dinâmico não resolvido promovível a bloqueio estrito.

## 6. Marco CI

Run:

`33443838223`

Commit:

`641fbf71ff144a4809a4054e445c8dee4bb37eea`

Python:

`3.12.14`

Resultado:

```text
Ran 261 tests in 1.194s
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
- ID `9777258147`;
- SHA-256 `422e0586eac56df72edc9a4a793d3d49669dc667ebbd7949cee7368c58dfcfd9`.

## 7. Impacto sobre B40

B40 pode avançar de `INSPECAO_PENDENTE` para `EM_CORRECAO`.

Ainda faltam para homologação:

1. reconciliar a árvore operacional integral por B06;
2. configurar as tabelas/chaves/guards reais;
3. executar o auditor em modo estrito;
4. corrigir transições sem CAS;
5. testar duas operações concorrentes sobre o mesmo cliente/competência;
6. provar comportamento de conflito/retry;
7. revalidar o caso T L/B08;
8. comprovar atomicidade e transações no SQLite real.

## 8. Regra preservada

**CAS detectável em fixtures não equivale a concorrência homologada.**

O risco B40 continua aberto até a árvore e o banco reais provarem as transições concorrentes.

## 9. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
