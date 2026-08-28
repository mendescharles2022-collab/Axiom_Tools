# Contrato V8 — Semântica temporal dos tributos federais no Extrato Domínio

Data: 28/08/2026
Status: **contrato obrigatório / risco de parser a validar / V8 não homologada**

## 1. Evidência documental

Extratos Mensais reais do Domínio exibem explicitamente:

- competência geral/cálculo da folha;
- coluna `IRRF conforme competência do cálculo`;
- coluna `IRRF conforme competência do pagamento`;
- aviso de que o INSS utiliza competência de cálculo e o IRRF utiliza competência de pagamento;
- aviso de consolidação dos tributos federais entre matriz e filiais.

Portanto um único campo `competencia` não é suficiente para representar toda a semântica fiscal do documento.

## 2. Regra canônica

O parser deve separar pelo menos:

- `competencia_calculo`;
- `competencia_pagamento`, quando identificável/aplicável;
- competência operacional do ciclo;
- período de apuração/fato gerador informado na guia externa;
- proveniência de cada valor.

## 3. INSS

Valores previdenciários do Extrato seguem a competência de cálculo conforme aviso do próprio documento.

A composição federal esperada deve preservar essa origem temporal.

## 4. IRRF

IRRF não pode ser associado automaticamente à competência do cabeçalho apenas porque aparece no mesmo Extrato Mensal.

O motor deve usar a dimensão `conforme competência do pagamento` para o cruzamento fiscal aplicável, preservando a coluna de cálculo como informação de origem/comparação quando útil.

## 5. Consolidação matriz/filiais

O aviso do Extrato também informa que tributos federais são consolidados entre matriz e filiais.

Logo:

- saldos federais repetidos em Extratos de inscrições/estabelecimentos vinculados não devem ser somados automaticamente;
- a composição precisa identificar o grupo empregador/consolidação;
- FGTS ou outras dimensões podem ter granularidade diferente e devem ser tratadas por seus próprios contratos.

O caso Jair Ferreira Camargo permanece controle de regressão desse princípio.

## 6. Valor federal autoritativo

Para o Extrato Domínio, a seção `Apuração Tributos Federais → Saldo à recolher` é a referência agregada esperada para o batimento federal, com decomposição preservada.

Linhas intermediárias não devem ser usadas isoladamente para decidir ausência de obrigação.

## 7. Modelo de proveniência

Cada componente federal extraído deve poder guardar:

- tipo do encargo;
- valor;
- competência semântica usada;
- campo/seção de origem;
- documento;
- grupo matriz/filial quando aplicável;
- regra de consolidação;
- versão do parser.

## 8. Regressões mínimas

1. Extrato com IRRF diferente entre coluna de cálculo e pagamento;
2. IRRF de férias aparecendo em uma dimensão temporal e não na outra;
3. INSS permanecendo associado à competência de cálculo;
4. matriz/filial com saldo federal consolidado repetido — contar uma única obrigação econômica;
5. valores zero em ambas as colunas sem criação artificial de DARF;
6. guia externa/DARF com período de apuração confrontada com a competência fiscal correta, não apenas com o cabeçalho da folha.

## 9. Estado de evidência

A existência desta semântica está comprovada por documentos reais.

Não foi recuperado nesta sessão o parser V8 integral para provar se a implementação atual escolhe a coluna errada.

Portanto B32 permanece `TESTE_PENDENTE_RUNTIME`, e não `CONFIRMADO_RUNTIME`, até inspeção/regressão na árvore canônica reconciliada.
