# Rastreador canônico — Execução de correção V8

Data inicial: 28/08/2026  
Status: **FASE DE CORREÇÃO PREPARADA / RUNTIME AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

Este arquivo passa a ser o rastreador vivo da fase de correção e homologação da V8.

Os documentos `AUDITORIA_CANONICA_V8_20260828_ETAPA*.md` permanecem como histórico de investigação. A partir deste ponto, o andamento principal deve ser atualizado aqui para evitar dezenas de arquivos de etapa sem necessidade.

## 1. Legenda de estado

- `NAO_INICIADO` — ainda não confrontado na árvore oficial reconciliada;
- `INSPECAO_PENDENTE` — regra conhecida, mas causa/implementação precisa ser confirmada no runtime;
- `PRONTO_PARA_CORRIGIR` — causa e regra suficientes para implementação assim que a árvore oficial estiver disponível;
- `EM_CORRECAO` — alteração de código em curso na árvore oficial;
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
| B42 — proveniência de build | `PRONTO_PARA_CORRIGIR` | fonte única de versão + commit + schema + manifesto do build |
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
- o inventário atual de `tests/` continua sem a suíte operacional do runtime.

Conclusão operacional:

**B06 não será resolvido por simples checkout de commit histórico conhecido.**

A fonte de reconciliação continua sendo a cópia operacional controlada do runtime/servidor ou pacote canônico equivalente, seguida de filtragem de dados sensíveis e versionamento da árvore de código.

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
- [ ] versão/build/schema rastreáveis;
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
- [ ] backup e migração em cópia aprovados;
- [ ] instalação Windows aprovada;
- [ ] rollback código + banco + configuração executado com sucesso.

## 10. Estado desta atualização

Atualizações de governança já aplicadas ao repositório em 28/08/2026:

- `docs/STATUS_ATUAL.md` atualizado para refletir a auditoria completa;
- `README.md` alinhado ao estado `main ≠ runtime`;
- mapa de cobertura B01–B50 preservado;
- este rastreador criado como fonte viva da fase de correção;
- histórico Git investigado e descartado como fonte suficiente para recuperar a árvore operacional completa.

Próximo avanço real: reconciliação da árvore operacional ou recuperação de evidência de runtime suficiente para começar a implementação sobre a fonte oficial.
