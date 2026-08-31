# Rastreador canônico — Execução de correção V8

Data: 31/08/2026  
Status: **B01–B50 REVISTOS / 0 INSPEÇÕES / 0 PRONTOS / TOOLING ATÉ ETAPA 79 / RUNTIME WINDOWS FÍSICO AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

## 1. Marco canônico atual do tooling

GitHub Actions run `33452559940`  
Commit `9939b660d17c68c6848cb8d9cb5e24fffefd38dd`  
Python `3.12.14`

```text
POWERSHELL_B06_SMOKE_OK
POWERSHELL_B06_CONSUMER_SMOKE_OK
Ran 514 tests in 1.665s
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

- ID `9780276903`;
- SHA-256 `511d75258d3f7f28a519708d61407963ef6bf2c0ecf8b74051252464b5432e1f`.

Este é o marco de tooling. Ele **não** representa homologação da árvore operacional integral.

## 2. Evolução canônica — Etapas 42–79

A auditoria foi retomada sem reiniciar o trabalho anterior e sem descartar patrimônio válido.

- Etapa 42 — cobertura de config/identidade no tooling de reconciliação;
- Etapas 43–49 — reconfirmação dos defeitos B01–B28 e isolamento das causas nos deltas/runtime recuperado;
- Etapa 50 — B29–B33, parser, competência, IRRF e 13º;
- Etapa 51 — B34–B40, banco, segurança e concorrência;
- Etapa 52 — B41–B50, instalação, UX, escala, Sintegra, retenção e acervo;
- Etapas 53–55 — mapa causal, governança e reconciliação de config/identidade;
- Etapa 56 — B49, banco ↔ filesystem bidirecional read-only;
- Etapa 57 — B48, retenção segura Simular→Revisar→Confirmar→Revalidar;
- Etapas 58–59 — preflights de banco e rollback/readiness;
- Etapa 60 — B42, cadeia release→build→runtime→installer;
- Etapa 61 — B38, autorização/CSRF;
- Etapa 62 — B34, string ↔ Enum;
- Etapa 63 — B40, compare-and-set + `rowcount`;
- Etapa 64 — B28, idempotência/retry;
- Etapa 65 — B04, linhagem/vigência;
- Etapa 66 — B08, histórico/chamada com regressão T L;
- Etapa 67 — B36, migração global → fonte;
- Etapa 68 — B32, IRRF temporal/proveniência;
- Etapas 69–72 — B06, handoff único, launcher Windows, autodiscovery SQLite e smoke PowerShell do produtor;
- Etapa 73 — B01/B02/B03/B39, candidato não destrutivo, GET puro, gate de saída e reautorização de IDs;
- Etapa 74 — B07/B09/B10/B11/B37, universo operacional e semântica das máquinas de estado;
- Etapa 75 — B12–B17/B50, composição multi-documento, identidade PF/CAEPF e identidade econômica;
- Etapa 76 — B18–B27, decisão por fonte, aplicabilidade e eConsignado;
- Etapa 77 — B29/B30/B31/B33, parser Domínio, saldo federal, proveniência e dezembro/13º;
- Etapa 78 — B43/B44/B46/B47, contratos executáveis de UI para Pendências, A4, Monitor e Sintegra;
- Etapa 79 — B06, consumidor canônico do handoff: validação externa e interna, extração segura, diff runtime↔repo, preflight SQLite, wrapper PowerShell e smoke produtor+consumidor no mesmo CI.

Resultado da fase: **nenhum B permanece em inspeção ou apenas pronto para correção sem critério executável**.

## 3. Snapshot formal de estados

Fonte: `config/blocker_status_v8_current.json`.

| Estado | Quantidade |
|---|---:|
| `PRONTO_PARA_CORRIGIR` | 0 |
| `INSPECAO_PENDENTE` | 0 |
| `EM_CORRECAO` | 46 |
| `BLOQUEADO_POR_RUNTIME` | 4 |
| `CORRIGIDO_TESTADO` | 0 |
| `CORRIGIDO_HOMOLOGADO` | 0 |

Em correção: todos os bloqueadores exceto B05, B06, B45 e B49.  
Bloqueados pelo runtime: B05, B06, B45 e B49.

Regra permanente:

**patch encontrado ≠ tooling verde ≠ correção integrada ≠ homologação.**

## 4. B06 — gate estrutural/material atual

A `main` continua sendo uma fundação reduzida e não pode ser tratada como se fosse automaticamente a instalação operacional integral.

### Produtor já preparado/testado

- exportador runtime por whitelist;
- bloqueio de banco/documentos/segredos no ZIP de código;
- config segura e identidade de release;
- manifesto e hashes SHA-256;
- cópia SQLite consistente via backup;
- ZIP de código/configuração + SQLite separado + relatório + manifesto comum;
- prova de não mutação da origem;
- launcher `BUILD_RUNTIME_HANDOFF_V8.ps1` parametrizado, sem drive hardcoded e sem remoção/movimentação;
- autodiscovery limitada a exatamente um SQLite válido;
- `POWERSHELL_B06_SMOKE_OK` no CI.

### Consumidor acrescentado na Etapa 79

- `consume_runtime_reconciliation_handoff.py` valida o manifesto externo e seus hashes;
- valida ZIP de código, SHA/tamanho da cópia SQLite e relatório da clonagem;
- extrai ZIP apenas em staging isolado, bloqueando traversal, symlink e payload excessivo;
- verifica novamente conteúdo proibido, possíveis segredos e o manifesto interno;
- executa diff runtime ↔ repositório sem esconder `CHANGED`, `RUNTIME_ONLY` ou `REPO_ONLY`;
- executa preflight SQLite sobre a cópia do handoff;
- prova handoff intacto antes/depois;
- nunca marca a V8 como homologada;
- wrapper `CONSUME_RUNTIME_HANDOFF_V8.ps1` compatível com Windows PowerShell 5.1;
- smoke CI executa produtor e consumidor na mesma cadeia e exige `POWERSHELL_B06_CONSUMER_SMOKE_OK`.

B06 continua `BLOQUEADO_POR_RUNTIME` porque a instalação Windows física do escritório ainda não foi coletada e consumida. A diferença agora é que o caminho físico está integralmente preparado e testado.

## 5. Guardrails funcionais já preparados

### Reprocessamento, Conferência e saídas

B01/B02/B03/B39 possuem auditores para candidato não destrutivo, GET sem mutação, gate único de saída e reautorização backend de seleções manuais.

### Fechamento, chamadas e estados

B07/B08/B09/B10/B11/B37/B40 possuem contratos para universo operacional, separação de fechados/retificações, semântica de `PRONTA`, histórico de chamada e compare-and-set.

### Documentos, identidade e composição

B12–B17/B50 possuem planner que separa identidade física, lógica e econômica. A regressão Jair mantém federal consolidado uma vez e FGTS aditivo por matrícula; PF rural exige identidade CAEPF/unidade quando aplicável.

### Decisão por fonte e aplicabilidade

B18–B23/B36 impedem decisão global cega, tratam FGTS zero, MEI/DAE, deduções, afastamentos/faltas e impedimentos por obrigação.

### eConsignado

B24–B28 exigem Etapa 0 do orquestrador, universo da chamada, fotografia preservada, resultado externo separado da conclusão de negócio e idempotência/retry.

### Parser e competência

B29–B33 protegem diretor ≠ empregado, saldo federal autoritativo, proveniência, IRRF por competência de pagamento e tratamento especial de dezembro/13º.

### Banco, segurança e release

B34/B35/B38/B41/B42 possuem auditores/preflights para Enum/string, integridade/FKs/invariantes, auth/CSRF, rollback e cadeia de identidade de release.

### UI operacional

B43/B44/B46/B47 possuem política canônica em `config/operational_ui_contract_v8.json`:

- Pendências por competência ativa, PROC secundário;
- A4 retrato, cabeçalho repetível e controle de quebra;
- Monitor com `status_operacional` canônico;
- Sintegra exigindo separadamente backend configurado e `href` visível.

### Escala, manutenção e acervo

B45 depende de benchmark >600 no runtime; B48 possui fluxo de retenção não destrutivo; B49 possui auditoria banco↔filesystem bidirecional read-only.

## 6. C01–C28

Mapa canônico:

`config/regression_case_blocker_map_v8_202608.json`

Cobertura causal: `28/28`.

Nenhum caso pode virar PASS enquanto seus bloqueadores estruturais associados não forem corrigidos/testados na árvore operacional reconciliada.

## 7. Sequência física B06 preparada

Quando a instalação Windows real estiver disponível para execução:

1. executar `BUILD_RUNTIME_HANDOFF_V8.ps1` com saída externa à árvore operacional;
2. preservar juntos manifesto, ZIP, SQLite e relatório, sem edição manual;
3. levar o diretório de handoff ao ambiente de auditoria/reconciliação;
4. executar `CONSUME_RUNTIME_HANDOFF_V8.ps1` com staging novo e externo ao repositório;
5. revisar `RECONCILIATION.jsonl`, resumo e `DATABASE_HOMOLOGATION_PREFLIGHT.json`;
6. classificar divergências e fixar o baseline antes de qualquer integração de código.

A origem operacional não entra na área de escrita da auditoria.

## 8. Ordem operacional após materialização do B06

1. classificar/revisar o diff runtime ↔ repositório;
2. fixar baseline reconciliado;
3. executar B35/B49 sobre a cópia SQLite/acervo real;
4. aplicar os guardrails B01–B44/B46–B48/B50 sobre a árvore reconciliada;
5. corrigir os achados reais por dependência causal;
6. benchmark B45 com volume representativo;
7. executar C01–C28 sobre casos reais/fixtures vinculadas;
8. gerar build com proveniência final;
9. instalar no Windows;
10. comprovar rollback físico e smoke final.

## 9. Gate final

Modo final continua exigindo cumulativamente:

- 50/50 B homologados;
- 28/28 C PASS;
- mapa causal válido;
- release READY;
- build verificável;
- dez gates externos PASS.

## 10. Situação atual

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**

A auditoria/tooling avançou até a Etapa 79. O produtor e o consumidor B06 estão testados ponta a ponta em CI. O gargalo material continua sendo obter a fotografia da instalação Windows física; o próximo trabalho lógico é transformar o diff produzido pelo consumidor em um plano de reconciliação revisável, nunca numa cópia automática de runtime sobre repositório.
