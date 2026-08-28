# Auditoria canônica V8 — Etapa 2

Data: 28/08/2026
Base canônica auditada: `Axiom_Tools(20260827-175623).zip`
Status: **auditoria em andamento / pacote final ainda não gerado**

## 1. Escopo efetivamente reaberto nesta etapa

A auditoria foi retomada diretamente sobre o ZIP integral mais recente fornecido pelo usuário, incluindo:

- `app/src/axiom_tools`;
- testes empacotados;
- banco operacional `data/axiom_tools.db`;
- módulos de Fechamento Mensal, Processamento, Conferência, Impressão, Entregas, eConsignado e Clientes.

O código Python da árvore extraída passa em compilação sintática. A suíte web completa não é executável no ambiente Linux de auditoria sem instalar Flask e demais dependências; isso é uma limitação do ambiente de auditoria, não uma conclusão funcional sobre o produto. A validação estrutural e de banco continua normalmente.

## 2. Estado real da competência 08/2026 no banco canônico

Aplicando o perfil de participação do fechamento, existem 339 clientes no ciclo:

- 296 `FECHADA`;
- 31 `PRONTA`;
- 7 `RETIFICACAO`;
- 5 `ADIADA`.

A T L Empreendimentos Agrícolas permanece gravada como `PRONTA`, chamada 1, confirmando que a decisão operacional de 2ª chamada não foi persistida no snapshot atual.

## 3. Central de Conferência continua misturando trabalho vivo com fechados

A função `clientes_conferencia_ids()` inclui atualmente:

- `PRONTA` da chamada atual;
- `FECHADA`;
- `RETIFICACAO`.

Ao executar a Conferência de 08/2026 no banco canônico, o escopo `CICLO` monta 318 empresas, apesar de apenas 31 estarem `PRONTA`.

Isso confirma que a Central ainda mistura operação corrente com clientes já encerrados. O escopo canônico da mesa de trabalho deve ficar restrito ao trabalho vivo da chamada; fechados ficam no histórico e retificações em fluxo próprio.

## 4. A consulta da Conferência ainda possui efeito colateral de escrita

`conference.py::conferencia_competencia()` chama `sincronizar_resultados_conferencia()` durante a própria montagem da resposta.

Consequência: abrir uma tela/relatório que consulta a Conferência pode fechar clientes e criar histórico. Isso viola o princípio de leitura sem efeito colateral.

Correção obrigatória: cálculo da Conferência deve ser puro/leitura. Sincronização de fechamento só deve ocorrer após evento explícito concluído: fim do processamento/reprocessamento, resolução auditável ou conclusão de retificação.

## 5. Reprocessamento destrutivo confirmado novamente

`central.py::reprocessar_arquivo()` ainda executa a sequência:

1. snapshot do registro vigente;
2. exclusão de `processamento_item_pessoa`;
3. exclusão de `processamento_arquivo` vigente;
4. somente depois tenta a nova leitura.

Logo, uma leitura pior substitui a boa antes de ser validada.

### Evidência Jair Ferreira Camargo

O histórico de reprocessamento conserva versões válidas de agosto:

- `449-Extrato Mensal.pdf`: cliente 826, 08/2026, PROCESSADO 100%, FGTS R$ 129,68, saldo federal R$ 511,43;
- `450-Extrato Mensal.pdf`: cliente 826, 08/2026, PROCESSADO 100%, FGTS R$ 259,36, saldo federal R$ 511,43.

Após novos reprocessamentos, os registros vigentes passaram para `REVISAO` 90%, perderam o cliente e passaram a trazer FGTS zero.

Isso prova duas regressões distintas:

- perda de identidade do cliente;
- piora dos dados extraídos.

O histórico existente contém dados suficientes para recuperação segura, mas a correção estrutural deve impedir que um candidato pior volte a substituir a versão boa.

## 6. Regra de Jair — federal não soma, FGTS soma

A evidência histórica confirma exatamente a regra de negócio validada pelo usuário:

- DARF / tributos federais: R$ 511,43 aparece nas duas matrículas e representa a mesma apuração consolidada; não somar;
- FGTS: R$ 129,68 + R$ 259,36 = R$ 389,04; somar as matrículas;
- preservar origem/matrícula no detalhamento.

A conferência atual ainda usa apenas `_ultimo_tipo(emp, "EXTRATO_MENSAL")`, portanto não consegue representar esse caso corretamente.

## 7. Centro de Impressão possui bypass adicional de segurança

Além do problema já identificado de filtro visual opcional, foi confirmado um bypass no serviço:

`printing.service::_rows_selecionadas()` quando recebe `ids` retorna os documentos selecionados diretamente por ID e não reaplica os filtros recebidos, inclusive `cliente_ids`.

Consequência: mesmo que a view calcule um conjunto permitido de clientes, uma seleção explícita de IDs pode ignorar esse gate no serviço.

Correção obrigatória: seleção por ID deve ser intersectada no backend com o mesmo escopo canônico autorizado. Nenhum documento não fechado/conferido pode ser liberado por seleção manual.

## 8. Central de Entregas também não possui gate canônico no serviço

`delivery.service::gerar_cliente()` valida parametrização eletrônica e existência de PDFs, mas não valida por si só que o cliente está `FECHADA` na competência e sem retificação pendente.

A listagem pode filtrar corretamente, porém chamadas diretas ao serviço não devem conseguir contornar a regra.

Regra: autorização de saída deve existir no serviço e não apenas na interface.

## 9. Saídas automáticas continuam confundindo PROCESSADO com validado

`processing.output::gerar_saidas_documento()` usa `row.status == 'PROCESSADO'` para atender `somente_validados`.

O worker chama essa geração imediatamente após processamento/arquivamento.

Isso continua incompatível com a arquitetura V8:

`PROCESSADO` = sucesso técnico do motor;
`CONFERIDO/FECHADO` = autorizado para saída.

## 10. eConsignado ainda consulta universo amplo demais

`consignados.py::clientes_consulta()` seleciona clientes ativos ou historicamente ativos pela data de inativação e deduplica por raiz/CPF, mas não restringe o universo ao Fechamento Mensal da competência, chamada atual e movimento aplicável.

Assim, a consulta oficial ainda pode incluir empregadores que não pertencem à chamada operacional corrente.

Correção obrigatória: o universo do job deve ser derivado da composição mensal vigente, excluindo chamada futura, sem movimento e não aplicáveis, preservando deduplicação matriz/filial.

## 11. Movimento mensal ainda não é soberano na Conferência

Em `conference.py`, a regra atual usa:

`sem_movimento = sem_movimento_competencia OR cadastro.movimento_folha == SEM_MOVIMENTO`.

Isso permite que um perfil cadastral histórico marque como sem movimento uma empresa que foi explicitamente classificada `COM_MOVIMENTO` na competência.

Regra correta: existindo composição mensal, a competência é soberana. O cadastro é somente fallback para competências sem controle mensal.

## 12. Decisão manual ainda é global por cliente

A tabela `processamento_conferencia_manual` possui uma única decisão por `competencia + cliente_id`.

Isso não representa os casos já validados em agosto em que uma fonte é justificada e outra continua pendente, por exemplo:

- DARF impedida por procuração expirada, mas FGTS ainda exigível;
- FGTS tratado na rescisão, mas DARF precisa ser conferida;
- DARF sob responsabilidade da equipe Fiscal sem liberar automaticamente eConsignado/FGTS.

Correção obrigatória: decisões/justificativas por fonte, preservando compatibilidade com a decisão global legada apenas como visão agregada.

## 13. Regressão Sintegra confirmada no ZIP canônico

`clients_views.py` ainda envia ao template os dois links:

- Sintegra Nacional;
- Sintegra Goiás.

O template atual da ficha não os renderiza. Portanto a retirada dos atalhos foi regressão visual, não mudança de backend.

Os atalhos serão restaurados sem desfazer a nova modelagem de inscrições estaduais.

## 14. Próxima sequência da auditoria

A próxima etapa deve fechar, nesta ordem:

1. reprocessamento candidato/versionado sem destruição da versão vigente;
2. recuperação segura dos Extratos 449/450;
3. composição multi-Extrato com federal deduplicado e FGTS aditivo por matrícula;
4. composição de múltiplas GFD/FGTS rescisório;
5. decisão/justificativa por fonte;
6. gate único de autorização para Impressão, Entregas e Saídas automáticas;
7. universo eConsignado limitado à competência/chamada;
8. recalculadora de Conferência disparada por evento, não por abertura de tela;
9. regressão dos 28 casos de agosto;
10. restauração dos atalhos Sintegra e auditoria visual final.

Nenhum pacote final deve ser gerado antes dessa regressão integral.
