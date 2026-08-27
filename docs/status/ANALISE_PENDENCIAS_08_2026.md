# Análise das Pendências — Competência 08/2026

Status: em discussão operacional caso a caso
Data: 27/08/2026

Este documento registra os casos reais discutidos na conferência da competência 08/2026. A finalidade é separar pendência real, falha de processamento, falsa divergência e situação excepcional antes da correção consolidada.

## Regra operacional confirmada

- Documentos impressos manualmente pelo usuário durante a contingência foram impressos fora do Axiom Tools.
- O bloqueio de impressão do Tools deve permanecer: guias só devem ser liberadas pelo sistema quando estiverem batidas e conferidas.
- A correção deve eliminar falsas pendências, não afrouxar o controle de impressão.
- Reprocessamento deve detectar substituição/atualização de arquivos, criar nova versão, preservar histórico e recalcular todos os cruzamentos afetados.

## Caso 1 — 307 Looks Ltda

Situação confirmada:
- houve alteração posterior do cenário por rescisão recebida às pressas;
- os arquivos foram atualizados/substituídos;
- mesmo assim o sistema manteve a leitura anterior.

Classificação: falha estrutural de reprocessamento/versionamento.

Correção esperada:
- detectar novo conteúdo/hash;
- processar nova versão;
- preservar anterior no histórico;
- invalidar resultado derivado antigo;
- recalcular conferência automaticamente.

## Caso 2 — Alex Douglas de Andrade

Situação confirmada:
- empresa tinha um único empregado;
- ocorreu dispensa sem justa causa;
- FGTS do vínculo já foi tratado no processo rescisório/multa;
- em agosto não há FGTS mensal a exigir;
- permanece DARF previdenciária/INSS;
- DARF foi incluída, mas o reprocessamento não atualizou a conferência.

Classificação: falsa ausência de FGTS + falha de reprocessamento da DARF.

Correção esperada:
- FGTS mensal = não aplicável / tratado na rescisão;
- não exigir GFD mensal;
- reprocessar e vincular a DARF existente;
- recalcular conferência.

## Caso 3 — Casa das Carnes e Panificadora Lago Azul

Situação confirmada:
- processamento Domínio foi realizado;
- no envio posterior ao eSocial/RFB, houve retorno informando procuração expirada;
- por isso não foi possível prosseguir para geração da guia.

Classificação: impedimento externo de emissão, não ausência documental comum.

Correção esperada:
- DARF = justificado / impedimento externo;
- motivo = procuração RFB expirada;
- registrar que Domínio foi processado e a geração foi impedida pelo retorno externo;
- resolver apenas a fonte DARF;
- não marcar falsamente como conferido.

## Caso 4 — Comercial Faria Ltda

Situação confirmada:
- houve desligamento;
- parte do FGTS foi recolhida previamente por causa do prazo relacionado à rescisão;
- posteriormente existe o contexto mensal da competência;
- o Extrato Domínio não representou bem a composição e o motor/OCR não interpretou corretamente.

Classificação: falha de composição de múltiplas evidências FGTS.

Correção esperada:
- não presumir uma única GFD por cliente/competência;
- compor GFD mensal + recolhimento rescisório/antecipado quando aplicável;
- preservar cada guia individualmente;
- considerar conferido quando a soma das evidências explicar o valor esperado.

## Caso 5 — Construtora & Empreendimentos Messias

Situação confirmada:
- DARF foi localizada e confere;
- GFD foi efetivamente gerada e colocada entre os arquivos;
- o sistema não leu/processou a guia;
- o reprocessamento não corrigiu a ausência.

Classificação: falha de descoberta/classificação/vinculação da GFD.

Correção esperada:
- revarrer conexões e arquivos no reprocessamento;
- identificar arquivo novo/alterado;
- classificar, extrair, persistir e recalcular a conferência.

## Caso 6 — D A F Castro

Situação confirmada:
- usuário conferiu manualmente os dados;
- valores da folha e da consulta eConsignado conferem;
- divergência exibida pelo sistema é falsa;
- provável combinação de leitura incompleta do Extrato Domínio e/ou persistência/associação incorreta do retorno da API.

Classificação: falsa divergência por falha de leitura/persistência.

Correção esperada:
- leitura integral dos valores do Extrato Domínio;
- persistência correta do retorno eConsignado;
- recomposição automática;
- resultado deve ser conferido se demais fontes estiverem satisfeitas.

## Caso 7 — D&L Alimentos

Situação confirmada:
- empresa tinha apenas um empregado;
- empregado foi desligado em julho;
- em agosto não há empregados registrados nem FGTS da competência;
- API ainda retorna dados de consignado relativos ao vínculo já encerrado.

Classificação: retorno residual/histórico da API não deve gerar ausência automática.

Correção esperada:
- eConsignado pode rodar antes dos arquivos, mas sua resposta deve ser confirmada pela realidade da competência;
- cruzar retorno com Extrato Domínio/eSocial;
- verificar empregados ativos, data efetiva de desligamento e base/valor de FGTS;
- se não houver vínculo vigente/FGTS, gerar observação para confirmação e não bloquear como ausência de documento.

## Caso 8 — Delfino Pereira Ribeiro

Situação confirmada:
- GFD foi gerada e colocada entre os arquivos;
- o Tools não leu a guia;
- mesmo padrão ocorreu com outros produtores rurais PF;
- durante a contingência, o usuário precisou imprimir várias guias manualmente, fora do Tools.

Classificação: possível falha sistemática de descoberta/classificação/vínculo de GFD em produtores rurais PF.

Correção esperada:
- auditar caminho, nomenclatura, CPF/CAEPF, identificação do cliente e regra de classificação das GFDs desse perfil;
- manter bloqueio de impressão do Tools até conferência real.

## Caso 9 — Denes Mariano de Castro

Situação confirmada:
- empregado possui muitos filhos;
- salário-família elevado compensou integralmente o valor previdenciário;
- saldo da DARF ficou zerado;
- portanto a ausência da DARF é legítima e não deve gerar pendência.

Classificação: falha de interpretação do Extrato Domínio / apuração federal.

Correção esperada:
- leitor deve compreender saldo previdenciário após salário-família e demais deduções;
- quando saldo final a recolher for zero, classificar DARF como não aplicável / sem saldo a recolher;
- não criar ausência de DARF.

## Próximo caso

Caso 10 — Elenice Batista Santos Silva (MEI).
