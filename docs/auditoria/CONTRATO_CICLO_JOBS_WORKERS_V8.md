# Contrato V8 — Ciclo de vida de jobs, workers e retomada

Data: 28/08/2026
Status: **contrato de auditoria / verificação direta do worker integral pendente**

## 1. Motivo

A V8 utiliza processamento em fila, jobs de integração e execução incremental. Em ambiente Windows de escritório, backend/worker pode ser reiniciado por atualização, manutenção, falha ou reboot.

A operação não pode depender de um processo permanecer vivo do início ao fim para preservar a verdade do ciclo.

## 2. Princípio

Estado essencial de job deve ser persistido. Memória do processo pode acelerar execução, mas não pode ser a única fonte para saber:

- o que foi solicitado;
- por quem;
- para qual competência/chamada;
- qual item estava em execução;
- quais itens já concluíram;
- o que precisa ser retomado;
- se a execução falhou ou foi interrompida.

## 3. Estados do job

Vocabulário conceitual:

```text
CRIADO
AGUARDANDO
EM_EXECUCAO
PAUSADO
CONCLUIDO
CONCLUIDO_COM_FALHA_TECNICA
INTERROMPIDO
CANCELADO
```

Estados de negócio da Conferência não pertencem ao job.

## 4. Escopo persistido

Ao criar job, persistir ao menos:

- tipo;
- competência;
- chamada;
- conjunto/critério de clientes autorizado;
- parâmetros de execução;
- usuário solicitante ou origem automática;
- data/hora;
- versão do build/regra relevante.

O job não deve recalcular silenciosamente um universo maior depois de iniciado.

## 5. Itens do job

Processamentos grandes devem possuir unidades rastreáveis/checkpoints.

Por item, conforme tipo:

- pendente;
- em execução;
- concluído;
- falha técnica;
- ignorado por idempotência;
- cancelado.

A conclusão do item precisa ser persistida antes de avançar o checkpoint.

## 6. Lease/posse de execução

Para impedir dois workers executando o mesmo job simultaneamente, utilizar mecanismo equivalente a lease/claim persistido:

- worker_id;
- claimed_at;
- heartbeat/expiração quando necessário;
- atualização condicional.

Após timeout/queda comprovada, outro worker pode retomar de checkpoint seguro.

Não usar apenas flag `EM_EXECUCAO` eterna sem mecanismo de recuperação.

## 7. Reinício do backend/worker

Na inicialização:

1. localizar jobs não finais;
2. identificar jobs realmente abandonados;
3. não presumir que todo `EM_EXECUCAO` deve ser reiniciado do zero;
4. retomar a partir do último checkpoint confirmado;
5. garantir idempotência dos itens reaplicados por segurança.

## 8. Escrita atômica por item

Um item só é `CONCLUIDO` quando suas escritas essenciais estiverem confirmadas.

Exemplo documental:

```text
extração
-> persistência do candidato/documento
-> vínculos
-> checkpoint do item
```

Falha entre persistência e checkpoint deve poder ser reconhecida na retomada sem duplicar dados.

## 9. Reprocessamento

Reprocessar arquivo deve criar execução/candidato rastreável, não apagar primeiro e tentar reconstruir depois.

Se worker cair durante o candidato:

- vigente continua intacto;
- candidato incompleto permanece recuperável/descartável;
- retomada não promove resultado parcial.

## 10. eConsignado

O job de eConsignado deve manter:

- competência/chamada;
- clientes consultados;
- resultado por cliente;
- tentativa/erro;
- fotografia válida anterior.

Reinício não pode consultar novamente 840 clientes por perder o escopo do job mensal.

## 11. Cancelamento

Cancelamento precisa ser cooperativo e auditável.

- impedir novos itens;
- permitir concluir/rollback seguro do item atômico corrente;
- não marcar itens não executados como falha;
- preservar resultados já válidos;
- registrar usuário/motivo quando cancelamento manual.

## 12. Atualização/manutenção

Antes de instalar versão:

- impedir criação de novos jobs;
- solicitar parada segura;
- aguardar item atômico ou marcar interrupção recuperável;
- não matar processo no meio de promoção de versão/fechamento sem proteção transacional.

Após atualização, somente retomar jobs se a versão/schema for compatível com o estado persistido.

## 13. Idempotência de efeitos downstream

Retomar item não pode duplicar:

- documento;
- contrato eConsignado;
- ocorrência;
- histórico idêntico;
- versão de fechamento;
- retificação;
- saída física/eletrônica.

Saída final merece chave idempotente própria e gate canônico.

## 14. Monitor

A UI deve mostrar verdade persistida do job:

- etapa;
- progresso;
- último avanço;
- estado técnico;
- falhas técnicas;
- opção de detalhes.

Não fabricar `PROCESSAMENTO_CONCLUIDO` apenas pela matemática do percentual se o job persistido diz outra coisa; primeiro corrigir a máquina de estado.

## 15. Jobs órfãos

Rotina administrativa pode detectar:

- job `EM_EXECUCAO` sem heartbeat/worker válido;
- item preso acima do timeout operacional;
- candidato incompleto;
- arquivo temporário ligado a job morto.

A ação padrão deve ser diagnóstico/retomada segura, não apagar registros.

## 16. Regressões obrigatórias

1. matar/reiniciar worker no meio de lote -> retoma sem duplicar itens concluídos;
2. reiniciar durante candidato de reprocessamento -> vigente permanece intacto;
3. dois workers tentam mesmo job -> somente um possui claim válido;
4. job eConsignado preserva universo da chamada após restart;
5. cancelamento deixa resultados já concluídos válidos e pendentes não executados;
6. retomada não duplica histórico/ocorrência/contrato;
7. atualização com job ativo entra em parada segura;
8. job abandonado é detectável e recuperável;
9. percentual e estado técnico permanecem coerentes;
10. falha técnica de um item não apaga resultados válidos dos demais.

## 17. Estado de evidência

Os registros históricos confirmam existência de filas/jobs/reprocessamento e a necessidade aprovada de checkpoints/idempotência, mas o worker integral não está disponível nesta sessão para verificar a implementação linha a linha.

Portanto, este documento é `CONTRATO_OBRIGATORIO` e a implementação precisa ser verificada na árvore reconciliada antes da homologação.
