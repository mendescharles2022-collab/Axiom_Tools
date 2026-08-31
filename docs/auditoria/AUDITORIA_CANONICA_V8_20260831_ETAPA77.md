# Auditoria canônica V8 — Etapa 77

Data: 31/08/2026  
Status: **B29/B30/B31/B33 com tooling executável e regressões / B32 já coberto anteriormente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 77 converteu os contratos de parser/proveniência e competência especial em validadores executáveis:

- B29 — diretor/pró-labore não pode virar empregado por inferência superficial;
- B30 — saldo federal autoritativo precisa vir da seção correta do Extrato Domínio;
- B31 — competência e valores precisam carregar proveniência suficiente;
- B33 — dezembro e 13º precisam de semântica/calendário especiais.

B32 permanece em `EM_CORRECAO` desde a Etapa 68, com validador temporal específico para IRRF.

## 2. B29/B30/B31 — contrato de extração Domínio

Novo tooling:

`scripts/validate_dominio_extraction_contract.py`

O validador trabalha sobre a saída estruturada do parser e exige:

- método e evidência da competência;
- classificação das pessoas coerente com tipo da linha e vínculo;
- contagens agregadas compatíveis com as pessoas extraídas;
- FGTS agregado vindo da fonte autoritativa;
- saldo federal vindo da fonte autoritativa;
- proveniência por campo: fonte, seção, rótulo, página e regra.

## 3. Diretor ≠ empregado

São bloqueados:

- vínculo `Diretor` classificado como `EMPREGADO`;
- linha `Contr.` classificada como empregado;
- `Situação: Trabalhando` usada como evidência suficiente para transformar diretor em celetista.

## 4. Fixtures contratuais

### P DA SILVA CARMO

A fixture estruturada aprovada mantém:

```text
empregados = 0
contribuintes = 1
vínculo = DIRETOR
FGTS = R$ 0,00
federal = R$ 220,00
```

A presença de `Situação: Trabalhando` não altera a categoria.

### 2A Peças

A fixture aprovada mantém:

```text
empregados = 2
contribuintes = 1
FGTS = R$ 345,57
federal = R$ 518,44
```

A soma do FGTS individual dos empregados precisa bater com o valor agregado dentro da tolerância.

## 5. Fontes autoritativas

FGTS mensal:

```text
INSS FGTS, PIS e ISS -> Valor do FGTS
```

Identificador canônico usado pela fixture:

`INSS_FGTS_PIS_ISS_VALOR_FGTS`

Federal:

```text
Apuração Tributos Federais -> Saldo à recolher
```

Identificador canônico:

`APURACAO_TRIBUTOS_FEDERAIS_SALDO`

Campo intermediário ou proximidade textual não substituem essas fontes.

## 6. B33 — dezembro e 13º

Novo tooling:

`scripts/validate_special_competence_calendar.py`

Regras principais:

- `13/AAAA` precisa ser classificado como `THIRTEENTH`;
- 13º não pode ser tratado como mês normal;
- inferência por calendário genérico é bloqueada para 13º;
- inferência especial precisa registrar `calendar_rule_id`;
- dezembro inferido não pode usar regra mensal genérica quando a janela especial for necessária;
- dezembro e 13º são identidades distintas;
- proveniência do método/evidência é obrigatória.

## 7. Marco CI compartilhado com a Etapa 76

Run `33448515415`  
Commit `4aa402201fe7b5ed46d4b3ec317a0e4eeec5725f`

```text
POWERSHELL_B06_SMOKE_OK
Ran 478 tests in 1.487s
OK
```

Artifact:

- ID `9778892183`;
- SHA-256 `1e19c9b52c570cb88fd48c6e8d24a62e1a352de3032a64756bda879a92546c02`.

O preflight continua deliberadamente não final:

- B homologados `0/50`;
- C PASS `0/28`;
- mapa causal `28/28`;
- evidências externas PASS `1/10`;
- release READY `False`;
- build OK `False`.

## 8. Impacto de estados

Passam para `EM_CORRECAO`:

- B29;
- B30;
- B31;
- B33.

B32 já estava em `EM_CORRECAO`.

Nenhum parser é considerado homologado até validar documentos reais na árvore reconciliada.

## 9. Estado após Etapas 76–77

Após atualizar o snapshot canônico:

- `PRONTO_PARA_CORRIGIR`: 4;
- `INSPECAO_PENDENTE`: 0;
- `EM_CORRECAO`: 42;
- `BLOQUEADO_POR_RUNTIME`: 4;
- `CORRIGIDO_TESTADO`: 0;
- `CORRIGIDO_HOMOLOGADO`: 0.

Restarão em `PRONTO_PARA_CORRIGIR` apenas B43, B44, B46 e B47.

## 10. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
