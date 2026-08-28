# Contrato V8 — Reprocessamento candidato

Data: 28/08/2026
Status: contrato obrigatório de auditoria; defeito atual confirmado; implementação ainda não homologada.

## Evidência confirmada

A auditoria do ZIP canônico confirmou que o reprocessamento atual substitui a interpretação vigente antes de saber se a nova leitura será melhor.

Caso real: os Extratos 449 e 450 de Jair Ferreira Camargo tinham cliente 826, competência 08/2026, status PROCESSADO e 100% de completude. Depois de reprocessamentos, ficaram em REVISAO, 90% e sem cliente vinculado.

## Regra central

Reprocessar deve criar uma interpretação candidata separada da versão vigente.

Fluxo:

1. preservar a versão vigente;
2. criar candidato ligado ao documento e à versão-base;
3. executar leitura, identificação, competência, classificação e extração no candidato;
4. validar o candidato;
5. comparar candidato com a versão vigente;
6. rejeitar candidato pior sem tocar na vigente;
7. promover candidato melhor somente em operação atômica;
8. preservar a versão anterior no histórico;
9. recalcular a Conferência somente depois da promoção.

## Promoção

Antes de promover, comparar pelo menos:

- cliente/identidade;
- CPF/CNPJ/CAEPF/matrícula;
- competência;
- tipo documental;
- campos obrigatórios;
- valores materiais;
- pessoas/vínculos;
- completude/confiança;
- proveniência.

Percentual isolado não decide promoção.

Um candidato que perde cliente, competência ou campo essencial não pode substituir automaticamente uma versão válida.

## Concorrência

A promoção deve verificar que a versão vigente ainda é a mesma usada na comparação. Se outro worker tiver promovido nova versão, o candidato precisa ser comparado novamente.

Retry da mesma tentativa deve ser idempotente.

## Falhas e restart

Falha durante o processamento do candidato mantém a versão vigente intacta.

Falha antes de concluir a promoção mantém a versão antiga como vigente.

Se a promoção concluir e o recálculo posterior for interrompido, checkpoint/evento deve permitir retomar o recálculo sem duplicar a promoção.

## Pessoas e dados dependentes

Itens de pessoas e valores da versão vigente não devem ser removidos antecipadamente para reconstrução.

Cada candidato/versão deve manter seu próprio conjunto de dados ou mecanismo histórico equivalente.

## Cliente já fechado

Uma versão documental promovida não altera snapshot fechado retroativamente.

Depois da promoção documental:

- sem mudança material: fechamento vigente permanece;
- mudança material: criar retificação candidata Vn+1 e bloquear novas saídas até conclusão.

## Arquivo físico

Reprocessar interpretação não altera automaticamente o PDF original. Hash, origem e vínculo físico permanecem rastreáveis.

## Regressões obrigatórias

1. Extrato 449 não pode cair de uma versão válida para candidato sem cliente.
2. Extrato 450 idem.
3. Cliente 826 e competência 08/2026 devem ser recuperáveis com histórico preservado.
4. Candidato tecnicamente pior é rejeitado.
5. Candidato comprovadamente melhor pode ser promovido.
6. Falha de parser não degrada a versão vigente.
7. Workers concorrentes não promovem sobre estado obsoleto.
8. Retry não cria promoções duplicadas.
9. Versões anteriores e pessoas permanecem auditáveis.
10. Conference só recalcula depois da promoção concluída.
11. Mudança material em cliente fechado gera retificação, não alteração retroativa.
12. Candidato rejeitado continua auditável.

## Inspeção ainda necessária

No runtime reconciliado, verificar:

- limites transacionais da função atual;
- dependências entre arquivo e itens de pessoas;
- comportamento em exceção durante o reprocessamento;
- chamadas ao worker e à Conference após a nova persistência.

Relaciona-se principalmente aos bloqueadores B01, B04, B12, B15, B16, B28, B35, B40, B48, B49 e B50.
