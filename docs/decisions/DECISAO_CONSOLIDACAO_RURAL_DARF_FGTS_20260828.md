# Decisão — Consolidação rural de DARF e FGTS

Data: 28/08/2026

## Regra confirmada

Para empregador/produtor rural com múltiplas matrículas/inscrições vinculadas ao mesmo contribuinte, como o caso Jair Ferreira Camargo:

- **DARF / Apuração de Tributos Federais:** quando matriz e filial exibirem a mesma apuração federal consolidada, o motor **não deve somar as bases/valores das duas matrículas**. A informação federal deve ser tratada como consolidada/repetida entre as unidades, usando uma única referência de apuração para o contribuinte.
- **FGTS:** os valores permanecem individualizados nos Extratos Domínio por matrícula. Portanto o motor deve **somar o FGTS esperado das matrículas aplicáveis** e comparar essa soma com a guia/recolhimento FGTS consolidado correspondente.
- O sistema deve preservar o detalhamento por matrícula para auditoria, mas distinguir claramente **valor repetido/consolidado** de **valor aditivo por unidade**.

## Critério de regressão obrigatório

No caso Jair Ferreira Camargo:

- duas matrículas rurais;
- DARF federal não pode ser duplicada pela soma das duas apurações;
- FGTS deve resultar da soma das duas parcelas informadas separadamente nos Extratos Domínio;
- a conferência final deve comparar uma única DARF consolidada e o FGTS consolidado corretamente composto.

Essa regra deve ser implementada de forma genérica para múltiplas matrículas/inscrições do mesmo contribuinte, sem hardcode por cliente.
