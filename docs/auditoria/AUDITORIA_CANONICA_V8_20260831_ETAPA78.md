# Auditoria canônica V8 — Etapa 78

Data: 31/08/2026  
Status: **B43/B44/B46/B47 COM TOOLING EXECUTÁVEL / V8 NÃO HOMOLOGADA**

## 1. Escopo

Esta etapa encerra a fila `PRONTO_PARA_CORRIGIR` sem promover falsamente nenhum bloqueador para corrigido ou homologado.

Foram transformados em contratos executáveis os quatro bloqueadores de experiência operacional que ainda não possuíam guardrail automatizado:

- B43 — Pendências orientada pela competência ativa;
- B44 — relatório A4 retrato;
- B46 — Monitor com fonte única de status operacional;
- B47 — atalhos Sintegra preservados e realmente visíveis.

O tooling é deliberadamente parametrizável para ser aplicado à árvore operacional depois da reconciliação B06.

## 2. Tooling introduzido

Arquivos principais:

- `scripts/audit_operational_ui_contract.py`;
- `config/operational_ui_contract_v8.json`;
- `tests/test_audit_operational_ui_contract.py`;
- `tests/test_operational_ui_contract_policy.py`.

O auditor trabalha por contratos declarativos com:

- globs de arquivos elegíveis;
- quantidade mínima de arquivos;
- regras obrigatórias;
- alternativas obrigatórias;
- padrões proibidos;
- relatório estável com achados e hash.

Ele não altera a árvore auditada.

## 3. B43 — Pendências

O contrato canônico exige:

1. contexto baseado na competência ativa/de trabalho;
2. `PROC` apenas como filtro secundário quando presente;
3. bloqueio de marcadores que indiquem `PROC` como contexto primário/default da tela.

A regressão cobre a ausência da competência ativa e o retorno indevido ao desenho orientado por `PROC`.

B43 passa para `EM_CORRECAO`, pois existe critério executável, mas ainda precisa ser aplicado e validado na árvore operacional reconciliada.

## 4. B44 — A4

O contrato exige estaticamente:

- `A4 portrait`;
- cabeçalho de tabela repetível em impressão;
- controle de quebra de blocos/linhas;
- ausência de `A4 landscape` no alvo contratual.

Isso protege o patrimônio válido já observado no V8F2.

A verificação estática **não substitui** preview/impressão física no runtime. Portanto B44 passa somente para `EM_CORRECAO`.

## 5. B46 — Monitor

O contrato exige um marcador canônico de status operacional:

`status_operacional`

Também bloqueia marcadores explícitos de uma fonte primária legada paralela, evitando reintrodução de dupla verdade visual/técnica.

A simplificação concreta da tela e a integração com a máquina real de estados continuam dependentes da árvore reconciliada.

B46 passa para `EM_CORRECAO`.

## 6. B47 — Sintegra

A regressão foi endurecida para exigir **duas provas independentes**:

1. backend configurando a URL Sintegra (`sintegra_go_url = ...` ou `sintegra_nacional_url = ...`);
2. atalho realmente visível/renderizável no template por `href` relacionado ao Sintegra.

Foram protegidos explicitamente os dois falsos positivos:

- backend existente sem botão/atalho visual;
- botão/template presente sem backend configurado.

Um único trecho do template não pode satisfazer simultaneamente as duas metades do contrato.

B47 passa para `EM_CORRECAO`.

## 7. Evidência CI

GitHub Actions:

- run: `33452021223`;
- commit auditado: `47da595d2eed0d6a18176bc4eddb0cc2dd3e6891`;
- Python: `3.12.14`;
- PowerShell: `POWERSHELL_B06_SMOKE_OK`;
- testes: `494 OK`;
- mapa causal: `28/28`;
- artifact: `v8-release-preflight#9780092100`;
- SHA-256 do artifact: `21010ecfbd5bf75d2fed3b691ba5a5a11c6e63de78878e6eafa0b40af4891db4`.

Preflight do mesmo marco:

- bloqueadores homologados: `0/50`;
- casos C PASS: `0/28`;
- evidências externas PASS: `1/10`;
- release READY: `False`;
- build OK: `False`.

## 8. Snapshot após a Etapa 78

Estado correto de governança:

| Estado | Quantidade |
|---|---:|
| `PRONTO_PARA_CORRIGIR` | 0 |
| `INSPECAO_PENDENTE` | 0 |
| `EM_CORRECAO` | 46 |
| `BLOQUEADO_POR_RUNTIME` | 4 |
| `CORRIGIDO_TESTADO` | 0 |
| `CORRIGIDO_HOMOLOGADO` | 0 |

Bloqueados materialmente pelo runtime: B05, B06, B45 e B49.

Todos os demais B possuem agora critério executável/guardrail para a fase de integração.

## 9. Limite desta etapa

A Etapa 78 **não significa que 46 defeitos foram corrigidos no sistema operacional**.

Ela significa que os 46 bloqueadores não dependentes exclusivamente do runtime deixaram de ser itens soltos de diagnóstico e passaram a possuir ferramenta, contrato, regressão ou preflight executável capaz de governar a correção real.

Regra preservada:

**tooling verde ≠ correção integrada ≠ homologação.**

## 10. Próximo gate material

O próximo avanço de maior valor é B06: consumir o handoff produzido pela instalação Windows física, verificar manifesto/hashes, materializar staging seguro, reconciliar runtime ↔ repositório e executar preflights sobre a cópia SQLite, sempre sem alterar a origem operacional.

Até isso ocorrer:

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
