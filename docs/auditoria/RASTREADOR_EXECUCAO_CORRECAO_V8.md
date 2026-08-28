# Rastreador canônico — Execução de correção V8

Data inicial: 28/08/2026  
Status: **FASE DE CORREÇÃO PREPARADA / RUNTIME AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

Este arquivo é o rastreador vivo da fase de correção e homologação da V8.

Os documentos `AUDITORIA_CANONICA_V8_20260828_ETAPA*.md` permanecem como histórico de investigação. O andamento principal passa a ser atualizado aqui para evitar novos documentos de etapa sem necessidade.

## 1. Legenda de estado

- `NAO_INICIADO` — ainda não confrontado na árvore oficial reconciliada;
- `INSPECAO_PENDENTE` — regra conhecida, mas causa/implementação precisa ser confirmada no runtime;
- `PRONTO_PARA_CORRIGIR` — causa e regra suficientes para implementação assim que a árvore oficial estiver disponível;
- `EM_CORRECAO` — alteração de código/integração em curso;
- `IMPLEMENTADO_NAO_TESTADO` — código alterado, regressão ainda não executada;
- `TESTE_EM_EXECUCAO` — suíte/protocolo sendo executado;
- `CORRIGIDO_TESTADO` — correção passou no teste específico, mas pacote/migração integrada ainda não homologados;
- `CORRIGIDO_HOMOLOGADO` — passou regressão integrada, migração/build aplicável e homologação exigida;
- `BLOQUEADO_POR_RUNTIME` — não há código/banco necessário disponível para avançar com segurança.

`Documentado` não é estado de correção.

## 2. Gate zero — reconciliação da fonte

| Item | Estado | Critério de saída |
|---|---|---|
| B06 — `main` ≠ runtime | `BLOQUEADO_POR_RUNTIME` | árvore operacional completa reconciliada no repositório oficial |
| B42 — proveniência de build | `EM_CORRECAO` | identidade canônica integrada ao runtime/health/logs/instalador + manifesto do mesmo build |
| Suíte operacional original | `BLOQUEADO_POR_RUNTIME` | testes do runtime auditado versionados e executáveis |
| Banco de homologação/cópia | `BLOQUEADO_POR_RUNTIME` | cópia segura disponível para migração/invariantes |

### Ação obrigatória

Não iniciar correção de runtime sobre a fundação reduzida da `main` fingindo que ela é a V8 operacional.

A reconciliação deve trazer apenas código, templates, assets, testes, scripts de migração e arquivos controlados. Permanecem fora:

- banco operacional;
- PDFs/documentos de clientes;
- certificados;
- credenciais/tokens;
- logs;
- caches;
- backups com dados reais;
- temporários.

### Investigação adicional do histórico Git — 28/08/2026

Foi auditado o histórico disponível do repositório buscando possibilidade de recuperar a árvore operacional de um commit antigo.

Resultado:

- o repositório possui menos de três páginas de 100 commits na API; a terceira página retorna vazia;
- as páginas existentes são dominadas por documentação/auditoria e não revelaram commit contendo a árvore operacional completa V7/V8;
- o inventário atual de `src/` continua reduzido;
- o inventário atual de `tests/` não contém a suíte operacional do runtime.

Conclusão operacional:

**B06 não será resolvido por simples checkout de commit histórico conhecido.**

A fonte de reconciliação continua sendo a cópia operacional controlada do runtime/servidor ou pacote canônico equivalente, seguida de filtragem de dados sensíveis e versionamento da árvore de código.

### Ferramentas de desbloqueio preparadas — estado atual

#### Exportação segura do runtime

`scripts/export_runtime_reconciliation.py`

- whitelist explícita de código, testes, scripts, migrations, templates, static e metadata controlada;
- suporta layouts `app/src` e `src`;
- não copia banco, documentos, certificados, credenciais, logs, backups, caches ou temporários;
- bloqueia symlink/junction/reparse point nas origens copiadas;
- bloqueia saída posicionada dentro da própria árvore exportada;
- detecta nomes sensíveis e possíveis segredos hardcoded;
- gera `RECONCILIATION_MANIFEST.csv`, informação da exportação e ZIP com SHA-256;
- **9 testes automatizados aprovados**.

`scripts/export_runtime_reconciliation.ps1`

- launcher Windows fino para o exportador Python;
- execução real ainda precisa ser comprovada no Windows operacional.

#### Auditoria independente do pacote exportado

`scripts/audit_runtime_reconciliation.py`

- valida manifesto, tamanho e SHA-256;
- bloqueia tentativa de `../`/saída da raiz;
- detecta arquivo extra fora do manifesto e caminho duplicado;
- revalida arquivos sensíveis e possíveis segredos sem confiar apenas no exportador;
- compara `src`, `tests`, `scripts`, migrations, alembic, templates, static e metadata;
- classifica `SAME`, `CHANGED`, `RUNTIME_ONLY` e `REPO_ONLY`;
- gera relatório CSV/JSON;
- **9 testes automatizados aprovados**.

#### Pipeline de reconciliação ponta a ponta

`tests/test_reconciliation_pipeline_e2e.py`

Foram versionados 3 cenários:

1. runtime simulado → export ZIP → extração → auditoria sem divergência;
2. divergência runtime × repositório produz código de retorno específico;
3. adulteração posterior ao manifesto é rejeitada antes da comparação.

Esses 3 testes estão **versionados, mas ainda aguardam execução comprovada** sobre a árvore atual do `main`.

### B42 — proveniência de build

A correção deixou de ser apenas contrato e entrou em implementação de tooling.

`config/release_identity.toml`

- passa a ser a fonte canônica da identidade de release;
- está deliberadamente com `state = "UNRELEASED"`;
- `release_version` e `schema_version` permanecem vazios até a reconciliação/homologabilidade da árvore;
- enquanto não estiver `READY`, o caminho oficial de build é bloqueado.

`scripts/generate_build_provenance.py`

- usa a identidade canônica, não release/schema digitados no comando oficial;
- exige Git limpo;
- grava commit, ref, release, schema, Python e plataforma;
- gera manifesto SHA-256 do payload;
- registra hash do próprio arquivo canônico de release;
- bloqueia banco, arquivos sensíveis, symlink e possível segredo hardcoded;
- **12 testes automatizados aprovados**.

`scripts/verify_build_provenance.py`

- verifica o hash do próprio `BUILD_PROVENANCE.json`;
- verifica todos os arquivos/bytes do payload;
- rejeita arquivo extra, ausente ou alterado;
- rejeita caminhos inseguros/duplicados e chave JSON duplicada;
- quando recebe o repositório fonte, confirma commit e identidade canônica;
- **9 testes automatizados aprovados**.

B42 permanece `EM_CORRECAO` porque ainda faltam, após a reconciliação:

- runtime consumir a identidade canônica;
- `/health` expor versão/build/schema de forma controlada;
- log de inicialização registrar o mesmo build;
- instalador/backup/rollback consumir o manifesto;
- pacote final ser gerado e verificado por esse caminho.

### CI

`.github/workflows/reconciliation-tests.yml` foi ampliado para a suíte de tooling V8 com Python 3.12.

Até esta atualização, commits feitos pela integração não produziram workflow run automático observável. Portanto:

- CI está **CONFIGURADA**;
- CI ainda **NÃO ESTÁ COMPROVADA COMO EXECUTADA**;
- não será contabilizada como evidência de homologação.

### Contagem atual do tooling

- 9 testes do auditor de reconciliação — aprovados;
- 9 testes do exportador — aprovados;
- 12 testes do gerador de proveniência — aprovados;
- 9 testes do verificador de build — aprovados;
- 3 testes end-to-end de reconciliação — versionados, aguardando execução comprovada.

**Total definido: 42 testes.**  
**Total já aprovado em execução controlada: 39 testes.**

Consequência: **B06 continua bloqueado pelo runtime; B42 está em correção com núcleo de tooling implementado e testado.**

## 3. Lote A — integridade do ciclo e saídas

| ID | Tema | Estado atual | Prova necessária |
|---|---|---|---|
| B01 | Reprocessamento destrutivo | `PRONTO_PARA_CORRIGIR` | candidato não substitui vigente antes da promoção; regressão 307/J Bernardes/449-450 |
| B02 | Conference GET com mutação | `PRONTO_PARA_CORRIGIR` | abrir/recarregar Conference não altera banco/histórico/status |
| B03 | Gate único de saída | `PRONTO_PARA_CORRIGIR` | IDs manuais não bypassam gate; saída vinculada à versão FECHADA |
| B04 | Versão/retificação vigente | `INSPECAO_PENDENTE` | snapshot integral + retificação preservando versão anterior |
| B07 | Universo operacional duplicado | `PRONTO_PARA_CORRIGIR` | universo único por competência/chamada em todos os módulos |
| B08 | T L / 2ª chamada | `INSPECAO_PENDENTE` | identificar cláusula/concorrência causadora e provar persistência da chamada 2 |
| B09 | Fechados na mesa viva | `PRONTO_PARA_CORRIGIR` | Conference exclui FECHADA do fluxo vivo |
| B10 | Retificação misturada ao ciclo | `PRONTO_PARA_CORRIGIR` | retificação separada do ciclo normal, saída bloqueada enquanto pendente |
| B11 | Estado antecipado | `PRONTO_PARA_CORRIGIR` | `PRONTA`/`PROCESSADO` não criam `EM_CONFERENCIA` artificial |
| B37 | Máquinas de estado misturadas | `PRONTO_PARA_CORRIGIR` | estados técnico/documento/obrigação/ciclo/consulta/retificação separados |
| B39 | Seleção manual por IDs | `PRONTO_PARA_CORRIGIR` | backend intersecta IDs recebidos com universo autorizado |
| B40 | Concorrência lógica | `INSPECAO_PENDENTE` | compare-and-set/versionamento impede escrita obsoleta |

## 4. Lote B — documentos, identidade, composição e aplicabilidade

| IDs | Família | Estado atual |
|---|---|---|
| B12–B13 | Multi-Extrato / federal x FGTS rural | `PRONTO_PARA_CORRIGIR` |
| B14 | Multi-GFD/FGTS rescisório | `PRONTO_PARA_CORRIGIR` |
| B15 | Descoberta → vínculo | `PRONTO_PARA_CORRIGIR` |
| B16 | PF/CAEPF | `PRONTO_PARA_CORRIGIR` |
| B17 | Deduplicação lógica | `PRONTO_PARA_CORRIGIR` |
| B18 | Decisão por fonte | `PRONTO_PARA_CORRIGIR` |
| B19 | FGTS zero | `PRONTO_PARA_CORRIGIR` |
| B20 | MEI/DAE | `PRONTO_PARA_CORRIGIR` |
| B21 | Deduções previdenciárias | `PRONTO_PARA_CORRIGIR` |
| B22 | Afastamentos/faltas | `PRONTO_PARA_CORRIGIR` |
| B23 | Fiscal/impedimento externo | `PRONTO_PARA_CORRIGIR` |
| B29 | Diretor ≠ empregado | `PRONTO_PARA_CORRIGIR` |
| B30 | Federal autoritativo | `PRONTO_PARA_CORRIGIR` |
| B31 | Competência/proveniência | `PRONTO_PARA_CORRIGIR` |
| B32 | IRRF por competência de pagamento | `INSPECAO_PENDENTE` |
| B33 | Dezembro/13º | `PRONTO_PARA_CORRIGIR` |

## 5. Lote C — eConsignado

| ID | Tema | Estado atual |
|---|---|---|
| B24 | fora do orquestrador | `PRONTO_PARA_CORRIGIR` |
| B25 | universo excessivo | `PRONTO_PARA_CORRIGIR` |
| B26 | falso `CONFERIDO` | `PRONTO_PARA_CORRIGIR` |
| B27 | retorno residual | `PRONTO_PARA_CORRIGIR` |
| B28 | retry/idempotência | `INSPECAO_PENDENTE` |

Regra de aceite: resultado de API é fotografia/evidência. A obrigação só conclui após cruzamento contextual.

## 6. Lote D — cadastro, banco, migração e segurança

| ID | Tema | Estado atual |
|---|---|---|
| B05 | Migração V8 | `BLOQUEADO_POR_RUNTIME` |
| B34 | inativação string/Enum | `PRONTO_PARA_CORRIGIR` |
| B35 | FKs/invariantes | `BLOQUEADO_POR_RUNTIME` |
| B36 | decisão global legada → fonte | `INSPECAO_PENDENTE` |
| B38 | Auth/CSRF novas rotas | `INSPECAO_PENDENTE` |
| B41 | backup/rollback | `BLOQUEADO_POR_RUNTIME` |

Nenhuma migração pode fabricar certeza por fonte a partir de decisão global ambígua do legado.

## 7. Lote E — UX operacional, desempenho e acervo

| ID | Tema | Estado atual |
|---|---|---|
| B43 | Pendências orientada por PROC | `PRONTO_PARA_CORRIGIR` |
| B44 | A4 retrato | `PRONTO_PARA_CORRIGIR` |
| B45 | escala >600 | `BLOQUEADO_POR_RUNTIME` |
| B46 | Monitor duplicado/confuso | `PRONTO_PARA_CORRIGIR` |
| B47 | Sintegra GO/atalhos | `PRONTO_PARA_CORRIGIR` |
| B48 | retenção/limpeza | `INSPECAO_PENDENTE` |
| B49 | banco ↔ filesystem | `BLOQUEADO_POR_RUNTIME` |
| B50 | hash ≠ obrigação | `PRONTO_PARA_CORRIGIR` |

## 8. Regressão real — competência 08/2026

A regressão obrigatória usa:

- `MATRIZ_REGRESSAO_V8_AGOSTO_2026.md`;
- `PROTOCOLO_REGRESSAO_28_CASOS_V8.md`.

Regra:

- cada caso registra estado inicial;
- ação/evento executado;
- delta de banco;
- versão vigente antes/depois;
- estado por fonte;
- estado agregado;
- saída autorizada ou bloqueada;
- ausência de contaminação entre casos.

Nenhuma correção visual isolada homologa um caso.

## 9. Critérios integrados finais

Antes de qualquer pacote final:

- [ ] runtime reconciliado com GitHub;
- [ ] identidade canônica de release em `READY` somente no momento correto;
- [ ] versão/build/schema rastreáveis e verificados;
- [ ] suíte original executada;
- [ ] bloqueadores críticos corrigidos;
- [ ] 28 casos executados;
- [ ] `PRAGMA integrity_check = ok`;
- [ ] `PRAGMA foreign_key_check` sem violações novas;
- [ ] invariantes lógicas aprovadas;
- [ ] benchmark aprovado;
- [ ] segurança das mutações aprovada;
- [ ] relatório A4 homologado em preview real;
- [ ] pacote gerado da mesma árvore testada;
- [ ] `BUILD_PROVENANCE.json` verificado contra payload e fonte;
- [ ] backup e migração em cópia aprovados;
- [ ] instalação Windows aprovada;
- [ ] rollback código + banco + configuração executado com sucesso.

## 10. Estado desta atualização

Atualizações de governança e tooling aplicadas ao repositório em 28/08/2026:

- `docs/STATUS_ATUAL.md` e `README.md` alinhados ao rastreador vivo;
- mapa de cobertura B01–B50 preservado;
- histórico Git investigado e descartado como fonte suficiente para recuperar a árvore operacional completa;
- exportador e auditor da reconciliação implementados/testados;
- identidade canônica de release criada como `UNRELEASED`;
- gerador e verificador de proveniência implementados/testados;
- 42 testes de tooling definidos, 39 já aprovados em execução controlada;
- 3 cenários end-to-end aguardam execução comprovada;
- workflow de CI ampliado, porém ainda sem run automático comprovado.

Próximo avanço técnico: documentar o uso do fluxo de proveniência e continuar preparando o Gate Zero sem alterar artificialmente a versão `0.1.0` da fundação reduzida antes da reconciliação do runtime.
