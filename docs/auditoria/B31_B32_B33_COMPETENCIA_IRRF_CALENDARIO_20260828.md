# B31/B32/B33 — Competência, proveniência, IRRF e calendário especial

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## B31 — Competência e proveniência

Foi criado o núcleo `competence_provenance.py` com as origens lógicas canônicas:

- `DOCUMENTO_EXPLICITO`;
- `FONTE_ESTRUTURADA`;
- `CONTEXTO_OCORRENCIA`;
- `CALENDARIO_INFERIDO`;
- `DECISAO_MANUAL`.

A Central passa a persistir, além do valor da competência:

- `competencia_metodo`;
- `competencia_janela`;
- `competencia_regra_versao`;
- `competencia_determinada_em`;
- `competencia_evidencia`.

O backfill do legado é explícito e metadata-only: somente registros cujo `dados_json` já demonstra a origem são preenchidos. Origem desconhecida não é fabricada.

O reprocessamento candidato também passa a comparar a força da proveniência. Um candidato de mesma competência não pode substituir automaticamente `DOCUMENTO_EXPLICITO` por `CALENDARIO_INFERIDO`, mesmo que sua completude seja maior.

Fixtures de integração:

- eSocial com `perApur=2026-08` persiste `08/2026 · DOCUMENTO_EXPLICITO`;
- eSocial sem período explícito, enviado em 02/09/2026, persiste `08/2026 · CALENDARIO_INFERIDO`, janela `25/08/2026 a 09/09/2026` e versão da regra `P25-09`.

## B32 — IRRF por competência de pagamento

O Extrato Mensal Domínio possui duas visões lado a lado:

- IRRF conforme competência do cálculo;
- IRRF conforme competência do pagamento.

Foi criado `extrair_irrf_dupla_competencia()`, preservando separadamente as bases/valores das duas visões e registrando:

`irrf_criterio_competencia = PAGAMENTO`.

A visão IRRF não substitui o total federal autoritativo já definido em B30: `Apuração Tributos Federais → Saldo à recolher` continua soberano para o total do documento.

Evidência documental real usada: Extrato Mensal da 2A Peças, onde a base de férias é R$ 1.960,20 pela competência do cálculo e R$ 0,00 pela competência do pagamento. O próprio documento informa que INSS usa competência de cálculo e IRRF usa competência de pagamento.

## B33 — Dezembro e 13º

Nenhuma data especial foi hardcoded.

O calendário eSocial passa a versionar as exceções anuais e manter histórico. Dezembro e 13º continuam definidos por configuração de exercício.

Foram testadas janelas configuradas de exemplo:

- 13/2026: 15/12/2026 a 19/12/2026;
- 12/2026: 20/12/2026 a 09/01/2027.

Essas datas pertencem exclusivamente ao fixture de teste e não viraram regra fixa de produção.

Garantias:

- exceção anual vence fallback mensal;
- editar a janela incrementa sua versão e preserva histórico;
- duas exceções ativas não podem disputar a mesma data;
- fallback mensal 25→09 continua configurável.

## Evidência de testes

Teste versionado:

`runtime_overlay/app/tests/modules/test_competence_temporal_v8.py`

Resultados na árvore corrigida:

- 11/11 testes específicos PASS;
- regressão não-web acumulada: **393/393 PASS**;
- 0 failures;
- 0 errors;
- 0 skips.

Hashes da árvore testada:

- `competence_provenance.py`: `6d096f2383a219741381f776c6199c27a9d73373f332b5a30f402ed5019d7784`;
- `calendar_esocial.py`: `87170d792ce32edd9722298ea04c4cfd314599d024094b97be4aed162ea7121c`;
- `central.py`: `1cfe73737fdd60ca0cd577e25087dc0a165da173583ee1b465bab1c54e7c6912`;
- `reprocessing.py`: `9c73b88473cf86d7dee307f1937163232595af17d6b6ef975e3991ae4f3eff33`;
- `esocial_engine.py`: `4f08325d70a4ee5c3b3baed9bc87d3ff4de9e6a4e072f4c06f627770a300736b`;
- `dominio_advanced.py`: `341c1135130315a49fb819fb2056f7900674fa70b8a9a63f6f3b5818372c6794`;
- teste específico: `2692f9a18f11ae73f80fcc9805489a772d9df4eb3e6636bd8d3af22351c2009c`.

## Estado

B31, B32 e B33 podem ser classificados como `CORRIGIDO_TESTADO` na cópia canônica recuperada.

Ainda não são `CORRIGIDO_HOMOLOGADO`: dependem da promoção da árvore reconciliada, migração controlada e homologação Windows/runtime final.
