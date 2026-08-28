# Protocolo de benchmark operacional — V8

Data: 28/08/2026
Status: **protocolo de homologação / execução pendente no runtime reconciliado**

## 1. Objetivo

Provar que a V8 suporta a carteira e os volumes documentais reais sem depender de renderização integral, varreduras globais, transações longas ou crescimento explosivo de consultas/memória.

O benchmark não substitui a regressão funcional dos 28 casos.

## 2. Perfis de carga

### Perfil A — operação atual representativa

Preparar cenário com aproximadamente:

- 700 clientes cadastrados;
- 300–400 participantes no ciclo mensal conforme elegibilidade;
- 500+ recibos/contracheques;
- 400+ relatórios/extratos Domínio;
- ~180 evidências/arquivos FGTS;
- 300–400 documentos/consultas DARF/e-CAC;
- consultas eConsignado restritas ao universo da competência/chamada.

### Perfil B — crescimento

Preparar cenário com pelo menos:

- 1.000 clientes cadastrados;
- composição mensal proporcionalmente maior;
- 1,5x a 2x o volume documental do Perfil A;
- múltiplas matrículas/filiais/CAEPFs;
- reprocessamentos seletivos simultâneos a navegação normal.

O objetivo do Perfil B é revelar crescimento não linear antes que a carteira real alcance esse patamar.

## 3. Endpoints/telas críticos

Medir pelo menos:

- Fechamento Mensal — lista/paginação/busca/filtros;
- Processamento — sessões/fila/pendências técnicas;
- Central de Conferência — lista e detalhe;
- Retificações;
- Central de Entregas;
- Centro de Impressão;
- ficha de cliente;
- dashboard apenas nos indicadores que consultem essas bases.

## 4. Métricas de consulta

Por endpoint:

- tempo total;
- quantidade de queries SQL;
- linhas retornadas;
- paginação aplicada no banco ou em memória;
- consultas repetidas idênticas;
- existência de N+1;
- plano de consulta (`EXPLAIN QUERY PLAN`) nos SQLs críticos;
- uso dos índices previstos.

Não fixar meta artificial de milissegundos antes da medição-base. Primeiro comparar comportamento e crescimento entre perfis.

## 5. Métricas do worker

Por etapa:

- documentos processados/minuto;
- tempo médio e p95 aproximado por arquivo;
- quantidade de leitura nativa;
- quantidade de OCR fallback;
- hits de hash/cache;
- falhas técnicas;
- retries;
- tempo parado aguardando locks;
- tamanho máximo de fila;
- memória aproximada do processo.

## 6. Reprocessamento seletivo

Cenários:

- 1 arquivo;
- 10 arquivos;
- 50 arquivos;
- todos os documentos pendentes de um único cliente;
- pequeno conjunto de clientes.

Provar que nenhum cenário pequeno revarre desnecessariamente toda a competência ou toda a carteira.

## 7. Conferência

Abrir a Central deve:

- consultar apenas o universo vivo;
- paginar;
- não carregar histórico/documentos completos de todos os clientes;
- não recalcular o ciclo inteiro;
- não escrever no banco durante navegação.

Medir abertura de lista e abertura de detalhe separadamente.

## 8. eConsignado

O número de empregadores consultados deve corresponder ao universo autorizado do job, não à carteira histórica.

O benchmark deve registrar:

- universo previsto;
- universo realmente enviado à consulta;
- excluídos por chamada/sem movimento/não aplicabilidade;
- retries.

Qualquer expansão silenciosa do universo é falha funcional e de desempenho.

## 9. Impressão/Entregas

Testar lotes de tamanhos crescentes.

Observar:

- tempo de autorização pelo gate;
- tempo de geração;
- memória;
- uso de temporários;
- isolamento de falha por item;
- possibilidade de retomada sem regenerar tudo desnecessariamente.

## 10. Concorrência operacional

Simular simultaneamente:

- usuário navegando Fechamento/Conferência;
- worker processando lote;
- consulta eConsignado;
- geração de pequeno lote de saída.

Registrar:

- `database is locked`;
- timeout;
- espera excessiva;
- escrita obsoleta rejeitada;
- responsividade das telas.

## 11. Critérios de reprovação imediata

Reprovar se houver:

- carregamento integral da carteira em tela paginada;
- filtro aplicado apenas via JavaScript após buscar tudo;
- N+1 explosivo por cliente/documento;
- reprocessamento de pequeno conjunto disparando varredura global;
- eConsignado consultando carteira histórica fora do ciclo;
- Conferência recalculando todos ao abrir;
- centenas de PDFs completos mantidos simultaneamente em memória sem necessidade;
- locks/timeouts recorrentes;
- degradação superlinear evidente entre Perfil A e B.

## 12. Evidência final

Salvar relatório por build contendo:

- commit/build/schema;
- máquina/ambiente Windows usado;
- tamanho da base;
- volumes por tipo;
- métricas dos endpoints;
- métricas dos workers;
- query plans principais;
- ocorrências de lock/erro;
- comparação Perfil A × Perfil B;
- conclusão `PASS/FAIL` por cenário.

## 13. Homologação

B45 só pode receber `CORRIGIDO_HOMOLOGADO` depois dessa bateria rodar sobre a mesma árvore que será empacotada e instalada.
