# Contrato V8 — Concorrência SQLite, workers e consistência lógica

Data: 28/08/2026
Status: **fundação SQLite anterior confirmada / concorrência lógica V8 ainda não homologada**

## 1. Fundação existente

A consolidação estrutural do Axiom Tools já registrou para o SQLite:

- foreign keys habilitadas;
- `busy_timeout=10000`;
- WAL;
- `synchronous=NORMAL`;
- acesso ao banco somente pelo backend no servidor;
- SQLite Backup API para backup consistente.

Essa fundação continua adequada ao estágio atual e não há evidência que justifique migrar para PostgreSQL/MySQL apenas por causa da V8.

## 2. O que WAL resolve e o que não resolve

WAL/busy timeout ajudam a lidar com concorrência física de leitura/escrita.

Eles NÃO impedem concorrência lógica, por exemplo:

1. rotina A lê cliente em chamada 1;
2. usuário move para chamada 2;
3. rotina A grava depois seu snapshot antigo e devolve chamada 1.

Esse tipo de erro exige controle de estado/versão/compare-and-set, não troca de banco.

## 3. Escritas curtas

Transações SQLite de mutação devem ser curtas.

Não manter transação aberta enquanto:

- lê PDF;
- executa OCR;
- chama API externa;
- aguarda filesystem;
- renderiza relatório;
- espera ação humana.

Fluxo correto:

```text
processar fora da transação
-> abrir transação curta
-> validar estado esperado
-> persistir/promover
-> commit
```

## 4. Reprocessamento

Nova leitura deve ocorrer fora da transação que protege a versão vigente.

A promoção do candidato usa transação curta e compare-and-set sobre a versão esperada.

Exemplo conceitual:

```text
promover candidato somente se vigente_id ainda for o mesmo que foi comparado
```

Se outra rotina promoveu versão antes, recarregar e reavaliar em vez de sobrescrever.

## 5. Fechamento e chamada

Mudar status/chamada deve validar o estado lido originalmente.

Exemplo:

```sql
UPDATE fechamento_mensal_cliente
SET status=?, chamada=?
WHERE competencia=?
  AND cliente_id=?
  AND status=?
  AND chamada=?
```

A quantidade de linhas afetadas deve ser conferida.

Zero linhas = conflito/estado alterado; não assumir sucesso.

## 6. Obrigações por fonte

Ao resolver DARF/FGTS/eConsignado, a gravação deve considerar versão/`updated_at` quando houver possibilidade de dois usuários/processos atuarem na mesma obrigação.

Se o estado mudou entre leitura e gravação, exigir recarga/confirmação quando a ação não puder ser mesclada de forma segura.

## 7. Workers e jobs

A V8 utiliza processamento em fila/jobs e deverá crescer em volume.

Para qualquer fila persistente, o claim de item precisa ser atômico.

Modelo conceitual:

```text
PENDENTE -> PROCESSANDO
```

somente por um worker.

A implementação final deve provar que dois workers/retries não processam e promovem o mesmo item simultaneamente.

O código integral de claim da fila não foi recuperado nesta sessão; portanto não há defeito confirmado neste ponto, mas há regressão obrigatória.

## 8. Idempotência de worker

Reexecutar o mesmo item após falha/restart não pode:

- duplicar documento;
- duplicar valores;
- duplicar histórico;
- duplicar retificação;
- duplicar saída;
- perder versão vigente.

Hash e identidade lógica devem participar da deduplicação, lembrando que hash diferente não implica obrigação econômica diferente.

## 9. Lease/timeout de item em processamento

Se a fila usa estado `PROCESSANDO`, precisa haver política para worker morto/restart.

A implementação pode usar lease/timestamp/tentativas ou mecanismo equivalente.

Requisito funcional:

- item abandonado pode ser recuperado;
- item ativo não é roubado por outro worker prematuramente;
- retry é auditável;
- limite de tentativas/erro técnico não transforma pendência de negócio em falha técnica.

## 10. Ordem dos especialistas

O orquestrador mensal deve respeitar a sequência canônica sem exigir uma transação longa:

`eConsignado -> Domínio -> eSocial -> e-CAC/DARF -> FGTS Digital -> cruzamento`

Cada etapa grava checkpoint próprio e é retomável.

Falha em uma etapa não deve apagar resultados válidos das etapas anteriores.

## 11. Recalculo da Conferência

Vários eventos podem solicitar recálculo do mesmo cliente/competência em sequência.

O recálculo deve ser:

- idempotente;
- derivado das evidências vigentes;
- seguro contra chamadas duplicadas;
- incapaz de fechar usando snapshot anterior à última decisão/documento.

Quando possível, usar número de revisão/versão das evidências para detectar cálculo obsoleto.

## 12. Saídas

Geração de saída também precisa de proteção contra corrida:

1. gate autoriza cliente fechado;
2. antes de persistir/entregar, confirmar que não surgiu retificação material posterior ao gate;
3. vincular saída à versão de fechamento que a autorizou.

Assim uma retificação criada durante a geração não produz saída silenciosamente associada ao estado errado.

## 13. Backup

O backup consistente deve continuar usando SQLite Backup API com coordenação adequada do runtime.

Para atualizações/migrações de versão, o procedimento já adotado de parar o backend antes de alterar a base real continua preferível.

Não copiar `.sqlite` cru em momento arbitrário como única estratégia de backup operacional quando houver escrita ativa.

## 14. Testes de concorrência obrigatórios

1. dois pedidos de reprocessamento do mesmo arquivo;
2. promoção concorrente de dois candidatos;
3. usuário move chamada enquanto recálculo usa snapshot antigo;
4. dois usuários resolvem a mesma fonte;
5. worker morre após claim e item é recuperado;
6. dois workers tentam claim do mesmo item;
7. retry não duplica retificação;
8. dois eventos pedem recálculo simultâneo;
9. retificação nasce enquanto saída está sendo preparada;
10. `database is locked` não deixa operação parcialmente persistida;
11. restart do backend recupera itens pendentes/processando conforme política;
12. integridade permanece `ok` após cenários concorrentes.

## 15. T L como teste de corrida

Além da regressão funcional normal, executar cenário específico:

- processo A carrega T L em chamada 1;
- usuário grava chamada 2;
- processo A tenta persistir estado calculado sobre snapshot antigo.

Resultado obrigatório:

- chamada 2 permanece;
- escrita obsoleta é rejeitada/reciclada;
- histórico não fica contraditório.

## 16. Critério de homologação

WAL ativo não basta para declarar concorrência segura.

A V8 só estará homologada quando transições críticas forem protegidas contra estado obsoleto e workers/jobs forem idempotentes e recuperáveis.
