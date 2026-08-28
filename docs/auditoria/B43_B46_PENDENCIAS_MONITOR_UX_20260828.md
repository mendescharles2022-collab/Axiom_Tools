# B43/B46 — Pendências e Auditoria do Processamento

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## B43 — Pendências orientadas pela competência

O backend já herdava a competência ativa do Processamento quando o usuário não informava o filtro. O problema remanescente era de prioridade operacional na interface.

Correções:

- a competência passa a ser o primeiro eixo visual/filtro;
- a tela mostra se o escopo corresponde à competência ativa do Fechamento ou a uma consulta histórica;
- a busca por cliente/arquivo e motivo da pendência permanecem primárias;
- a chave PROC foi movida para `Filtros avançados`;
- a linha principal do documento não começa mais pela PROC;
- a PROC continua disponível no detalhe expandido e para rastreabilidade;
- o botão de limpeza volta à competência ativa em vez de induzir o usuário a reconstruir manualmente o escopo.

A mudança não remove a chave PROC nem reduz auditoria técnica; apenas deixa de tratá-la como eixo operacional do trabalho mensal.

## B46 — Monitor/Auditoria sem dupla verdade

A tela de Auditoria passa a declarar explicitamente a separação de responsabilidades:

- `Execução` = acompanhamento ao vivo, blocos, arquivos, etapas e percentual;
- `Pendências` = revisão documental e extrações incompletas;
- `Auditoria` = histórico técnico, reprocessamentos, arquivamento e saídas.

Correções:

- Revisão e Incompletos saem dos KPIs principais da Auditoria e viram encaminhamento para Pendências;
- Erros técnicos permanecem no resumo principal;
- detalhes de motores/pipeline ficam em bloco técnico secundário expansível;
- competência/cliente/situação passam a ser os filtros primários da atividade histórica;
- PROC e paginação ficam no bloco avançado;
- a coluna principal usa Competência; PROC continua exibida como detalhe de rastreabilidade do arquivo;
- rótulos de situação usam apresentação amigável, sem expor o código cru como eixo da interface.

## Evidência de testes

Teste versionado:

`runtime_overlay/app/tests/modules/test_processing_pending_monitor_ux_v8.py`

Resultados na cópia canônica:

- 7/7 testes específicos PASS;
- bateria não-web executável neste ambiente: 259/259 PASS;
- 0 failures;
- 0 errors;
- 0 skips.

A suíte HTTP completa continua reservada para o ambiente com Flask/Flask-WTF/Windows usado na homologação final.

## Estado

B43 e B46 podem ser classificados como `CORRIGIDO_TESTADO` na árvore canônica reconciliada.

Ainda não são `CORRIGIDO_HOMOLOGADO`: falta ensaio visual/runtime Windows e promoção da árvore final.
