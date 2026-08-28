# B35 — Invariantes SQLite e impressão histórica

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## Objetivo

Executar os três níveis exigidos pelo contrato V8:

1. integridade física/estrutural;
2. integridade referencial declarada;
3. invariantes lógicas de negócio.

## Resultado inicial no banco real

### SQLite

- `PRAGMA integrity_check`: `ok`;
- `PRAGMA foreign_key_check`: 0 violações.

### Fechamento/versões/retificações

Foram verificadas, entre outras:

- fechamento cliente sem competência: 0;
- fechamento com cliente inexistente: 0;
- chamada incompatível: 0;
- `versao_atual` sem versão correspondente: 0;
- FECHADA sem versão: 0;
- RETIFICACAO sem registro DETECTADA: 0;
- retificação com base inexistente: 0;
- ADIADA dentro da chamada atual/anterior: 0;
- retificação DETECTADA duplicada: 0;
- versão sem cliente/fechamento: 0;
- versão acima de `versao_atual`: 0;
- lacuna de numeração de versões: 0.

### Processamento/eConsignado

- processamento com `cliente_id` órfão: 0;
- `superado_por_id` órfão: 0;
- documento vigente já superado: 0;
- consulta eConsignado sem job: 0;
- consulta/snapshot eConsignado com cliente inexistente: 0;
- empregador duplicado no mesmo job: 0;
- contrato duplicado na mesma fotografia: 0.

## Achado lógico que `foreign_key_check` não detectava

A tabela `processamento_impressao_item` guardava apenas:

- `impressao_id`;
- `processamento_id`;
- ordem.

Após reprocessamentos destrutivos, 200 linhas de itens impressos apontavam para `processamento_id` que já não existia.

Detalhamento:

- referências históricas afetadas: 200;
- IDs de processamento únicos afetados: 100;
- lote 1: 100 referências afetadas;
- lote 2: 94;
- lote 3: 6;
- todos os 100 IDs únicos ainda possuíam evidência em `processamento_reprocessamento_historico`.

A cronologia confirma a relação com o reprocessamento:

- lotes impressos em 27/08/2026 entre 13:32 e 13:36;
- os IDs removidos foram reprocessados em 27/08/2026 entre 14:25 e 14:26.

Nenhum registro foi apagado para maquiar a inconsistência.

## Correção

Cada item de impressão passa a manter fotografia imutável do documento efetivamente impresso:

- `snapshot_json`;
- SHA-256 do processamento original;
- cliente da fotografia;
- competência;
- tipo documental;
- nome original.

Para novos lotes, a fotografia é gravada no momento da impressão.

Para o legado, o backfill segue esta ordem:

1. processamento vivo, quando ainda existe;
2. snapshot preservado em `processamento_reprocessamento_historico`, quando o registro vivo já foi removido;
3. se nenhuma evidência existir, o item permanece explicitamente pendente para auditoria — nunca é inventado.

## Ensaio em cópia do banco real

Antes da migração de metadata:

- `integrity_check = ok`;
- `foreign_key_check = 0`;
- violações lógicas bloqueantes: 200, todas no histórico de impressão.

Depois da migração em cópia:

- `integrity_check = ok`;
- `foreign_key_check = 0`;
- violações lógicas bloqueantes: 0;
- 414/414 itens de impressão possuem snapshot;
- 214 snapshots reconstruídos de processamento ainda vivo;
- 200 snapshots reconstruídos do histórico de reprocessamento;
- 0 itens sem evidência.

## Observação eConsignado legado

Foram encontrados 4 jobs históricos de competência 05/2026 sem linha em `fechamento_mensal`.

Eles são anteriores ao contrato operacional V8 e foram preservados como histórico. Não foram apagados nem receberam vínculo retroativo fabricado. A regra B24 já exige que novos jobs nasçam da competência/chamada do Fechamento.

## Auditor reproduzível

Código:

`runtime_overlay/app/src/axiom_tools/db/invariants_v8.py`

Regressão:

`runtime_overlay/app/tests/db/test_invariants_v8.py`

Patch de preservação da impressão:

`docs/auditoria/patches/B35_IMPRESSAO_SNAPSHOT_IMUTAVEL.patch`

## Testes

- regressão B35 específica: 2/2 PASS;
- regressão não-web acumulada: 400/400 PASS;
- failures: 0;
- errors: 0.

## Estado

B35: `CORRIGIDO_TESTADO` na cópia canônica auditada.

Isso não equivale a homologação Windows. O mesmo auditor deverá ser executado antes/depois da migração do banco físico e integrado ao gate final de instalação.
