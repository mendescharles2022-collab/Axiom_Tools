# Auditoria canônica V8 — Etapa 20

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Esta etapa aprofundou a relação entre:

- fechamento automático;
- snapshot/versionamento;
- materialidade de retificação;
- banco SQLite;
- autorização de impressão/entrega/saída.

## 2. Evidência histórica e de runtime recuperada

A V5.6.14V4 já implementava:

- snapshot versionado por cliente + competência;
- `fechamento_mensal_versao`;
- `fechamento_mensal_retificacao`;
- `versao_atual`;
- backfill de snapshot V1 para fechamentos existentes;
- detecção de mudança material;
- preservação da versão anterior;
- bloqueio de saída durante retificação.

Logs da instalação real mostram `retification.py` com consulta específica para localizar registros `status='FECHADA'` sem versão correspondente.

Conclusão: `FECHADA` sem versão nunca deve ser tratada como estado operacional válido.

## 3. Contrato de snapshot e saídas

Foi criado `CONTRATO_SNAPSHOT_FECHAMENTO_SAIDAS_V8.md`.

Regra central:

```text
FECHADA
não é suficiente para autorizar saída.
```

A saída precisa estar ligada a uma `versao_fechamento` vigente e auditável.

Quando houver retificação material:

- versão antiga permanece histórica;
- novas saídas ficam bloqueadas;
- conclusão cria Vn+1;
- novas saídas passam a referenciar Vn+1.

## 4. Materialidade

Foi criado `CONTRATO_MATERIALIDADE_RETIFICACAO_V8.md`.

Nova evidência deve ser classificada como:

- `SEM_MUDANCA`;
- `COMPLEMENTAR_NAO_MATERIAL`;
- `MUDANCA_MATERIAL`;
- `INDETERMINADA_REVISAO`.

Arquivo novo, isoladamente, não cria retificação.

## 5. Casos reais aplicados à materialidade

### Jair Ferreira Camargo

Segundo Extrato com matrícula econômica adicional e FGTS que leva o total para R$ 389,04 é material se a versão vigente considerar apenas uma matrícula.

O federal R$ 511,43 permanece uma única obrigação consolidada.

### Leosmar Teodoro de Sousa

Segundo Extrato equivalente não deve criar retificação apenas por ser outro arquivo.

### Alex Douglas de Andrade

Contexto rescisório pode mudar a aplicabilidade do FGTS mensal sem eliminar automaticamente a DARF previdenciária.

### MEI/DAE

Trocar falsa expectativa genérica de GFD pela obrigação DAE correta é mudança material da natureza da obrigação.

## 6. Invariantes do banco

Foi criado `INVARIANTES_BANCO_FECHAMENTO_VERSIONADO_V8.md`.

Entre as invariantes obrigatórias:

- FECHADA possui versão;
- `versao_atual` aponta para versão existente;
- versões são monotônicas;
- versão histórica é imutável;
- uma retificação aberta por cliente/competência;
- RETIFICACAO possui versão base;
- concluir retificação cria nova versão atomicamente;
- saída aponta para versão válida;
- versão/retificação órfã é inválida.

## 7. Piso de homologação já existente

A V4 validou em cópia real:

- backfill de snapshots;
- mudança material;
- repetição sem retificação;
- conclusão com nova versão;
- bloqueio de saída durante retificação.

A V8 não pode ser homologada com garantias inferiores.

## 8. Impacto na matriz de bloqueadores

Esta etapa reforça principalmente:

- B01 — reprocessamento destrutivo;
- B03 — gate único de saída;
- B04 — versão/retificação vigente;
- B05 — migração V8;
- B10 — fluxo próprio de retificação;
- B35 — invariantes do banco;
- B40 — concorrência lógica;
- B41 — backup/rollback.

## 9. Provas ainda necessárias no runtime reconciliado

1. consulta de FECHADA sem versão retorna zero;
2. `versao_atual` inválida retorna zero;
3. versão duplicada/órfã retorna zero;
4. retificação aberta duplicada retorna zero;
5. saída em cliente FECHADA sem versão é recusada;
6. saída durante RETIFICACAO é recusada;
7. conclusão de Vn+1 preserva Vn e libera nova saída apenas para Vn+1;
8. nova evidência não material não cria retificação falsa.

## 10. Estado final

Nenhum desses pontos está marcado como `CORRIGIDO_HOMOLOGADO`.

A auditoria continua. Nenhum pacote final está autorizado.
