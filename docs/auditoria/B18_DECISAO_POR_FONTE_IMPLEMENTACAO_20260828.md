# B18 — Decisão manual por fonte — Implementação auditada

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base operacional: `Axiom_Tools(20260828-175237).zip` recuperado e validado.

## Objetivo

Eliminar a decisão manual global por cliente/competência como mecanismo de autorização do fechamento. Cada decisão passa a existir por obrigação/fonte, inicialmente:

- DARF;
- FGTS;
- ECONSIGNADO.

A tabela legada `processamento_conferencia_manual` permanece apenas como histórico legado e não é propagada para as fontes novas.

## Implementação na cópia canônica

Foi criada `processamento_conferencia_fonte` com chave primária composta por `competencia + cliente_id + fonte`.

Foram implementados:

- `decisoes_conferencia_fontes()`;
- `salvar_conferencia_fonte()`;
- agregação de decisões por fonte na Conference;
- histórico da Conference baseado nas decisões por fonte;
- rotas `conference.decisao` e `documents.processamento_guias_conferencia_manual` exigindo `fonte` explícita;
- formulários separados por obrigação aplicável;
- recálculo explícito da Conference após decisão por fonte.

## Regra de agregação

Uma decisão manual em uma fonte nunca libera as fontes irmãs.

Exemplo obrigatório de regressão:

- DARF automático divergente;
- DARF manual = JUSTIFICADO;
- FGTS automático = DIVERGENTE;
- resultado agregado = DIVERGENTE.

Somente quando todas as fontes aplicáveis estiverem resolvidas o agregado poderá chegar a CONFERIDO ou JUSTIFICADO.

## Evidência de teste

Teste específico versionado em:

`runtime_overlay/app/tests/modules/test_conference_source_decisions_v8.py`

Resultado local na árvore operacional corrigida:

- 8/8 testes específicos PASS;
- regressão não-web acumulada: 347/347 PASS;
- 0 failures;
- 0 errors;
- 0 skips.

## Hashes da árvore testada

- `operations.py`: `c9893acb69869afdc3eb74a1540735813757579d1dbbcac95be11e0fb664a619`
- `conference.py`: `0f334d828254e4a09505d277c8b698e674430f830be9a0d6825896bbcbf9fa85`
- `conference_views.py`: `1d573de9cfb06c9c5106c2075084001dae6d7407a93e22098b338c306fa5b2f9`
- `documents_views.py`: `69f000e91a91b15f3eabba894d9951dc52b9c64708a761c3a3be2da6af7f6e4a`
- `conference/index.html`: `fcbb887893c9087bde14fd56ba3a118866b44c2e582368e46735d6a834c140f2`
- `documents/processing_guias.html`: `b91dac9a36f3038b397f1a24a91edc2fb6456a72c5526b43bb27e76fc45d21f3`

## Estado

B18 pode ser classificado como `CORRIGIDO_TESTADO` na cópia canônica recuperada.

Ainda não é `CORRIGIDO_HOMOLOGADO`: falta promoção da árvore reconciliada, bateria Windows/runtime e homologação final da V8.
