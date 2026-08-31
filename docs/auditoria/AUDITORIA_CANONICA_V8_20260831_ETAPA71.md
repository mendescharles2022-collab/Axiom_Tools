# Auditoria canônica V8 — Etapa 71

Data: 31/08/2026  
Status: **B06 com autodiscovery SQLite conservador testado / runtime real ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 71 reduziu mais um ponto de atrito da coleta física B06 sem permitir seleção heurística arriscada do banco operacional.

Arquivos evoluídos:

- `scripts/build_runtime_reconciliation_handoff.py`;
- `scripts/BUILD_RUNTIME_HANDOFF_V8.ps1`;
- `tests/test_build_runtime_reconciliation_handoff.py`;
- `tests/test_runtime_handoff_windows_launcher.py`.

## 2. Regra de seleção do SQLite

O parâmetro do banco passa a ser opcional somente sob regra estrita:

- **exatamente um SQLite válido descoberto no runtime** → seleção automática permitida;
- **nenhum SQLite válido** → coleta bloqueada e exige `--database`/`-Database` explícito;
- **mais de um SQLite válido** → coleta bloqueada e lista candidatos relativos para escolha explícita;
- arquivo com extensão `.sqlite`, `.sqlite3` ou `.db` sem cabeçalho SQLite válido → ignorado na autodetecção;
- banco explicitamente informado também precisa possuir cabeçalho SQLite válido.

Não existe ranking por nome, tamanho, data ou diretório para escolher entre múltiplos bancos.

## 3. Escopo da descoberta

A descoberta percorre a árvore operacional sem seguir symlinks e ignora áreas que não devem decidir o banco vivo, como:

- `.git`;
- `.venv` / `venv`;
- caches Python/testes;
- documentos/uploads;
- logs;
- backups;
- temporários;
- certificados;
- caches operacionais.

Diretórios usuais de dados/banco, como `data`, `database` e `db`, permanecem pesquisáveis.

## 4. Proveniência da seleção

O manifesto B06 passa a registrar:

`source.database_selection`

Valores previstos:

- `EXPLICIT`;
- `AUTO_DISCOVERED_SINGLE`.

Assim a fotografia informa se o banco veio de escolha explícita ou de descoberta inequívoca.

## 5. Launcher Windows

`-Database` deixa de ser obrigatório em:

`scripts/BUILD_RUNTIME_HANDOFF_V8.ps1`

O launcher:

- envia `--database` ao Python somente quando o parâmetro foi informado;
- avisa quando a autodiscovery conservadora está ativa;
- mantém `RuntimeRoot` e `OutputDir` obrigatórios;
- mantém as proteções da Etapa 70;
- exibe ao final o banco selecionado e o método de seleção registrado no manifesto.

## 6. Regressões adicionadas

Cobertura nova prova:

1. banco único válido dentro do runtime é selecionado automaticamente;
2. múltiplos bancos válidos bloqueiam seleção automática;
3. extensão falsa de SQLite é ignorada;
4. SQLite localizado em pasta de backup não participa da seleção automática;
5. ausência de SQLite válido exige caminho explícito;
6. banco explícito sem cabeçalho SQLite é rejeitado;
7. launcher só inclui `--database` quando houver caminho explícito;
8. `Database` é opcional no launcher, sem remover as validações quando informado.

## 7. Marco CI

Run `33446139531`  
Commit `7181b47a58a73843ff3dd8e10ff5947081bd81b1`

```text
Ran 336 tests in 1.585s
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

- ID `9778084041`;
- SHA-256 `b958e73077c5e0dadd1f7372bdbe3d22d44890ad0cc14bbf62c4bb4854263cc9`.

## 8. Limite

B06 permanece:

`BLOQUEADO_POR_RUNTIME`

A Etapa 71 reduz a necessidade de localizar manualmente o SQLite quando a instalação possuir uma única base inequívoca. Ela **não executa o launcher na instalação física** e não transforma autodiscovery em homologação.

`RUNTIME_BASELINE` permanece `NOT_RUN`.

## 9. Estado geral

- `PRONTO_PARA_CORRIGIR`: 34;
- `INSPECAO_PENDENTE`: 0;
- `EM_CORRECAO`: 12;
- `BLOQUEADO_POR_RUNTIME`: 4;
- `CORRIGIDO_TESTADO`: 0;
- `CORRIGIDO_HOMOLOGADO`: 0.

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
