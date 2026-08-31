# Auditoria canônica V8 — Etapa 66

Data: 31/08/2026  
Status: **B08 em correção / histórico de transições e chamadas auditável / causa real T L ainda depende do runtime / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 66 criou auditoria read-only do histórico de estado/chamada para localizar regressões como o caso T L.

Novo script:

`scripts/audit_state_transition_history.py`

## 2. Contrato

A política descreve:

- tabela de histórico;
- chave de cliente/competência;
- coluna de ordenação;
- estado;
- chamada;
- transições de estado permitidas;
- piso mínimo de chamada por estado;
- proibição opcional de redução de chamada;
- tabela de estado atual, quando existente.

## 3. Caso T L cercado

A regressão sintética reproduz explicitamente:

`PRONTA / chamada 1 → ADIADA / chamada 2 → PRONTA / chamada 1`

O auditor bloqueia esse fluxo com:

- `CALL_DECREASE`;
- `PROTECTED_CALL_FLOOR_REGRESSION`.

Assim, uma empresa que alcançou um estado protegido de 2ª chamada não pode regressar silenciosamente para chamada 1.

## 4. Outras verificações

São detectados:

- chamada incompatível com o estado;
- transição de estado proibida;
- ordem de histórico duplicada;
- chamada inválida no histórico;
- divergência entre último histórico válido e snapshot atual;
- registro atual sem histórico válido;
- chamada inválida no snapshot atual;
- alteração do SQLite durante a auditoria.

## 5. Regressões

Foram adicionados doze testes específicos, incluindo prova de não mutação e dados inválidos sem exceção não controlada.

## 6. Marco CI

Run:

`33444558459`

Commit:

`067d626c0ddaa96ffb1588f358dfa18b90d1136c`

Python:

`3.12.14`

Resultado:

```text
Ran 292 tests in 1.520s
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

- ID `9777519633`;
- SHA-256 `547de95d40a7551676e20e243b43b125502e6e8b8cd6a5a86ac2320b3050a136`.

## 7. Impacto sobre B08

B08 pode avançar de `INSPECAO_PENDENTE` para `EM_CORRECAO`.

O tooling agora consegue apontar o evento exato em que estado/chamada regrediram, desde que o runtime real possua histórico suficiente.

Ainda faltam:

1. reconciliar schema/runtime por B06;
2. localizar/configurar o histórico real de T L;
3. executar a auditoria na competência afetada;
4. identificar a origem concreta da transição indevida;
5. cruzar com B40/CAS;
6. corrigir o caminho que promoveu/reabriu a empresa;
7. testar navegação, sincronização, restart e concorrência;
8. validar C27 no runtime.

## 8. Limite

**A regressão T L está cercada no tooling, mas a causa operacional ainda não está provada.**

## 9. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
