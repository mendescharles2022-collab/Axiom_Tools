# Auditoria canônica V8 — Etapa 82

Data: 31/08/2026  
Status: **ACEITE IMUTÁVEL DE BASELINE B06 TESTADO / SEM EXECUÇÃO AUTOMÁTICA / RUNTIME WINDOWS FÍSICO AINDA NÃO COLETADO / V8 NÃO HOMOLOGADA**

## 1. Objetivo

A Etapa 81 separou a fila automática de divergências da decisão humana e criou um validador capaz de afirmar quando uma revisão está completa e quando o baseline está efetivamente pronto.

Ainda faltava registrar de forma imutável **qual baseline foi aceito**, sem confundir aceite com execução.

A Etapa 82 fecha essa lacuna.

## 2. Novo artefato

Novo script:

`scripts/build_reconciliation_baseline_acceptance.py`

Saída:

`RECONCILIATION_BASELINE_ACCEPTANCE.json`

O manifesto só pode ser criado quando a revisão, revalidada contra o plano original, resultar cumulativamente em:

- `review_complete = true`;
- `baseline_ready = true`;
- `automatic_write_allowed = false`;
- `v8_homologated = false`.

O script reutiliza diretamente `validate_reconciliation_review.validate_review`; não cria uma segunda regra paralela de revisão.

## 3. Separação entre aceite e execução

Mesmo quando o baseline está pronto, o manifesto declara obrigatoriamente:

- `automatic_write_allowed = false`;
- `execution_performed = false`;
- `v8_homologated = false`.

Portanto:

**baseline aceito ≠ reconciliação aplicada ≠ V8 homologada.**

O script não copia, move, remove, mescla ou modifica arquivos do runtime ou do repositório.

## 4. Vínculos criptográficos

O aceite registra:

- `plan_sha256`;
- SHA-256 canônico da revisão humana completa;
- `review_validation_sha256` produzido pelo validador da Etapa 81;
- `acceptance_sha256` do próprio manifesto.

Cada decisão preserva ainda os hashes do runtime e do repositório originados no plano, impedindo que o aceite perca a identidade concreta da divergência revisada.

## 5. Decisões registradas

O manifesto contém, para cada item revisável:

- área;
- caminho relativo;
- estado da divergência;
- ação originalmente proposta;
- risco;
- SHA-256 do runtime;
- SHA-256 do repositório;
- decisão humana;
- revisor;
- motivo;
- evidências.

A cobertura precisa ser exatamente igual à fila revisável do plano.

## 6. Pendências e decisões intermediárias são bloqueadas

O aceite não pode nascer se existir:

- `PENDING`;
- `MERGE_REQUIRED`;
- `SECURITY_REVIEW_REQUIRED`.

Esses estados podem fazer parte de uma revisão válida, mas não de um baseline pronto.

Assim, o artefato final de aceite só registra decisões já resolvidas.

## 7. Conteúdo sensível

A política da Etapa 80 e o validador da Etapa 81 continuam sendo a autoridade.

Conteúdo `CRITICAL` não pode receber `ADOPT_RUNTIME`.

Um item sensível pode participar de um baseline aceito quando uma decisão permitida e resolvida, como `KEEP_REPO`, possui revisor, motivo e evidência válidos.

O manifesto apenas registra essa decisão; não executa nenhuma mudança.

## 8. Regressões

Novo arquivo:

`tests/test_reconciliation_baseline_acceptance.py`

Cobertura:

- revisão segura e completa gera aceite;
- esqueleto `PENDING` é rejeitado;
- `MERGE_REQUIRED` é rejeitado como baseline não pronto;
- `SECURITY_REVIEW_REQUIRED` é rejeitado como baseline não pronto;
- item sensível `KEEP_REPO` com evidência pode ser aceito;
- item sensível `ADOPT_RUNTIME` permanece proibido;
- plano adulterado é rejeitado;
- metadado da revisão adulterado é rejeitado;
- hashes de plano, revisão, validação e aceite ficam vinculados;
- hash do aceite é estável;
- inputs não são mutados;
- hashes concretos runtime/repo são preservados por decisão;
- CLI recusa sobrescrever aceite existente.

## 9. Fronteira automática preservada

O smoke PowerShell B06 continua terminando no esqueleto de revisão `PENDING`.

A Etapa 82 **não** foi acoplada ao consumidor automático e o CI não simula uma aprovação do próprio pipeline.

Os testes do aceite usam revisões sintéticas explicitamente preenchidas apenas para exercitar o contrato.

Isso preserva a regra:

**automação prepara; humano decide; tooling valida e registra; tooling não se autoaprova.**

## 10. Evidência canônica

GitHub Actions:

- run: `33461787567`;
- commit auditado: `8929aeb07140fa0a52c160725e274b97c3011d71`;
- Python: `3.12.14`;
- testes: `559 OK`;
- produtor: `POWERSHELL_B06_SMOKE_OK`;
- consumidor: `POWERSHELL_B06_CONSUMER_SMOKE_OK`;
- plano: `POWERSHELL_B06_PLAN_SMOKE_OK`;
- esqueleto: `POWERSHELL_B06_REVIEW_SKELETON_SMOKE_OK`;
- mapa causal: `28/28`;
- artifact: `v8-release-preflight#9783408220`;
- SHA-256: `8871c62216d587d2156e62ae348515f3a84f2efddc53086a1cd9106cb05fb679`.

Preflight do mesmo marco:

- B homologados: `0/50`;
- C PASS: `0/28`;
- mapa causal: `28/28`;
- evidências externas PASS: `1/10`;
- release READY: `False`;
- build OK: `False`.

## 11. Estado correto do B06

B06 permanece **`BLOQUEADO_POR_RUNTIME`**.

Nenhum aceite real foi produzido porque ainda não existe nesta auditoria a fotografia física da instalação Windows e, consequentemente, não existe revisão humana real das diferenças dessa instalação.

A cadeia preparada agora é:

1. handoff físico;
2. consumo seguro;
3. diff;
4. plano read-only;
5. esqueleto `PENDING`;
6. revisão humana;
7. validação da revisão;
8. aceite imutável do baseline;
9. somente depois, reconciliação em staging/integração controlada.

## 12. Próximo avanço seguro

O próximo passo automatizável deve trabalhar **a partir do aceite**, nunca diretamente do diff ou da revisão incompleta.

Uma futura materialização deve ocorrer primeiro em staging isolado, com ações derivadas das decisões aceitas e verificação posterior do resultado, sem escrever diretamente sobre a instalação operacional ou sobre a `main`.

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
