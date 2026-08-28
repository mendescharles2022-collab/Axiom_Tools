# Invariantes de banco — Fechamento versionado V8

Data: 28/08/2026
Status: **contrato obrigatório de auditoria / implementação ainda não homologada**

## 1. Origem

A V5.6.14V4 introduziu:

- `fechamento_mensal_versao`;
- `fechamento_mensal_retificacao`;
- `versao_atual` em `fechamento_mensal_cliente`;
- backfill de snapshot V1 para fechamentos existentes.

A instalação real preservada em logs também possui rotina que procura registros `FECHADA` sem versão correspondente.

Portanto, `FECHADA` sem snapshot válido deve ser tratada como violação de invariante.

## 2. Invariantes obrigatórias

### I01 — FECHADA possui versão

Para todo registro:

```text
fechamento_mensal_cliente.status = FECHADA
```

deve existir ao menos uma versão correspondente em `fechamento_mensal_versao`.

### I02 — versao_atual existe

Quando `versao_atual` estiver preenchida, deve existir exatamente a versão indicada para o mesmo `cliente_id + competencia`.

### I03 — versão vigente é a máxima concluída

Na ausência de mecanismo explícito diferente, `versao_atual` deve apontar para a maior versão homologada/concluída daquele cliente e competência.

### I04 — versões são monotônicas

A sequência de versão por `cliente_id + competencia` não pode regredir nem reutilizar número já existente para outro snapshot.

### I05 — uma retificação aberta por vez

Para o mesmo `cliente_id + competencia`, deve existir no máximo uma retificação ativa/detectada aguardando conclusão.

### I06 — RETIFICACAO possui versão base

Cliente em `RETIFICACAO` precisa possuir versão base válida e preservada.

### I07 — concluir retificação gera nova versão

Conclusão de retificação deve criar Vn+1, apontar `versao_atual` para ela e encerrar a retificação correspondente atomicamente.

### I08 — snapshot antigo nunca é reescrito

Versões históricas são imutáveis. Correção posterior cria nova versão; não altera o conteúdo de Vn.

### I09 — saída aponta para versão válida

Saída final autorizada deve referenciar versão existente do mesmo cliente/competência.

### I10 — retificação pendente bloqueia novas saídas

Se existir mudança material em retificação aberta, o gate de saída deve bloquear geração nova até conclusão.

### I11 — FECHADA sem versão é auto-reparável apenas por regra segura

Migração/backfill pode criar V1 para fechamento legado somente quando houver dados suficientes e regra determinística para reconstruir o snapshot.

Se houver ambiguidade, o sistema deve registrar revisão, não inventar snapshot silenciosamente.

### I12 — versão órfã é inválida

Não deve existir `fechamento_mensal_versao` apontando para cliente inexistente ou competência sem contexto válido.

### I13 — retificação órfã é inválida

Retificação deve apontar para cliente, competência e versão base existentes.

### I14 — histórico acompanha transições

Transições relevantes de FECHADA → RETIFICACAO → FECHADA precisam ter registro histórico coerente, sem pular evento.

## 3. Consultas de auditoria obrigatórias

A homologação V8 deve executar, em cópia do banco real:

1. FECHADA sem versão;
2. `versao_atual` inexistente;
3. versão maior que `versao_atual` sem justificativa;
4. duplicidade de número de versão por cliente/competência;
5. mais de uma retificação aberta por cliente/competência;
6. RETIFICACAO sem versão base;
7. versões órfãs;
8. retificações órfãs;
9. saídas apontando para versão inexistente;
10. saídas novas durante retificação pendente;
11. inconsistência entre histórico e estado atual.

## 4. Relação com V4

A V4 já comprovou em cópia real:

- backfill de snapshots;
- detecção de mudança material;
- conclusão com nova versão;
- repetição sem criar retificação;
- bloqueio de saída durante retificação.

A V8 não pode homologar com garantias inferiores às que já existiam.

## 5. Relação com bloqueadores

Principalmente:

- B03;
- B04;
- B05;
- B10;
- B35;
- B41.

## 6. Critério de aprovação

Todas as consultas acima precisam retornar zero violações na base migrada de homologação, salvo registros explicitamente classificados e corrigidos durante migração controlada.
