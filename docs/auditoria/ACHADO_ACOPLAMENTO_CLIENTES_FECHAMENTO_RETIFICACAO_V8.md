# Achado — Acoplamento entre cadastro de Clientes e histórico do Fechamento/Retificação

Data: 28/08/2026
Status: **defeito estrutural confirmado por evidência do runtime**

## 1. Evidência recuperada

Trechos preservados da instalação real mostram:

- `closing/service.py` usa `FROM fechamento_mensal_cliente f JOIN clientes c ON c.id=f.cliente_id` para a visão/listagem mensal;
- `closing/retification.py` usa `FROM fechamento_mensal_retificacao r JOIN clientes c ON c.id=r.cliente_id` para listar retificações;
- o histórico em `closing/service.py` usa `LEFT JOIN clientes c ON c.id=h.cliente_id`.

A implementação, portanto, já trata de forma diferente o desaparecimento do cadastro mestre:

- histórico tolera cliente ausente;
- visão mensal e retificação ativa dependem do cliente ainda existir.

## 2. Conflito com a regra de Clientes

A AXT-003 permitiu exclusão administrativa real do cadastro, inclusive quando há histórico, removendo dependências obrigatórias conforme a política então existente.

Depois, o produto introduziu:

- Fechamento Mensal;
- versões de fechamento;
- retificações;
- decisões mensais;
- saídas vinculadas ao cliente.

O contrato antigo de exclusão não foi totalmente reconciliado com essas entidades posteriores.

## 3. Impacto concreto

Se o cadastro mestre for excluído sem estratégia histórica adequada, podem ocorrer, conforme FK/DELETE efetivamente configurados:

- retificação deixar de aparecer por causa do `INNER JOIN`;
- cliente mensal desaparecer da visão operacional mesmo com registro de fechamento existente;
- tentativa de exclusão falhar por FK;
- ou, pior, dependências serem apagadas por cascade/política antiga;
- histórico continuar parcialmente visível via `LEFT JOIN`, criando visões inconsistentes entre módulos.

A ocorrência exata depende do DDL/FKs do runtime e ainda precisa ser testada em cópia do banco; o acoplamento via JOIN está confirmado.

## 4. Severidade

**Alta — integridade histórica e consistência entre módulos.**

O problema não deve ser corrigido trocando todos os `JOIN` por `LEFT JOIN` indiscriminadamente.

É necessário definir a identidade histórica e a política de exclusão do cadastro mestre.

## 5. Regra correta

Fechamentos, versões, retificações, decisões, histórico e saídas devem continuar auditáveis independentemente da existência futura do cadastro mestre ativo.

Soluções tecnicamente aceitáveis incluem:

- snapshot/tombstone histórico de identidade;
- FK para entidade histórica estável distinta do cadastro ativo;
- política que impeça hard-delete do identificador histórico, mantendo remoção administrativa do cadastro operacional por outra camada.

A decisão física será tomada na implementação reconciliada, mas não pode destruir o passado.

## 6. Migração necessária

Antes de qualquer alteração de schema:

1. auditar FKs atuais de `fechamento_mensal_cliente`, `fechamento_mensal_historico`, `fechamento_mensal_versao`, `fechamento_mensal_retificacao` e saídas;
2. identificar `ON DELETE` configurado;
3. testar exclusão em cópia do banco com cliente sem histórico e com histórico;
4. garantir que `PRAGMA foreign_key_check` permaneça limpo;
5. preservar snapshots e retificações antigas;
6. ajustar queries para consumir identidade histórica correta.

## 7. Regressões mínimas

1. excluir cadastro sem histórico segue permitido conforme política administrativa;
2. excluir cadastro com fechamento histórico não apaga versões;
3. retificação histórica continua consultável;
4. histórico mostra identidade congelada mesmo sem cadastro mestre;
5. nenhuma FK fica órfã;
6. visão mensal antiga continua consistente;
7. saída histórica continua ligada à versão de fechamento;
8. renomear cadastro atual não reescreve identidade histórica;
9. inativação não produz o mesmo efeito de exclusão;
10. módulos diferentes não mostram histórias contraditórias após exclusão administrativa.

## 8. Relação com contratos existentes

Complementa:

- `CONTRATO_CICLO_VIDA_CLIENTE_HISTORICO_V8.md`;
- `CONTRATO_CONTEUDO_SNAPSHOT_FECHAMENTO_V8.md`;
- `INVARIANTES_BANCO_FECHAMENTO_VERSIONADO_V8.md`.

Relaciona-se principalmente aos bloqueadores B34, B35, B41, B48 e B49.
