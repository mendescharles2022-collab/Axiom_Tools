# Contrato V8 — Transições do Fechamento Mensal e chamadas

Data: 28/08/2026
Status: **contrato de regressão / causa exata da reversão T L ainda não isolada**

## 1. Evidência disponível

A árvore operacional real de 26/08 contém `modules/closing/service.py` com:

- criação de `fechamento_mensal` e `fechamento_mensal_cliente`;
- tabela `fechamento_mensal_historico`;
- atualização de status/chamada/impedimento em torno da linha 150;
- fechamento em torno da linha 177;
- atualização de `chamada_atual` em torno da linha 202;
- atualização de clientes para `PRONTA`/chamada em torno da linha 205;
- helpers de conjuntos de clientes em torno das linhas 214/219.

Também existe `closing/retification.py` com histórico, versões e atualização para `RETIFICACAO`.

O snapshot auditado de 08/2026 mostra T L Empreendimentos Agrícolas como `PRONTA`, chamada 1, apesar da decisão operacional de 2ª chamada.

Ainda não há evidência suficiente para afirmar se a causa foi:

- falha no comando que adiou;
- falha na persistência do histórico;
- sincronização posterior que sobrescreveu o estado;
- migração/backfill;
- recomposição indevida do ciclo.

Por isso a causa permanece `A ISOLAR`.

## 2. Máquina de transição

Transições devem ser explícitas, validadas e auditáveis.

### Abertura da competência

Cliente elegível começa na chamada 1 com estado operacional inicial compatível com a arquitetura V8.

### Adiar para próxima chamada

Ao adiar um cliente:

- nova chamada > chamada atual;
- status agregado deve refletir `ADIADA`/próxima chamada;
- motivo/impedimento obrigatório conforme ação;
- histórico registra estado anterior e novo;
- cliente sai imediatamente do universo operacional da chamada atual;
- nenhuma sincronização de Conferência pode trazê-lo de volta antes da chamada correspondente.

### Avançar chamada

Ao avançar `chamada_atual`:

- somente clientes programados para essa nova chamada são liberados;
- clientes de chamadas posteriores continuam adiados;
- clientes fechados não reabrem;
- clientes em retificação não retornam ao ciclo normal;
- histórico da liberação é registrado.

### Fechar

Fechamento ocorre somente por regra derivada das obrigações aplicáveis ou evento válido de conclusão.

### Retificação

Nova evidência material em `FECHADA` cria `RETIFICACAO`, preservando versão anterior.

## 3. Proibição de atualização ampla destrutiva

Nenhum `UPDATE` em massa de mudança de chamada pode selecionar clientes apenas por competência sem predicado suficiente de estado/chamada alvo.

Antes de executar qualquer transição em lote, a implementação deve definir explicitamente:

```text
competencia
status atual permitido
chamada atual esperada
chamada destino
```

Se o estado atual não corresponder ao esperado, a operação deve falhar ou ignorar de forma auditável; não sobrescrever silenciosamente.

## 4. Concorrência e compare-and-set

Para evitar que sincronizações concorrentes revertam decisão administrativa, transições sensíveis devem preferir semântica de compare-and-set:

```sql
UPDATE ...
SET ...
WHERE competencia=?
  AND cliente_id=?
  AND status=?
  AND chamada=?
```

A quantidade de linhas afetadas precisa ser verificada.

Se zero linhas forem alteradas, o sistema deve recarregar o estado e informar conflito de transição em vez de assumir sucesso.

## 5. Histórico como prova, não decoração

Cada evento de chamada deve registrar:

- competência;
- cliente;
- estado anterior;
- chamada anterior;
- novo estado;
- nova chamada;
- motivo/impedimento;
- observação;
- usuário;
- data/hora;
- origem/ação que provocou a transição.

A projeção atual precisa ser reconciliável com a sequência histórica.

## 6. Invariante de chamada futura

Para qualquer cliente:

```text
cliente.chamada > fechamento.chamada_atual
=> cliente NÃO pertence ao universo operacional corrente
```

Isso vale para:

- Processamento;
- Conferência;
- eConsignado;
- alertas/pendências do ciclo;
- Impressão/Entregas por competência corrente.

## 7. Invariante de FECHADA

```text
status = FECHADA
```

não pode ser convertido para `PRONTA` por avanço de chamada, abertura de tela ou recomposição comum.

Somente mudança material cria fluxo de `RETIFICACAO`.

## 8. Invariante de RETIFICACAO

`RETIFICACAO` não pode ser liberada para a chamada corrente como `PRONTA` por rotina genérica de avanço.

A conclusão de retificação usa fluxo próprio e gera nova versão.

## 9. Regressão T L Empreendimentos Agrícolas

Cenário obrigatório:

1. competência 08/2026 aberta na chamada 1;
2. T L inicialmente elegível;
3. usuário move T L para chamada 2 com motivo;
4. confirmar banco imediatamente;
5. abrir/atualizar Conferência;
6. processar outros clientes;
7. sincronizar fechamento;
8. executar eConsignado da chamada 1;
9. reiniciar aplicação;
10. consultar novamente o fechamento.

Em todos os passos 4–10, enquanto `chamada_atual=1`:

```text
T L = ADIADA / chamada 2
```

e não aparece como pendência da 1ª chamada.

Depois de avançar explicitamente para chamada 2:

- T L é liberada uma única vez;
- histórico registra `ADIADA -> liberada na chamada 2`;
- não perde o motivo histórico do adiamento.

## 10. Teste de colisão

Simular:

- usuário adia cliente para chamada 2;
- processo de sincronização carrega snapshot antigo da chamada 1;
- sincronização tenta gravar estado antigo depois da decisão administrativa.

Resultado obrigatório:

- decisão mais recente não é sobrescrita;
- compare-and-set impede escrita obsoleta;
- conflito é auditado se necessário.

## 11. Critério de homologação

A falha da T L só pode ser marcada corrigida após identificar o ponto de reversão ou provar por regressão que todas as rotas capazes de alterar status/chamada obedecem aos invariantes acima.
