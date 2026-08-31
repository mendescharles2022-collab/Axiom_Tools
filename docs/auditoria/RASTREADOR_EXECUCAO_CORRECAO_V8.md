# Rastreador canônico — Execução de correção V8

Data: 31/08/2026  
Status: **DIAGNÓSTICO B01–B50 REVISTO / TOOLING AVANÇADO ATÉ ETAPA 57 / RUNTIME INTEGRAL AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

## 1. Marco canônico atual do tooling

GitHub Actions run `33440070146`  
Commit `0b980637de843fb1fbef61836da4a03b975dff2f`  
Python `3.12.14`

```text
Ran 215 tests in 0.899s
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

- ID `9775877239`;
- SHA-256 `bee98e0797da5549b8d63cc0f2fd092d4cc9bcac031ef3dc07bf8c753a5cf8c4`.

Este é o marco de tooling. Ele **não** representa homologação da árvore operacional integral.

## 2. Etapas 42–57

A auditoria foi retomada sem reiniciar trabalho anterior.

- Etapa 42 — lacuna de config/identidade no tooling de reconciliação;
- Etapa 43 — B01/B02 reconfirmados no V8F2 e side effect do validador;
- Etapa 44 — origem histórica B02 V6→V7 e investigação B08;
- Etapa 45 — B03 isolado em autorização espalhada;
- Etapa 46 — B07/B09/B10 e mitigação B11;
- Etapa 47 — B12–B17/multi-documento e identidade econômica;
- Etapa 48 — B18–B23/decisão por fonte e aplicabilidade;
- Etapa 49 — B24–B28/eConsignado;
- Etapa 50 — B29–B33/parser, competência, IRRF e 13º;
- Etapa 51 — B34–B40/banco, segurança e concorrência;
- Etapa 52 — B41–B50/instalação, UX, escala, Sintegra, retenção e acervo;
- Etapa 53 — mapa causal C01–C28 → B01–B50;
- Etapa 54 — validador causal e integração de governança;
- Etapa 55 — config/release_identity no tooling B06/B42, preflight causal e recuperação de CI;
- Etapa 56 — B49 bidirecional banco ↔ filesystem;
- Etapa 57 — B48 retenção segura: Simular → Revisar → Confirmar → Revalidar, sem executor destrutivo.

Com isso, B01–B50 possuem diagnóstico/restrição de evidência revisados e C01–C28 estão causalmente amarrados à matriz de bloqueadores.

## 3. Snapshot formal de estados

O arquivo `config/blocker_status_v8_current.json` foi atualizado em 31/08 com notas de diagnóstico e avanço real de tooling, sem falsa homologação.

| Estado | Quantidade |
|---|---:|
| `PRONTO_PARA_CORRIGIR` | 35 |
| `INSPECAO_PENDENTE` | 7 |
| `EM_CORRECAO` | 4 |
| `BLOQUEADO_POR_RUNTIME` | 4 |
| `CORRIGIDO_TESTADO` | 0 |
| `CORRIGIDO_HOMOLOGADO` | 0 |

Em correção: B35, B41, B42, B48.  
Bloqueados pelo runtime: B05, B06, B45, B49.

Regra permanente:

**patch encontrado ≠ teste executado ≠ homologação.**

## 4. Runtime/pacote operacional preservado

Foi localizada no acervo a cópia:

`Axiom_Tools(20260827-175623).zip`

com `399.270.206` bytes, coincidente com a base canônica da auditoria de 27/08.

A plataforma desta sessão ainda não permitiu materializar seus bytes.

Foi materializada a cadeia de deltas V → V8F2, incluindo:

`AXIOM_TOOLS_V5_6_14V8F2_CONSOLIDADO_20260827.zip`

SHA-256 calculado:

`E30B4189F883F1B8FB0B48574C36FF72DA7EE8679B7118E96FDEF17BF93AB2D2`

Os deltas são evidência operacional válida sobre os arquivos que contêm, mas não substituem B06.

## 5. B06 — gate para implementação consolidada

Não implementar B01/B02/B03 sobre a fundação reduzida da `main` como se ela fosse o runtime final.

Tooling preparado e testado:

- exportador runtime por whitelist;
- bloqueio de banco/documentos/segredos;
- `config` seguro e `release_identity.toml` incluídos;
- paths absolutos removidos dos artefatos;
- auditor runtime ↔ repositório;
- comparação de identidade/config;
- launcher PowerShell;
- manifesto SHA-256;
- E2E;
- preflight com mapa causal 28/28.

A lacuna de tooling da Etapa 42 está fechada no repositório.

B06 continua `BLOQUEADO_POR_RUNTIME` até:

1. exportar a instalação Windows/ZIP integral;
2. auditar o export;
3. reconciliar árvore e suíte operacionais completas;
4. estabelecer baseline da mesma árvore que será corrigida e empacotada.

## 6. C01–C28 — gate causal

Arquivo:

`config/regression_case_blocker_map_v8_202608.json`

Validador:

`scripts/validate_regression_case_blocker_map.py`

O preflight recusa mapa causal inválido.

Nenhum C pode ser considerado PASS somente por resultado visual final quando seus bloqueadores estruturais associados ainda estão abertos.

## 7. Correções parciais válidas a preservar

### B11 / V8A

Distinção visual baseada em existência real de dossiê melhora `Aguardando processamento` x `Em conferência`.

### B19 / FGTS zero

V8F2 usa FGTS zero do Extrato da competência como evidência mais forte que expectativa cadastral. Falta regressão real integrada.

### B26 / eConsignado

MTE/Dataprev positivo sem fonte local/recolhimento retorna `AGUARDANDO_FONTES`, não `CONFERIDO`. Falta caso real integrado D A F Castro.

### B31 / competência e-CAC

V8F2 amplia reconhecimento de PA e preserva `competencia_metodo`. Proveniência completa/ranking de força ainda pendentes.

### B43 / Pendências

V8F2 abre por competência ativa, pagina no backend e mantém PROC como filtro técnico secundário.

### B44 / relatório

V8F2 define `A4 portrait`, cabeçalho repetível e quebra controlada. Impressão real ainda não homologada.

### B38 / autenticação-CSRF

Nos deltas materializados:

- V8A: 13/13 POSTs protegidos;
- V4: 36/36;
- V8F2: 30/30;
- formulários POST recuperados possuem `csrf_token`.

Autorização de negócio/concorrência continuam pendentes.

## 8. Causas críticas já isoladas

### B01

V8F2 ainda remove vigente/pessoas e faz `commit()` antes da nova leitura. Exige candidato isolado + promoção atômica.

### B02

Fechamento automático entrou no agregador `conferencia_competencia()` no salto V6→V7. GET precisa voltar a ser leitura pura.

### B03/B39

Views aplicam filtros diferentes e serviços ainda precisam de gate único de saída por versão FECHADA, inclusive contra IDs manipulados.

### B07/B09/B10

Universo recuperado da Conferência inclui PRONTA + FECHADA + RETIFICACAO. Mesa viva precisa excluir fechados e retificações.

### B12–B17/B50

Extrato/GFD são reduzidos ao último documento do tipo em caminhos recuperados; hash físico não representa identidade econômica.

### B18/B23

Decisão manual permanece global por competência+cliente em código recuperado; precisa ser por fonte/obrigação.

### B37/B46

Monitor mantém dupla verdade entre estado persistido e estado operacional derivado.

### B40

Transições recuperadas atualizam por `competencia + cliente_id` sem compare-and-set de estado/chamada/revisão lidos.

## 9. B08 — T L

Falha operacional permanece confirmada: cliente deveria estar na 2ª chamada e apareceu PRONTA na 1ª.

Hipóteses já eliminadas:

- sincronização genérica não sobrescreve ADIADA existente;
- classificação cadastral atua só em PRONTA;
- sincronização de resultados ignora ADIADA;
- migrações V7/V8/V8A recuperadas não reabrem ADIADA genericamente.

Ainda candidatos:

- persistência inicial inadequada;
- avanço/liberação explícita;
- lost update/B40;
- código externo ainda não recuperado.

B08 continua `INSPECAO_PENDENTE`.

## 10. B41/B42

### B41

Tooling de bundle/verificação/restauração existe e é testado, porém V8F2 não inclui SQLite/config completa no backup e não rollbacka falha pós-restart/health-check. Ensaio físico Windows segue pendente.

### B42

Build provenance e reconciliação de `release_identity.toml` estão testados. Runtime, `/health`, logs, instalador e pacote ainda precisam consumir a mesma identidade.

## 11. B45

Há paginação backend em caminhos auditados, mas permanecem:

- N+1 em `listar_sessoes()`;
- muitas consultas em `status_sessao()`;
- polling de 2 segundos;
- ausência de benchmark final >600 clientes/query plans/locks.

B45 continua bloqueado pelo runtime.

## 12. B47

Regressão Sintegra isolada:

- V5.6.14V renderizava Sintegra Nacional e Goiás;
- V1 substituiu o template e removeu os botões;
- backend manteve URLs;
- V3A/V4 recuperados seguem sem os atalhos.

Correção final deve restaurar apenas os botões, preservando a nova modelagem de inscrições.

## 13. B48/B49

### B48 — retenção segura

Tooling não destrutivo preparado e testado:

- `scripts/plan_retention_cleanup.py` — `DRY_RUN_ONLY`, com fingerprint de candidatos (`mtime_ns` + SHA-256);
- `scripts/review_retention_plan.py` — decisão por item/categoria/evidência, vinculada ao hash do plano;
- `scripts/authorize_retention_manifest.py` — confirmação explícita e manifesto autorizado, ainda `execution_performed=false`;
- `scripts/revalidate_retention_manifest.py` — rechecagem read-only de raiz, path, reparse, existência, tamanho, `mtime_ns` e SHA-256.

Proteções:

- originais, arquivos gerenciados, versões históricas, saídas finais e backups não podem ser marcados `ELIGIBLE`;
- item elegível precisa ter evidência;
- root lógico acompanha a cadeia;
- arquivo substituído após a confirmação é bloqueado;
- nenhum estágio implementado até aqui apaga ou move arquivo.

A Etapa 57 registrou também o CI vermelho `33439569866`, que detectou referência com traversal (`../segredo`), e sua correção antes do marco verde final.

B48 está `EM_CORRECAO`. O executor destrutivo foi deliberadamente adiado até existirem política/schema/acervo reais e prova de que os itens são transitórios/reconstruíveis.

### B49 — banco ↔ filesystem

Tooling é bidirecional.

Banco → filesystem:

`scripts/audit_db_filesystem_links.py`

Filesystem → banco:

`scripts/audit_filesystem_db_index.py`

Executor único:

`scripts/audit_db_filesystem_bidirectional.py`

Cobertura inclui:

- arquivo do banco ausente;
- tamanho/SHA divergentes;
- arquivo físico não indexado (`UNINDEXED_FILE`);
- path traversal;
- roots autorizados;
- reparse/symlink;
- bloqueio de SQL mutável;
- prova de não mutação do SQLite.

B49 continua bloqueado apenas pela falta de execução com schema/roots/banco/acervo reais.

## 14. B35 — invariantes

Confirmadas no repositório:

1. FECHADA sem versão é inválida;
2. `versao_atual` precisa apontar para versão existente.

Pendente no real:

- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`;
- invariantes adicionais do schema reconciliado;
- comparação antes/depois de migração e instalação.

## 15. Gate final

Ferramentas:

- `scripts/validate_release_gate.py`;
- `scripts/build_current_preflight.py`;
- `scripts/build_evidence_index.py`.

Modo final exige:

- 50/50 B homologados;
- 28/28 C PASS;
- mapa causal válido;
- release READY;
- build verificável;
- dez gates externos PASS.

## 16. Ordem após B06

1. baseline + suíte operacional original;
2. B01 — candidato não destrutivo;
3. B02 — GET puro + evento de fechamento;
4. B03/B39 — gate único de saída;
5. B07/B09/B10/B11/B37 — universos/máquinas de estado;
6. B40/B08 — CAS/transições e T L;
7. B18/B36 + schema B05 — decisão por fonte/migração;
8. B12/B13/B14/B17/B50 — composição multi-documento;
9. B15/B16/B49 — descoberta/vínculo e auditoria real;
10. B19–B23 — aplicabilidade;
11. B24–B28 — eConsignado;
12. B29–B33 — parser/proveniência/13º;
13. B34/B35/B38 — bordas, banco e segurança;
14. B43/B44/B46/B47 — UX/regressões;
15. B45/B48 — benchmark/manutenção;
16. C01–C28;
17. build/proveniência final;
18. instalação Windows + rollback comprovado.

## 17. Situação atual

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**

A auditoria e o tooling avançaram até a Etapa 57. O maior gate estrutural continua sendo B06: reconciliar a árvore operacional integral antes de aplicar correções de domínio sobre uma fundação incompleta.
