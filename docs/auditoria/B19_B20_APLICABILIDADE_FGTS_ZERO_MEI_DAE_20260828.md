# B19/B20 — Aplicabilidade: FGTS zero e MEI/DAE

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## B19 — FGTS zero

A Conference passa a priorizar a evidência da própria competência. Quando o Extrato Mensal do Domínio existe e traz `fgts_total = 0`, o cadastro genérico não pode fabricar uma ausência de GFD.

Fixture real validado:

- cliente 498 — Larissa B Maia;
- competência 08/2026;
- FGTS Domínio: R$ 0,00;
- `exibir_fgts = false`;
- check FGTS: `NAO_APLICAVEL`;
- DARF previdenciário continua independente.

## B20 — MEI / DAE

O perfil MEI não usa duas obrigações independentes DARF + GFD para o fechamento mensal. A Conference passa a trabalhar com fonte `DAE`, comparando a guia unificada contra:

`previdenciário esperado da folha + FGTS esperado da folha`.

O perfil operacional passa a reutilizar a regra canônica de Clientes (`resolver_perfil`), considerando classificação e, quando disponível, `cliente_rfb.opcao_mei`.

Fixture real validado:

- cliente 270 — Elenice Batista Santos Silva;
- competência 08/2026;
- previdenciário esperado: R$ 170,20;
- FGTS esperado: R$ 129,68;
- DAE esperada: R$ 299,88;
- guia unificada lida: R$ 299,88;
- resultado DAE: `CONFERIDO`;
- `exibir_fgts = false`;
- fonte de decisão manual: `DAE`, não DARF/FGTS.

## Decisão por fonte

B18 foi ampliado para aceitar `DAE` entre as fontes válidas. Para MEI, o agregador usa DAE como obrigação financeira principal e não cria DARF e FGTS como fontes irmãs artificiais.

## Evidência de testes

Teste versionado:

`runtime_overlay/app/tests/modules/test_applicability_fgts_mei_v8.py`

Resultados na árvore corrigida:

- 5/5 testes específicos PASS;
- regressão não-web acumulada: 352/352 PASS;
- 0 failures;
- 0 errors;
- 0 skips.

Hashes da árvore testada após B20:

- `operations.py`: `b2291a31151f8426cb030e9729397eb6e9445fc70e709908bbf9ab0e0326d858`
- `conference.py`: `ff0cbf7a144381aae8094ba7b75f55e280788895d9892ba0e626b3c20228e539`

## Estado

B19 e B20 podem ser classificados como `CORRIGIDO_TESTADO` na cópia canônica. Ainda dependem da promoção/reconciliação da árvore e homologação Windows para `CORRIGIDO_HOMOLOGADO`.
