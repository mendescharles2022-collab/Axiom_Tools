# Auditoria canônica V8 — Etapa 11

Data: 28/08/2026
Status: **auditoria em andamento / nenhum pacote final liberado**

## 1. Escopo

A Etapa 11 auditou a capacidade de explicar e reconstruir eventos críticos da V8.

A fundação transversal de auditoria já existia desde a AXT-003 e foi validada em versões anteriores, mas os fluxos V8 exigem correlação entre processamento, Conferência, Fechamento, retificação e saída.

## 2. Fundação existente preservada

A auditoria comum já prevê:

- evento;
- categoria;
- nível;
- entidade/id;
- usuário;
- data/hora;
- origem;
- IP;
- método/rota;
- detalhes estruturados;
- sucesso/falha.

A V4 também introduziu referência curta para erros 500 cruzável com o log técnico.

A V8 reutiliza essa fundação.

## 3. Novo requisito: correlação ponta a ponta

Uma operação lógica precisa ser rastreável por correlation ID ou mecanismo equivalente.

Exemplo:

`arquivo -> candidato -> promoção -> obrigação -> recálculo -> fechamento -> versão -> saída`

Sem essa correlação, o sistema possui vários históricos parciais, mas não consegue explicar causalidade.

## 4. Reprocessamento

A auditoria deve registrar antes/depois de:

- identidade;
- competência;
- inscrição;
- tipo documental;
- valores relevantes;
- vigente/candidato;
- promoção/rejeição;
- motivo;
- recálculos disparados.

Isso permitirá explicar precisamente a regressão observada nos Extratos 449/450.

## 5. Decisão por fonte

Cada justificativa precisa registrar a fonte específica.

DARF justificada não pode aparecer no histórico como `cliente justificado` sem granularidade.

## 6. Chamadas

A mudança T L 1 -> 2 precisa ser reconstruível com:

- estado/chamada anteriores;
- novo estado/chamada;
- motivo;
- usuário;
- horário;
- origem;
- eventuais tentativas obsoletas rejeitadas depois.

## 7. Fechamento e retificação

Fechamento registra versão e conjunto de obrigações conclusivas.

Retificação registra:

- versão base;
- candidata;
- gatilho;
- deltas;
- bloqueio de saída;
- conclusão;
- nova versão.

## 8. eConsignado

A Conferência deve apontar qual fotografia/job oficial sustentou o resultado da obrigação.

Não basta guardar somente o estado corrente do contrato.

## 9. Saídas

Impressão/Entrega deve guardar a versão de fechamento que autorizou a saída.

Assim, após uma retificação posterior, o histórico continua explicável.

## 10. Enriquecimento cadastral

RFB/SEFAZ GO deve registrar por campo:

- origem;
- valor anterior;
- valor proposto;
- valor aplicado;
- consulta;
- usuário/data.

Situação externa nunca deve apagar o histórico da decisão interna.

## 11. Logs x auditoria de negócio

Separar:

- logs técnicos rotativos;
- auditoria estruturada de negócio;
- documentos físicos.

GET comum não deve poluir a auditoria de negócio como se fosse mutação.

## 12. Documento produzido

- `CONTRATO_AUDITORIA_RASTREABILIDADE_V8.md`;
- este documento.

## 13. Estado ao final da Etapa 11

A fundação de auditoria é reaproveitável, mas a V8 ainda precisa provar a correlação entre todas as fases do ciclo.

Continuam não homologados:

- trilha reprocessamento vigente/candidato;
- decisão por fonte;
- trilha de conflito de chamada;
- versão de fechamento nas saídas;
- fotografia eConsignado usada na Conferência;
- correlação completa dos eventos dos 28 casos.

Nenhum pacote V8 deve ser liberado antes da regressão integral.
