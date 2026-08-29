# Checkpoint de execução — Auditoria Canônica V8

Data: 28/08/2026 21:39 (America/Sao_Paulo)
Branch: `audit-v8-runtime-reconciliation`

## Regra operacional

Todo trabalho da continuidade da Auditoria Canônica V8 deve ser persistido no repositório. Código, testes, contratos técnicos, evidências, correções de CI e decisões de implementação não devem permanecer apenas no chat ou em arquivos temporários.

A branch de trabalho permanece `audit-v8-runtime-reconciliation`. A `main` não deve receber alterações antes do fechamento técnico e validação do conjunto.

## Trabalho já persistido nesta continuidade

### CI e evidências

- Recuperação da trilha de `test_evidence` dos bloqueadores V8.
- CI ampliado para executar tooling e suítes funcionais V8 versionadas.
- Preflight V8 continua bloqueando release final enquanto existirem bloqueadores abertos.

### B01 — reprocessamento destrutivo

Foi localizado no pacote operacional V8C o defeito real: a implementação antiga salvava snapshot histórico e removia o registro vigente de `processamento_arquivo` antes de saber se o novo processamento era superior.

Correção persistida:

- `runtime_overlay/app/src/axiom_tools/modules/processing/reprocessing_candidate.py`
- `runtime_overlay/app/tests/modules/test_reprocessing_candidate_v8.py`

Novo comportamento:

1. a lógica destrutiva antiga executa somente em clone SQLite;
2. o banco vivo permanece intacto durante o reprocessamento;
3. o resultado do clone é registrado como candidato;
4. candidato regressivo é rejeitado;
5. promoção exige que a base não tenha mudado desde a geração do candidato;
6. a versão substituída é preservada no histórico;
7. a decisão do candidato é idempotente.

Caso de regressão Jair 449/450 coberto explicitamente: uma versão vigente `PROCESSADO 100%` não pode ser substituída por candidato `REVISAO 90%`.

### B03 — gate de saída

Persistido gate canônico de backend em:

- `runtime_overlay/app/src/axiom_tools/modules/processing/output_gate.py`
- `runtime_overlay/app/tests/modules/test_output_gate_v8.py`

O gate exige fechamento `FECHADA`, versão vigente válida e ausência de retificação `DETECTADA`. Seleções explícitas de documentos são revalidadas por cliente, competência e documento vigente.

### B42 — identidade de build/runtime

Persistido em:

- `runtime_overlay/app/src/axiom_tools/core/build_identity.py`
- `runtime_overlay/app/tests/core/test_build_identity_v8.py`

O runtime passa a consumir `build_provenance.json`, validar identidade do produto, commit, hashes e compatibilidade de schema. Também há payload operacional enxuto para health e registro estruturado de inicialização.

### B41/B42 — rollback e transição

Scripts de rollback foram ampliados para registrar e validar:

- identidade anterior;
- identidade alvo;
- versão da aplicação;
- versão de schema;
- commit.

Arquivos alterados:

- `scripts/create_rollback_bundle.py`
- `scripts/verify_rollback_bundle.py`
- `tests/test_rollback_identity_v8.py`

### B45 — escala

Persistidos índices de escala e testes de query plan:

- `runtime_overlay/app/src/axiom_tools/modules/closing/performance.py`
- `runtime_overlay/app/tests/modules/test_scale_indexes_v8.py`

O cenário sintético usa 1.000 clientes e 3.000 documentos e exige uso dos índices esperados pelo SQLite nos filtros operacionais principais.

## Fontes operacionais recuperadas da Biblioteca

Foram usados como referência técnica os pacotes históricos do próprio Axiom Tools, sem tratá-los como fonte canônica final de código:

- `AXIOM_TOOLS_REPROCESSAMENTO_INCREMENTAL_V5_6_14V8C_CORRIGIDO_20260827.zip`
- `AXIOM_TOOLS_REPROCESSAMENTO_INCREMENTAL_V5_6_14V8C_20260827.zip`
- `AXIOM_TOOLS_V5_6_14V8F2_CONSOLIDADO_20260827.zip`
- `AXIOM_TOOLS_RUNTIME_COMPETENCIA_V5_6_14V8E_20260827.zip`
- `AXIOM_TOOLS_COMPETENCIA_EXECUCAO_V5_6_14V8D_20260827.zip`
- `AXIOM_TOOLS_FLUXO_COMPETENCIA_V5_6_14V8B_20260827.zip`
- `AXIOM_TOOLS_RETIFICACAO_INTELIGENTE_V5_6_14V4_20260825.zip`

Esses pacotes servem para reconstruir a evolução do runtime e localizar a implementação operacional real. Não devem ser copiados cegamente sobre a V8 reconciliada.

## Limitação ainda aberta — B06

O snapshot canônico `Axiom_Tools(20260828-175237).zip` está preservado na Biblioteca, mas a materialização dos 399 MB para o ambiente de trabalho retornou 403. A reconciliação integral da árvore ainda não pode ser declarada concluída enquanto esse conteúdo não for comparado integralmente.

Pacotes menores já foram materializados e analisados para desbloquear correções pontuais.

## Estado de CI observado nesta continuidade

O run GitHub Actions `33221638848` concluiu com `success` após inclusão da proteção de reprocessamento candidato. O CI continua como gate obrigatório para novas correções.

## Próximas integrações obrigatórias

- integrar o mecanismo de candidato no `central.py` operacional, preservando o fluxo existente;
- concluir a reconciliação B06 da árvore canônica;
- integrar o gate B03 às rotas reais de Impressão, Entregas e saída automática;
- integrar identidade B42 ao startup/health do runtime final;
- medir B45 sobre árvore e banco reconciliados;
- concluir migração/schema e recuperação 449/450 com evidência no banco canônico;
- não promover bloqueador para homologado sem evidência de runtime físico quando exigida.
