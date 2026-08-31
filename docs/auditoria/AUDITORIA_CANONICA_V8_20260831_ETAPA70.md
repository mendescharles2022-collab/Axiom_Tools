# Auditoria canônica V8 — Etapa 70

Data: 31/08/2026  
Status: **B06 com launcher Windows de execução única testado / runtime real ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 70 reduziu o handoff B06 a uma execução operacional única no Windows, mantendo o orquestrador Python da Etapa 69 como fonte canônica da lógica.

Novo launcher:

`scripts/BUILD_RUNTIME_HANDOFF_V8.ps1`

Nova cobertura:

`tests/test_runtime_handoff_windows_launcher.py`

## 2. Princípio

O launcher não replica a lógica de coleta/migração em PowerShell.

Ele apenas:

- valida parâmetros/caminhos;
- resolve um Python disponível com prioridade para ambientes virtuais;
- chama `build_runtime_reconciliation_handoff.py`;
- valida as flags críticas do manifesto retornado;
- falha se o handoff não comprovar origem intacta e separação código × banco.

Isso mantém uma única implementação funcional do handoff e reduz risco de duas regras divergentes.

## 3. Proteções Windows

O launcher testado:

- exige `RuntimeRoot`, `Database` e `OutputDir`;
- não possui drive do servidor codificado;
- aceita `PythonExe` explícito, mas também procura `.venv`, `venv`, `py.exe` e `python.exe`;
- bloqueia `OutputDir` dentro do runtime;
- bloqueia banco de origem dentro de `OutputDir`;
- não contém `Remove-Item`, `Move-Item`, `Clear-Content` ou `Set-Content` sobre a árvore operacional;
- exige modo `RUNTIME_RECONCILIATION_HANDOFF_NOT_HOMOLOGATION`;
- exige `source_mutation_performed=false`;
- exige `database_in_code_zip=false`;
- exige `kept_separate_from_code_zip=true`;
- encerra explicitamente com `V8 homologada: NÃO`.

## 4. Regressões

Foram adicionados sete controles estáticos cobrindo:

1. parâmetros obrigatórios;
2. chamada ao handoff Python canônico;
3. ausência de drive Windows hardcoded;
4. ausência de comandos destrutivos/movimentação;
5. confinamento da saída fora do runtime;
6. validação das flags de segurança do manifesto;
7. resolução controlada de Python.

## 5. Marco CI

Run `33445712854`  
Commit `57c9af8c54b5a2c8fd49534671cf43a6cad0e5a7`

```text
Ran 328 tests in 1.416s
OK
```

Preflight:

```text
Final OK: False
Bloqueadores homologados: 0/50
Casos PASS: 0/28
Mapa causal: 28/28
Evidências PASS: 1/10
Release READY: False
Build OK: False
```

Artifact:

- ID `9777930296`;
- SHA-256 `11c10192254f7de653a00c318e0de3b39910184b1a3f320a2fa6cb7e576f1a38`.

## 6. Guia operacional

O documento:

`docs/auditoria/GUIA_EXPORTACAO_RUNTIME_RECONCILIACAO_V8.md`

foi atualizado para tornar o handoff único o fluxo preferencial do B06.

O exportador legado de código permanece disponível para diagnóstico isolado, mas não é mais o caminho principal para estabelecer a fotografia operacional completa.

## 7. Limite

B06 permanece:

`BLOQUEADO_POR_RUNTIME`

O launcher está testado por análise/regressão no CI, mas **a execução física em Windows ainda não ocorreu nesta sessão**.

O gate `RUNTIME_BASELINE` continua `NOT_RUN`.

## 8. Próximo passo real

Executar o launcher no ambiente Windows com:

- raiz operacional real;
- caminho real do SQLite;
- diretório de saída externo ao runtime.

Depois, reconciliar os artefatos produzidos e executar os preflights de banco/acervo sobre a fotografia real.

## 9. Estado geral

- `PRONTO_PARA_CORRIGIR`: 34;
- `INSPECAO_PENDENTE`: 0;
- `EM_CORRECAO`: 12;
- `BLOQUEADO_POR_RUNTIME`: 4;
- `CORRIGIDO_TESTADO`: 0;
- `CORRIGIDO_HOMOLOGADO`: 0.

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
