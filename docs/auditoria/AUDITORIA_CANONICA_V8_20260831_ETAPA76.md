# Auditoria canônica V8 — Etapa 76

Data: 31/08/2026  
Status: **B18–B27 com tooling executável e regressões, exceto B28 já coberto em etapa anterior / aplicação ao runtime ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 76 consolidou três famílias que antes estavam parcialmente implementadas nos deltas, mas sem contrato executável completo:

- B18/B23 — decisão por fonte, obrigação e componente;
- B19/B20/B21/B22 — aplicabilidade mensal por evidência autoritativa;
- B24/B25/B26/B27 — eConsignado como Etapa 0 do ciclo, com universo correto e conclusão contextual.

B28 permanece em `EM_CORRECAO` desde a Etapa 64, com auditor próprio de idempotência/retry.

## 2. B18/B23 — decisão por fonte/obrigação

Novo tooling:

`scripts/validate_source_obligation_decisions.py`

Chave canônica:

```text
competência + cliente + obrigação + componente
```

O validador bloqueia:

- decisão global `*`/`GLOBAL`/`TODAS`;
- decisão para obrigação inexistente;
- `previous_state` obsoleto;
- revisão mensal obsoleta;
- metadados/proveniência incompletos;
- `decision_id` duplicado.

A conclusão do cliente é derivada somente após avaliar todas as obrigações aplicáveis.

Regressão central:

```text
DARF JUSTIFICADA + FGTS PENDENTE => cliente NÃO fechável
```

Também são mantidos separados componentes como:

```text
FGTS/MENSAL
FGTS/RESCISORIO
```

## 3. B19–B22 — aplicabilidade mensal

Novo tooling:

`scripts/derive_monthly_obligation_applicability.py`

Precedência adotada:

**evidência mensal autoritativa > ocorrência mensal > expectativa cadastral genérica**.

### FGTS zero

Se a base mensal autoritativa está disponível e o valor é zero dentro da tolerância:

```text
FGTS_DIGITAL = NAO_APLICAVEL
```

mesmo que o cadastro genérico indique FGTS esperado.

### MEI/DAE

Quando o perfil mensal exigir DAE:

- DAE é obrigação própria;
- expectativa genérica de GFD não prevalece sobre o perfil específico.

### Deduções previdenciárias

O motor valida a coerência:

```text
federal bruto - deduções = saldo autoritativo
```

O saldo final autoritativo é a referência para a necessidade de DARF.

### Afastamentos/faltas

Ausência integral sem incidência monetária pode tornar FGTS/DARF não aplicáveis quando não houver evidência autoritativa mais forte em sentido contrário.

Uma incidência positiva autoritativa não é anulada simplesmente porque existe apontamento de afastamento.

## 4. B24–B27 — eConsignado

Novo tooling:

`scripts/validate_econsignado_cycle_contract.py`

Ordem canônica exigida:

```text
ECONSIGNADO -> DOMINIO -> ESOCIAL -> ECAC_DARF -> FGTS_DIGITAL -> CONFERENCIA
```

O job precisa estar vinculado ao mesmo comando/orquestrador do ciclo.

O universo consultado deve corresponder exatamente ao universo elegível da competência/chamada.

São bloqueados:

- cliente extra fora do ciclo;
- cliente da chamada futura;
- cliente sem movimento quando mensalmente não aplicável;
- cliente elegível omitido.

## 5. Resultados oficiais não são conclusão de negócio

Estados da consulta oficial permanecem separados:

- `COM_CONSIGNADO`;
- `SEM_CONSIGNADO`;
- `SEM_PROCURACAO`;
- `ERRO_TECNICO`.

`SEM_PROCURACAO` não é erro técnico.

Erro técnico posterior não pode apagar fotografia válida anterior.

`COM_CONSIGNADO` não pode gerar `CONFERIDA` sozinho.

## 6. Casos protegidos

### D A F Castro

`CONFERIDA` é bloqueada quando faltar fonte necessária ou houver incompatibilidade entre fontes.

### D&L Alimentos

Retorno residual sem vínculo ativo, remuneração e FGTS pode ficar como observação contextual a confirmar, sem bloquear sozinho.

### Rescisão

Parcela mensal, garantias e componentes rescisórios precisam estar separados antes da conclusão.

## 7. Marco CI compartilhado com a Etapa 77

Run `33448515415`  
Commit `4aa402201fe7b5ed46d4b3ec317a0e4eeec5725f`

```text
POWERSHELL_B06_SMOKE_OK
Ran 478 tests in 1.487s
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

- ID `9778892183`;
- SHA-256 `1e19c9b52c570cb88fd48c6e8d24a62e1a352de3032a64756bda879a92546c02`.

## 8. Impacto de estados

Passam para `EM_CORRECAO`:

- B18;
- B19;
- B20;
- B21;
- B22;
- B23;
- B24;
- B25;
- B26;
- B27.

B28 já estava em `EM_CORRECAO`.

Nenhum deles é promovido para `CORRIGIDO_TESTADO` sem aplicação e regressão sobre a árvore reconciliada.

## 9. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
