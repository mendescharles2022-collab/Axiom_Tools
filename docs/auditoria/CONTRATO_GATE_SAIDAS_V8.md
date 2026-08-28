# Contrato V8 — Gate único de autorização de saídas

Data: 28/08/2026
Status: **contrato de auditoria / implementação ainda não homologada**

## 1. Origem da regra

A regra de não liberar documentos antes de conferência não é nova.

A DEC-004 vinculante já determinava que o usuário deveria conferir antes de impressão, consolidação ou fechamento de lote, com pendências e conflitos visíveis.

A AXT-006 reforçou que pendências não devem ser escondidas para produzir lote artificialmente limpo.

A AXT-007 estabeleceu que somente documentos conferidos/selecionados entram no lote.

A arquitetura V8 acrescenta a necessidade de transformar essa regra funcional em autorização obrigatória de backend.

## 2. Falhas confirmadas na base canônica

### Centro de Impressão

- filtro visual de conferência pode ficar vazio;
- sem filtro, a listagem não fica obrigatoriamente restrita ao conjunto autorizado;
- seleção explícita de IDs no serviço não reaplica necessariamente `cliente_ids`/escopo permitido.

### Central de Entregas

- a listagem aplica escopo mais seguro;
- ações individuais/selecionadas podem chamar `gerar_cliente()` sem revalidar o mesmo gate no serviço.

### Saídas automáticas

- `processing/output.py` usa `row.status == 'PROCESSADO'` como equivalente a `somente_validados`;
- o worker pode gerar saída imediatamente após processamento técnico.

Essas três ocorrências representam o mesmo defeito arquitetural: autorização distribuída e inconsistente.

## 3. Princípio canônico

Toda saída final operacional passa por um único gate de backend.

Filtros, botões desabilitados e listagens são UX; não são segurança nem autorização.

`PROCESSADO` nunca equivale a `CONFERIDO` ou `FECHADO`.

## 4. Condições mínimas do gate

Existindo Fechamento Mensal para a competência, a saída é autorizada somente quando:

- cliente pertence à competência correspondente;
- cliente está `FECHADA`;
- todas as obrigações aplicáveis estão concluídas (`CONFERIDA`, `JUSTIFICADA` ou `NAO_APLICAVEL`, conforme regra válida);
- não existe retificação material pendente;
- documento pertence ao cliente/competência autorizados;
- ação solicitada é compatível com o destino/configuração do cliente;
- seleção manual de IDs é intersectada com o universo permitido.

## 5. Operações obrigatoriamente protegidas

O mesmo gate deve ser usado por:

- impressão individual;
- impressão selecionada;
- impressão em lote;
- prévia final do lote;
- geração de PDF consolidado;
- entrega eletrônica individual;
- entrega selecionada;
- entrega em lote;
- geração automática de saídas;
- qualquer chamada direta de serviço equivalente.

Nenhuma rota alternativa pode reconstruir uma versão simplificada dessa regra.

## 6. Retificação

Cliente fechado que recebe mudança material passa para fluxo de retificação.

Enquanto existir retificação material pendente:

- versão fechada anterior permanece preservada;
- nova saída operacional fica bloqueada;
- histórico da saída anterior permanece intacto;
- após conclusão da retificação, uma nova versão de saída pode ser gerada com rastreabilidade.

## 7. Contingência manual

A contingência realizada pelo escritório fora do Tools em 27/08 não altera o contrato do sistema.

Se futuramente existir função de contingência dentro do Tools, ela deve ser explícita, excepcional, auditável e não pode se disfarçar de saída normal autorizada.

Não criar bypass silencioso para “resolver urgência”.

## 8. Resposta de autorização

O gate deve retornar decisão explicável, por exemplo:

```text
autorizado = NAO
motivo = CLIENTE_NAO_FECHADO
cliente_id = ...
competencia = 08/2026
estado = PRONTA
```

ou:

```text
autorizado = NAO
motivo = RETIFICACAO_PENDENTE
```

Isso permite que Impressão, Entregas e worker exibam a mesma causa sem duplicar lógica.

## 9. Regressões obrigatórias

1. documento `PROCESSADO` de cliente `PRONTA` não imprime;
2. seleção manual por ID não burla gate;
3. chamada direta ao serviço de entrega não burla gate;
4. cliente `FECHADA` com retificação pendente não gera nova saída;
5. cliente `FECHADA` sem retificação pode gerar saída;
6. documento de outra competência não entra em lote por ID;
7. filtros visuais não alteram a decisão do backend;
8. Impressão, Entregas e Saídas automáticas retornam a mesma decisão para o mesmo cliente/competência;
9. histórico de lotes anteriores não é apagado por retificação;
10. falha de impressão/entrega não transforma documentos em concluídos automaticamente.

## 10. Critério de homologação

A V8 não pode ser homologada enquanto existir qualquer caminho capaz de liberar documento não autorizado pela mesma regra canônica de backend.
