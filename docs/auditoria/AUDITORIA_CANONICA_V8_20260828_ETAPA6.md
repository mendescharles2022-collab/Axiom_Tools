# Auditoria canônica V8 — Etapa 6

Data: 28/08/2026
Base de evidência: ZIP canônico `Axiom_Tools(20260827-175623).zip`, banco auditado e documentação histórica do projeto.
Status: **auditoria em andamento / nenhum pacote final liberado**.

## 1. Escopo desta etapa

A Etapa 6 fechou contratos que ainda estavam difusos entre versões anteriores e a arquitetura V8:

- eConsignado como Etapa 0 do processamento;
- universo mensal correto da consulta;
- separação entre resultado da fonte e conclusão da Conferência;
- gate único de autorização de saídas;
- inativação/reativação de clientes;
- separação das máquinas de estado técnico, mensal e por obrigação.

## 2. eConsignado — excesso de universo confirmado

Na competência 08/2026, o job auditado consultou 840 empregadores, enquanto o Fechamento Mensal possuía 339 clientes participantes do ciclo.

Distribuição do job:

- 19 com consignado;
- 684 sem consignado;
- 137 sem procuração;
- 0 erros;
- 58 contratos.

A causa estrutural já identificada é `clientes_consulta()` derivar o universo do cadastro histórico/situação, e não da composição mensal/chamada.

Correção contratual: o job deve nascer do Fechamento Mensal e respeitar competência, chamada, movimento aplicável e deduplicação do empregador.

## 3. eConsignado — fluxo separado do processamento

O endpoint principal `/processamento/processar` apenas enfileira conexões.

O eConsignado possui fluxo próprio em `/processamento/consignados/sincronizar`, usando `criar_job()` + `lancar_job()`.

Isso permite que a fotografia oficial seja executada fora de ordem ou sequer executada.

Contrato V8: a consulta passa a ser Etapa 0 do mesmo orquestrador mensal.

## 4. eConsignado — falso `CONFERIDO`

A V8F2 já registrava falha real em D A F Castro Ltda: o bloco eConsignado podia aparecer `CONFERIDO` mesmo com fontes MTE/Dataprev, Domínio, Comunicado e FGTS Digital incompletas/incompatíveis.

A correção não é trocar uma condição isolada. O modelo precisa separar:

- resultado da consulta (`COM_CONSIGNADO`, `SEM_CONSIGNADO`, `SEM_PROCURACAO`, `ERRO_TECNICO`);
- estado da obrigação após cruzamento (`CONFERIDA`, `DIVERGENTE`, `JUSTIFICADA`, etc.).

## 5. Gate único de saída — regra antiga, proteção atual insuficiente

A DEC-004, a AXT-006 e a AXT-007 já estabeleciam que a conferência antecede impressão/consolidação e que pendências não devem ser escondidas.

A auditoria canônica mostrou, porém, três caminhos com proteção inconsistente:

- Centro de Impressão;
- Central de Entregas;
- Saídas automáticas.

Falhas já confirmadas incluem seleção manual de IDs capaz de contornar escopo de clientes, ações POST de Entregas sem revalidação equivalente e `PROCESSADO` usado como sinônimo de validado em saídas automáticas.

Contrato: todas as saídas usam um único gate de backend, com `FECHADA` + ausência de retificação material pendente como base da autorização.

## 6. Inativação — falha funcional real da suíte

A suíte do ZIP canônico confirmou:

`classificacao_inativacao` pode chegar como string, enquanto o repositório assume sempre Enum e acessa `.value`.

A correção precisa normalizar entrada e testar o fluxo completo de inativação/reativação.

Também deve preservar:

- histórico;
- pasta física;
- documentos;
- competências anteriores;
- efeito somente nos ciclos futuros conforme data efetiva.

## 7. Máquinas de estado — causa comum de várias confusões

A auditoria já havia confirmado que a persistência de sessão pode manter `COM_PENDENCIAS` enquanto a projeção visual apresenta `PROCESSAMENTO_CONCLUIDO` ao chegar a 100%.

Isso não deve ser resolvido com mais um rótulo.

A V8 precisa separar, no mínimo:

### A. Estado técnico da sessão

`NAO_INICIADO`, `PROCESSANDO`, `CONCLUIDO`, `CONCLUIDO_COM_FALHA_TECNICA`, `INTERROMPIDO`.

### B. Estado mensal do cliente

`AGUARDANDO_PROCESSAMENTO`, `EM_PROCESSAMENTO`, `EM_CONFERENCIA`, `PENDENTE`, `ADIADA`, `FECHADA`, `RETIFICACAO`.

### C. Estado por obrigação

`PENDENTE`, `CONFERIDA`, `DIVERGENTE`, `JUSTIFICADA`, `NAO_APLICAVEL`, `IMPEDIDA_EXTERNAMENTE`, `RETIFICACAO`.

### D. Resultado de fonte externa

No eConsignado, por exemplo: `COM_CONSIGNADO`, `SEM_CONSIGNADO`, `SEM_PROCURACAO`, `ERRO_TECNICO`.

Nenhuma dessas máquinas pode promover implicitamente a outra.

## 8. Conferência continua obrigatoriamente read-only

A evidência anterior permanece válida: `conferencia_competencia()` chama sincronização durante montagem da tela.

Contrato reforçado nesta etapa:

- abrir/atualizar a Conferência não é evento de negócio;
- GET/consulta não fecha cliente;
- não cria histórico;
- não altera chamada;
- não promove candidato;
- não altera movimento mensal.

Mudanças acontecem por eventos explícitos e auditáveis.

## 9. Documentos produzidos nesta etapa

- `CONTRATO_ECONSIGNADO_V8.md`;
- `CONTRATO_GATE_SAIDAS_V8.md`;
- `CONTRATO_INATIVACAO_CLIENTES_V8.md`;
- `CONTRATO_ESTADOS_OPERACIONAIS_V8.md`;
- este documento.

## 10. Regressões adicionadas

Além da matriz dos 28 casos:

1. job eConsignado da 1ª chamada não consulta cliente da 2ª;
2. `SEM_CONSIGNADO` é resultado válido, não erro;
3. `SEM_PROCURACAO` é informativo/auditável, não falha técnica;
4. D A F Castro não fica `CONFERIDO` com fontes incompatíveis;
5. erro da API não apaga fotografia anterior válida;
6. documento `PROCESSADO` de cliente não fechado não sai;
7. seleção manual por ID não burla Impressão;
8. chamada direta de Entregas não burla gate;
9. retificação pendente bloqueia nova saída;
10. inativação funciona recebendo Enum ou string canônica;
11. inativação não apaga filesystem/histórico;
12. 100% técnico não significa cliente fechado;
13. `PRONTA` sem evidência não vira `Em conferência` automaticamente;
14. abrir Conferência não escreve no banco de fechamento.

## 11. Estado ao final da Etapa 6

A auditoria permanece aberta.

Continuam sem evidência de correção/homologação no runtime canônico:

- reprocessamento candidato/versionado;
- recuperação segura dos Extratos 449/450;
- composição multi-Extrato/multi-GFD implementada;
- decisão por fonte implementada;
- gate único implementado;
- eConsignado integrado ao orquestrador e restrito ao ciclo;
- Conferência read-only;
- correção funcional da inativação;
- regressão integral dos 28 casos;
- restauração/homologação visual do Sintegra;
- reconciliação entre código do repositório e árvore operacional do ZIP.

Nenhum pacote V8 deve ser liberado antes dessas verificações.
