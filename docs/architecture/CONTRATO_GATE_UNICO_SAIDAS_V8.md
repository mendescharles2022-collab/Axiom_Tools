# Contrato V8 — Gate único de autorização de saídas

Data: 28/08/2026
Status: **contrato obrigatório / regressão confirmada / V8 não homologada**

## 1. Fundamento

A V4 já bloqueava saídas automáticas enquanto uma retificação estivesse pendente.

A V7 já estabelecia que Impressão e Entregas seriam liberadas a partir de `FECHADA`.

A auditoria V8 encontrou regressões:

- `processing/output.py` usa `PROCESSADO` como sinônimo de validado;
- o Centro de Impressão pode receber IDs manualmente sem validar fechamento no próprio serviço;
- a Central de Entregas filtra corretamente a listagem em parte do fluxo, mas ações POST podem chamar geração sem repetir a autorização no backend;
- filtros visuais podem restringir a tela, mas não constituem controle de autorização.

## 2. Regra canônica

Toda saída final deve passar por um único serviço de autorização de backend.

Nenhum módulo pode decidir sozinho se um documento pode sair.

Consumidores obrigatórios do gate:

- Centro de Impressão;
- Central de Entregas;
- saídas automáticas do Processamento;
- geração individual;
- geração selecionada;
- geração em lote;
- reimpressão/reentrega quando aplicável.

## 3. Chave de autorização

A decisão deve ser feita por:

`competencia + cliente_id + fechamento_versao_id + tipo_saida`

Apenas `cliente_id` ou `documento_id` é insuficiente.

## 4. Condições mínimas

Quando a competência estiver sob Fechamento Mensal, autorizar apenas se:

1. o cliente pertence à composição mensal pertinente;
2. o estado agregado atual é `FECHADA`;
3. existe versão vigente válida do fechamento;
4. não há retificação material pendente;
5. a versão solicitada é a vigente, salvo reimpressão histórica explicitamente autorizada;
6. os documentos solicitados pertencem ao cliente/competência;
7. a seleção recebida do front é intersectada com o universo autorizado no backend.

## 5. Estados que não autorizam saída final

Não autorizam:

- `AGUARDANDO_PROCESSAMENTO`;
- `EM_PROCESSAMENTO`;
- `PRONTA`;
- `EM_CONFERENCIA`;
- `DIVERGENTE`;
- `ADIADA`;
- `RETIFICACAO`;
- `PROCESSADO` de documento isolado;
- consulta externa `SEM_CONSIGNADO`, `COM_CONSIGNADO` ou equivalente.

## 6. Retificação

Ao detectar mudança material após fechamento:

- preservar a saída histórica já realizada e sua versão de origem;
- bloquear novas saídas operacionais até conclusão da retificação;
- após concluir, nova saída deve apontar para a nova versão vigente;
- nunca substituir silenciosamente o arquivo histórico de uma versão anterior.

## 7. Seleção manual

Seleção manual continua sendo funcionalidade de seleção, não autorização.

Se o usuário enviar IDs de clientes/documentos fora do universo permitido, o serviço deve:

- rejeitar os itens não autorizados;
- não processá-los parcialmente como se fossem válidos;
- registrar ocorrência/auditoria com motivo de bloqueio.

## 8. Regressão mínima

Testar no backend, sem depender da UI:

- FECHADA + versão vigente + sem retificação → autoriza;
- PRONTA → bloqueia;
- RETIFICACAO → bloqueia;
- FECHADA sem snapshot/versão → bloqueia;
- documento `PROCESSADO` de cliente não fechado → bloqueia;
- ID manual de cliente não autorizado → bloqueia;
- lote misto com autorizado e não autorizado → política explícita e auditável, sem bypass;
- conclusão de retificação → nova versão passa a autorizar;
- reimpressão histórica, se oferecida, exige ação própria e identifica versão histórica.

## 9. Auditoria

Toda saída deve registrar pelo menos:

- competência;
- cliente;
- versão de fechamento;
- tipo de saída;
- documentos incluídos;
- usuário/origem;
- data/hora;
- correlation_id;
- resultado da autorização.

## 10. Regra final

`PROCESSADO` significa sucesso técnico do processamento.

`FECHADA + versão vigente + sem retificação pendente` é a condição de autorização operacional para saída final.
