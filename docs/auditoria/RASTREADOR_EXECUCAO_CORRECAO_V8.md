# Rastreador canônico — Execução de correção V8

Data: 28/08/2026  
Status: **RUNTIME AINDA NÃO RECONCILIADO / V8 NÃO HOMOLOGADA**

## 1. Marco canônico do tooling

GitHub Actions run `33196049264`  
Commit `eb695be6531c7711ac36b3f45e0d9d31eb809233`  
Python 3.12.14

```text
Ran 165 tests in 1.115s
OK
```

Preflight:

- B homologados `0/50`;
- C PASS `0/28`;
- evidências externas `1/10`;
- release READY `False`;
- build OK `False`.

Artifact `v8-release-preflight`:

- ID `9695772154`;
- 2.288 bytes;
- SHA-256 `380162c6ed4b1d5b01b0f7c7c834f8f1d300699db54b4b050ed967b5e9181d85`.

## 2. Snapshot B01–B50

| Estado | Quantidade |
|---|---:|
| `PRONTO_PARA_CORRIGIR` | 35 |
| `INSPECAO_PENDENTE` | 8 |
| `EM_CORRECAO` | 3 |
| `BLOQUEADO_POR_RUNTIME` | 4 |
| `CORRIGIDO_TESTADO` | 0 |
| `CORRIGIDO_HOMOLOGADO` | 0 |

Em correção: B35, B41, B42.  
Bloqueados pelo runtime: B05, B06, B45, B49.

## 3. B06 — próximo gate operacional

Não implementar B01/B02/B03 sobre a fundação reduzida da `main`.

Pronto/testado:

- exportador runtime;
- launcher PowerShell;
- auditor de reconciliação;
- E2E;
- preflight automático/artifact.

Pendente:

1. exportar instalação Windows real ou recuperar pacote canônico equivalente;
2. auditar export;
3. reconciliar árvore controlada;
4. trazer suíte operacional original;
5. estabelecer baseline.

## 4. B35 — avanço com invariantes confirmadas

Estado `EM_CORRECAO`.

`config/sqlite_invariants_closing_confirmed_v8.json` registra apenas regras comprovadas pelo runtime preservado:

1. `CLOSING_FECHADA_WITHOUT_VERSION` — FECHADA sem versão é inválida;
2. `CLOSING_CURRENT_VERSION_MUST_EXIST` — `versao_atual` deve apontar para versão existente.

`tests/test_closing_confirmed_invariants.py` possui quatro regressões específicas, aprovadas no CI canônico.

Não foi adicionada invariante sobre retificação `DETECTADA` única porque os trechos recuperados não provam se o índice parcial da linha 59 é `UNIQUE`.

Pendente: executar essas invariantes contra cópia real do banco e acrescentar somente novas regras comprovadas pelo schema/runtime.

## 5. B42 — proveniência

Estado `EM_CORRECAO`.

Pronto: identidade canônica, geração/verificação de build, Git limpo, SHA-256 e bloqueio de conteúdo sensível.

Pendente: runtime, `/health`, logs, instalador e pacote final consumirem a mesma identidade.

## 6. B41 — rollback

Estado `EM_CORRECAO`.

Pronto: bundle, verificador e restauração em staging.

Pendente: arquivos reais, cópia real, rollback físico Windows e smoke posterior.

## 7. Achado runtime — Processamento ainda carrega Auditoria

Registro:

`docs/auditoria/ACHADO_RUNTIME_RESIDUO_AUDITORIA_NO_PROCESSAMENTO_V8.md`.

Template operacional preservado mostra `PROCESSAMENTO DE ARQUIVOS` no eyebrow e `<h1>` começando em `Aud...`.

Reforça B37/B43/B46; não cria novo bloqueador.

## 8. B08/T L

Falha operacional permanece confirmada: T L deveria estar na 2ª chamada e apareceu `PRONTA` chamada 1.

O runtime preservado mostra atualização de `chamada_atual` e depois `SET status='PRONTA', chamada=?`, mas a cláusula `WHERE` continua truncada.

Portanto a causa exata **não foi atribuída** a essa rotina. B08 segue `INSPECAO_PENDENTE` até recuperar o código completo ou reproduzir a transição no runtime reconciliado.

## 9. Gate final

Ferramentas:

- `scripts/validate_release_gate.py`;
- `scripts/build_current_preflight.py`;
- `scripts/build_evidence_index.py`.

Modo final exige 50/50 B homologados, 28/28 C PASS, release READY, build verificável e dez gates externos PASS.

## 10. Ordem após B06

1. baseline/suíte original;
2. B01;
3. B02;
4. B03/B39;
5. B07/B08;
6. B09/B10/B11/B37/B40;
7. B12–B23/B29–B33;
8. B24–B28;
9. B34/B36/B38;
10. B43/B44/B46/B47/B50;
11. migração/invariantes reais;
12. C01–C28;
13. benchmark runtime;
14. build/pacote;
15. instalação Windows + rollback.

## 11. Situação atual

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**

O próximo salto de valor continua sendo remover B06 e trabalhar sobre a árvore operacional real.
