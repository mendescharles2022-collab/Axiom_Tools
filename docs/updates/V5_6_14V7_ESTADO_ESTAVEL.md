# V5.6.14V7 — Estado estável instalado

Data de homologação operacional: 26/08/2026.

## Natureza

Versão estável imediatamente anterior à reformulação V8.

## Comportamento entregue

- Fechamento Mensal disponível no menu lateral.
- Competência pode ser aberta em `MM/AAAA`.
- Clientes ativos são carregados para o ciclo mensal.
- Sem movimento é uma condição da competência, sem alterar o cadastro permanente.
- Chamadas, impedimentos, histórico e retificações versionadas permanecem preservados.
- Fechamento automático é calculado a partir da conferência aplicável.
- Central de Conferência integra o ciclo mensal.

## Limitação identificada após homologação

A tela do Fechamento Mensal ficou operacionalmente pesada para uma carteira superior a 600 clientes e passou a concentrar ações que pertencem à Conferência.

Por decisão funcional posterior, a V8 deve simplificar o Fechamento Mensal para painel de competência e deslocar resolução de exceções para a Central de Conferência.

## Regra de estabilidade

Não incorporar código da V8 como concluído até existir validação integrada e pacote instalável com rollback.
