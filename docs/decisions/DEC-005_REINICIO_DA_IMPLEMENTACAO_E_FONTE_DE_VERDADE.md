# DEC-005 — Reinício da Implementação e Fonte de Verdade

Versão: 1.0  
Data: 16/08/2026  
Status: Permanente e vinculante

## Contexto

Foram produzidas tentativas locais de implementação da AXT-001 que apresentaram regressões e divergências em relação às regras oficiais do projeto.

O projeto seguirá com nova implementação limpa.

## Decisão

1. A documentação oficial do repositório é a fonte de verdade do Axiom Tools.
2. A AXT-000 permanece concluída e não será recriada como funcionalidade.
3. A AXT-001 será implementada novamente do zero.
4. Código produzido em tentativas locais anteriores não deve ser copiado automaticamente.
5. Reaproveitamento de ideia ou trecho só é permitido quando novamente avaliado e compatível com a documentação vigente.
6. Login/Dashboard não pertencem à AXT-001; passam para AXT-002.
7. Sprints futuras não devem ser antecipadas dentro da Sprint atual.
8. Documentos oficiais não devem depender do nome de um executor específico.

## Convenção documental

- `DEC-*` = decisão permanente;
- `AXT-*` = Sprint de execução;
- `STATUS_ATUAL.md` = situação do projeto;
- `ROADMAP_OFICIAL_AXIOM_TOOLS.md` = sequência de Sprints.

## Regra para execução

Antes de iniciar uma Sprint, qualquer executor deve ler:

1. `docs/STATUS_ATUAL.md`;
2. a Sprint correspondente;
3. as decisões `DEC-*` citadas como dependência;
4. a arquitetura oficial.

## Homologação

Nenhuma Sprint é considerada concluída apenas porque o código foi produzido. Ela precisa cumprir critérios de aceite e testes definidos na própria Sprint.

Esta decisão formaliza o reinício funcional do projeto sem apagar a história registrada pelo Git.