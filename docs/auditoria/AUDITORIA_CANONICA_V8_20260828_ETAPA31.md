# Auditoria canônica V8 — Etapa 31

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 31 cruza o defeito funcional B34 (`classificacao_inativacao` string/Enum) com o acoplamento estrutural entre cadastro mestre e histórico mensal/retificação.

## 2. Defeito funcional confirmado

A suíte do ZIP canônico confirmou que `classificacao_inativacao` pode chegar como string enquanto o repositório assume sempre Enum e acessa `.value`.

O contrato existente `docs/auditoria/CONTRATO_INATIVACAO_CLIENTES_V8.md` permanece válido.

A correção deve normalizar a entrada em ponto único e produzir erro de validação para valor inválido, nunca falha acidental de atributo.

## 3. Não basta remover `.value`

A homologação precisa provar o fluxo inteiro:

- inativação;
- classificação/motivo;
- data efetiva;
- histórico;
- reativação;
- preservação de filesystem/documentos;
- efeito apenas sobre ciclos futuros conforme data efetiva.

## 4. Acoplamento estrutural confirmado

Auditoria posterior do runtime preservado mostrou comportamento desigual:

- listagens/retificações ativas utilizam `JOIN clientes` em pontos relevantes;
- histórico mensal utiliza `LEFT JOIN clientes`.

Isso demonstra dependência parcial do passado operacional em relação à existência atual do cadastro mestre.

## 5. Consequência da exclusão administrativa

A AXT-003 permitiu exclusão administrativa real do cadastro, preservando o filesystem.

Com versionamento mensal V4/V8, a exclusão não pode eliminar a capacidade de reconstruir:

- cliente/identidade histórica;
- fechamento;
- snapshots;
- retificações;
- decisões;
- saídas;
- auditoria.

Portanto o fechamento precisa manter identidade histórica própria/snapshot suficiente e consultas históricas não podem depender exclusivamente de `clientes` existir hoje.

## 6. Competência corrente na saída do escritório

A inativação tem data efetiva.

Uma empresa que sai do escritório no fim de uma competência pode ainda precisar concluir aquele ciclo e seus impedimentos.

A inativação não deve:

- apagar o cliente da composição já congelada;
- esconder ocorrência de procuração revogada;
- apagar documentos;
- reescrever retrospectivamente fechamento.

Competências posteriores passam a respeitar a situação cadastral/data efetiva conforme elegibilidade mensal.

## 7. Regressões mínimas

1. inativar com Enum;
2. inativar com string canônica;
3. string inválida → validação controlada;
4. reativar e preservar histórico anterior;
5. abrir/listar fechamento histórico após inativação;
6. abrir/listar fechamento histórico após exclusão administrativa em fixture controlada;
7. consultar retificação histórica sem depender do cadastro ativo;
8. competência já aberta antes da data efetiva permanece auditável;
9. competência futura exclui automaticamente conforme regra de elegibilidade;
10. pasta/documentos permanecem intactos.

## 8. Estado dos bloqueadores

- B34 permanece `CONFIRMADO_RUNTIME`, não corrigido;
- a dependência `JOIN clientes` em histórico vivo/retificação permanece defeito estrutural a corrigir;
- B35 deve incluir invariantes de referências históricas;
- nenhum item foi marcado `CORRIGIDO_HOMOLOGADO`.

## 9. Próxima frente

Consolidar protocolo executável da regressão dos 28 casos reais de agosto, impedindo que uma correção pontual de um cliente masque regressão em outro mecanismo.
