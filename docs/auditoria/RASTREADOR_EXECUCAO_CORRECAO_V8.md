# Rastreador canônico — Execução de correção V8

Data: 31/08/2026  
Status: **B01–B50 REVISTOS / 0 INSPEÇÕES / 0 PRONTOS / TOOLING ATÉ ETAPA 78 / RUNTIME WINDOWS AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

## 1. Marco canônico atual do tooling

GitHub Actions run `33452021223`  
Commit `47da595d2eed0d6a18176bc4eddb0cc2dd3e6891`  
Python `3.12.14`

```text
POWERSHELL_B06_SMOKE_OK
Ran 494 tests in 1.584s
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

- ID `9780092100`;
- SHA-256 `21010ecfbd5bf75d2fed3b691ba5a5a11c6e63de78878e6eafa0b40af4891db4`.

Este é o marco de tooling. Ele **não** representa homologação da árvore operacional integral.

## 2. Evolução canônica — Etapas 42–78

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
- Etapas 69–72 — B06, handoff único, launcher Windows, autodiscovery SQLite e smoke PowerShell real em CI;
- Etapa 73 — B01/B02/B03/B39, candidato não destrutivo, GET puro, gate de saída e reautorização de IDs;
- Etapa 74 — B07/B09/B10/B11/B37, universo operacional e semântica das máquinas de estado;
- Etapa 75 — B12–B17/B50, composição multi-documento, identidade PF/CAEPF e identidade econômica;
- Etapa 76 — B18–B27, decisão por fonte, aplicabilidade e eConsignado;
- Etapa 77 — B29/B30/B31/B33, parser Domínio, saldo federal, proveniência e dezembro/13º;
- Etapa 78 — B43/B44/B46/B47, contratos executáveis de UI para Pendências, A4, Monitor e Sintegra.

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

Tooling já preparado/testado:

- exportador runtime por whitelist;
- bloqueio de banco/documentos/segredos no ZIP de código;
- config segura e identidade de release;
- auditor runtime ↔ repositório;
- manifesto e hashes SHA-256;
- pipeline E2E de reconciliação em fixtures;
- preflight causal 28/28;
- cópia SQLite consistente via backup;
- handoff único com ZIP de código/configuração + banco separado + relatório + manifesto comum;
- prova de não mutação da origem;
- launcher PowerShell parametrizado, sem drive hardcoded e sem remoção/movimentação;
- autodiscovery limitada a exatamente um SQLite válido;
- smoke PowerShell em CI com `POWERSHELL_B06_SMOKE_OK`.

B06 continua `BLOQUEADO_POR_RUNTIME` até executar essa cadeia contra a instalação Windows física e consumir os artefatos produzidos numa reconciliação verificável.

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

## 7. Ordem operacional após materialização do B06

1. verificar e consumir o handoff real;
2. reconciliar runtime ↔ repositório e fixar baseline;
3. executar B35/B49 sobre a cópia SQLite/acervo real;
4. aplicar os guardrails B01–B44/B46–B48/B50 sobre a árvore reconciliada;
5. corrigir os achados reais por dependência causal;
6. benchmark B45 com volume representativo;
7. executar C01–C28 sobre casos reais/fixtures vinculadas;
8. gerar build com proveniência final;
9. instalar no Windows;
10. comprovar rollback físico e smoke final.

## 8. Gate final

Modo final continua exigindo cumulativamente:

- 50/50 B homologados;
- 28/28 C PASS;
- mapa causal válido;
- release READY;
- build verificável;
- dez gates externos PASS.

## 9. Situação atual

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**

A auditoria/tooling avançou até a Etapa 78. O trabalho lógico preparatório não possui mais itens em mera inspeção ou apenas `PRONTO_PARA_CORRIGIR`. O gargalo material é B06: obter e consumir uma fotografia verificável da instalação Windows real sem tocar na origem operacional.
