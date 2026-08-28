# Protocolo executável — Regressão dos 28 casos reais de 08/2026

Data: 28/08/2026
Status: **protocolo de homologação / execução pendente na árvore runtime reconciliada**

## 1. Objetivo

Transformar `MATRIZ_REGRESSAO_V8_AGOSTO_2026.md` em uma execução reproduzível que valide negócio, persistência e efeitos colaterais.

Não basta conferir se a ocorrência desapareceu da tela.

## 2. Preparação obrigatória

Executar somente em cópia controlada da base/fixtures ou ambiente de homologação.

Antes da bateria:

- registrar commit/build/schema;
- registrar hash da base inicial;
- executar `PRAGMA integrity_check`;
- executar `PRAGMA foreign_key_check`;
- capturar contagens das tabelas críticas;
- congelar configuração da competência 08/2026;
- congelar composição/chamada;
- registrar versão dos motores/parsers.

## 3. Registro por caso

Cada caso deve produzir um resultado estruturado contendo pelo menos:

- `caso_id`;
- cliente/identidade de teste;
- fixture/documentos usados;
- estado inicial por fonte;
- estado agregado inicial;
- ação executada;
- eventos/correlation_ids gerados;
- estado final por fonte;
- estado agregado final;
- versão de fechamento antes/depois;
- retificação antes/depois;
- documentos vigentes/candidatos;
- saídas autorizadas/bloqueadas;
- deltas inesperados em outros clientes;
- resultado `PASS/FAIL`;
- evidência da falha quando `FAIL`.

## 4. Isolamento

Cada teste unitário/integração usa transação/fixture isolada quando possível.

A regressão de ponta a ponta também deve rodar em sequência sobre uma base preparada para detectar contaminação entre casos.

Um caso não pode depender da correção manual feita pelo teste anterior.

## 5. Quatro níveis de teste

### Nível A — regra pura

Validar parser, aplicabilidade, deduplicação, composição e agregador com fixtures pequenas.

### Nível B — integração de domínio

Validar persistência, reprocessamento candidato, decisões por fonte, fechamento e retificação.

### Nível C — fluxo HTTP/worker

Validar rotas, autenticação, CSRF, jobs, restart, Conferência somente leitura e ações explícitas.

### Nível D — runtime Windows

Validar instalação/atualização, caminhos reais configurados, workers/serviços, preview/impressão, backup/rollback e desempenho.

Um caso só é considerado homologado quando passa em todos os níveis que lhe forem aplicáveis.

## 6. Famílias da bateria

### Reprocessamento/versionamento

Casos 1, 2, 5, 11, 16, 17 e 26.

Assertivas obrigatórias:

- vigente não é destruída antes da promoção;
- candidato pior é rejeitado;
- promoção recalcula apenas o necessário;
- histórico preservado;
- restart não promove candidato parcial.

### Descoberta/leitura/vínculo

Casos 5, 8, 11, 13, 16 e 17.

Assertivas:

- estágio exato de falha;
- documento físico existente não vira `AUSENTE` genérico;
- redescoberta/reconciliação atualiza composição.

### Aplicabilidade e saldo zero

Casos 2, 9, 10, 15, 18, 20, 21, 23 e 28, além do controle P DA SILVA CARMO.

Assertivas:

- aplicabilidade antes de busca da guia;
- zero/N/A não gera ausência artificial;
- MEI usa DAE;
- diretor/pró-labore não cria empregado;
- deduções usam saldo final esperado.

### FGTS/múltiplas evidências

Casos 2, 4, 12, 17, 24 e 25.

Assertivas:

- reemissão não dobra;
- componente econômico distinto pode somar;
- mensal/rescisório/antecipado identificados;
- matrícula/origem preservada.

### eConsignado

Casos 6, 7, 12, 14, 19, 24 e 25.

Assertivas:

- status de API ≠ status da Conferência;
- universo respeita chamada;
- contexto de vínculo/remuneração/rescisão;
- fotografia versionada;
- retry idempotente.

### Decisão/impedimento por fonte

Casos 3, 22 e 24.

Assertivas:

- decisão DARF não resolve FGTS/eConsignado;
- motivo/evidência auditáveis;
- agregado deriva das fontes.

### Chamada

Caso 27.

Assertivas:

- mudança 1→2 persistida;
- excluído de todos os jobs/mesas da chamada 1;
- restart não reverte;
- avanço global para 2 libera conforme elegibilidade.

## 7. Casos com valores exatos

Quando a matriz possui valor validado, o teste deve comparar números, não apenas status.

Controles principais:

- Jair: federal R$ 511,43 uma vez; FGTS R$ 389,04, preservando R$ 129,68 + R$ 259,36 por origem;
- Larissa: DARF previdenciária R$ 178,31, FGTS zero/N/A;
- Ponto Kent: DARF R$ 758,37 e FGTS R$ 722,15;
- P DA SILVA CARMO: federal R$ 220,00 e FGTS zero/N/A.

Tolerância monetária, quando necessária, deve ser explícita e nunca usada para encobrir duplicação/soma indevida.

## 8. Testes negativos obrigatórios

Além do cenário feliz, provocar:

- documento ilegível;
- cliente não identificado;
- competência conflitante;
- API externa falhando;
- worker reiniciado;
- candidato pior;
- seleção manual de saída não autorizada;
- GET repetido da Conferência;
- estado concorrente/revisão obsoleta;
- reemissão com hash diferente mas obrigação equivalente.

## 9. Não regressão transversal

Após cada família, validar que não houve:

- aumento inesperado de `FECHADA`;
- desaparecimento de retificações;
- duplicação de versões;
- saída para cliente não fechado;
- alteração em cliente de chamada futura;
- perda de vínculo de documentos já válidos;
- exclusão/movimentação de arquivos físicos.

## 10. Relatório final da bateria

Gerar tabela com 28 casos + controle P DA SILVA CARMO:

`Caso | Família | Nível A | Nível B | Nível C | Nível D | Resultado | Evidência`

Sem `XFAIL` permanente para defeito tecnicamente corrigível.

Teste não executado deve informar motivo concreto e só pode permanecer pendente se realmente exigir recurso físico indisponível.

## 11. Critério de aprovação

A regressão de agosto só é aprovada quando:

- todos os 28 casos passam nos níveis aplicáveis;
- controle P DA SILVA CARMO passa;
- nenhum bloqueador crítico produz efeito colateral;
- banco final mantém integridade e invariantes;
- nenhuma saída indevida é gerada;
- nenhum documento original é perdido;
- build testado é o mesmo build empacotado.
