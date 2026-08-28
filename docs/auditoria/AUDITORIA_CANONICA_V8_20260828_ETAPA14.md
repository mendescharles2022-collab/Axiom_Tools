# Auditoria canônica V8 — Etapa 14

Data: 28/08/2026
Status: **auditoria em andamento / sem pacote final**

## 1. Escopo

Esta etapa tratou capacidade, escala, paginação, carga de banco e comportamento em lotes.

## 2. Evidência de origem

A V7 estável registrou que o Fechamento Mensal ficou operacionalmente pesado para carteira acima de 600 clientes. Essa limitação foi uma das razões para a redistribuição de responsabilidades na V8.

Logo, desempenho não é otimização opcional: faz parte do problema funcional que a V8 deve resolver.

## 3. Contrato criado

Foi criado `CONTRATO_CAPACIDADE_DESEMPENHO_V8.md`.

O contrato exige:

- paginação e filtros no backend;
- ausência de renderização massiva escondida por JS;
- Fechamento sem recomputar Conferência;
- Processamento em lotes/checkpoints;
- reprocessamento seletivo;
- hash/cache;
- OCR somente fallback;
- eConsignado limitado ao universo mensal;
- Conferência carregando apenas trabalho vivo;
- geração de impressão/entrega com memória controlada;
- índices SQLite coerentes;
- análise de N+1;
- coleta de métricas de execução.

## 4. Critérios técnicos para a regressão

Quando a árvore operacional estiver reconciliada:

1. instrumentar número de queries dos endpoints principais;
2. usar `EXPLAIN QUERY PLAN` nos filtros de competência/status/chamada;
3. medir abertura do Fechamento com carteira representativa;
4. medir paginação/busca de Processamento e Pendências;
5. medir reprocessamento seletivo;
6. medir lote de impressão/entrega;
7. registrar memória aproximada do worker;
8. registrar ocorrências de lock/timeout SQLite.

## 5. Proibições

- considerar uma tela 'rápida' se ela carrega tudo e só pagina no navegador;
- consultar todos os clientes para eConsignado por conveniência;
- recalcular toda a competência ao abrir Conferência;
- iniciar OCR sem necessidade;
- manter PDFs massivos simultaneamente em memória sem justificativa;
- corrigir desempenho removendo histórico, auditoria ou rastreabilidade.

## 6. Estado

Nenhum benchmark da V8 foi homologado nesta etapa porque a árvore integral do runtime ainda não está disponível nesta sessão.

O contrato de desempenho passa a integrar os critérios obrigatórios do pacote final.
