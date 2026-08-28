# Mapa de transição de testes — V7 para V8

Data: 28/08/2026
Status: **contrato de atualização de regressão / arquivos de teste atuais ainda a confrontar na árvore canônica**

## 1. Objetivo

Evitar dois erros durante a correção da V8:

1. alterar código correto da V8 apenas para satisfazer teste que protege comportamento V7 superado;
2. apagar teste antigo sem criar regressão equivalente para o novo contrato.

Teste legado só deve mudar quando a regra posterior estiver documentada e a cobertura substituta existir.

## 2. Regra V7: `PRONTA` apresentada como `Em conferência`

V7 determinou explicitamente:

`PRONTA -> Em conferência`

Na V8 essa equivalência foi superada.

### Regra V8

- `PRONTA`/elegível sem evidência processada -> `Aguardando processamento`;
- sessão ativa -> `Em processamento`;
- evidência suficiente para análise -> `Em conferência`.

### Teste antigo a substituir

Qualquer teste que afirme apenas:

```text
status PRONTA => label Em conferência
```

não é mais canônico.

### Regressão substituta

Testar a transição por evidência/estágio real.

## 3. Regra V7: Ciclo atual incluía liberadas + fechadas

V7 definiu a Central de Conferência com escopo padrão contendo liberadas + fechadas, excluindo adiadas.

Na V8 a mesa padrão é trabalho vivo.

### Regra V8

- PRONTA/EM_CONFERENCIA da chamada corrente: mesa viva;
- FECHADA: histórico/consulta;
- RETIFICACAO: fluxo próprio;
- chamada futura: fora da mesa corrente.

### Teste antigo a substituir

Teste que exige FECHADA dentro de `CICLO` por padrão.

### Regressão substituta

- cliente fechado não aparece na mesa normal;
- histórico fechado continua acessível;
- nova mudança material gera retificação, não retorno à mesa comum.

## 4. Regra V7: decisão manual global pode concluir o ciclo

V7 permitia decisão manual `Conferido/Justificado` na Central concluir o cliente.

Os casos reais de agosto provaram que essa granularidade é insuficiente.

### Regra V8

Decisão é por fonte/obrigação.

DARF justificada não conclui FGTS/eConsignado.

### Teste antigo a substituir

Teste que grava decisão global e espera `FECHADA` independentemente das demais fontes.

### Regressão substituta

- justificar DARF;
- manter FGTS pendente;
- cliente continua aberto;
- somente todas as obrigações conclusivas permitem fechamento.

## 5. Regra V7: retificação dentro do escopo amplo de Conferência

V4/V7 permitiam que retificação estivesse no escopo amplo da Conferência.

V8 separa retificação da mesa viva.

### Preservar

- detecção material;
- snapshot anterior;
- candidata Vn+1;
- bloqueio de saída;
- conclusão versionada.

### Alterar

- localização visual/operacional da retificação.

### Regressão substituta

- retificação aparece na área própria;
- não mistura contadores da chamada corrente;
- conclusão mantém versão anterior.

## 6. Regra V7: próxima chamada fora do ciclo

Essa regra continua válida e deve ser preservada.

Não é teste legado a remover.

### Regressão obrigatória

T L Empreendimentos Agrícolas permanece chamada 2 durante toda a chamada 1, mesmo após refresh/processamento/eConsignado/reinício.

## 7. Regra V7: sem movimento mensal não herdado automaticamente

Essa regra continua válida e foi reforçada pela V8.

Não remover teste que garanta:

- nova competência nasce `COM_MOVIMENTO` por padrão conforme contrato vigente;
- marcação mensal é explícita;
- cadastro histórico não sobrepõe composição mensal;
- reversão preserva histórico.

## 8. Regra V7: impressão/entrega exigem FECHADA

Continua válida e deve ficar mais forte na V8.

Não remover.

### Regressão nova

Além da UI/listagem, testar o backend/serviço e seleção direta por IDs.

## 9. Regra V4: saída bloqueada durante retificação

Continua válida integralmente.

Não remover.

Deve ser ampliada para:

- impressão;
- entrega;
- saídas automáticas;
- qualquer chamada direta de serviço.

## 10. Regra de sessão técnica

Se testes antigos esperarem `COM_PENDENCIAS` em sessão apenas por divergência de Conferência, devem ser revisados.

### Regra V8

Sessão técnica:

- 100% percorrida sem falha técnica = concluída;
- divergência de negócio pertence à Conferência.

### Regressão substituta

Testar separadamente:

- conclusão técnica;
- contador de falhas técnicas;
- estado de negócio do cliente.

## 11. Não alterar testes por aparência de sucesso

Procedimento obrigatório para cada falha da suíte:

1. identificar expectativa;
2. localizar contrato que a originou;
3. verificar se o contrato ainda vale;
4. classificar:
   - falha funcional real;
   - teste legado superado;
   - falha ambiental;
   - risco não reproduzido;
5. se superado, criar primeiro o novo teste;
6. só depois remover/alterar expectativa antiga.

## 12. Matriz resumida

| Comportamento | V7 | V8 | Ação no teste |
|---|---|---|---|
| `PRONTA = Em conferência` | Sim | Não necessariamente | Substituir |
| FECHADA no ciclo padrão da Central | Sim | Não | Substituir |
| Retificação na mesa comum | Sim | Não | Substituir mantendo lógica de versão |
| Decisão manual global fecha cliente | Sim | Não | Substituir por fonte |
| Próxima chamada fora do ciclo | Sim | Sim | Preservar/reforçar |
| Sem movimento mensal separado | Sim | Sim | Preservar/reforçar |
| Saídas exigem FECHADA | Sim | Sim | Preservar e ampliar backend |
| Retificação bloqueia saída | Sim | Sim | Preservar e ampliar |
| 100% técnico = sessão concluída | Parcial/inconsistente | Sim | Ajustar sem confundir negócio |

## 13. Critério de conclusão

A suíte V8 deve testar o comportamento aprovado atual, sem apagar garantias antigas que continuam válidas e sem manter expectativas que contradizem a arquitetura posterior.
