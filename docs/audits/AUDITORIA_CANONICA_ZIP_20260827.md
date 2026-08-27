# Auditoria canônica — ZIP operacional 27/08/2026

Base analisada: `Axiom_Tools(20260827-175623).zip`.

Status: **EM AUDITORIA / NÃO HOMOLOGADO**.

## Diretriz de simplificação

A auditoria deve eliminar duplicidades de código, regras, estados, telas e caminhos operacionais sempre que houver sobreposição, preservando funcionalidades, histórico, auditoria, retificação, motores especialistas, impressão, entregas e reprocessamento.

Regra de UX: o fluxo normal deve exigir o mínimo de decisões manuais. Detalhes técnicos permanecem disponíveis em área avançada, mas não devem comandar a operação mensal.

## Ordem operacional revisada

A consulta oficial do Crédito do Trabalhador / eConsignado passa a ser a **Etapa 0 do processamento da competência**, antes da avaliação dos arquivos Domínio.

Fluxo aprovado:

`Competência aberta → eConsignado → Domínio → eSocial → e-CAC/DARF → FGTS Digital → cruzamento/conferência`

Regras:

- a consulta eConsignado deve nascer do mesmo comando de processamento da competência, e não depender de execução manual em tela separada;
- resultado `SEM_CONSIGNADO` é resultado válido;
- `SEM_PROCURACAO` é situação informativa/auditável e não erro técnico;
- falha real de conexão/API deve ficar registrada como pendência técnica sem apagar resultados anteriores válidos;
- a consulta deve usar o universo mensal aplicável da competência/chamada, e não consultar indiscriminadamente todo o cadastro histórico;
- a fotografia oficial deve estar disponível antes dos motores documentais para que Domínio, comunicados e FGTS possam ser comparados contra a referência MTE/Dataprev.

## Achado confirmado no ZIP — eConsignado separado do processamento

O endpoint principal de processamento (`/processamento/processar`) apenas chama `enfileirar_conexoes()`.

A consulta eConsignado possui fluxo separado (`/processamento/consignados/sincronizar`) com `criar_job()` + `lancar_job()`.

Portanto, na base atual, a consulta oficial **não é etapa do processamento** e pode ocorrer antes, depois ou nem ocorrer. Isso será consolidado no orquestrador.

## Achado confirmado no ZIP — universo excessivo da consulta

Na cópia do banco auditada:

- competência operacional: `08/2026`;
- último job eConsignado 08/2026: **840 empregadores consultados**;
- com consignado: 19;
- sem consignado: 684;
- sem procuração: 137;
- erros: 0;
- contratos: 58.

A função `clientes_consulta()` seleciona clientes do cadastro por situação/data e não usa diretamente a composição mensal/chamada do Fechamento Mensal. A integração deverá consultar apenas o universo mensal elegível.

## Monitor de Execução — problema estrutural de status

A camada de persistência ainda grava sessões concluídas como `COM_PENDENCIAS` quando existem documentos em `REVISAO`.

Depois, `listar_sessoes()` e `status_sessao()` sobrescrevem visualmente esse estado com `PROCESSAMENTO_CONCLUIDO` quando o percentual chega a 100%.

Isso cria duas verdades para a mesma sessão e foi uma das causas da confusão visual já observada.

Correção requerida:

- sessão técnica deve possuir estados próprios e únicos: não iniciado, processando, pausado, concluído, concluído com falha técnica, interrompido/cancelado;
- `100%` representa somente percurso técnico;
- pendências técnicas devem ser um contador/estado separado;
- divergências documentais e de batimento pertencem à Conferência e não alteram o estado técnico da sessão;
- remover a duplicação `status` x `status_operacional` quando ela representar a mesma coisa.

## Monitor de Execução — simplificação visual

A tela atual repete informação em chips de sessão, percentual grande, barra de progresso, KPIs, fluxo de pacotes e contador `Atenção`.

A revisão deve priorizar uma leitura operacional simples:

1. competência e etapa atual;
2. progresso enquanto houver execução;
3. ao concluir, trocar o destaque percentual por `Processamento concluído`;
4. exibir separadamente `Pendências técnicas`;
5. exibir motores/etapas de negócio em ordem: eConsignado, Domínio, eSocial, e-CAC/DARF, FGTS Digital e cruzamento;
6. mover leitura/triagem/extração/checkpoints/blocos para `Detalhes técnicos`.

## Demais falhas críticas já incorporadas à auditoria

- MEI/DAE prevalecer sobre expectativa genérica de GFD;
- FGTS zero não gerar ausência artificial;
- FGTS mensal + rescisório como composição de múltiplas evidências;
- eConsignado não ficar `CONFERIDO` com fontes ausentes/incompatíveis;
- cliente em chamada futura fora da cobrança da chamada atual;
- reprocessamento não destrutivo e capaz de preservar versão válida anterior;
- descoberta de arquivo novo/alterado deve terminar antes da recomposição da Conferência;
- recuperação de identidade de MMT, Alex e extratos regressivos;
- Pendências orientada por competência, deixando PROC/chave como detalhe avançado;
- justificativas por ocorrência/fonte sem esconder outras pendências;
- relatórios de pendências em A4 retrato;
- eliminação de duplicidades entre módulos/rotas/validações/telas.

## Critério de entrega

Não gerar pacote final antes de concluir auditoria estrutural, corrigir as falhas críticas, executar regressões sobre casos reais e validar que a simplificação não remove funcionalidades úteis.
