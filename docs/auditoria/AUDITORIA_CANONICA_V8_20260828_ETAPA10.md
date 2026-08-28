# Auditoria canônica V8 — Etapa 10

Data: 28/08/2026
Status: **auditoria em andamento / nenhum pacote final liberado**

## 1. Escopo desta etapa

A Etapa 10 auditou a concorrência operacional entre:

- SQLite;
- backend;
- workers/jobs;
- Fechamento Mensal;
- reprocessamento;
- Conferência;
- saídas.

O objetivo foi separar concorrência física do banco de concorrência lógica de negócio.

## 2. Fundação SQLite anterior permanece adequada

A consolidação estrutural já registrou:

- foreign keys;
- `busy_timeout=10000`;
- WAL;
- `synchronous=NORMAL`;
- banco acessado apenas pelo backend do servidor;
- SQLite Backup API.

Não há evidência de que a V8 exija troca de banco apenas para resolver os defeitos atuais.

## 3. WAL não resolve escrita obsoleta

O caso T L e outras transições demonstram risco de concorrência lógica:

```text
rotina lê estado A
usuário grava estado B
rotina antiga grava novamente estado A
```

Mesmo com WAL perfeito, essa sequência é possível se o código não validar versão/estado esperado.

A correção exige compare-and-set/controle otimista nas transições críticas.

## 4. Transações longas devem ser evitadas

PDF/OCR/API/filesystem não devem ocorrer dentro de transação SQLite longa.

Fluxo canônico:

1. coletar/processar candidato fora da transação;
2. abrir transação curta;
3. verificar estado/versão vigente;
4. persistir/promover;
5. commit;
6. recalcular projeções/eventos de forma idempotente.

## 5. Reprocessamento concorrente

Dois reprocessamentos do mesmo documento não podem promover versões independentemente sem verificar qual vigente foi comparado.

Promoção deve falhar/reavaliar se a versão vigente mudou enquanto o candidato era processado.

Isso protege contra:

- leitura antiga sobrescrevendo leitura mais nova;
- duas promoções simultâneas;
- histórico fora de ordem.

## 6. Workers — ponto de auditoria ainda sem código integral

O código integral do claim da fila não foi recuperado nesta sessão.

Portanto não foi registrado defeito específico de claim duplicado.

Mas a regressão final deve provar:

- claim atômico;
- um item por worker;
- recuperação de item abandonado;
- retry idempotente;
- restart seguro;
- limite/tentativas auditáveis.

Classificação:

`RISCO OPERACIONAL A TESTAR`.

## 7. Recalculo da Conferência

Eventos duplicados podem pedir recálculo do mesmo cliente/competência.

O cálculo deve ser idempotente e derivar sempre das evidências vigentes.

Não pode fechar cliente com base em snapshot anterior a:

- documento recém-promovido;
- mudança de chamada;
- decisão por fonte;
- alteração de movimento;
- retificação.

## 8. Saída x retificação concorrente

A autorização de saída precisa ficar vinculada à versão de fechamento.

Cenário de teste:

1. cliente FECHADA passa no gate;
2. antes da saída persistir, surge mudança material/retificação;
3. sistema deve impedir que a saída seja registrada como se pertencesse ao novo estado.

A saída deve identificar a versão que a autorizou ou revalidar o gate antes da conclusão.

## 9. Backup

A estratégia já existente de SQLite Backup API continua correta.

Em atualização/migração, parar o backend antes de alterar a base real continua sendo a opção mais segura.

Não substituir por cópia cega do arquivo SQLite enquanto houver escrita ativa.

## 10. Testes de concorrência adicionados

1. dois reprocessamentos do mesmo arquivo;
2. promoção concorrente de candidatos;
3. T L movida para chamada 2 enquanto cálculo antigo tenta gravar chamada 1;
4. dois usuários resolvendo a mesma obrigação;
5. dois workers disputando o mesmo item;
6. worker morto e recuperação do item;
7. retry sem duplicar retificação;
8. dois recálculos simultâneos;
9. retificação surgindo durante saída;
10. lock/erro SQLite sem persistência parcial;
11. restart recuperando fila corretamente;
12. `integrity_check` após cenários concorrentes.

## 11. Documento produzido

- `CONTRATO_CONCORRENCIA_SQLITE_WORKERS_V8.md`;
- este documento.

## 12. Estado ao final da Etapa 10

A infraestrutura SQLite existente é suficiente como base, mas a V8 ainda precisa provar segurança contra concorrência lógica.

Continuam abertos para implementação/homologação:

- compare-and-set nas transições críticas;
- promoção versionada de reprocessamento;
- claim/idempotência de worker;
- recálculo idempotente;
- vínculo de saída à versão de fechamento;
- testes de corrida T L/reprocessamento/retificação.

Nenhum pacote V8 deve ser liberado antes da regressão integral.
