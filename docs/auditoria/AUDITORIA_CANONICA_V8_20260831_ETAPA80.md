# Auditoria canônica V8 — Etapa 80

Data: 31/08/2026  
Status: **PLANO READ-ONLY DE RECONCILIAÇÃO B06 TESTADO / RUNTIME WINDOWS FÍSICO AINDA NÃO COLETADO / V8 NÃO HOMOLOGADA**

## 1. Lacuna encerrada

A Etapa 79 passou a produzir um diff confiável entre a fotografia do runtime e o repositório.

Um diff bruto, porém, ainda não é uma decisão de reconciliação. Os estados `SAME`, `CHANGED`, `RUNTIME_ONLY` e `REPO_ONLY` precisavam ser transformados em uma fila de revisão explícita, sem copiar automaticamente conteúdo do runtime para o repositório e sem permitir que configuração sensível fosse promovida por engano.

A Etapa 80 fecha essa lacuna com um planner deliberadamente somente leitura.

## 2. Política canônica

Novo arquivo:

`config/runtime_reconciliation_plan_policy_v8.json`

A política declara:

- estados admitidos no diff;
- ação proposta por estado;
- áreas e padrões sensíveis;
- ação obrigatória para diferenças sensíveis;
- `automatic_write_allowed = false`.

Mapeamento padrão:

| Estado | Ação proposta |
|---|---|
| `SAME` | `NO_ACTION` |
| `CHANGED` | `REVIEW_MERGE` |
| `RUNTIME_ONLY` | `REVIEW_IMPORT_RUNTIME` |
| `REPO_ONLY` | `REVIEW_KEEP_REPO` |

As ações são propostas para revisão. Nenhuma delas executa cópia, merge, remoção ou alteração.

## 3. Proteção de conteúdo sensível

Diferenças em áreas como `config_app`, `config_root` e `metadata`, ou caminhos relacionados a release identity, segurança, autenticação, credenciais, segredos, tokens e `.env`, não recebem ação comum de importação/merge.

Elas são elevadas para:

`SECURITY_REVIEW_REQUIRED`

com risco `CRITICAL`.

Mesmo um arquivo `RUNTIME_ONLY` sensível não pode ser classificado como importação direta.

Um item sensível `SAME` continua sendo `NO_ACTION`, pois não há divergência a resolver.

## 4. Planner read-only

Novo arquivo:

`scripts/plan_runtime_reconciliation.py`

O planner:

- rejeita política que permita escrita automática;
- valida status, caminhos relativos, hashes e tamanhos;
- rejeita traversal, status desconhecido e linhas duplicadas;
- exige hashes iguais quando o status é `SAME`;
- rejeita `CHANGED` com hashes iguais;
- classifica risco e ação proposta;
- marca cada item divergente como `review_required = true`;
- marca cada entrada com `automatic_write = false`;
- grava no plano raiz `automatic_write_allowed = false`;
- vincula o plano ao hash do diff e ao hash da política;
- produz `plan_sha256` estável;
- mantém `v8_homologated = false`;
- nunca executa ações propostas.

O CLI também recusa sobrescrever um plano existente.

## 5. Integração ao consumidor B06

`scripts/consume_runtime_reconciliation_handoff.py` foi ampliado para gerar automaticamente, após o diff:

`RECONCILIATION_PLAN.json`

O relatório final `RUNTIME_HANDOFF_CONSUMPTION.json` agora registra:

- arquivo do plano;
- SHA-256 lógico do plano;
- quantidade de itens que exigem revisão;
- `automatic_reconciliation_write = false`.

O consumidor continua executando o preflight SQLite na cópia do handoff e continua sem alterar handoff, repositório ou instalação operacional.

## 6. Windows PowerShell

`scripts/CONSUME_RUNTIME_HANDOFF_V8.ps1` foi ampliado para:

- aceitar política de reconciliação opcional;
- exigir que `RECONCILIATION_PLAN.json` exista;
- exigir `automatic_reconciliation_write = false` no relatório;
- exigir `automatic_write_allowed = false` no plano;
- conferir o hash do plano reportado pelo consumidor;
- exigir que relatório e plano mantenham `v8_homologated = false`.

Marcador adicional de smoke:

`POWERSHELL_B06_PLAN_SMOKE_OK`

## 7. Regressões

### Planner isolado

`tests/test_plan_runtime_reconciliation.py` cobre:

- mapeamento dos quatro estados;
- ausência total de escrita automática;
- config divergente → revisão de segurança;
- release identity `RUNTIME_ONLY` nunca vira importação direta;
- caminho `auth/...` protegido mesmo fora da área config;
- duplicidade bloqueada;
- traversal bloqueado;
- inconsistências status/hash bloqueadas;
- status desconhecido bloqueado;
- política não pode habilitar escrita;
- input não é mutado;
- hash do plano é estável;
- CLI não sobrescreve plano existente.

### Integração consumidor + plano

`tests/test_consume_runtime_reconciliation_plan.py` comprova que:

- o consumidor gera o plano;
- o hash do plano fica vinculado ao relatório;
- a contagem de revisão é coerente;
- uma diferença real vira `REVIEW_MERGE` e não escrita automática.

### Smoke PowerShell

O CI executa:

`runtime descartável -> produtor B06 -> consumidor B06 -> diff -> plano -> preflight SQLite`

No smoke do marco final foram gerados, de propósito, itens `RUNTIME_ONLY` e `REPO_ONLY`. O resultado foi uma fila de 10 itens para revisão, com escrita automática desativada.

## 8. Evidência canônica

GitHub Actions:

- run: `33453077178`;
- commit auditado: `92bb4ee0d2cf05497231ca3ee469568d1c7c0413`;
- Python: `3.12.14`;
- testes: `529 OK`;
- produtor: `POWERSHELL_B06_SMOKE_OK`;
- consumidor: `POWERSHELL_B06_CONSUMER_SMOKE_OK`;
- plano: `POWERSHELL_B06_PLAN_SMOKE_OK`;
- mapa causal: `28/28`;
- artifact: `v8-release-preflight#9780448410`;
- SHA-256: `707bab421adf2623da569a5664934281d92cb0982dc421ec673387b3636368c7`.

Preflight:

- B homologados: `0/50`;
- C PASS: `0/28`;
- evidências externas PASS: `1/10`;
- release READY: `False`;
- build OK: `False`.

## 9. Estado correto do B06

B06 permanece **`BLOQUEADO_POR_RUNTIME`**.

A Etapa 80 não coletou a instalação Windows física e não reconciliou os arquivos reais do escritório.

Ela apenas prepara com segurança o que acontecerá depois da coleta real:

1. produzir o handoff físico;
2. consumir o handoff em staging;
3. gerar diff;
4. gerar plano de revisão;
5. revisar cada divergência;
6. somente após decisões explícitas fixar o baseline reconciliado.

Nenhum arquivo do runtime foi copiado automaticamente para `main` nesta etapa.

## 10. Próximo avanço seguro

O plano ainda contém apenas **ações propostas**. A próxima etapa deve criar um artefato separado de revisão humana, vinculado ao `plan_sha256`, exigindo decisão explícita por item divergente e impedindo aprovação em massa de conteúdo sensível.

Esse artefato continuará sem executar alterações.

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
