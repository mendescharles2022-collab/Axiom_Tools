# Auditoria canônica V8 — Etapa 25

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo desta etapa

A Etapa 25 aprofundou três bloqueadores já presentes na matriz canônica:

- B02 — Central de Conferência com efeito colateral de escrita;
- B03/B39 — autorização inconsistente de saídas e bypass por seleção manual;
- B18/B36 — decisão global de Conferência insuficiente e migração necessária para decisão por fonte.

Nenhum deles foi marcado como corrigido.

## 2. Conferência somente leitura

A auditoria do ZIP canônico já havia confirmado que a montagem da Conferência chama sincronização de fechamento durante a própria consulta.

Foi criado `docs/architecture/CONTRATO_CONFERENCIA_EVENT_DRIVEN_V8.md`.

Regra consolidada:

- GET/read, busca, paginação, filtro e abertura de detalhe não podem alterar banco de negócio;
- fechamento automático é consequência de evento persistido, não de navegação;
- recálculo deve receber explicitamente cliente, competência, causa e correlation_id;
- repetição do mesmo evento deve ser idempotente;
- escrita concorrente deve validar revisão/estado esperado.

### Regressão obrigatória

Abrir e navegar repetidamente na Conferência sobre cópia real do banco deve produzir zero delta em fechamento, versões, retificações, decisões e histórico de negócio.

## 3. Gate único de saídas

As evidências históricas reforçam que o problema V8 é regressão:

- V4 bloqueava saída automática durante retificação pendente;
- V7 liberava Impressão e Entregas a partir de `FECHADA`;
- V8 auditada possui caminhos que usam `PROCESSADO`, seleção manual ou proteção apenas visual/listagem.

Foi criado `docs/architecture/CONTRATO_GATE_UNICO_SAIDAS_V8.md`.

Regra consolidada:

`FECHADA + versão vigente válida + ausência de retificação material pendente`

é a condição mínima de autorização operacional quando a competência participa do Fechamento Mensal.

Toda saída — individual, selecionada, lote ou automática — precisa passar pelo mesmo serviço de backend.

IDs enviados pelo navegador são seleção, nunca autorização.

## 4. Decisão por fonte

A V7 permitia decisão manual `Conferido/Justificado` em nível global suficiente para concluir ciclo.

Os casos reais de agosto demonstraram que a V8 precisa de granularidade por obrigação.

Foi criado `docs/architecture/CONTRATO_DECISAO_POR_FONTE_V8.md`.

A chave passa a ser equivalente a:

`competencia + cliente + obrigacao + componente opcional`

Assim, uma decisão sobre DARF não resolve implicitamente FGTS, DAE ou eConsignado.

A situação do cliente passa a ser derivada dos estados das obrigações.

## 5. Migração do legado de decisão manual

A busca desta etapa não recuperou com evidência suficiente a tabela/colunas exatas que persistem as decisões manuais globais do runtime V7/V8.

Portanto:

- não será inventado schema legado;
- B36 permanece `CONTRATO_OBRIGATORIO` + inspeção de banco/runtime;
- uma decisão global antiga não poderá ser replicada automaticamente para todas as fontes;
- decisões ambíguas devem ser preservadas como legado/revisão, sem fabricar justificativas.

## 6. Relação com snapshots/retificação

A decisão por fonte que participou de um fechamento precisa estar representada no snapshot da versão vigente.

Uma saída deve apontar para essa versão.

Se decisão/evidência posterior provocar mudança material:

- preservar a versão antiga;
- criar retificação candidata;
- bloquear novas saídas;
- somente nova versão concluída volta a autorizar saída operacional.

## 7. Estado dos bloqueadores ao final da etapa

- B02 — `CONFIRMADO_RUNTIME`, não corrigido;
- B03 — `REGRESSAO_CONFIRMADA`, não corrigido;
- B18 — `CONTRATO_OBRIGATORIO`, não implementado/homologado;
- B36 — migração do legado ainda exige inspeção do banco reconciliado;
- B39 — bypass por IDs continua bloqueador de backend.

## 8. Próxima frente

A próxima etapa deve aprofundar o eConsignado e sua relação com:

- universo mensal/chamada;
- vínculo ativo/desligamento;
- afastamento/remuneração;
- rescisão/garantias;
- idempotência de API;
- falso `CONFERIDO`;
- persistência de fotografia da consulta.
