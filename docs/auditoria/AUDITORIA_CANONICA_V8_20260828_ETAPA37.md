# Auditoria canônica V8 — Etapa 37

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 37 revisa B40 — concorrência lógica — contra o contrato já existente `CONTRATO_CONCORRENCIA_SQLITE_WORKERS_V8.md`.

## 2. Fundação física

A fundação SQLite anterior já trabalha com WAL, busy timeout, foreign keys e transações no backend.

Isso permanece adequado e não há evidência que justifique trocar de banco apenas por causa da V8.

## 3. Bloqueador real

Concorrência lógica é independente do mecanismo de lock do SQLite.

Exemplo crítico:

1. processo A lê estado/chamada/revisão N;
2. processo B grava N+1;
3. processo A tenta persistir resultado calculado sobre N;
4. a aplicação precisa rejeitar/recalcular, nunca sobrescrever N+1 silenciosamente.

## 4. Pontos que exigem compare-and-set/revisão esperada

No mínimo:

- promoção de candidato de reprocessamento;
- chamada/status mensal;
- decisão por fonte;
- movimento mensal;
- conclusão de retificação;
- recálculo/agregador do fechamento;
- autorização/persistência de saída quando pode surgir retificação concorrente.

## 5. T L como cenário-mestre

Executar regressão:

- rotina A carrega T L na chamada 1;
- usuário grava chamada 2;
- rotina A tenta gravar resultado antigo;
- zero linhas afetadas/conflito deve ser detectado;
- chamada 2 permanece;
- histórico registra apenas transições válidas.

## 6. Reprocessamento

Nova leitura ocorre fora da transação curta de promoção.

Ao promover:

- validar que a versão vigente ainda é a comparada;
- se mudou, recarregar/reavaliar;
- nunca substituir uma versão mais nova com candidato calculado sobre base antiga.

## 7. Jobs/workers

O claim de item precisa ser atômico e retry idempotente.

Ainda não foi recuperado o código integral do claim/lease da fila V8, portanto:

- não é declarado defeito específico nessa implementação;
- continua teste obrigatório no runtime reconciliado.

## 8. Conferência event-driven

Dois eventos simultâneos de recálculo do mesmo cliente devem convergir para o estado derivado das evidências vigentes.

Um recálculo antigo não pode fechar o cliente ignorando decisão/documento mais recente.

## 9. Saídas

Entre autorização e persistência da saída, validar que a versão de fechamento continua vigente e que nenhuma retificação material nasceu.

Saída deve ficar vinculada à versão que efetivamente a autorizou.

## 10. Evidência de homologação

Rodar os testes de concorrência do contrato, incluindo:

- dois reprocessamentos do mesmo arquivo;
- candidatos concorrentes;
- dois usuários na mesma obrigação;
- worker morto/recovery;
- dois workers no mesmo item;
- dois recálculos;
- retificação durante geração de saída;
- escrita obsoleta da chamada T L.

Registrar estado antes/depois, rowcount/conflito, correlation_ids e integridade final do SQLite.

## 11. Estado do bloqueador

B40 permanece `CONTRATO_OBRIGATORIO` / execução pendente no runtime.

Nenhuma evidência desta etapa autoriza marcá-lo como corrigido.

## 12. Próxima frente

Auditar B37 — máquinas de estado misturadas — e garantir que sessão técnica, documento, obrigação, cliente mensal, consulta externa e retificação não compartilhem rótulos com significados incompatíveis.
