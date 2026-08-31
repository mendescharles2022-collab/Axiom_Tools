# Auditoria canônica V8 — Etapa 45

Data: 31/08/2026  
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Continuação da reconstrução histórica por deltas preservados, agora com foco no B03 — gate único de autorização de Impressão/Entregas.

Foram inspecionados especialmente:

- V5.6.14V — Consolidação Operacional;
- V5.6.14V1 — Ajustes Operacionais;
- V5.6.14V3A — Entregas, Impressão e Inscrições;
- deltas posteriores já materializados até V5.6.14V8F2.

## 2. Regra canônica B03

O contrato V8 exige que toda saída final passe por um único gate de backend e que a autorização seja baseada, no mínimo, em:

`competencia + cliente_id + fechamento_versao_id + tipo_saida`

`PROCESSADO` significa sucesso técnico de processamento e não autorização operacional.

## 3. Central de Entregas — defeito estrutural confirmado

### Serviço de entrega

No `modules/delivery/service.py` preservado em V3A, `_docs_cliente(...)` seleciona documentos com a condição:

`p.status='PROCESSADO'`

além de vigência e tipos documentais aplicáveis.

`gerar_cliente(...)`:

- valida parametrização de entrega eletrônica;
- chama `_docs_cliente(...)`;
- gera/copía os PDFs e manifesto;
- registra `processamento_entrega_historico`.

O serviço não exige:

- cliente `FECHADA`;
- versão vigente do fechamento;
- ausência de retificação material;
- versão de fechamento vinculada à saída.

Logo a camada de serviço trata `PROCESSADO` como suficiente para gerar entrega.

## 4. V3A tentou restringir a listagem, mas não o backend

O `delivery_views.py` do V3A adiciona integração com Fechamento Mensal na **listagem**:

- `_escopo(...)` detecta se existe fechamento;
- para escopo `FECHADOS`, obtém `clientes_fechados_ids(...)`;
- a página GET usa esses IDs ao chamar `listar_clientes(...)`.

Isso melhora a projeção visual, mas não constitui autorização.

### POST individual

`POST /entregas/gerar-cliente/<cliente_id>` chama diretamente:

`gerar_cliente(con, ..., cliente_id, competencia)`

sem recalcular/intersectar o `cliente_id` com o conjunto de clientes fechados.

### POST selecionados

`POST /entregas/gerar-selecionados` recebe IDs do formulário e chama `gerar_cliente(...)` para cada ID.

Também não intersecta a seleção recebida com o universo autorizado de fechamento.

### POST competência

O fluxo de geração por competência passa por `_escopo(...)` e é mais restritivo, mas a existência de rotas individual/selecionados sem o mesmo gate já viola a exigência de autorização única.

## 5. Evolução histórica do defeito

No pacote V5.6.14V, a Central de Entregas ainda não possuía integração com `clientes_fechados_ids(...)`.

No V3A, a integração com fechados foi adicionada na camada de view/listagem, mas o serviço continuou usando documento `PROCESSADO` como critério de geração.

Portanto o desenho evoluiu de:

`sem filtro de fechamento`

para:

`filtro visual/parcial de fechamento`

sem completar a etapa necessária:

`gate obrigatório no serviço de backend`.

Esse histórico explica por que a interface podia aparentar restringir a entrega enquanto ações diretas/POST ainda tinham caminho de bypass.

## 6. Centro de Impressão — seleção continua sendo filtro, não autorização

No `printing_views.py` V3A:

- `_clientes_conferencia(...)` deriva IDs com base em status de Conferência;
- a tela GET usa esse filtro quando solicitado;
- o POST de lote recebe `selecionados` diretamente do formulário;
- os IDs são encaminhados ao serviço `gerar_lote_impressao(...)`.

No V8F2, o `documents_views.py` mantém padrão semelhante no Centro de Impressão incorporado:

- recebe `selecionados` do front;
- opcionalmente calcula `cliente_ids` por filtro de Conferência;
- chama `gerar_lote_impressao(...)`.

A presença de filtro de Conferência não equivale ao gate canônico `FECHADA + versão vigente + sem retificação`.

Além disso, como já registrado na Etapa 44, o próprio helper de filtro de Conferência pode acionar B02 por chamar o agregador mutável.

## 7. Persistência após V3A

Nos deltas materializados V4, V6, V7, V8, V8A, V8B, V8C, V8D, V8E, V8F e V8F2 não foi encontrada substituição posterior de `modules/delivery/service.py` que introduzisse o gate único exigido.

Isso é consistente com a auditoria canônica de 28/08, que já registrava B03 como regressão confirmada.

## 8. Diagnóstico B03

A causa arquitetural está suficientemente isolada:

1. autorização foi espalhada por filtros de UI/view;
2. serviços de geração continuaram capazes de operar com critérios técnicos (`PROCESSADO`) ou IDs recebidos;
3. não existe prova de um serviço central único de autorização por versão de fechamento;
4. consumidores diferentes aplicam filtros diferentes.

B03 permanece `PRONTO_PARA_CORRIGIR`.

## 9. Direção de correção

Quando B06 liberar a árvore operacional:

1. criar gate único de backend;
2. obrigar Entregas, Impressão e Saídas automáticas a usá-lo;
3. nunca confiar em `cliente_ids`/document IDs do front como autorização;
4. cruzar seleção com universo autorizado no backend;
5. vincular toda saída à versão de fechamento vigente;
6. bloquear `PRONTA`, `RETIFICACAO`, documento apenas `PROCESSADO` e versão ausente;
7. preservar reimpressão histórica somente por fluxo explícito/versionado;
8. adicionar regressões de bypass por POST direto.

## 10. Estado

Nenhum bloqueador é promovido nesta etapa.

A V8 permanece **NÃO HOMOLOGADA**.
