# Rastreador canônico — Execução de correção V8

Data inicial: 28/08/2026  
Status: **RUNTIME AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

Este é o arquivo vivo da fase de correção/homologação. Os documentos `AUDITORIA_CANONICA_V8_20260828_ETAPA*.md` permanecem como histórico da investigação.

## 1. Estados utilizados

- `NAO_INICIADO`;
- `INSPECAO_PENDENTE`;
- `PRONTO_PARA_CORRIGIR`;
- `EM_CORRECAO`;
- `IMPLEMENTADO_NAO_TESTADO`;
- `TESTE_EM_EXECUCAO`;
- `CORRIGIDO_TESTADO`;
- `CORRIGIDO_HOMOLOGADO`;
- `BLOQUEADO_POR_RUNTIME`.

`Documentado` não é sinônimo de corrigido.

## 2. Gate Zero — fonte oficial

| Item | Estado | Situação |
|---|---|---|
| B06 — `main` ≠ runtime | `BLOQUEADO_POR_RUNTIME` | árvore operacional completa ainda não reconciliada |
| B42 — proveniência de build | `EM_CORRECAO` | núcleo de tooling implementado/testado; integração runtime/health/logs/instalador pendente |
| Suíte operacional original | `BLOQUEADO_POR_RUNTIME` | testes do runtime ainda não versionados |
| Banco operacional/cópia real | `BLOQUEADO_POR_RUNTIME` | tooling pronto; base real de homologação ainda não disponível nesta sessão |

### Regra

Não implementar a V8 operacional sobre a fundação reduzida da `main` fingindo que ela é o runtime auditado.

## 3. Tooling de reconciliação — implementado

Arquivos principais:

- `scripts/export_runtime_reconciliation.py`;
- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/audit_runtime_reconciliation.py`;
- `tests/test_export_runtime_reconciliation.py`;
- `tests/test_audit_runtime_reconciliation.py`;
- `tests/test_reconciliation_pipeline_e2e.py`.

Estado:

- exportador: **9 testes aprovados**;
- auditor: **9 testes aprovados**;
- pipeline E2E: **3 testes versionados, execução comprovada ainda pendente**;
- launcher PowerShell: execução no Windows real pendente;
- GitHub Actions: configurado, mas nenhum run automático observável até agora.

## 4. B42 — proveniência de build

Arquivos:

- `config/release_identity.toml`;
- `scripts/generate_build_provenance.py`;
- `scripts/verify_build_provenance.py`;
- `docs/auditoria/GUIA_PROVENIENCIA_BUILD_V8.md`;
- testes correspondentes.

Estado da identidade:

```text
state = UNRELEASED
release_version = vazio
schema_version = vazio
```

Isso é intencional: nenhum build final pode ser gerado antes da reconciliação/homologabilidade.

Cobertura:

- gerador de proveniência: **12 testes aprovados**;
- verificador independente: **9 testes aprovados**.

Ainda falta para concluir B42:

- runtime consumir a identidade canônica;
- `/health` expor versão/build/schema;
- log de inicialização registrar a mesma identidade;
- instalador/backup/rollback usar o manifesto;
- pacote final ser gerado/verificado pelo mesmo caminho.

## 5. SQLite — B35/B05/B41

### Auditor baseline somente leitura

`scripts/audit_sqlite_baseline.py`

Verifica:

- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`;
- `user_version`/`application_id`;
- schema, índices, views e triggers;
- definições de FK;
- contagens opcionais;
- hash canônico do schema.

A conexão usa `mode=ro` + `query_only=ON`.

**7 testes aprovados.**

### Comparador pré/pós-migração

`scripts/compare_sqlite_audits.py`

Distingue:

- objetos adicionados;
- objetos removidos;
- objetos alterados;
- deltas de registros;
- nova violação de FK;
- regressão de integridade.

Mudança de schema não é automaticamente chamada de sucesso nem de erro.

**7 testes aprovados.**

### Cópia consistente para ensaio

`scripts/clone_sqlite_for_migration.py`

- origem aberta somente leitura;
- cópia via API nativa `sqlite3.Connection.backup()`;
- destino nunca sobrescrito;
- uso de `.partial` até validação;
- auditoria de origem e cópia;
- promoção atômica somente após equivalência básica.

**6 testes aprovados.**

### Estado dos bloqueadores

| ID | Estado | Observação |
|---|---|---|
| B35 — FK/invariantes | `EM_CORRECAO` | checks estruturais implementados/testados; invariantes lógicas dependem do schema reconciliado |
| B05 — migração V8 | `BLOQUEADO_POR_RUNTIME` | tooling de ensaio pronto; migração real não pode ser escrita sem o schema operacional |
| B41 — backup/rollback | `BLOQUEADO_POR_RUNTIME` | cópia segura preparada; rollback integrado exige pacote/banco/configuração reais |

Fluxo aprovado quando a cópia real estiver disponível:

1. baseline pré-migração;
2. cópia consistente;
3. migração somente na cópia;
4. baseline pós-migração;
5. comparação pré/pós;
6. invariantes lógicas V8;
7. regressão funcional;
8. somente depois avaliar atualização real.

## 6. Contagem atual do tooling

| Família | Testes aprovados | Pendentes |
|---|---:|---:|
| Reconciliação | 18 | 3 E2E |
| Proveniência de build | 21 | 0 |
| SQLite/migração | 20 | 0 |
| **Total** | **59** | **3** |

**62 testes definidos; 59 aprovados em execuções controladas.**

Essa suíte ainda não substitui os testes operacionais do runtime V7/V8.

## 7. Lote A — ciclo e saídas

| ID | Tema | Estado |
|---|---|---|
| B01 | reprocessamento destrutivo | `PRONTO_PARA_CORRIGIR` |
| B02 | Conference GET com mutação | `PRONTO_PARA_CORRIGIR` |
| B03 | gate único de saída | `PRONTO_PARA_CORRIGIR` |
| B04 | versão/retificação vigente | `INSPECAO_PENDENTE` |
| B07 | universo operacional duplicado | `PRONTO_PARA_CORRIGIR` |
| B08 | T L / 2ª chamada | `INSPECAO_PENDENTE` |
| B09 | fechados na mesa viva | `PRONTO_PARA_CORRIGIR` |
| B10 | retificação misturada ao ciclo | `PRONTO_PARA_CORRIGIR` |
| B11 | estado antecipado | `PRONTO_PARA_CORRIGIR` |
| B37 | máquinas de estado misturadas | `PRONTO_PARA_CORRIGIR` |
| B39 | seleção manual por IDs | `PRONTO_PARA_CORRIGIR` |
| B40 | concorrência lógica | `INSPECAO_PENDENTE` |

## 8. Lote B — documentos/identidade/aplicabilidade

`PRONTO_PARA_CORRIGIR`: B12, B13, B14, B15, B16, B17, B18, B19, B20, B21, B22, B23, B29, B30, B31 e B33.

`INSPECAO_PENDENTE`: B32 — IRRF por competência de pagamento.

## 9. Lote C — eConsignado

- B24 — `PRONTO_PARA_CORRIGIR`;
- B25 — `PRONTO_PARA_CORRIGIR`;
- B26 — `PRONTO_PARA_CORRIGIR`;
- B27 — `PRONTO_PARA_CORRIGIR`;
- B28 — `INSPECAO_PENDENTE`.

## 10. Lote D — cadastro/migração/segurança

- B34 — `PRONTO_PARA_CORRIGIR`;
- B35 — `EM_CORRECAO`;
- B36 — `INSPECAO_PENDENTE`;
- B38 — `INSPECAO_PENDENTE`;
- B05/B41 — `BLOQUEADO_POR_RUNTIME`.

## 11. Lote E — UX/desempenho/acervo

- B43, B44, B46, B47 e B50 — `PRONTO_PARA_CORRIGIR`;
- B48 — `INSPECAO_PENDENTE`;
- B45 e B49 — `BLOQUEADO_POR_RUNTIME`.

## 12. Regressão real de 08/2026

Obrigatórios:

- `MATRIZ_REGRESSAO_V8_AGOSTO_2026.md`;
- `PROTOCOLO_REGRESSAO_28_CASOS_V8.md`.

Nenhum caso será homologado apenas porque uma pendência desapareceu da tela.

## 13. Gate final de homologação

Antes de qualquer pacote V8 final:

- [ ] runtime reconciliado com GitHub;
- [ ] identidade de release em `READY` no momento correto;
- [ ] versão/build/schema verificados;
- [ ] suíte original executada;
- [ ] bloqueadores críticos corrigidos;
- [ ] 28 casos executados;
- [ ] `integrity_check` aprovado;
- [ ] `foreign_key_check` aprovado;
- [ ] invariantes lógicas aprovadas;
- [ ] benchmark aprovado;
- [ ] segurança aprovada;
- [ ] A4 homologado;
- [ ] pacote gerado da mesma árvore testada;
- [ ] `BUILD_PROVENANCE.json` verificado;
- [ ] migração em cópia aprovada;
- [ ] instalação Windows aprovada;
- [ ] rollback código + banco + configuração comprovado.

## 14. Próximo avanço real

Sem a árvore/banco operacional, não fabricar schema, migração ou correção fictícios.

Pode-se continuar preparando tooling genérico seguro, mas a próxima mudança de estado dos bloqueadores operacionais depende da exportação do runtime Windows ou do pacote canônico equivalente.
