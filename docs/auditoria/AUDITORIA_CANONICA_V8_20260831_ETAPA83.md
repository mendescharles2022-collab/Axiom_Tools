# Auditoria canônica V8 — Etapa 83

Data: 31/08/2026  
Status: **MATERIALIZAÇÃO DO BASELINE RECONCILIADO SOMENTE EM STAGING TESTADA / SEM ESCRITA NAS ORIGENS / RUNTIME WINDOWS FÍSICO AINDA NÃO COLETADO / V8 NÃO HOMOLOGADA**

## 1. Objetivo

A Etapa 82 passou a registrar um aceite imutável do baseline somente após revisão humana completa e pronta.

Ainda faltava transformar esse aceite em uma árvore concreta para auditoria posterior sem escrever diretamente no runtime operacional nem na `main`.

A Etapa 83 fecha essa lacuna com materialização exclusiva em staging isolado.

## 2. Novo materializador

Novo script:

`scripts/materialize_reconciled_staging.py`

O script recebe:

- runtime extraído do handoff;
- repositório base;
- `RECONCILIATION_BASELINE_ACCEPTANCE.json` válido;
- diretório novo de staging.

A saída é uma árvore reconciliada nova, independente das origens.

## 3. Aceite é revalidado antes da materialização

O materializador exige:

- versão suportada;
- modo `RECONCILIATION_BASELINE_ACCEPTANCE_NOT_EXECUTION`;
- `review_complete = true`;
- `baseline_ready = true`;
- `automatic_write_allowed = false`;
- `execution_performed = false`;
- `v8_homologated = false`;
- `acceptance_sha256` lógico válido.

Somente decisões resolvidas são aceitas:

- `ADOPT_RUNTIME`;
- `KEEP_REPO`;
- `EXCLUDE_WITH_REASON`.

## 4. Mapeamento explícito de áreas

O materializador reutiliza semanticamente o mesmo desenho do auditor de reconciliação, incluindo:

- `src_app` / `src_root` → `src`;
- `tests_app` / `tests_root` → `tests`;
- `scripts_app` / `scripts_root` → `scripts`;
- migrations, alembic, templates, static e config;
- metadata de `pyproject.toml`, `requirements.txt` e `requirements-dev.txt`.

Como dois layouts de runtime podem apontar para o mesmo destino, o materializador detecta **colisão de destino** antes de criar o staging.

Assim, `src_app/a.py` e `src_root/a.py` não podem ser aplicados silenciosamente ao mesmo `src/a.py`.

## 5. Fontes são revalidadas contra o aceite

Antes da criação do staging, cada decisão confirma os hashes esperados do runtime e do repositório.

Se qualquer fonte mudar após o aceite:

- a materialização é recusada;
- o diretório de staging ainda não existe;
- a revisão precisa ser refeita sobre a nova fotografia.

Isso evita aplicar uma decisão humana antiga sobre conteúdo que já mudou.

## 6. Staging nasce do repositório e recebe apenas decisões aceitas

A base do staging copia somente o escopo canônico necessário do repositório:

- `src`;
- `tests`;
- `scripts`;
- `migrations`;
- `alembic`;
- `templates`;
- `static`;
- `config`;
- metadata de build/dependências conhecida.

Não copia `.git`, dados operacionais ou outros diretórios fora do escopo.

Aplicação das decisões:

- `ADOPT_RUNTIME` copia o arquivo aceito do runtime **somente para o staging** e revalida o hash;
- `KEEP_REPO` exige que o staging preserve exatamente o hash aceito do repositório;
- `EXCLUDE_WITH_REASON` remove apenas o arquivo do staging, nunca da origem.

## 7. Proteções das origens

O staging:

- não pode ficar dentro do runtime;
- não pode ficar dentro do repositório;
- deve ser um diretório novo;
- nunca sobrescreve staging existente;
- bloqueia symlink nas origens copiadas;
- não chama nenhuma operação de escrita sobre runtime ou repositório.

O relatório declara explicitamente:

- `repository_write_performed = false`;
- `runtime_write_performed = false`;
- `operational_deployment_performed = false`;
- `automatic_write_to_sources = false`;
- `v8_homologated = false`.

## 8. Segurança do staging materializado

Depois da aplicação das decisões, a árvore é novamente verificada com os guardrails de reconciliação:

- conteúdo proibido;
- possíveis segredos embutidos;
- symlinks.

Se ocorrer erro após a criação, apenas o staging novo é removido.

Runtime e repositório permanecem intactos.

## 9. Relatório imutável da árvore

O staging recebe:

`RECONCILED_STAGING_REPORT.json`

O relatório contém:

- `acceptance_sha256`;
- decisões materializadas;
- quantidade de arquivos;
- relação dos arquivos com tamanho e SHA-256;
- `tree_sha256` canônico;
- flags explícitas de não deployment e não escrita nas origens;
- `report_sha256`.

O hash da árvore é estável para os mesmos inputs.

## 10. Regressões

Novo arquivo:

`tests/test_materialize_reconciled_staging.py`

Cobertura:

- aceite válido materializa somente staging;
- runtime e repositório permanecem byte a byte intactos;
- runtime-only pode ser excluído sem importação;
- repo-only pode ser excluído apenas do staging;
- mudança do runtime após aceite é bloqueada antes da saída;
- mudança do repo após aceite é bloqueada antes da saída;
- aceite adulterado é rejeitado;
- saída dentro de runtime/repo é rejeitada;
- staging existente não é sobrescrito;
- colisões entre layouts são bloqueadas;
- segredo embutido em arquivo adotado bloqueia e limpa staging;
- symlink na origem é bloqueado;
- `tree_sha256` e `report_sha256` são estáveis.

## 11. Evidência canônica

GitHub Actions:

- run: `33462096429`;
- commit auditado: `6a9d9f9096f1a98e550fa9a39019fe3c1df2d8b5`;
- Python: `3.12.14`;
- testes: `571 OK`;
- produtor: `POWERSHELL_B06_SMOKE_OK`;
- consumidor: `POWERSHELL_B06_CONSUMER_SMOKE_OK`;
- plano: `POWERSHELL_B06_PLAN_SMOKE_OK`;
- esqueleto: `POWERSHELL_B06_REVIEW_SKELETON_SMOKE_OK`;
- mapa causal: `28/28`;
- artifact: `v8-release-preflight#9783514548`;
- SHA-256: `9530f6de0f7950f326be67614dbc03db6d03fe6c58507c7e38190ab056790c02`.

Preflight do mesmo marco:

- B homologados: `0/50`;
- C PASS: `0/28`;
- mapa causal: `28/28`;
- evidências externas PASS: `1/10`;
- release READY: `False`;
- build OK: `False`.

## 12. Estado correto do B06

B06 permanece **`BLOQUEADO_POR_RUNTIME`**.

Os testes da Etapa 83 materializam fixtures sintéticas. Eles não significam que o runtime Windows físico foi coletado, que decisões humanas reais foram tomadas ou que uma árvore física reconciliada já existe.

A cadeia preparada agora é:

1. handoff físico;
2. consumo seguro;
3. diff;
4. plano;
5. esqueleto PENDING;
6. revisão humana;
7. validação;
8. aceite imutável;
9. materialização somente em staging;
10. verificação independente do staging;
11. somente depois, integração/correções controladas.

## 13. Próximo avanço seguro

A próxima etapa deve verificar de forma independente o staging já materializado:

- validar o `RECONCILED_STAGING_REPORT.json` e seu hash;
- recalcular a árvore e comparar `tree_sha256`;
- confirmar cada decisão do aceite no destino;
- detectar arquivo extra, faltante ou adulterado;
- detectar recriação de item excluído;
- verificar novamente symlinks, conteúdo proibido e segredos;
- provar que a verificação é read-only.

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
