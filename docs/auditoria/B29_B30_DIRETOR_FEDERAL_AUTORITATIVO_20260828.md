# B29/B30 — Diretor ≠ empregado e federal autoritativo

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## Fixture documental real

Documento: `21537-Extrato Mensal.pdf` — P DA SILVA CARMO — 08/2026.

O documento traz simultaneamente:

- `Contr: 1 POLIANA DA SILVA CARMO Situação: Trabalhando`;
- `Vínculo: Diretor`;
- pró-labore R$ 2.000,00;
- INSS R$ 220,00;
- Base/Valor FGTS R$ 0,00;
- `No. Empregados: 0`;
- `No. Contribuintes: 1`;
- linha monetária `Contribuintes: 0,00` no resumo previdenciário;
- `Saldo à recolher: 220,00` na seção Apuração Tributos Federais.

## B29 — Diretor ≠ empregado

Foi criado `extrair_situacoes_extrato()` para separar formalmente:

- situação da pessoa (`Trabalhando`, afastado etc.);
- tipo de registro no Extrato (`EMPREGADO` ou `CONTRIBUINTE`);
- vínculo (`Diretor`, `Celetista` etc.);
- contagem oficial `No. Empregados`;
- contagem oficial `No. Contribuintes`.

Regra canônica: `Situação: Trabalhando` nunca prova vínculo empregatício.

O parser especialista Domínio passou a persistir:

- `numero_empregados`;
- `numero_contribuintes`;
- `tem_empregados`;
- `tem_contribuintes`;
- `pessoas_resumo`;
- `vinculos_resumo`.

O parser legado `_dados_extrato()` foi alinhado ao mesmo contrato, removendo regex antiga que lia incorretamente o quadro de Situações.

## B30 — Federal autoritativo

A fonte autoritativa do total federal é a seção `Apuração Tributos Federais → Saldo à recolher`.

Foi materializado o metadado:

`federal_fonte_autoritativa = APURACAO_TRIBUTOS_FEDERAIS_SALDO_A_RECOLHER`

A linha monetária `Contribuintes: 0,00` não é usada como quantidade de contribuintes nem como saldo federal.

Fixture real P DA SILVA CARMO:

- previdenciário esperado: R$ 220,00;
- DARF previdenciário: R$ 220,00;
- resultado: `CONFERIDO`;
- FGTS: `NAO_APLICAVEL`.

## Evidência de testes

Teste versionado:

`runtime_overlay/app/tests/modules/test_dominio_relationship_federal_v8.py`

Resultados na árvore corrigida:

- 5/5 testes específicos PASS;
- regressão não-web acumulada: 382/382 PASS;
- 0 failures;
- 0 errors;
- 0 skips.

Hashes da árvore testada:

- `dominio_advanced.py`: `c9d8064da30668a24d7f198dc3959319012084d0aa198190217db6f91ad503ce`
- `dominio_engine.py`: `d96d470cff0b2e87a01bab2f892dd6d467b51859332ecb3c40cb2fce3525233d`
- `dominio.py`: `3d84588768c886c03eeb5d491d25f365956f06ea04f983af45a904a3218b1ae6`
- teste específico: `9481c150d86623a92422957ccc427fad681c3ec17dab67af0f81597d31e9fc63`

## Estado

B29 e B30 podem ser classificados como `CORRIGIDO_TESTADO` na cópia canônica recuperada.

Ainda não são `CORRIGIDO_HOMOLOGADO`: dependem da promoção da árvore reconciliada, execução Windows/runtime e homologação final da V8.
