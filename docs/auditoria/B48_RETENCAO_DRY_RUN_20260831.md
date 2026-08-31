# B48 — Retenção/limpeza — dry-run seguro

Data: 31/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: `Axiom_Tools(20260828-175237).zip`.

## Achado do snapshot

O ZIP contém:

- `backups/`: 11.553 arquivos, ~919 MB;
- `temp/`: 838 arquivos, ~61,8 MB;
- `logs/`: 1 arquivo;
- `app/downloads/`: 13 arquivos.

Uma política genérica `temp > 7 dias` foi simulada e marcaria 279 arquivos (~31,5 MB). A inspeção mostrou que grande parte desses itens são ZIPs de atualização, instaladores PowerShell, manifestos, relatórios e validadores das versões V5.6.14S/T. Portanto idade e localização em `temp` não são prova de descartabilidade.

Nenhum arquivo foi removido ou movido.

## Política canônica

Foi versionada `config/retention_policy_v8.json`.

A política só considera elegíveis namespaces explicitamente efêmeros:

- `temp/cache/**`;
- `temp/work/**`;
- `temp/staging/**`;

com idade mínima de 7 dias.

Não há regra de exclusão para:

- `backups/`;
- pacotes/manifestos/relatórios históricos atualmente existentes em `temp/`;
- banco SQLite;
- documentos processados;
- retificações, snapshots ou evidências de auditoria;
- logs por regra implícita.

## Segurança

O planner `scripts/plan_retention_cleanup.py` opera apenas como `DRY_RUN_ONLY` e não possui código de exclusão.

A exclusão física continua uma ação separada e só poderá existir para itens classificados por política explícita, depois de validação do relatório.

## Estado

B48 pode ser classificado como `CORRIGIDO_TESTADO` quanto à arquitetura/política de retenção: o mecanismo rejeita a ideia de que `temp` seja sinônimo de lixo e protege evidência histórica por default.

A homologação final no Windows deverá rodar o dry-run na instalação efetiva antes de qualquer rotina destrutiva ser habilitada.
