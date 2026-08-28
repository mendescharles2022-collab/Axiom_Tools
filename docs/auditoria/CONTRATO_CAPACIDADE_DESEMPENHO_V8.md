# Contrato V8 — Capacidade, desempenho e escala operacional

Data: 28/08/2026
Status: **contrato de auditoria / benchmark ainda pendente na árvore reconciliada**

## 1. Motivo

A V7 já registrou limitação operacional: a tela de Fechamento Mensal ficou pesada para uma carteira superior a 600 clientes.

A V8 foi criada, entre outros motivos, para simplificar responsabilidades e reduzir carga operacional. A homologação precisa provar essa melhoria também em escala.

## 2. Escala de projeto

A solução deve ser dimensionada para crescimento da carteira e para centenas de documentos por etapa do fechamento.

O desenho não pode pressupor que todos os clientes/documentos caberão confortavelmente em uma única renderização, transação ou lote de memória.

## 3. Regras de consulta de tela

Listagens operacionais devem possuir, quando o volume justificar:

- paginação;
- busca;
- filtros aplicados no backend;
- ordenação determinística;
- limite explícito de registros por página;
- contagens agregadas calculadas sem carregar todas as linhas em memória;
- estado vazio claro;
- preservação de filtros durante navegação.

Não é aceitável renderizar centenas/milhares de registros completos apenas para esconder parte deles via JavaScript.

## 4. Fechamento Mensal

Deve ser painel de acompanhamento, não tela que pré-calcula toda a Conferência.

Ao abrir:

- consultar estado mensal persistido/agregado;
- evitar executar parsers;
- evitar recompor conferência inteira;
- evitar varredura de documentos;
- evitar carregar históricos completos por cliente.

Detalhes devem ser buscados sob demanda.

## 5. Processamento

Deve operar em ciclos/lotes e manter checkpoints.

Regras:

- nenhuma competência grande deve depender de uma única transação longa;
- lote deve ser retomável;
- reprocessar um subconjunto não deve revarrer tudo sem necessidade;
- hash/cache devem impedir processamento idêntico inútil;
- concorrência deve ser controlada para não saturar CPU, disco ou SQLite;
- OCR é fallback, não caminho padrão;
- leitura nativa ocorre uma vez e é reutilizada pelos especialistas.

## 6. Ordem operacional

O orquestrador deve respeitar a sequência funcional vigente da competência e não disparar todas as fontes indiscriminadamente.

A consulta eConsignado usa apenas o universo da competência/chamada; os motores documentais processam apenas evidências elegíveis; o cruzamento final deve ser incremental conforme os componentes ficam prontos.

## 7. Conferência

A tela deve trabalhar com clientes efetivamente em conferência e carregar detalhes sob demanda.

Não deve:

- incluir fechados na mesa viva;
- incluir chamada futura;
- recalcular todos os clientes ao abrir;
- carregar todos os documentos históricos de todos os clientes na mesma resposta.

## 8. Impressão e Entregas

Geração em lote deve possuir limites e processamento controlado.

Regras:

- compor lote após gate de autorização;
- não manter centenas de PDFs inteiros simultaneamente em memória se houver alternativa streaming/temporária segura;
- preservar ordem A-Z e rastreabilidade;
- falha em um item não deve exigir regenerar itens já válidos quando tecnicamente evitável;
- arquivos temporários precisam de ciclo de vida controlado.

## 9. Banco SQLite

Consultas de alta frequência devem ser sustentadas por índices coerentes com os filtros reais da operação.

Índices candidatos precisam ser verificados para:

- competência + status + chamada;
- cliente + competência;
- documento + cliente + competência + tipo;
- obrigação + cliente + competência + fonte;
- jobs por competência/status;
- histórico por entidade/data.

A auditoria deve usar `EXPLAIN QUERY PLAN` nos caminhos críticos depois da árvore/schema estarem reconciliados.

## 10. N+1 e consultas repetidas

Rotas de listagem não podem executar uma consulta por cliente para obter cada KPI/documento quando uma consulta agregada ou preload controlado resolver.

A regressão deve instrumentar a quantidade de queries dos endpoints críticos.

## 11. Benchmarks funcionais mínimos

A homologação deve incluir cenários representativos de:

- centenas de clientes na competência;
- centenas de documentos Domínio;
- centenas de guias/arquivos das demais fontes;
- múltiplas páginas de listagem;
- reprocessamento seletivo;
- mudança de chamada em lote;
- geração de lote de impressão/entrega.

O objetivo não é perseguir um número artificial de milissegundos, e sim provar ausência de crescimento explosivo, travamento de UI, timeout ou consumo desnecessário de memória.

## 12. Métricas a coletar

- tempo de resposta de listagens principais;
- número de queries SQL por endpoint;
- tempo de processamento por etapa;
- throughput de documentos/minuto;
- tamanho de fila;
- uso aproximado de memória do worker;
- quantidade de OCR acionados;
- hits de hash/cache;
- tempo de geração de lotes;
- ocorrências de `database is locked`/timeout.

## 13. Critérios de aceite

1. Fechamento com centenas de clientes permanece navegável;
2. filtros e paginação acontecem no backend;
3. Processamento retoma por checkpoint;
4. reprocessamento seletivo não reexecuta universo inteiro;
5. eConsignado não consulta cadastro histórico global;
6. Conferência abre sem recomputar ciclo inteiro;
7. rotas críticas não apresentam padrão N+1 evidente;
8. SQLite utiliza índices nos filtros principais;
9. impressão/entrega em lote não causa pico descontrolado de memória;
10. falha em um item é isolável e auditável.
