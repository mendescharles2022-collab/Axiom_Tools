# Auditoria canônica V8 — Etapa 81

Data: 31/08/2026  
Status: **REVISÃO HUMANA DA RECONCILIAÇÃO B06 ESTRUTURADA E TESTADA / RUNTIME WINDOWS FÍSICO AINDA NÃO COLETADO / V8 NÃO HOMOLOGADA**

## 1. Lacuna encerrada

A Etapa 80 passou a transformar o diff runtime ↔ repositório em `RECONCILIATION_PLAN.json`, com ações propostas e escrita automática desativada.

Ainda faltava separar duas responsabilidades que não podem ser confundidas:

1. o sistema pode preparar a fila de divergências;
2. a decisão sobre cada divergência precisa permanecer explicitamente humana.

A Etapa 81 fecha essa lacuna sem transformar revisão em execução e sem permitir que a automação fabrique aprovação.

## 2. Esqueleto de revisão humana

Novo arquivo:

`scripts/create_reconciliation_review_skeleton.py`

O gerador recebe o plano de reconciliação já validado e produz:

`RECONCILIATION_REVIEW_SKELETON.json`

Regras do esqueleto automático:

- inclui somente entradas `review_required = true`;
- fica vinculado ao `plan_sha256`;
- todas as decisões nascem como `PENDING`;
- `reviewer = ""`;
- `reason = ""`;
- `evidence = []`;
- `automatic_write_allowed = false`;
- `review_complete = false`;
- `baseline_ready = false`;
- `v8_homologated = false`;
- recusa sobrescrever arquivo existente;
- recusa plano adulterado ou com hash lógico inválido.

O gerador não possui caminho para preencher decisão humana.

## 3. Validador separado

Novo arquivo:

`scripts/validate_reconciliation_review.py`

A revisão preenchida é validada separadamente contra o plano original.

Para toda decisão diferente de `PENDING`, o validador exige cumulativamente:

- revisor identificado;
- motivo explícito;
- pelo menos uma evidência;
- metadados do item idênticos aos do plano.

Ele rejeita:

- item ausente;
- item duplicado;
- item que não pertence à fila revisável;
- alteração de área, caminho, status, risco, hashes ou ação proposta;
- `plan_sha256` divergente;
- tentativa de habilitar escrita automática;
- tentativa de marcar V8 homologada;
- `PENDING` com campos humanos já preenchidos.

## 4. Proteção de conteúdo sensível

Itens de risco `CRITICAL`, inclusive configuração, autenticação, segurança, identidade de release e outros padrões protegidos pela política da Etapa 80, não podem receber `ADOPT_RUNTIME`.

Uma decisão `SECURITY_REVIEW_REQUIRED` pode significar que o item foi analisado e classificado, mas não libera o baseline.

Da mesma forma, `MERGE_REQUIRED` pode encerrar a revisão daquela divergência sem afirmar que o baseline está pronto.

Assim:

**review_complete ≠ baseline_ready.**

## 5. Integração ao consumidor B06

`scripts/consume_runtime_reconciliation_handoff.py` foi ampliado para gerar automaticamente, depois do plano:

`RECONCILIATION_REVIEW_SKELETON.json`

O relatório `RUNTIME_HANDOFF_CONSUMPTION.json` agora registra também:

- arquivo do esqueleto;
- SHA-256 lógico do esqueleto;
- quantidade de itens pendentes;
- `human_review_decisions_written = false`.

O consumidor continua sem alterar handoff, repositório ou instalação operacional.

Ele prepara a fila; não decide a fila.

## 6. Windows PowerShell

`scripts/CONSUME_RUNTIME_HANDOFF_V8.ps1` agora exige e valida os três artefatos da reconciliação:

1. `RECONCILIATION_PLAN.json`;
2. `RECONCILIATION_REVIEW_SKELETON.json`;
3. `RUNTIME_HANDOFF_CONSUMPTION.json`.

O wrapper confere:

- vínculo do esqueleto ao `plan_sha256`;
- hash do esqueleto reportado pelo consumidor;
- quantidade de pendências;
- `human_review_decisions_written = false`;
- `review_complete = false`;
- `baseline_ready = false`;
- todas as decisões exatamente `PENDING`;
- revisor e motivo vazios;
- evidências vazias;
- escrita automática desativada;
- V8 não homologada.

Marcador adicional de smoke:

`POWERSHELL_B06_REVIEW_SKELETON_SMOKE_OK`

## 7. Regressões

`tests/test_reconciliation_review_workflow.py` cobre, entre outros:

- cobertura exata dos itens revisáveis;
- vínculo ao hash do plano;
- rejeição de plano adulterado;
- ausência e duplicidade de decisões;
- alteração indevida de metadados;
- exigência de revisor, motivo e evidência;
- proibição de preenchimento falso em item `PENDING`;
- proteção de item sensível contra `ADOPT_RUNTIME`;
- distinção entre revisão completa e baseline pronto;
- cenário seguro integralmente resolvido;
- `MERGE_REQUIRED` sem baseline pronto;
- exclusão explícita de item runtime-only com justificativa/evidência;
- tentativa de escrita automática ou homologação;
- recusa de sobrescrita do esqueleto.

Os testes estáticos dos launchers também foram atualizados para exigir o novo artefato e o novo marcador do smoke.

## 8. Evidência canônica

GitHub Actions:

- run: `33461512550`;
- commit auditado: `dcb1544188a3abbd79c5e7ab74c14de2a46e0c94`;
- Python: `3.12.14`;
- testes: `547 OK`;
- produtor: `POWERSHELL_B06_SMOKE_OK`;
- consumidor: `POWERSHELL_B06_CONSUMER_SMOKE_OK`;
- plano: `POWERSHELL_B06_PLAN_SMOKE_OK`;
- esqueleto: `POWERSHELL_B06_REVIEW_SKELETON_SMOKE_OK`;
- mapa causal: `28/28`;
- artifact: `v8-release-preflight#9783312623`;
- SHA-256: `52f7ca6f8edd246efc500bfd6dc1ddb44e1687fce4f9fc7991af22c643a424dc`.

No smoke, a cadeia descartável produziu intencionalmente:

- `SAME = 0`;
- `CHANGED = 0`;
- `RUNTIME_ONLY = 1`;
- `REPO_ONLY = 9`;
- revisão obrigatória = `10`;
- decisões humanas preenchidas = `NÃO`;
- preflight DB = `OK`.

Preflight do mesmo marco:

- B homologados: `0/50`;
- C PASS: `0/28`;
- mapa causal: `28/28`;
- evidências externas PASS: `1/10`;
- release READY: `False`;
- build OK: `False`.

## 9. Estado correto do B06

B06 permanece **`BLOQUEADO_POR_RUNTIME`**.

A Etapa 81 não coletou a instalação Windows física e não preencheu decisões humanas reais.

A cadeia segura disponível passa a ser:

1. produzir o handoff físico;
2. consumir em staging isolado;
3. gerar diff;
4. gerar plano;
5. gerar esqueleto `PENDING`;
6. revisar cada divergência humanamente;
7. validar a revisão;
8. somente então avaliar a fixação do baseline reconciliado.

Nenhuma diferença foi aplicada automaticamente ao `main`.

## 10. Próximo avanço seguro

Depois de uma revisão humana válida, ainda falta um artefato imutável que registre **qual baseline foi aceito**, vinculado ao plano e à revisão, sem executar cópia, merge, remoção ou homologação.

A próxima etapa deve criar esse manifesto de aceitação somente quando a revisão estiver `review_complete = true` e `baseline_ready = true`.

O manifesto deverá continuar declarando explicitamente:

- escrita automática desativada;
- execução não realizada;
- V8 não homologada.

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
