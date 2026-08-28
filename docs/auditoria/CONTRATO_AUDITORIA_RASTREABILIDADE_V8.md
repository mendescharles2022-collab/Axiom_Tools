# Contrato V8 — Auditoria transversal e rastreabilidade ponta a ponta

Data: 28/08/2026
Status: **fundação de auditoria existente / extensão V8 ainda não homologada**

## 1. Fundação existente

A consolidação estrutural AXT-003 já definiu uma fundação transversal de auditoria contendo, quando aplicável:

- evento;
- categoria;
- nível;
- entidade e identificador;
- usuário;
- data/hora;
- origem;
- IP;
- método/rota;
- detalhes estruturados;
- sucesso/falha.

A Auditoria Operacional V4 também passou a devolver referência curta em erro HTTP 500 para cruzamento com o log técnico.

A V8 deve reutilizar essa fundação, não criar trilhas paralelas desconectadas.

## 2. Problema da V8

Os fluxos V8 atravessam várias entidades:

```text
arquivo físico
-> processamento
-> versão/candidato
-> identidade/inscrição
-> obrigação/fonte
-> Conferência
-> fechamento
-> versão de fechamento
-> impressão/entrega
```

Registrar cada etapa isoladamente não basta se depois não for possível reconstruir a sequência causal.

## 3. Correlation ID / operação lógica

Toda ação composta deve possuir identificador de correlação ou mecanismo equivalente.

Exemplos:

- reprocessamento de um arquivo;
- anexo pela ocorrência;
- recálculo de um cliente;
- mudança de chamada;
- conclusão de retificação;
- geração de lote/entrega.

Esse identificador deve aparecer nos eventos filhos relevantes e nos logs técnicos.

## 4. Reprocessamento

A trilha precisa responder:

- quem pediu;
- qual documento/arquivo lógico;
- qual versão era vigente;
- por que reprocessou;
- qual candidato foi criado;
- qual motor/especialista executou;
- resultado técnico;
- identidade antes/depois;
- competência antes/depois;
- inscrição antes/depois;
- valores antes/depois;
- candidato promovido ou rejeitado;
- motivo da promoção/rejeição;
- quais cruzamentos foram recalculados.

Não registrar apenas `reprocessado com sucesso`.

## 5. Decisão por fonte

Cada decisão/justificativa deve registrar:

- competência;
- cliente;
- fonte/obrigação;
- estado anterior;
- novo estado;
- motivo;
- observação;
- evidências associadas;
- usuário;
- data/hora;
- correlation ID da ocorrência quando houver.

A decisão global agregada do cliente é consequência e não deve esconder a decisão fonte a fonte.

## 6. Mudança de chamada

Registrar obrigatoriamente:

- chamada anterior;
- chamada nova;
- status anterior;
- status novo;
- motivo/impedimento;
- usuário;
- data/hora;
- origem da ação;
- versão/estado esperado usado no compare-and-set.

Se houver conflito de concorrência, registrar tentativa recusada sem substituir o evento válido anterior.

## 7. Fechamento

Quando um cliente fecha, a trilha deve permitir identificar:

- versão do fechamento;
- obrigações que estavam conclusivas;
- justificativas vigentes;
- documentos/evidências usadas;
- data/hora;
- evento que disparou o último recálculo;
- se foi fechamento inicial ou conclusão de retificação.

## 8. Retificação

Registrar:

- versão base;
- candidata;
- gatilho/materialidade;
- deltas principais;
- documentos envolvidos;
- data/hora da detecção;
- saídas bloqueadas;
- usuário/ação de conclusão quando manual;
- nova versão fechada.

Não apagar a candidata rejeitada/concluída do histórico.

## 9. eConsignado

Cada fotografia do job deve registrar:

- competência;
- chamada;
- universo consultado;
- data/hora;
- resultado por empregador;
- contratos retornados;
- impedimentos/falhas;
- versão/fotografia anterior quando comparável;
- correlation ID do ciclo/job.

A Conferência deve apontar qual fotografia oficial foi usada no cruzamento.

## 10. Saídas

Impressão/Entrega precisa registrar:

- cliente;
- competência;
- versão de fechamento autorizadora;
- documentos incluídos;
- gate/decisão de autorização;
- usuário/worker;
- data/hora;
- destino/tipo de saída;
- sucesso/falha;
- lote, quando houver.

Uma saída antiga permanece ligada à versão antiga mesmo se houver retificação posterior.

## 11. Sintegra/RFB

Ao aplicar dado cadastral externo, registrar:

- fonte;
- data/hora da consulta;
- campo;
- valor anterior;
- valor proposto;
- valor aplicado;
- usuário;
- documento usado na consulta;
- status da consulta.

Não armazenar credenciais/segredos em auditoria.

## 12. Erros técnicos

Erro técnico deve possuir referência curta/correlation ID visível ao usuário quando útil.

Log técnico pode conter stack trace e contexto necessário, mas:

- não expor senha;
- não expor segredo/token;
- evitar conteúdo documental integral desnecessário;
- não mostrar traceback no front.

## 13. Eventos de leitura

Não registrar cada GET comum de Conferência como evento de negócio que polua o histórico.

Leitura pode ir para access log, mas não deve parecer decisão/mutação.

A trilha de negócio foca eventos que alteram ou explicam estado.

## 14. Imutabilidade lógica

Histórico de negócio não deve ser editado para “corrigir” o passado.

Correção gera novo evento explicativo.

Exemplo:

```text
CHAMADA_ALTERADA 1->2
TENTATIVA_OBSOLETA_REJEITADA
```

em vez de apagar o primeiro evento.

## 15. Reconstrução

Para cliente + competência, a auditoria deve conseguir reconstruir cronologicamente:

1. entrada no ciclo;
2. chamada/movimento;
3. documentos recebidos;
4. processamentos/reprocessamentos;
5. resultados por fonte;
6. decisões manuais;
7. fechamento;
8. retificações;
9. saídas.

Esse é o critério prático de qualidade da trilha.

## 16. Retenção e volume

Auditoria operacional pode crescer muito.

Não resolver removendo histórico importante.

Separar:

- auditoria estruturada de negócio;
- logs técnicos rotativos;
- conteúdo físico documental.

Logs técnicos podem rotacionar conforme política; histórico de negócio segue a retenção do produto e do escritório.

## 17. Regressões obrigatórias

1. reprocessar Jair gera trilha vigente -> candidato -> promoção/rejeição;
2. perda de identidade em candidato aparece no delta;
3. justificar DARF registra somente DARF;
4. mover T L para chamada 2 registra antes/depois;
5. tentativa obsoleta posterior não apaga a mudança;
6. fechamento registra versão e fontes conclusivas;
7. retificação liga Vn -> Vn+1;
8. saída registra versão de fechamento autorizadora;
9. erro 500 possui referência cruzável com log;
10. segredo/senha não aparece na auditoria;
11. aplicar dado SEFAZ/RFB preserva valor anterior e fonte;
12. GET da Conferência não cria evento de negócio de fechamento.

## 18. Critério de homologação

A V8 só será considerada auditável quando for possível explicar uma divergência real de agosto reconstruindo a sequência dos eventos sem depender de memória humana ou de inferência sobre o estado atual do banco.
