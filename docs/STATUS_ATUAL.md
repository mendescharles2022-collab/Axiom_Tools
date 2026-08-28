# Axiom Tools — Status Atual

Data: 28/08/2026  
Status: **V5.6.14V7 estável em servidor / V8 em auditoria e correção / V8 NÃO HOMOLOGADA**

## 1. Instalação estável confirmada

A referência operacional estável continua sendo:

**V5.6.14V7 — Ciclo Mensal com Fechamento Automático**

A V7 foi instalada no servidor em 26/08/2026 preservando banco, serviços, histórico e retificações.

A existência posterior de builds experimentais/auditados da família V8 não substitui automaticamente essa referência de estabilidade.

## 2. Situação atual da V8

A V8 passou por auditoria funcional, arquitetural, documental e de governança em 28/08/2026.

Resultado atual:

- 50 bloqueadores catalogados (`B01` a `B50`);
- todos possuem regra de tratamento e critério objetivo de prova;
- 28 casos reais da competência 08/2026 foram transformados em matriz de regressão e registro machine-readable;
- nenhum bloqueador foi promovido para `CORRIGIDO_HOMOLOGADO` sem execução no runtime reconciliado;
- nenhum pacote final V8 está autorizado.

Estado vivo:

- `docs/auditoria/RASTREADOR_EXECUCAO_CORRECAO_V8.md`

Mapas e regressão:

- `docs/auditoria/MAPA_COBERTURA_BLOQUEADORES_V8.md`
- `docs/auditoria/MATRIZ_REGRESSAO_V8_AGOSTO_2026.md`
- `docs/auditoria/PROTOCOLO_REGRESSAO_28_CASOS_V8.md`
- `config/regression_cases_v8_202608.json`
- `scripts/validate_regression_results.py`

## 3. Bloqueador de governança — repositório ≠ runtime

O `main` ainda não espelha integralmente a árvore operacional auditada.

Inventário atual confirma que:

- `src/axiom_tools` contém apenas a fundação reduzida;
- as implementações operacionais completas V8 ainda não estão versionadas integralmente;
- `tests/` ainda não contém a suíte operacional empacotada do runtime auditado;
- `pyproject.toml` ainda não representa a identidade operacional final da família V8.

Consequência:

**documentação e tooling no GitHub não são prova de correção do runtime.**

Antes da implementação/homologação final é obrigatório reconciliar a árvore operacional, sem versionar banco real, documentos de clientes, certificados, credenciais, logs, caches ou outros dados sensíveis.

### Tooling de reconciliação

Versionado:

- `scripts/export_runtime_reconciliation.py`;
- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/audit_runtime_reconciliation.py`;
- testes unitários do exportador/auditor;
- 3 testes ponta a ponta do pipeline;
- workflow de CI do tooling.

Situação:

- exportador e auditor possuem **18 testes aprovados**;
- os **3 testes E2E** estão versionados, mas ainda aguardam execução comprovada;
- o container desta auditoria não consegue resolver `github.com`, portanto não foi possível executar um clone limpo por rede;
- o workflow existe, mas ainda não foi observado run automático para commits feitos pela integração;
- launcher PowerShell continua pendente de execução no Windows.

B06 permanece **BLOQUEADO_POR_RUNTIME**.

## 4. Proveniência de build — B42

B42 está **EM CORREÇÃO**.

Já existem:

- `config/release_identity.toml`, atualmente `UNRELEASED`;
- `scripts/generate_build_provenance.py`;
- `scripts/verify_build_provenance.py`;
- manifesto de payload com SHA-256;
- exigência de Git limpo no caminho oficial;
- bloqueio de payload sensível/segredo hardcoded;
- verificação independente de commit, identidade e conteúdo.

Cobertura atual: **21 testes aprovados** nessa família.

B42 ainda depende da integração dessa identidade ao runtime reconciliado, `/health`, logs, instalador e pacote final.

## 5. SQLite, migração e invariantes — B05/B35

B35 está **EM CORREÇÃO**; B05 permanece **BLOQUEADO_POR_RUNTIME** para migração real.

Tooling versionado:

- `scripts/audit_sqlite_baseline.py`;
- `scripts/compare_sqlite_audits.py`;
- `scripts/clone_sqlite_for_migration.py`;
- `scripts/run_sqlite_invariants.py`.

O fluxo preparado é:

1. auditar a origem sem escrever;
2. criar cópia consistente via `sqlite3.Connection.backup()`;
3. migrar somente a cópia;
4. auditar o pós-migração;
5. comparar pré/pós;
6. executar invariantes lógicas versionadas.

O executor de invariantes aceita apenas consultas somente leitura e usa a regra:

**zero linhas = invariante atendida**.

Ainda não foram inventadas invariantes específicas da V8 sem o schema operacional real.

Cobertura atual da família SQLite/migração: **28 testes aprovados**.

## 6. Backup e rollback — B41

B41 possui tooling de preparação **EM CORREÇÃO**, mas rollback físico ainda não está homologado.

Versionado:

- `scripts/create_rollback_bundle.py`;
- `scripts/verify_rollback_bundle.py`;
- `scripts/restore_rollback_bundle.py`;
- `docs/auditoria/GUIA_BACKUP_ROLLBACK_V8.md`.

O bundle:

- usa lista explícita de arquivos controlados;
- preserva as origens;
- cria cópia SQLite consistente;
- registra versão/schema/commit e SHA-256;
- recusa sobrescrita e path traversal;
- é verificado independentemente;
- pode ser restaurado apenas em diretório novo de ensaio;
- revalida hashes, `integrity_check` e `foreign_key_check` após restauração.

Cobertura atual da família rollback: **14 testes aprovados**.

O rollback sobre a instalação real continua proibido até:

- runtime reconciliado;
- plano real dos arquivos controlados;
- bundle da instalação real;
- ensaio com cópia real do banco;
- teste físico Windows;
- smoke pós-rollback.

## 7. Segurança das rotas — B38

B38 permanece **INSPECAO_PENDENTE** para o runtime, mas já possui tooling estático preparado.

Versionado:

- `scripts/audit_route_security.py`;
- `config/route_security_policy.example.json`;
- `docs/auditoria/GUIA_AUDITORIA_SEGURANCA_ROTAS_V8.md`.

A ferramenta inventaria rotas, métodos mutantes, decorators, markers de autenticação configuráveis e possíveis exceções de CSRF.

Cobertura atual: **8 testes aprovados**.

Ausência de achado estático não equivale a segurança homologada. Proteção global, Flask-WTF, autorização de negócio, escopo e transação ainda exigem runtime.

## 8. Banco ↔ filesystem — B49

B49 possui tooling de auditoria **PREPARADO**, mas ainda depende do schema e acervo reais.

Versionado:

- `scripts/audit_db_filesystem_links.py`.

O auditor:

- abre SQLite somente leitura;
- usa roots físicos explícitos;
- usa consultas configuráveis depois da reconciliação;
- verifica caminho confinado, existência, arquivo versus diretório, symlink, tamanho e SHA-256 opcional;
- bloqueia query mutante;
- não embute tabela/campo V8 fictício.

Cobertura atual: **8 testes aprovados**.

## 9. Retenção / limpeza — B48

B48 possui planejador **DRY_RUN_ONLY** preparado.

Versionado:

- `scripts/plan_retention_cleanup.py`.

O planejador:

- nunca apaga ou move arquivos;
- usa roots e regras explícitas;
- classifica antigos como `CANDIDATE` e recentes como `KEEP_RECENT`;
- filtra por extensão quando configurado;
- rejeita glob inseguro;
- marca symlink para revisão;
- preserva integralmente o acervo durante análise.

Cobertura atual: **7 testes aprovados**.

Nenhuma política destrutiva real foi criada sem validar o acervo operacional.

## 10. Escala / desempenho — B45

B45 possui benchmark SQLite somente leitura preparado.

Versionado:

- `scripts/benchmark_sqlite_queries.py`.

O benchmark registra:

- warmup e repetições;
- média, p50, p95 e p99;
- contagem de linhas;
- `EXPLAIN QUERY PLAN`;
- threshold opcional de p95;
- bloqueio de query mutante.

Cobertura atual: **7 testes aprovados**.

Benchmark SQLite não substitui benchmark HTTP/UX, concorrência, workers ou Windows. As queries reais serão definidas somente depois da reconciliação do schema/runtime.

## 11. Regressão canônica de 08/2026

Além da matriz humana, a regressão possui agora registro verificável:

- `config/regression_cases_v8_202608.json` — `C01` a `C28` + controle documental P DA SILVA CARMO;
- `scripts/validate_regression_results.py` — valida cobertura, hash do registry, status e evidências;
- `tests/test_validate_regression_results.py` — **8 testes aprovados**.

Regras:

- o registry deve conter exatamente os 28 casos obrigatórios;
- cada resultado usa `PASS`, `FAIL`, `NOT_RUN` ou `BLOCKED`;
- `PASS` sem evidência é inválido;
- resultado duplicado, caso desconhecido ou registry divergente é bloqueado;
- modo final só aprova com **28 PASS com evidência**.

Esse tooling não executa os casos sozinho. Ele garante que a execução real não possa ser chamada de completa se um caso estiver ausente ou sem prova.

## 12. Contagem atual do tooling

No repositório:

- **122 testes definidos**;
- **119 testes aprovados em execuções controladas**;
- **3 testes E2E de reconciliação aguardando execução comprovada**.

Essa contagem é do tooling de auditoria/homologação, não da suíte operacional V7/V8.

## 13. Arquitetura funcional V8 preservada

A divisão aprovada permanece:

1. **Fechamento Mensal** — abre competência e acompanha o ciclo; não processa arquivos.
2. **Processamento de Arquivos** — trabalha somente no universo da competência/chamada aberta e produz evidências técnicas.
3. **Central de Conferência** — resolve divergências, ausências, justificativas, sem movimento mensal, anexos e reprocessamento.
4. **Fechado** — consequência do estado canônico das obrigações aplicáveis, nunca tradução de `PROCESSADO`.

A Conferência deve ser leitura sem efeitos colaterais ao abrir a tela. Mudanças de fechamento são dirigidas por eventos de negócio.

## 14. Máquinas de estado separadas

A V8 deve manter separados:

- sessão técnica;
- documento/processamento;
- obrigação/fonte;
- ciclo mensal do cliente;
- consulta externa;
- retificação;
- autorização de saída.

`PROCESSADO`, `100%`, `COM_CONSIGNADO`, `PRONTA` ou qualquer outro estado técnico/intermediário não autorizam impressão, entrega ou fechamento por si sós.

## 15. Regras operacionais centrais já consolidadas

- sem movimento permanente do cadastro ≠ sem movimento daquela competência;
- sem movimento mensal não é herdado silenciosamente;
- decisões manuais são por fonte/obrigação;
- justificativa de DARF não libera FGTS/eConsignado;
- 2ª chamada fica fora do universo da 1ª;
- cliente fechado não pertence à mesa viva de Conferência;
- nova evidência material em fechado gera retificação candidata e preserva versão anterior;
- saída final exige gate único e versão autorizadora;
- FGTS zero pode ser `NAO_APLICAVEL`;
- MEI usa DAE sem expectativa artificial de GFD autônoma;
- afastamento/faltas integrais com bases zeradas não geram guias artificiais;
- eConsignado usa o universo da competência/chamada e retorno da API é evidência, não conclusão;
- hash identifica conteúdo físico, não obrigação econômica;
- limpeza mensal não apaga acervo probatório, versões ou retificações.

## 16. Ordem oficial da fase de correção

Após reconciliação do runtime:

1. estabelecer baseline e executar suíte original;
2. B01 — reprocessamento candidato/versionado;
3. B02 — Conference GET somente leitura;
4. B03 — gate único de saída;
5. B07/B08 — universo e chamadas;
6. B12–B20 — identidade/composição/aplicabilidade;
7. B24–B28 — eConsignado;
8. schema/migração + invariantes;
9. regressão dos 28 casos;
10. benchmark;
11. segurança das rotas;
12. pacote da mesma árvore testada;
13. instalação Windows com backup, migração, smoke e rollback comprovado.

## 17. Critério para mudar status

Um item só pode passar para `CORRIGIDO_HOMOLOGADO` quando houver:

1. código corrigido na árvore oficial;
2. teste/regressão executado;
3. evidência objetiva;
4. atualização do mapa/rastreador;
5. ausência de regressão relacionada.

`Documentado`, `contratado`, `implementado`, `testado` e `homologado` são estados diferentes.

## 18. Estado de entrega

Neste momento:

- V8 **não homologada**;
- pacote final **não autorizado**;
- migração real **não autorizada**;
- rollback físico final **não comprovado**;
- runtime **ainda não reconciliado integralmente com o GitHub**.

A documentação de auditoria no `main` e o rastreador canônico continuam sendo a referência até a reconciliação e os testes do runtime real.
