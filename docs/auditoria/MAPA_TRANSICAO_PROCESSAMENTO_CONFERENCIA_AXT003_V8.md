# Mapa de transição — Processamento/Conferência AXT-003 → V8

Data: 28/08/2026
Status: **apoio obrigatório à auditoria de arquitetura, interface e testes**

## 1. Por que este mapa existe

A estrutura do Axiom Tools mudou rapidamente entre 17 e 28/08/2026.

Comportamentos que eram corretos em uma etapa podem ser resíduos obsoletos na V8 sem terem sido originalmente bugs.

Este mapa evita:

- remover algo válido sem entender sua origem;
- manter comportamento antigo só porque já estava implementado;
- acusar regressão onde houve mudança consciente de arquitetura.

## 2. AXT-003 estrutural — 17/08

A consolidação estrutural determinou que não se mantivessem como módulos autônomos antigos:

- OCR;
- Competências;
- Conferência.

Esses conceitos passariam a compor o futuro `Processamento de Arquivos` e a camada documental.

Na navegação daquele momento, o grupo Documentos continha essencialmente:

- Processamento de Arquivos;
- Documentos;
- Impressão em Lote.

Nesse contrato, fazia sentido Processamento absorver linguagem de auditoria/conferência.

## 3. V6 — Fechamento surge depois de Processamento

V6 introduziu Fechamento Mensal e o colocou no menu **logo após Processamento de Arquivos**.

Também concentrou no Fechamento várias ações administrativas:

- sem movimento;
- chamadas;
- fechar;
- não se aplica;
- impedimentos.

A arquitetura ainda estava em transição.

## 4. V7 — fechamento automático, mas conceitos ainda misturados

V7 removeu `Fechar selecionadas` e passou a fechar pelo batimento.

Porém ainda manteve comportamentos que depois seriam refinados:

- `PRONTA` apresentada como `Em conferência`;
- decisão manual global capaz de concluir cliente;
- Ciclo atual incluindo FECHADA;
- ações de movimento no Fechamento.

Essas regras foram válidas para V7, mas não são o contrato final V8.

## 5. V8 — separação definitiva de responsabilidades

A V8 estabelece:

### Fechamento Mensal

- origem da competência;
- composição mensal;
- chamadas;
- acompanhamento de status;
- histórico/retificação em visão própria.

### Processamento de Arquivos

- execução técnica;
- motores especialistas;
- fila/jobs;
- leitura/classificação/extração;
- pendências técnicas.

### Central de Conferência

- mesa de resolução operacional;
- batimentos;
- decisões por fonte;
- justificativas;
- anexar/reprocessar dentro da ocorrência;
- resolução de exceções.

## 6. Evidência de resíduo no runtime

Trecho preservado do template de Processamento mostra:

```text
PROCESSAMENTO DE ARQUIVOS
<h1>Aud...
```

O conteúdo integral do título não foi recuperado.

Classificação:

**resíduo provável de terminologia/UX a inspecionar**, e não defeito funcional confirmado por inferência.

## 7. O que procurar no runtime reconciliado

### No Processamento

Remover/migrar se ainda existirem:

- título `Auditoria` como papel principal;
- decisões `Conferido/Justificado`;
- fechamento do cliente;
- justificativa de ausência de guia;
- aplicação paralela de competência;
- filtros de negócio duplicando Conference.

Preservar:

- auditoria técnica/logs;
- detalhes de extração;
- confiança/completude;
- reprocessamento técnico;
- fila e sessões.

### Na Conferência

Confirmar que recebeu de volta as ações operacionais aprovadas:

- anexar documento;
- reprocessar;
- ocorrência;
- justificar por fonte;
- ver documentos;
- sem movimento mensal;
- próxima chamada/impedimento.

### No Fechamento

Confirmar que não reabsorveu a mesa documental.

## 8. Migração da suíte de testes

Testes herdados do período AXT-003/V6/V7 devem ser classificados antes de serem mantidos.

### Atualizar/remover expectativa antiga

- Processamento como tela que concentra Conference;
- PRONTA sempre igual a Em conferência;
- decisão global fecha cliente;
- FECHADA no trabalho vivo comum;
- competência reaplicada no Processamento.

### Preservar garantias

- autenticação;
- segurança documental;
- competência versionada;
- próxima chamada fora do ciclo corrente;
- saída bloqueada sem fechamento;
- retificação preservando Vn;
- sem movimento mensal separado do cadastro permanente.

## 9. Navegação

Contrato V8:

```text
Fechamento Mensal
-> Processamento de Arquivos
-> Central de Conferência
-> Saídas
```

O shell atual precisa ser inspecionado diretamente para confirmar a ordem; não há evidência recuperada suficiente para marcar a ordem atual como incorreta.

## 10. Critério de conclusão

A transição estará concluída quando:

- nomes das telas refletem os papéis V8;
- nenhuma ação de negócio importante existe duplicada em módulos diferentes;
- testes antigos foram migrados com justificativa;
- Processamento é técnico;
- Conference é resolução;
- Fechamento é composição/status;
- navegação ensina a mesma ordem do fluxo real.
