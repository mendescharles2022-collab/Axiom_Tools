# Rastreador canônico — Execução de correção V8

Data: 31/08/2026  
Status: **B01–B50 REVISTOS / 0 INSPEÇÕES / 0 PRONTOS / TOOLING ATÉ ETAPA 81 / RUNTIME WINDOWS FÍSICO AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

## 1. Marco canônico atual do tooling

GitHub Actions run `33461512550`  
Commit `dcb1544188a3abbd79c5e7ab74c14de2a46e0c94`  
Python `3.12.14`

```text
POWERSHELL_B06_SMOKE_OK
POWERSHELL_B06_CONSUMER_SMOKE_OK
POWERSHELL_B06_PLAN_SMOKE_OK
POWERSHELL_B06_REVIEW_SKELETON_SMOKE_OK
Ran 547 tests in 1.711s
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

- ID `9783312623`;
- SHA-256 `52f7ca6f8edd246efc500bfd6dc1ddb44e1687fce4f9fc7991af22c643a424dc`.

Este é o marco de tooling. Ele **não** representa homologação da árvore operacional integral.

## 2. Evolução canônica — Etapas 42–81

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
- Etapa 81 — B06 revisão humana: `RECONCILIATION_REVIEW_SKELETON.json` integralmente `PENDING`, validador separado, evidência obrigatória e distinção entre revisão completa e baseline pronto.

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

## 4. B06 — cadeia preparada até a revisão humana

A `main` continua sendo fundação reduzida e não substitui a instalação operacional.

### Produtor

`BUILD_RUNTIME_HANDOFF_V8.ps1` + `build_runtime_reconciliation_handoff.py`:

- lê a origem operacional;
- exporta código/config segura por whitelist;
- mantém banco fora do ZIP;
- clona SQLite via backup consistente;
- gera manifesto e hashes;
- não move/apaga arquivos operacionais;
- autodiscovery só aceita exatamente um SQLite válido.

### Consumidor

`CONSUME_RUNTIME_HANDOFF_V8.ps1` + `consume_runtime_reconciliation_handoff.py`:

- valida manifesto e hashes externos;
- extrai para staging seguro;
- bloqueia traversal, symlink e payload excessivo;
- revalida manifesto interno, conteúdo proibido e possíveis segredos;
- executa diff runtime↔repo;
- executa preflight SQLite sobre a cópia;
- fotografa o handoff antes/depois e comprova imutabilidade.

### Plano da Etapa 80

`plan_runtime_reconciliation.py` + `config/runtime_reconciliation_plan_policy_v8.json`:

- `SAME` → `NO_ACTION`;
- `CHANGED` → `REVIEW_MERGE`;
- `RUNTIME_ONLY` → `REVIEW_IMPORT_RUNTIME`;
- `REPO_ONLY` → `REVIEW_KEEP_REPO`;
- diferenças sensíveis → `SECURITY_REVIEW_REQUIRED`;
- `automatic_write_allowed = false`;
- nenhuma ação proposta executa escrita.

### Revisão da Etapa 81

`create_reconciliation_review_skeleton.py` + `validate_reconciliation_review.py`:

- consumidor gera `RECONCILIATION_REVIEW_SKELETON.json` ligado ao `plan_sha256`;
- toda decisão automática nasce `PENDING`;
- automação não preenche revisor, motivo ou evidência;
- decisão humana real exige revisor + motivo + evidência;
- metadados do plano não podem ser alterados durante a revisão;
- itens `CRITICAL` não podem adotar runtime diretamente;
- `MERGE_REQUIRED` e `SECURITY_REVIEW_REQUIRED` não liberam baseline;
- escrita automática e homologação permanecem proibidas.

B06 continua `BLOQUEADO_POR_RUNTIME` porque a fotografia física real ainda não foi produzida, revisada e reconciliada.

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
4. obter diff + `RECONCILIATION_PLAN.json` + `RECONCILIATION_REVIEW_SKELETON.json` + preflight SQLite;
5. preencher humanamente cada decisão necessária, com motivo e evidência;
6. validar a revisão contra o plano original;
7. somente com revisão completa e baseline pronto registrar a aceitação do baseline reconciliado;
8. somente depois aplicar correções na árvore reconciliada.

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

O tooling avançou até a Etapa 81. O próximo avanço seguro é criar um manifesto imutável de aceitação do baseline que só possa nascer de uma revisão humana já validada como `review_complete = true` e `baseline_ready = true`, continuando sem executar qualquer cópia, merge ou alteração automática.
