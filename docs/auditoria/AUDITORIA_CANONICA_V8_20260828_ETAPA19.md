# Auditoria canônica V8 — Etapa 19

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Esta etapa transformou a auditoria acumulada em controle central de homologação e aprofundou dois contratos diretamente relacionados aos defeitos documentais e à execução em fila:

- deduplicação/reemissão documental;
- ciclo de vida de jobs/workers e retomada.

## 2. Matriz central de bloqueadores

Foi criada `MATRIZ_BLOQUEADORES_HOMOLOGACAO_V8.md` com 50 bloqueadores iniciais organizados por:

- críticos;
- ciclo/escopo;
- composição documental;
- aplicabilidade de obrigações;
- eConsignado;
- parser/competência;
- banco;
- segurança;
- UX/desempenho;
- manutenção/acervo.

Cada item utiliza classificação explícita:

```text
CONFIRMADO_RUNTIME
REGRESSAO_CONFIRMADA
CONTRATO_OBRIGATORIO
TESTE_PENDENTE_RUNTIME
CORRIGIDO_HOMOLOGADO
```

Nenhum item está marcado `CORRIGIDO_HOMOLOGADO` nesta data.

## 3. Deduplicação documental

Foi criado `CONTRATO_DEDUPLICACAO_DOCUMENTAL_V8.md`.

A V8 deve distinguir três conceitos diferentes:

1. identidade física do arquivo — SHA-256;
2. identidade documental lógica — fingerprint por tipo/fonte;
3. identidade econômica da obrigação — decide repetição x componente aditivo.

### Casos de controle

#### Jair Ferreira Camargo

Dois documentos podem ser repetição na dimensão federal e aditivos na dimensão FGTS.

#### Leosmar Teodoro de Sousa

Dois Extratos equivalentes não podem ser somados apenas porque são dois arquivos.

#### GFD

Guia mensal + rescisória pode compor; reemissão da mesma guia não pode dobrar o valor.

## 4. Relações documentais

O contrato prevê classificação equivalente a:

```text
IDENTICO_FISICO
REEMISSAO_EQUIVALENTE
VERSAO_SUCESSORA
SUBSTITUI_DOCUMENTO
COMPLEMENTAR
UNIDADE_DISTINTA
COMPONENTE_ADITIVO
RELACAO_INDETERMINADA
```

Ambiguidade deve gerar revisão, nunca soma ou descarte destrutivo automático.

## 5. Jobs/workers

Foi criado `CONTRATO_CICLO_JOBS_WORKERS_V8.md`.

O contrato exige:

- estado essencial persistido;
- competência/chamada/escopo gravados no job;
- checkpoints por item;
- claim/lease para impedir dois workers no mesmo job;
- recuperação de job abandonado;
- retomada após restart sem duplicar resultados;
- cancelamento cooperativo;
- parada segura durante atualização;
- idempotência de efeitos downstream.

## 6. Reprocessamento e restart

Cenário crítico obrigatório:

`worker cai enquanto processa candidato de reprocessamento`

Resultado esperado:

- versão vigente continua intacta;
- candidato parcial não é promovido;
- retomada é possível;
- nenhuma pessoa/valor parcial contamina a Conferência;
- histórico não é duplicado.

## 7. eConsignado e restart

O job precisa persistir o universo autorizado da competência/chamada.

Reiniciar worker não pode recalcular a carteira histórica ampla e voltar a consultar universo como os 840 empregadores observados na auditoria de 08/2026.

## 8. Limite da evidência nesta etapa

Não foi recuperado nesta sessão o código integral do worker/job V8 para inspeção linha a linha.

Portanto:

- ciclo de jobs/workers permanece `CONTRATO_OBRIGATORIO`;
- não é declarado que claim/heartbeat/checkpoint estejam ausentes apenas pela falta do código;
- a árvore reconciliada deverá ser inspecionada e submetida aos testes de interrupção/restart antes da homologação.

## 9. Estado final

Continuam como bloqueadores prioritários da entrega:

1. reprocessamento candidato/versionado;
2. Conference somente leitura;
3. gate único de saída;
4. universo operacional canônico;
5. Jair 449/450 e multi-documento;
6. decisão por fonte;
7. eConsignado contextual e limitado à chamada;
8. transições de chamada/T L;
9. migração e invariantes do SQLite;
10. reconciliação `main` x runtime;
11. regressão dos 28 casos reais;
12. instalação Windows, rollback e proveniência do build;
13. retomada de jobs/workers;
14. benchmark operacional.

Nenhum pacote final deve ser produzido antes de esses itens receberem prova de correção na implementação que efetivamente será instalada.
