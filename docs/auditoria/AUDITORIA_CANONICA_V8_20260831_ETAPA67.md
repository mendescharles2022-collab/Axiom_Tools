# Auditoria canônica V8 — Etapa 67

Data: 31/08/2026  
Status: **B36 em correção / planner global→fonte implementado e testado / migração real não executada / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 67 criou um planejador read-only para migrar decisões/estados legados globais para granularidade por fonte.

Novo script:

`scripts/plan_per_source_state_migration.py`

## 2. Regra conservadora

Uma decisão global antiga não é replicada automaticamente para várias fontes.

Quando mais de uma fonte aplicável existe e a política não autoriza fan-out explicitamente, o planner bloqueia com:

`AMBIGUOUS_FANOUT`

Isso impede transformar uma decisão genérica histórica em várias decisões específicas sem evidência.

## 3. Verificações

O planner verifica:

- identidade única do destino `chave + fonte`;
- duplicidade no estado global legado;
- duplicidade no destino por fonte;
- ausência de fonte aplicável;
- conflito com decisão já migrada;
- decisão já migrada com o mesmo valor;
- fan-out explícito quando tecnicamente autorizado;
- hash do banco antes/depois.

Nenhum `INSERT`, `UPDATE` ou `DELETE` é executado.

## 4. Regressões

Foram adicionados dez testes, incluindo:

- fonte única inequívoca;
- múltiplas fontes bloqueadas;
- fan-out explicitamente autorizado;
- conflito de destino;
- estado já migrado;
- fonte inaplicável;
- índices/duplicidades;
- prova de não mutação.

## 5. Marco CI

Run `33444873556`  
Commit `af23e64da69ac69fe92db9ec39a56ba98dbad03e`

```text
Ran 312 tests in 1.368s
OK
```

Artifact `v8-release-preflight`:

- ID `9777628205`;
- SHA-256 `9fe1d37c0e51e17920f1dca7a706356a77bffa25ea1285fff920f8af4e63fdec`.

## 6. Impacto sobre B36

B36 pode avançar de `INSPECAO_PENDENTE` para `EM_CORRECAO`.

Ainda faltam:

1. schema legado real reconciliado;
2. universo real de fontes aplicáveis;
3. execução do planner em cópia do banco;
4. revisão dos casos ambíguos;
5. migração em clone com rollback;
6. comparação antes/depois;
7. homologação operacional.

## 7. Limite

**Plano seguro não equivale a migração executada.**

## 8. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
