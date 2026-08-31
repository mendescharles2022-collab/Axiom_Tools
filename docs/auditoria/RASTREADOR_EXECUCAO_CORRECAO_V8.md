# Rastreador canônico — Execução de correção V8

Data: 31/08/2026  
Status: **DIAGNÓSTICO B01–B50 REVISTO / 0 INSPEÇÕES PENDENTES / TOOLING ATÉ ETAPA 73 / RUNTIME WINDOWS AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

## 1. Marco canônico atual do tooling

GitHub Actions run `33447254039`  
Commit `e51bc61f13bbb21922b295eb57f8794a481962ed`  
Python `3.12.14`

```text
POWERSHELL_B06_SMOKE_OK
Ran 371 tests in 1.531s
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

- ID `9778467287`;
- SHA-256 `4ce32783f1cd0d4fd2df6300d39d7a7cb3c87e2b4054fdbe3b06c1bfad2e6919`.

Este é o marco de tooling. Ele **não** representa homologação da árvore operacional integral.

## 2. Evolução canônica — Etapas 42–73

A auditoria foi retomada sem reiniciar o trabalho anterior e sem descartar patrimônio válido.

- Etapa 42 — lacuna de config/identidade no tooling de reconciliação;
- Etapa 43 — B01/B02 reconfirmados no V8F2 e side effect do validador;
- Etapa 44 — origem histórica B02 V6→V7 e investigação B08;
- Etapa 45 — B03 isolado em autorização espalhada;
- Etapa 46 — B07/B09/B10 e mitigação B11;
- Etapa 47 — B12–B17, multi-documento e identidade econômica;
- Etapa 48 — B18–B23, decisão por fonte e aplicabilidade;
- Etapa 49 — B24–B28, eConsignado;
- Etapa 50 — B29–B33, parser, competência, IRRF e 13º;
- Etapa 51 — B34–B40, banco, segurança e concorrência;
- Etapa 52 — B41–B50, instalação, UX, escala, Sintegra, retenção e acervo;
- Etapa 53 — mapa causal C01–C28 → B01–B50;
- Etapa 54 — validador causal e integração de governança;
- Etapa 55 — config/release_identity no tooling B06/B42 e recuperação do CI;
- Etapa 56 — B49 bidirecional banco ↔ filesystem;
- Etapa 57 — B48 retenção segura sem executor destrutivo;
- Etapas 58–59 — consolidação de preflights/readiness e avanço da cadeia de tooling;
- Etapa 60 — B42, cadeia de identidade/proveniência de build;
- Etapa 61 — B38, preflight de autorização/CSRF por contrato explícito;
- Etapa 62 — B34, auditor string ↔ Enum para `classificacao_inativacao`;
- Etapa 63 — B40, auditor compare-and-set e `rowcount`;
- Etapa 64 — B28, idempotência/retry;
- Etapa 65 — B04, linhagem/vigência de versões e retificações;
- Etapa 66 — B08, histórico estado/chamada com regressão explícita T L;
- Etapa 67 — B36, planner read-only estado global → fonte;
- Etapa 68 — B32, competência temporal/proveniência IRRF;
- Etapa 69 — B06, handoff único runtime: código/config + SQLite separado + manifesto comum;
- Etapa 70 — B06, launcher Windows parametrizado para executar o handoff em um comando;
- Etapa 71 — B06, autodiscovery SQLite conservadora e `-Database` opcional somente quando a seleção for inequívoca;
- Etapa 72 — B06, smoke end-to-end do launcher sob PowerShell no CI, com runtime e SQLite reais descartáveis e trigger obrigatório para `scripts/*.ps1`;
- Etapa 73 — B01/B02/B03/B39, auditores executáveis para reprocessamento candidato, pureza GET, gate único de saída e reautorização backend de seleção manual.

Resultado da fase: **nenhum B permanece em mera inspeção sem critério executável**.

## 3. Snapshot formal de estados

Fonte: `config/blocker_status_v8_current.json`.

| Estado | Quantidade |
|---|---:|
| `PRONTO_PARA_CORRIGIR` | 30 |
| `INSPECAO_PENDENTE` | 0 |
| `EM_CORRECAO` | 16 |
| `BLOQUEADO_POR_RUNTIME` | 4 |
| `CORRIGIDO_TESTADO` | 0 |
| `CORRIGIDO_HOMOLOGADO` | 0 |

Em correção: B01, B02, B03, B04, B08, B28, B32, B34, B35, B36, B38, B39, B40, B41, B42 e B48.  
Bloqueados pelo runtime: B05, B06, B45 e B49.

Regra permanente:

**patch encontrado ≠ tooling verde ≠ correção integrada ≠ homologação.**

## 4. B06 — gate estrutural atual

Não implementar correções operacionais diretamente sobre uma fundação reduzida da `main` como se ela fosse o runtime final.

Tooling já preparado/testado:

- exportador runtime por whitelist;
- bloqueio de banco/documentos/segredos no ZIP de código;
- config segura e identidade de release;
- auditor runtime ↔ repositório;
- manifesto e hashes SHA-256;
- E2E de reconciliação;
- preflight causal 28/28;
- cópia SQLite consistente via backup;
- handoff único da Etapa 69 com ZIP de código/configuração + banco separado + relatório + manifesto comum;
- prova de não mutação da origem;
- equivalência efetiva de schema origem × cópia testada;
- launcher PowerShell da Etapa 70, parametrizado, sem drive hardcoded e sem comandos de remoção/movimentação;
- autodiscovery da Etapa 71, limitada a exatamente um SQLite com cabeçalho válido; zero/múltiplos exigem caminho explícito e o manifesto registra `database_selection`;
- smoke PowerShell da Etapa 72, executando o launcher real em CI e exigindo `POWERSHELL_B06_SMOKE_OK`.

B06 continua `BLOQUEADO_POR_RUNTIME` até:

1. executar o launcher contra a instalação Windows física real;
2. materializar o ZIP seguro e a cópia SQLite real;
3. auditar/reconciliar runtime ↔ repositório;
4. executar os preflights estruturais sobre a fotografia real;
5. estabelecer o baseline da mesma árvore que será corrigida e empacotada.

## 5. C01–C28 — gate causal

Mapa:

`config/regression_case_blocker_map_v8_202608.json`

O mapa cobre `28/28` casos. Nenhum caso pode ser marcado PASS enquanto seus bloqueadores estruturais associados permanecerem abertos.

## 6. Diagnósticos críticos preservados

### B01 — reprocessamento

O padrão destrutivo observado no V8F2 agora possui auditor executável. Ele bloqueia remoção de interpretação vigente antes do candidato, `commit` prematuro, falta de promoção e recálculo fora de ordem. A correção operacional final ainda exige candidato isolado + promoção atômica na árvore reconciliada.

### B02 — GET com efeito colateral

O defeito histórico V6→V7 agora possui auditor de grafo de chamadas. GET que alcance mutador ou SQL de escrita, direta ou indiretamente, é bloqueado. A correção integrada ainda depende da árvore real.

### B03/B39 — autorização de saída

Existe tooling executável para exigir gate canônico nos caminhos de geração/impressão/entrega e reinterseção backend dos IDs selecionados. `PROCESSADO` isolado não autoriza saída. A aplicação real aos serviços depende do B06.

### B07/B09/B10/B37

A mesa operacional recuperada mistura universos/estados. Fechados e retificações não pertencem ao ciclo vivo; status persistido e status derivado precisam de fonte de verdade única.

### B08/B40 — T L / concorrência

A regressão `PRONTA/1 → ADIADA/2 → PRONTA/1` está cercada por teste e deve bloquear por queda de chamada/piso protegido. A causa real será determinada no histórico operacional e cruzada com compare-and-set/lost update.

### B12–B17/B50

Extrato/GFD não podem ser reduzidos ao último arquivo do tipo. Hash físico não substitui identidade documental/econômica nem composição multi-documento.

### B18/B23/B36

Decisão global por competência+cliente precisa migrar para fonte/obrigação. O planner B36 não replica decisão para múltiplas fontes sem política explícita.

### B19–B23

Aplicabilidade deve respeitar FGTS zero, MEI/DAE, deduções previdenciárias, afastamentos/faltas e responsabilidade Fiscal por fonte.

### B24–B28

eConsignado precisa integrar o orquestrador, usar universo elegível, cruzar contexto e operar com idempotência/retry controlados.

### B29–B33

Diretor ≠ empregado; federal autoritativo, proveniência de competência, IRRF temporal e dezembro/13º precisam permanecer explícitos e testáveis.

### B34/B35/B38

Contrato Enum/string, integridade/FKs/invariantes e autorização/CSRF possuem tooling de auditoria; falta execução/correção na árvore real reconciliada.

### B41/B42

Rollback/readiness e cadeia de identidade estão testados em staging. Instalação/rollback físico Windows continuam pendentes.

### B43/B44/B46/B47

Preservar melhorias válidas de Pendências e A4; simplificar monitor e restaurar atalhos Sintegra sem reverter a nova modelagem de inscrições.

### B45

Há paginação, mas persistem N+1, `status_sessao()` pesado e polling. Benchmark >600 clientes depende da árvore real.

### B48/B49

Retenção segue deliberadamente não destrutiva até política/acervo reais. Auditoria banco ↔ filesystem é bidirecional e read-only; execução real depende do handoff B06.

## 7. Ordem após materialização do B06

1. reconciliar árvore/runtime e fixar baseline;
2. executar B35/B49 sobre a cópia real;
3. aplicar B01 — candidato não destrutivo;
4. aplicar B02 — GET puro + evento explícito de fechamento;
5. aplicar B03/B39 — gate único de saída;
6. B07/B09/B10/B11/B37 — universo e máquinas de estado;
7. B40/B08 — CAS, concorrência e causa T L;
8. B18/B36 + B05 — decisão por fonte/migração;
9. B12/B13/B14/B17/B50 — composição multi-documento;
10. B15/B16 — descoberta/identidade/vínculo;
11. B19–B23 — aplicabilidade;
12. B24–B28 — eConsignado;
13. B29–B33 — parser/proveniência/13º;
14. B34/B38 — bordas e segurança na árvore real;
15. B43/B44/B46/B47 — UX/regressões;
16. B45/B48 — benchmark/manutenção;
17. C01–C28;
18. build/proveniência final;
19. instalação Windows + rollback comprovado.

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

A auditoria/tooling avançou até a Etapa 73. O gargalo material continua sendo B06, mas as correções B01/B02/B03/B39 agora já possuem guardrails executáveis para aplicação imediata quando a árvore operacional for reconciliada.
