# Mapa de transição — regras V4/V7 → contrato V8

Data: 28/08/2026
Status: **apoio obrigatório à auditoria e à atualização da suíte de regressão**

Este documento identifica regras que foram corretas em versões anteriores, mas foram superadas por decisões posteriores da arquitetura V8. O objetivo é evitar dois erros opostos:

- manter comportamento antigo apenas porque existe teste legado;
- apagar teste válido sem registrar qual contrato posterior o substituiu.

## 1. Escopo `Ciclo atual` da Central de Conferência

### Contrato V7

A V5.6.14V7 definiu `Ciclo atual` como:

- empresas liberadas;
- empresas já fechadas;
- excluindo adiadas.

### Contrato V8

A mesa normal de Conferência passa a representar trabalho vivo da chamada corrente.

- clientes fechados ficam em histórico/snapshot;
- nova evidência material em fechado gera retificação;
- retificação possui fluxo próprio.

### Migração de teste

Teste que espera `FECHADA` dentro da mesa normal do ciclo deve ser atualizado para esperar ausência do fechado no trabalho vivo e presença no histórico/visão específica.

## 2. `PRONTA` apresentada como `Em conferência`

### Contrato V7

A V7 determinou que `PRONTA` fosse apresentada como `Em conferência`.

### Contrato V8

O estado visual deve refletir estágio real:

- sem evidência documental processada → `Aguardando processamento`;
- motor trabalhando → `Em processamento`;
- evidência processada e cliente encaminhado à mesa → `Em conferência`.

### Migração de teste

Teste que converte `PRONTA` diretamente em rótulo `Em conferência` sem verificar evidência/processamento é legado.

## 3. Decisão manual global `Conferido/Justificado`

### Contrato V7

A decisão manual global podia concluir o ciclo do cliente.

### Contrato V8

A decisão deve ser específica por fonte/obrigação.

Exemplos:

- DARF impedida externamente não resolve FGTS;
- FGTS rescisório resolvido não resolve DARF;
- DARF do Fiscal não libera eConsignado;
- ausência de desconto de consignado justificada não altera obrigação de FGTS.

O fechamento agregado deriva do conjunto de obrigações aplicáveis.

### Migração de teste

Teste que aplica uma única decisão ao cliente inteiro e espera `FECHADA` precisa ser substituído por cenários por fonte.

## 4. Retificação dentro da mesma mesa da Conferência

### Contrato V4

A V5.6.14V4 incluía empresas em retificação no escopo de Conferência/Auditoria do fechamento.

### Contrato V8

Retificação continua pertencendo à competência, mas deve ser tratada em fluxo próprio:

- snapshot anterior preservado;
- candidato Vn → Vn+1;
- saídas bloqueadas;
- análise de deltas;
- conclusão explícita da retificação;
- sem contaminar a mesa normal da chamada corrente.

### Migração de teste

Teste que exige `RETIFICACAO` no escopo operacional comum precisa passar a verificar a área/fluxo próprio de retificação.

## 5. `Sem movimento` e fechamento automático

### Contrato V7 válido em essência

A marcação mensal explícita `Sem movimento` encerra expectativas incompatíveis daquela competência sem alterar o cadastro permanente.

### Ajuste V8

A composição mensal é soberana quando existe. O cadastro histórico é somente fallback.

### Testes a preservar

- marcação mensal explícita reduz expectativas;
- reversão da marcação recompõe o ciclo;
- histórico da decisão é preservado.

### Testes a remover/alterar

- qualquer teste em que `cadastro.movimento_folha == SEM_MOVIMENTO` prevaleça sobre composição mensal explícita `COM_MOVIMENTO`.

## 6. Chamadas

### Contrato V7

Empresa em chamada futura não é cobrada no ciclo atual.

### Contrato V8

Regra permanece válida e ganha exigência de persistência/auditoria imediata:

- chamada anterior;
- nova chamada;
- motivo;
- observação;
- usuário;
- data/hora.

### Regressão crítica

T L Empreendimentos Agrícolas não pode permanecer `PRONTA`, chamada 1, após decisão válida de envio para 2ª chamada.

## 7. Retificação candidata/versionada

### Contrato V4 válido e preservado

A V4 já estabelecia:

- snapshot fechado versionado;
- mudança material cria candidato;
- versão anterior preservada;
- saída bloqueada durante retificação.

### Lacuna descoberta na V8 auditada

O reprocessamento documental comum ainda pode destruir a versão vigente antes de validar a nova leitura.

### Regra de continuidade

O conceito candidato/versionado da retificação deve ser estendido ao reprocessamento de documento:

- nova leitura é candidata;
- versão vigente não é apagada;
- promoção depende de comparação;
- leitura pior é rejeitada sem degradar produção.

## 8. `PROCESSADO` x `CONFERIDO/FECHADO`

### Contrato V7/V8

`PROCESSADO` deve significar execução técnica do motor, não autorização de saída.

### Achado atual

Saídas automáticas ainda usam `PROCESSADO` como condição equivalente a validado.

### Teste vigente obrigatório

Qualquer documento de cliente não `FECHADA`, ou com retificação pendente, deve ser rejeitado pelo gate de saída mesmo que o documento esteja tecnicamente `PROCESSADO`.

## 9. Gate de Impressão e Entregas

### Contrato anterior válido

Entregas e impressão dependem de `FECHADA`.

### Lacuna atual

Parte da proteção ficou somente na listagem/interface e pode ser contornada por ações diretas/seleção de IDs.

### Contrato V8

O gate deve existir no backend e ser reutilizado por:

- impressão individual;
- impressão selecionada;
- lote;
- entrega individual;
- entrega selecionada;
- entrega em lote;
- saídas automáticas.

## 10. Regra de atualização da suíte

Ao revisar testes do pacote canônico, cada alteração de expectativa deve registrar:

- comportamento anterior;
- versão que o introduziu;
- contrato V8 substituto;
- razão operacional real;
- caso de regressão correspondente.

Nenhum teste deve ser alterado apenas para "ficar verde".

Da mesma forma, nenhum comportamento antigo deve sobreviver apenas porque um teste o codificou antes da V8.
