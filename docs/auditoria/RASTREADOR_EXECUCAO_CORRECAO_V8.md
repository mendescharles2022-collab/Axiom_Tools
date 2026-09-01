# Rastreador canônico — Execução de correção V8

Data: 31/08/2026  
Status: **B01–B50 REVISTOS / 0 INSPEÇÕES / 0 PRONTOS / TOOLING ATÉ ETAPA 83 / RUNTIME WINDOWS FÍSICO AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

## 1. Marco canônico atual do tooling

GitHub Actions run `33462096429`  
Commit `6a9d9f9096f1a98e550fa9a39019fe3c1df2d8b5`  
Python `3.12.14`

```text
POWERSHELL_B06_SMOKE_OK
POWERSHELL_B06_CONSUMER_SMOKE_OK
POWERSHELL_B06_PLAN_SMOKE_OK
POWERSHELL_B06_REVIEW_SKELETON_SMOKE_OK
Ran 571 tests in 1.908s
OK
```

Preflight do mesmo marco:

- B homologados `0/50`;
- C PASS `0/28`;
- mapa causal C→B `28/28`;
- evidências externas PASS `1/10`;
- release READY `False`;
- build OK `False`.

Artifact `v8-release-preflight`:

- ID `9783514548`;
- SHA-256 `9530f6de0f7950f326be67614dbc03db6d03fe6c58507c7e38190ab056790c02`.

Este é o marco de tooling. Ele **não** representa homologação da árvore operacional integral.

## 2. Evolução canônica — Etapas 42–83

- Etapas 42–52 — auditoria causal B01–B50 e isolamento dos defeitos na base/deltas disponíveis;
- Etapas 53–68 — mapa causal, governança e toolings de banco, segurança, concorrência, versões, chamadas, estados e proveniência;
- Etapas 69–72 — B06 produtor: handoff único, launcher Windows, autodiscovery SQLite e smoke PowerShell;
- Etapa 73 — B01/B02/B03/B39: reprocessamento candidato, GET puro, gate único e seleção manual;
- Etapa 74 — B07/B09/B10/B11/B37: universo operacional e máquinas de estado;
- Etapa 75 — B12–B17/B50: composição multi-documento, identidade PF/CAEPF e identidade econômica;
- Etapa 76 — B18–B27: decisão por fonte, aplicabilidade e eConsignado;
- Etapa 77 — B29/B30/B31/B33: parser Domínio, saldo federal, proveniência e dezembro/13º;
- Etapa 78 — B43/B44/B46/B47: contratos executáveis de UI;
- Etapa 79 — B06 consumidor: validação externa/interna, extração segura, diff runtime↔repo, preflight SQLite e wrapper Windows;
- Etapa 80 — B06 plano read-only: `RECONCILIATION_PLAN.json`, ações propostas, proteção de conteúdo sensível e proibição de escrita automática;
- Etapa 81 — B06 revisão humana: `RECONCILIATION_REVIEW_SKELETON.json` integralmente `PENDING`, validador separado, evidência obrigatória e distinção entre revisão completa e baseline pronto;
- Etapa 82 — B06 aceite: `RECONCILIATION_BASELINE_ACCEPTANCE.json` só pode nascer de revisão `review_complete=true` e `baseline_ready=true`, com hashes vinculados e `execution_performed=false`;
- Etapa 83 — B06 materialização: baseline aceito só é aplicado em staging novo e isolado; fontes são revalidadas por hash e runtime/repositório permanecem intactos.

Resultado: **nenhum B permanece em inspeção ou apenas pronto para correção sem critério executável**.

## 3. Snapshot formal

Fonte: `config/blocker_status_v8_current.json`.

| Estado | Quantidade |
|---|---:|
| `PRONTO_PARA_CORRIGIR` | 0 |
| `INSPECAO_PENDENTE` | 0 |
| `EM_CORRECAO` | 46 |
| `BLOQUEADO_POR_RUNTIME` | 4 |
| `CORRIGIDO_TESTADO` | 0 |
| `CORRIGIDO_HOMOLOGADO` | 0 |

Bloqueados pelo runtime físico: **B05, B06, B45 e B49**.

Regra permanente:

**patch encontrado ≠ tooling verde ≠ correção integrada ≠ homologação.**

## 4. B06 — cadeia preparada até staging reconciliado

A `main` continua sendo fundação reduzida e não substitui a instalação operacional.

### Handoff e consumo

A cadeia `BUILD_RUNTIME_HANDOFF_V8.ps1` → `CONSUME_RUNTIME_HANDOFF_V8.ps1`:

- lê a origem operacional sem mutá-la;
- exporta código/config segura por whitelist;
- mantém banco fora do ZIP;
- clona SQLite via backup consistente;
- gera manifesto/hashes;
- extrai somente em staging seguro;
- bloqueia traversal, symlink, payload excessivo, conteúdo proibido e possíveis segredos;
- executa diff runtime↔repo e preflight SQLite;
- comprova handoff intacto.

### Plano, revisão e aceite

- Etapa 80: `plan_runtime_reconciliation.py` transforma diferenças em ações de revisão e mantém escrita automática desativada;
- Etapa 81: esqueleto nasce todo `PENDING`; decisão humana exige revisor + motivo + evidência; itens sensíveis têm proteção reforçada;
- Etapa 82: `build_reconciliation_baseline_acceptance.py` só registra baseline se revisão estiver completa e pronta, sempre com `execution_performed=false`.

### Materialização da Etapa 83

`materialize_reconciled_staging.py`:

- recebe apenas aceite válido;
- revalida `acceptance_sha256`;
- revalida os hashes do runtime e repo antes de criar saída;
- detecta colisões de destinos entre layouts equivalentes;
- cria staging fora de runtime e repo e recusa sobrescrita;
- `ADOPT_RUNTIME`, `KEEP_REPO` e `EXCLUDE_WITH_REASON` atuam só na árvore nova;
- bloqueia symlink, conteúdo proibido e possível segredo;
- remove somente staging parcial em caso de falha;
- gera `RECONCILED_STAGING_REPORT.json` com lista/hash de arquivos e `tree_sha256`;
- declara `repository_write_performed=false`, `runtime_write_performed=false`, `operational_deployment_performed=false` e `v8_homologated=false`.

B06 continua `BLOQUEADO_POR_RUNTIME` porque a fotografia física real ainda não foi produzida, revisada, aceita e materializada.

## 5. Guardrails funcionais preservados

- B01/B02/B03/B39 — candidato não destrutivo, GET puro, gate de saída, IDs reautorizados;
- B07/B08/B09/B10/B11/B37/B40 — universo, chamadas, estados e CAS;
- B12–B17/B50 — composição documental/econômica e identidade;
- B18–B23/B36 — decisão por fonte e aplicabilidade;
- B24–B28 — eConsignado Etapa 0, universo correto e idempotência/retry;
- B29–B33 — parser, saldo federal, competência, IRRF e 13º;
- B34/B35/B38/B41/B42 — Enum/string, banco, segurança, rollback e release identity;
- B43/B44/B46/B47 — Pendências, A4, Monitor e Sintegra;
- B48 — retenção segura;
- B49 — banco↔filesystem read-only;
- B45 — benchmark representativo depende do runtime.

## 6. C01–C28

Mapa canônico: `config/regression_case_blocker_map_v8_202608.json`.

Cobertura causal: `28/28`.

Nenhum caso pode virar PASS enquanto seus bloqueadores associados não forem corrigidos/testados na árvore operacional reconciliada.

## 7. Sequência física B06

Quando a instalação Windows real for coletada:

1. produzir o handoff fora da árvore operacional;
2. transportar o diretório sem editar seus artefatos;
3. consumir em staging novo;
4. obter diff + plano + esqueleto de revisão + preflight SQLite;
5. preencher humanamente cada decisão necessária, com motivo e evidência;
6. validar a revisão contra o plano original;
7. gerar o aceite imutável somente se o baseline estiver pronto;
8. materializar uma árvore reconciliada em staging isolado;
9. verificar independentemente relatório, árvore e decisões materializadas;
10. executar os guardrails sobre a árvore reconciliada;
11. somente depois integrar correções controladas.

A origem operacional não entra na área de escrita da auditoria.

## 8. Gate final

Exige cumulativamente:

- 50/50 B homologados;
- 28/28 C PASS;
- mapa causal válido;
- release READY;
- build verificável;
- dez gates externos PASS.

## 9. Situação atual

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**

O tooling avançou até a Etapa 83. O próximo avanço seguro é verificar independentemente a árvore materializada antes de executar qualquer auditor/guardrail sobre ela.
