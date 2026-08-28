# Auditoria canônica V8 — Etapa 30

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 30 aprofundou B32 — semântica temporal do IRRF — e a consolidação federal matriz/filiais no Extrato Domínio.

## 2. Evidência documental confirmada

Extratos Mensais reais exibem:

- `IRRF conforme competência do cálculo`;
- `IRRF conforme competência do pagamento`;
- aviso de que o INSS utiliza a competência de cálculo;
- aviso de que o IRRF utiliza a competência de pagamento;
- aviso de consolidação dos tributos federais entre matriz e filiais.

Logo, um único campo de competência do cabeçalho não representa sozinho toda a semântica tributária do documento.

## 3. Contrato criado

Foi criado `docs/architecture/CONTRATO_TEMPORAL_TRIBUTOS_FEDERAIS_V8.md`.

O parser/cross-check precisa preservar:

- competência de cálculo;
- competência de pagamento quando aplicável;
- competência operacional;
- período de apuração da guia externa;
- proveniência por componente.

## 4. Estado de evidência do B32

Ainda não foi recuperado o parser V8 integral para provar que a implementação atual usa a coluna errada.

Portanto B32 continua `TESTE_PENDENTE_RUNTIME`.

Não foi promovido artificialmente a defeito confirmado.

## 5. Relação com Jair / matriz-filial

O próprio Extrato Domínio confirma consolidação federal entre matriz e filiais.

Isso reforça a regra já estabelecida para o caso Jair:

- federal consolidado repetido não é somado automaticamente;
- outras dimensões, como FGTS por matrícula, seguem regra própria de composição.

## 6. Regressão mínima

A árvore canônica reconciliada deverá testar pelo menos:

- divergência entre coluna IRRF cálculo e pagamento;
- IRRF férias em dimensões temporais diferentes;
- INSS permanecendo na competência de cálculo;
- guia DARF confrontada com o período fiscal apropriado;
- matriz/filial sem duplicação do saldo federal consolidado.

## 7. Estado final

B32 permanece pendente de inspeção/teste de runtime.

B30 — valor federal autoritativo — permanece regra comprovada documentalmente e precisa ser preservada na regressão.

Nenhum bloqueador foi marcado `CORRIGIDO_HOMOLOGADO`.

## 8. Próxima frente

Auditar o defeito funcional `classificacao_inativacao` string/Enum e seu impacto sobre inativação, reativação, composição mensal futura e histórico preservado.
