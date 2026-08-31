# Auditoria canônica V8 — Etapa 44

Data: 31/08/2026  
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Reconstrução parcial da evolução operacional por pacotes incrementais preservados no acervo, com foco em B02 e B08.

Foram materializados e inspecionados, sem banco real e sem documentos de clientes:

- V5.6.14V6 — Fechamento por competência;
- V5.6.14V7 — Ciclo/fechamento automático;
- V5.6.14V8;
- V5.6.14V8A;
- V5.6.14V8B;
- V5.6.14V8C corrigido;
- V5.6.14V8D;
- V5.6.14V8E;
- V5.6.14V8F runtime fix/direto;
- V5.6.14V8F2 consolidado.

Esses pacotes são deltas e não substituem a reconciliação integral B06, mas permitem rastrear a introdução e persistência de determinadas regressões.

## 2. B02 — ponto de introdução isolado

### V6

O `conference.py` do pacote V5.6.14V6 não contém chamada a `sincronizar_resultados_conferencia(...)` dentro de `conferencia_competencia(...)`.

### V7

O pacote V5.6.14V7 introduz o fechamento automático no serviço de fechamento e passa a importar/chamar `sincronizar_resultados_conferencia(...)` dentro da própria montagem da Conferência.

A chamada aparece ao final de `conferencia_competencia(...)`.

### V8B e V8F2

O mesmo padrão permanece:

- V8B: `conferencia_competencia(...)` continua chamando `sincronizar_resultados_conferencia(...)`;
- V8F2: idem.

### Conclusão histórica

A regressão B02 foi introduzida no salto **V6 → V7**, quando o fechamento automático foi acoplado ao agregador usado também pelas telas GET.

O problema não é a existência do fechamento automático em si. O defeito é o **gatilho**: a sincronização foi posicionada dentro de uma função de projeção/leitura reutilizada por rotas GET.

A correção correta permanece a prevista no contrato event-driven V8:

- Conferência somente leitura;
- recálculo/fechamento automático acionado somente após evento persistido;
- idempotência e escopo `competencia + cliente_id + causa + correlation_id`.

## 3. B02 tem superfície maior do que a Central de Conferência

A inspeção da cadeia V8A → V8F2 mostra que o mesmo agregador mutável é reutilizado em outras telas de leitura.

### Fechamento Mensal GET

`closing_views.py`, rota GET `/fechamento-mensal/`, quando a aba é `controle`, chama `conferencia_competencia(...)` para montar `conferencia_map`.

Logo, abrir o Fechamento Mensal pode alcançar a mesma sincronização automática de fechamento.

Os pacotes V8B, V8C, V8D, V8E, V8F e V8F2 inspecionados não substituem `closing_views.py`; portanto não há evidência nesses deltas de que esse acoplamento tenha sido removido depois de V8A.

### Centro de Impressão GET

No `documents_views.py` do V8F2, `_clientes_impressao_conferencia(...)` chama `conferencia_competencia(...)` para derivar IDs quando existe filtro de Conferência.

A rota GET `/processamento/impressao` usa esse helper.

Portanto até uma consulta/filtro do Centro de Impressão pode alcançar o caminho mutável de B02.

### Efeito de arquitetura

B02 não é apenas “uma tela de Conferência que grava”. É um **agregador de leitura contaminado por efeito colateral**, reutilizado por múltiplas superfícies.

Isso reforça também:

- B37 — máquinas de estado misturadas;
- B46 — monitor/superfícies operacionais confusas;
- B03 — necessidade de separar autorização de saída da simples projeção de Conferência.

Não cria novo bloqueador.

## 4. B08 — investigação T L / 2ª chamada avançou, mas causa exata ainda não fechou

O caso canônico confirma:

- T L Empreendimentos Agrícolas foi configurada para 2ª chamada;
- apareceu indevidamente na 1ª chamada;
- enquanto a chamada atual for 1, deve permanecer fora do universo operacional.

### Serviço V8B completo recuperado

A inspeção integral de `modules/closing/service.py` do V8B permite eliminar algumas hipóteses.

#### `sincronizar_clientes_ativos(...)`

Usa `INSERT OR IGNORE` e só cria novos registros como `PRONTA`, chamada 1.

Não sobrescreve linha já existente `ADIADA`, chamada 2.

#### `aplicar_classificacao_cadastral(...)`

Seleciona somente linhas `status='PRONTA'` sem impedimento/fechamento.

Não transforma `ADIADA` em `PRONTA`.

#### `sincronizar_resultados_conferencia(...)`

Antes de fechar cliente, exige `status == 'PRONTA'`.

Ignora `ADIADA`.

Portanto o fechamento automático que explica B02 não explica, por si só, a reversão de T L.

#### `abrir_proxima_chamada(...)`

Converte `ADIADA` em `PRONTA` somente quando a chamada é explicitamente avançada e a linha tem chamada compatível com a nova chamada.

#### `liberar_clientes(...)`

É a rota explícita capaz de recolocar clientes selecionados em `PRONTA` na chamada atual.

### Migrações V7/V8/V8A

- V7 corrige herança indevida de `SEM_MOVIMENTO` e não altera `ADIADA` para `PRONTA`;
- V8/V8A trabalham apenas linhas `PRONTA` para relação operacional/movimento e não reabrem `ADIADA`.

### Resultado B08

A inspeção reduz o espaço causal:

- não há evidência, nos serviços/migrações recuperados, de uma sincronização genérica que transforme automaticamente `ADIADA/chamada 2` em `PRONTA/chamada 1`;
- as rotas explícitas de liberação/avanço continuam candidatas;
- também permanecem possíveis um estado que nunca foi persistido como `ADIADA`, código externo não recuperado ou operação sobre snapshot/configuração diferente.

Por isso B08 **permanece `INSPECAO_PENDENTE`**. A auditoria agora sabe, contudo, quais caminhos já podem ser descartados e quais precisam ser rastreados.

## 5. Consequência para a correção

B02 está suficientemente isolado para implementação assim que a árvore operacional canônica for reconciliada:

1. tornar `conferencia_competencia(...)` pura;
2. remover qualquer `commit`/sincronização de fechamento do caminho de leitura;
3. criar/usar agregador mutável por evento;
4. atualizar consumidores de Processamento, Fechamento e Impressão;
5. regressão banco antes/depois de 10 GETs;
6. testar evento real e idempotência.

B08 não deve receber correção especulativa antes de fechar o ponto de reversão.

## 6. Estado

Nenhum bloqueador é promovido nesta etapa.

A V8 permanece **NÃO HOMOLOGADA** e B06 continua sendo o gate para incorporar código operacional corrigido no `main` com segurança.
