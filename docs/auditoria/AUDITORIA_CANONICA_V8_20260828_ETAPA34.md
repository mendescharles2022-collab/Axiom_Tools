# Auditoria canônica V8 — Etapa 34

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 34 consolidou B45 — capacidade/desempenho — e transformou o contrato já existente em protocolo de benchmark reproduzível.

## 2. Evidência já confirmada

A V7 registrou que o Fechamento Mensal ficou operacionalmente pesado em carteira superior a 600 clientes.

A auditoria V8 também comprovou uma varredura desnecessária no eConsignado: universo de consulta maior que a composição mensal real.

Esses dois fatos mostram que desempenho e escopo funcional estão ligados.

## 3. Contrato existente preservado

`CONTRATO_CAPACIDADE_DESEMPENHO_V8.md` continua como regra canônica:

- paginação/filtro no backend;
- detalhes sob demanda;
- sem recomputar Conferência inteira ao abrir tela;
- processamento em lotes/checkpoints;
- reprocessamento seletivo;
- índices coerentes;
- inspeção de query plan;
- evitar N+1;
- memória controlada em impressão/entregas.

## 4. Protocolo criado

Foi criado `PROTOCOLO_BENCHMARK_OPERACIONAL_V8.md` com dois perfis:

- operação atual representativa;
- crescimento de carteira/volume.

O benchmark mede endpoints, queries SQL, workers, OCR fallback, cache/hash, fila, memória, locks, geração de lotes e concorrência operacional.

## 5. Critério importante

Não será definida meta artificial de milissegundos antes da medição-base.

O que será reprovado imediatamente:

- crescimento explosivo;
- carregamento integral para depois filtrar no browser;
- N+1 evidente;
- reprocessamento pequeno revarrendo tudo;
- eConsignado fora do ciclo;
- Conferência recomputando universo ao abrir;
- locks/timeouts recorrentes;
- memória descontrolada em lotes.

## 6. Estado do B45

B45 permanece `CONFIRMADO_RUNTIME` quanto à limitação histórica de escala e `TESTE_PENDENTE_RUNTIME` quanto ao desempenho da implementação final V8.

Nenhum benchmark foi executado nesta sessão porque a árvore runtime canônica ainda não está reconciliada/disponível integralmente.

## 7. Próxima frente

Consolidar o protocolo de migração, integridade SQLite e rollback de atualização antes de qualquer pacote final.
