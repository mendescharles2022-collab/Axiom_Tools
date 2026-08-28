# Análise das pendências — competência 08/2026

Data: 27/08/2026  
Status: **regras de negócio discutidas e entendidas caso a caso; correções a incorporar na auditoria consolidada**

Este documento registra a análise dos 28 casos que apareceram como divergentes/incompletos na competência 08/2026, com as explicações operacionais fornecidas pelo escritório e as correções de sistema derivadas.

## 1. 307 Looks Ltda
- Houve uma situação inicial e, depois, uma rescisão de última hora.
- Os arquivos foram atualizados/substituídos, mas o Tools continuou trabalhando com o estado anterior.
- Falha: reprocessamento não incorporou a nova versão dos documentos nem recompôs a conferência.
- Correção: detectar arquivo novo/alterado por conteúdo/hash, versionar, preservar histórico e refazer todos os cruzamentos afetados.

## 2. Alex Douglas de Andrade
- Empresa com um único empregado.
- Houve dispensa sem justa causa.
- O FGTS do vínculo já foi tratado no contexto rescisório/multa.
- Na competência permanece a DARF previdenciária/INSS.
- Falha: o Tools continuou exigindo FGTS mensal e não incorporou a DARF colocada posteriormente.
- Correção: reconhecer FGTS tratado na rescisão como não aplicável no mensal e reprocessar corretamente a DARF adicionada.

## 3. Casa das Carnes e Panificadora Lago Azul
- O processamento pela Domínio ocorreu normalmente.
- Na tentativa de envio ao eSocial/RFB, houve retorno de procuração expirada.
- Não é ausência de documento por falha interna; é impedimento externo de emissão.
- Correção: justificar somente a fonte DARF como `Impedimento externo — procuração RFB expirada`, com auditoria, sem chamar de conferido e sem esconder outras fontes.

## 4. Comercial Faria Ltda
- Houve desligamento na competência.
- Parte do FGTS foi recolhida previamente no contexto do desligamento, antes do vencimento mensal.
- O Extrato Domínio não refletiu adequadamente essa composição e o motor comparou apenas uma guia.
- Correção: aceitar múltiplas evidências de FGTS na mesma competência, preservando cada guia e confrontando a composição aplicável (mensal + rescisória/antecipada) contra o valor esperado.

## 5. Construtora & Empreendimentos Messias
- A guia FGTS foi efetivamente gerada e disponibilizada.
- O Tools não a leu/vinculou e continuou indicando ausência.
- Correção: reprocessamento deve varrer novamente conexões/pastas e incorporar arquivos existentes que ainda não viraram documento válido no banco.

## 6. D A F Castro
- O escritório conferiu manualmente e os valores da folha e da consulta eConsignado conferem.
- A divergência é falsa.
- Prováveis causas: leitura incompleta do Extrato Domínio e/ou persistência/associação incorreta do retorno da API.
- Correção: reforçar extração dos contratos e garantir que o retorno da API seja corretamente associado ao cliente/competência e recomposto na conferência.

## 7. D&L Alimentos
- A empresa tinha um único empregado, demitido em julho.
- Em agosto não havia empregado ativo nem FGTS a recolher.
- A API ainda retornou contratos de consignado residuais.
- Correção: retorno positivo do eConsignado deve ser confrontado com Domínio/eSocial. Sem vínculo ativo, sem remuneração e com FGTS zero, o retorno vira observação a confirmar, e não ausência/divergência bloqueante.
- Se houver data de desligamento no Extrato/eSocial, usá-la para classificar o retorno como residual/histórico.

## 8. Delfino Pereira Ribeiro
- A GFD existia e foi disponibilizada.
- O Tools não leu a guia.
- O mesmo padrão foi observado em outros produtores rurais PF.
- Correção: auditar especificamente descoberta, identidade e vínculo de GFD para produtor rural PF, incluindo CPF/CAEPF, caminhos e nomenclaturas.

## 9. Denes Mariano de Castro
- O empregado possui muitos filhos e o salário-família zerou o saldo previdenciário.
- Não há DARF a emitir quando o saldo efetivo é zero.
- Correção: o leitor do Extrato Domínio deve calcular corretamente `INSS apurado - deduções/créditos (incluindo salário-família) = saldo a recolher`.
- Saldo zero deve resultar em `DARF não aplicável / sem saldo a recolher`, e não ausência.

## 10. Elenice Batista Santos Silva
- Cliente MEI.
- Recolhimento do empregado ocorre via DAE.
- Correção: perfil MEI prevalece; não exigir GFD autônoma. Separar corretamente os componentes do DAE e confrontá-los com o Extrato Domínio.

## 11. Eloim Transportes
- Os Extratos Domínio de agosto foram colocados, mas o leitor não os processou/vinculou.
- DARF e FGTS foram localizados.
- Correção: reforçar cadeia de descoberta e vínculo `arquivo presente → detecção → leitura → identidade → competência → persistência → conferência`.

## 12. Empório Frios Itapaci
- Houve rescisão de funcionários em agosto.
- O Domínio provavelmente incorporou valores de garantias do consignado na rescisão, enquanto a API trouxe parcela mensal contratual.
- Correção: com rescisão, separar parcela mensal de garantias/rescisão e cruzar TRCT/Extrato/eConsignado/FGTS rescisório de forma composta.
- Se o cliente já estava fechado e surge mudança material, usar fluxo de retificação; não alterar fechamento silenciosamente.

## 13. Empresa Funerária Itapax
- Não houve situação atípica que justificasse ausência de GFD.
- A guia muito provavelmente existia.
- Correção: tratar como provável falha de descoberta/leitura/vínculo e validar fisicamente na auditoria.

## 14. GL Auto Center
- Empregado afastado por acidente de trabalho.
- FGTS continua devido.
- Não há desconto normal de consignado porque o empregado recebe benefício do INSS.
- Existe comunicado de pagamento direto do consignado pelo trabalhador à instituição financeira.
- Correção: `afastamento por acidente + pagamento direto comunicado` explica a ausência de desconto em folha; não gerar divergência de eConsignado. FGTS continua sendo conferido normalmente.

## 15. Gold Pallace Hotel
- Único empregado afastado por auxílio-doença.
- Sem pró-labore.
- Sem salário a pagar na competência.
- Sem DARF e sem FGTS.
- Correção: `afastamento integral + ausência de remuneração + bases zeradas` deve resultar em obrigações não aplicáveis, e não incompleto.

## 16. J Bernardes / Odonto Art
- Inicialmente as guias estavam ausentes.
- Depois foram adicionadas DARF e FGTS.
- Mesmo após reprocessamento, o Tools continuou apontando ausência.
- Correção: reprocessamento deve incorporar documentos adicionados depois da primeira execução e recalcular a conferência.

## 17. Jair Ferreira Camargo
- Existem duas matrículas rurais, matriz e filial.
- DARF é centralizada pela RFB e a Domínio centraliza a parte previdenciária na matriz.
- FGTS, porém, continua separado nos dois Extratos Domínio.
- O motor tratou apenas uma inscrição.
- Correção: manter extratos por inscrição, mas consolidar FGTS no nível do empregador/grupo antes de comparar com a GFD consolidada. Distinguir identidade documental de unidade de consolidação.

## 18. Larissa B Maia
- Não há empregados registrados.
- Não há FGTS.
- Existe apenas DARF previdenciária de R$ 178,31, localizada no mesmo valor.
- Correção: sem empregados + FGTS zero + DARF batida = conferido, sem exigir apuração extra artificial.

## 19. Lourenconi & Modesto
- Domínio e API divergem em R$ 230,91 em contrato da Viviane.
- Não há explicação operacional confirmada.
- Pode haver duplicidade/erro no retorno governamental.
- Correção: criar categoria `Inconsistência entre fontes — requer confirmação`. Antes de bloquear, comparar contrato por contrato, identificador, empregado, situação do vínculo, pagamento direto e duplicidades de API. Não escolher automaticamente qual fonte está errada.

## 20. Luriel Ferreira Malheiros
- Cliente MEI.
- Mesma regra da Elenice.
- Correção: DAE é a referência; não exigir GFD autônoma; separar componente federal e FGTS do DAE.

## 21. Marcos Augusto Pimentel Daibert
- Produtor rural PF.
- Empregado afastado pelo INSS durante a competência.
- Sem valores a recolher.
- Correção: afastamento integral + remuneração/bases zeradas = sem DARF/FGTS, sem incompletude artificial.

## 22. Maria Virginia S Souto
- Cliente em saída do escritório, com desligamento previsto para 31/08.
- Na tentativa de transmissão ao eSocial, foi constatada procuração revogada.
- Correção: justificar somente a DARF como `Impedimento externo — procuração RFB revogada`, com contexto e auditoria. Competências posteriores devem respeitar a saída do ciclo.

## 23. Ponto Kent
- INSS apurado R$ 893,45.
- Salário-família R$ 135,08.
- Saldo R$ 758,37.
- DARF localizada R$ 758,37.
- FGTS Domínio e GFD R$ 722,15.
- Correção: motor deve reconhecer as deduções previdenciárias e marcar conferido.

## 24. Predileta
### DARF
- Regra administrativa: a equipe Fiscal emite a DARF consolidada com tributos fiscais + parte previdenciária.
- O DP só gera FGTS.
- Correção: permitir parametrização `DARF — responsabilidade da equipe Fiscal`, não bloqueante para o fechamento do DP, mantendo possibilidade de anexação posterior para histórico/conferência.

### eConsignado
- Houve rescisão da empregada Josiane na competência.
- Correção: analisar contratos no contexto rescisório, garantias e eventual recolhimento rescisório; não tratar como simples parcela mensal ausente.

## 25. Ribeiro e Nascimento Art Vidros
- Caso de consignados e garantias na rescisão.
- Correção: separar parcela mensal, garantias utilizadas e recolhimento rescisório; cruzar TRCT/Extrato/FGTS/eConsignado sem comparar totais cegamente.

## 26. S S Santos Empreendimentos
- No primeiro processamento ainda não havia cálculo de valores.
- Depois foram apurados e adicionados relatórios/guias.
- O reprocessamento não incorporou corretamente os novos documentos.
- Correção: cliente deve poder evoluir de `sem dados` para `dados disponíveis`, invalidando o estado operacional anterior e recompondo a conferência.

## 27. T L Empreendimentos Agrícolas
- Cliente configurado para 2ª chamada.
- Entrou indevidamente no processamento/conferência da 1ª chamada.
- Correção: chamada futura fica fora do universo operacional atual, sem gerar divergência, incompleto ou bloqueio. Deve aparecer apenas como `Aguardando 2ª chamada` até liberação.

## 28. Wilmar Ferreira Pires
- Empregado com faltas em todos os dias da competência.
- Sem remuneração e sem guias a emitir.
- Correção: `faltas integrais na competência + remuneração/base zerada` deve resultar em obrigações não aplicáveis, com observação explicativa, e não incompleto.

# Regras transversais consolidadas

1. **Reprocessamento completo e não destrutivo**
   - detectar arquivo novo/alterado;
   - versionar;
   - preservar histórico;
   - não substituir resultado bom por leitura pior;
   - revarrer conexões;
   - aguardar processamento dos arquivos novos;
   - recalcular todos os cruzamentos da conferência.

2. **Domínio como fonte contextual, não apenas numérica**
   - ler empregados ativos;
   - demitidos e data efetiva de desligamento;
   - afastamentos;
   - faltas integrais;
   - salário-família e demais deduções;
   - bases e valores de FGTS;
   - composição previdenciária;
   - múltiplas inscrições/matrículas.

3. **eConsignado antes dos arquivos, mas não como verdade isolada**
   - consulta antecede Domínio/eSocial;
   - conclusão só após cruzar com vínculo real, afastamento, rescisão, pagamento direto e recolhimentos;
   - retorno residual sem vínculo ativo vira observação, não bloqueio;
   - divergência sem explicação vira `Inconsistência entre fontes — requer confirmação`.

4. **FGTS**
   - aceitar múltiplas guias/evidências na competência;
   - tratar recolhimento mensal, rescisório e antecipado de forma composta;
   - FGTS zero não gera ausência artificial;
   - produtores rurais PF e múltiplas matrículas exigem consolidação adequada.

5. **MEI**
   - DAE é a referência normal;
   - não exigir GFD autônoma;
   - separar corretamente componente federal e FGTS do DAE.

6. **Afastamentos e ausência de remuneração**
   - auxílio-doença, acidente de trabalho e outras situações devem alterar expectativas documentais conforme incidência real;
   - bases/valores zerados com contexto suficiente não devem ser classificados como informação insuficiente.

7. **Justificativas por fonte**
   - DARF, FGTS e eConsignado devem poder ser resolvidos separadamente;
   - motivos como procuração expirada/revogada devem ser auditáveis e não mascarar outras pendências.

8. **Chamadas**
   - cliente em chamada futura não participa do ciclo atual.

9. **Impressão**
   - manter bloqueio: somente documentos batidos/conferidos podem ser liberados pelo Centro de Impressão.
   - Em 27/08/2026, guias pendentes foram impressas manualmente fora do Axiom Tools; isso não constitui homologação do fluxo.

10. **Retificação**
   - se um cliente fechado recebe mudança material posterior, abrir fluxo de retificação; nunca alterar fechamento anterior silenciosamente.

# Próxima etapa

Incorporar estas regras na correção consolidada sobre o ZIP canônico de 27/08/2026 e continuar a auditoria A→Z, incluindo simplificação de duplicidades, reprocessamento, conferência, filtros, monitor, eConsignado, impressão A4 e regressão integral.
