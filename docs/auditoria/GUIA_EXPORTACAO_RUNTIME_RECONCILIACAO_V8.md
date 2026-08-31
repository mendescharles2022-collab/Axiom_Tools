# Guia — Handoff seguro do runtime para reconciliação V8

Data: 31/08/2026  
Status: **handoff B06 + launcher Windows testados / execução na instalação real ainda pendente**

## 1. Objetivo

Materializar uma fotografia controlada da instalação operacional do Axiom Tools para reconciliar o runtime com o repositório oficial, sem publicar dados operacionais e sem alterar a origem.

O fluxo preferencial B06 produz separadamente:

- ZIP seguro de código/configuração versionável;
- cópia SQLite consistente do banco;
- relatório estrutural da cópia;
- manifesto comum com SHA-256.

O banco **não entra** no ZIP de código.

## 2. Comando preferencial no Windows

Executar em PowerShell a partir de uma cópia do tooling de auditoria:

```powershell
powershell -ExecutionPolicy Bypass -File "<CAMINHO_DO_REPOSITORIO>\scripts\BUILD_RUNTIME_HANDOFF_V8.ps1" `
  -RuntimeRoot "<RAIZ_OPERACIONAL_DO_AXIOM_TOOLS>" `
  -Database "<CAMINHO_DO_BANCO_SQLITE_OPERACIONAL>" `
  -OutputDir "<DIRETORIO_EXTERNO_AO_RUNTIME>"
```

Regras obrigatórias:

- `OutputDir` deve ficar fora da árvore indicada em `RuntimeRoot`;
- o banco de origem não pode ficar dentro de `OutputDir`;
- o launcher não possui drive do servidor codificado;
- não é necessário informar Python quando `.venv`, `venv`, `py.exe` ou `python.exe` puder ser localizado com segurança;
- se necessário, informar explicitamente `-PythonExe "<CAMINHO_DO_PYTHON>"`.

Opcionalmente, pode ser usado um label controlado:

```powershell
-Label "axiom-tools-runtime-v8"
```

## 3. O que o launcher executa

O arquivo:

`scripts/BUILD_RUNTIME_HANDOFF_V8.ps1`

chama exclusivamente o orquestrador canônico:

`scripts/build_runtime_reconciliation_handoff.py`

O launcher:

1. valida runtime, banco, saída e label;
2. resolve o Python sem caminho de servidor hardcoded;
3. impede saída dentro do runtime;
4. impede banco de origem dentro da saída;
5. executa o handoff;
6. exige `RUNTIME_HANDOFF_MANIFEST.json`;
7. confirma no manifesto que a origem não foi alterada;
8. confirma que o banco não entrou no ZIP de código;
9. confirma que a cópia SQLite permaneceu separada;
10. termina declarando explicitamente `V8 homologada: NÃO`.

## 4. Whitelist do ZIP de código/configuração

Quando existirem, o exportador considera áreas versionáveis como:

- `app\src` ou `src`;
- `app\tests` ou `tests`;
- `app\scripts` ou `scripts`;
- `app\migrations` / `migrations`;
- `app\alembic` / `alembic`;
- `app\templates` / `templates`;
- `app\static` / `static`;
- `app\config` / `config`;
- `pyproject.toml`;
- `requirements*.txt` controlados;
- entrypoints Python diretamente na raiz e em `app`.

O script não faz espelhamento cego da instalação.

## 5. Conteúdo proibido no ZIP de código

O exportador remove/bloqueia:

- SQLite/DB;
- documentos e uploads;
- certificados e chaves privadas;
- `.env` e variantes;
- arquivos conhecidos de token/credencial/segredo;
- logs;
- backups;
- temporários;
- caches;
- `.venv`;
- `__pycache__`;
- compactados preexistentes;
- junction/symlink/reparse point dentro das origens copiadas.

Também existe varredura textual para possíveis segredos hardcoded. Se houver material suspeito, a coleta falha em vez de publicá-lo silenciosamente.

## 6. Tratamento do banco

O SQLite é tratado em trilha separada.

O handoff usa o tooling de backup/cópia consistente e registra:

- SHA-256 do banco de origem antes e depois;
- schema SHA-256;
- `user_version`;
- diagnóstico estrutural;
- equivalência de schema entre origem e cópia;
- cópia física separada do ZIP de código.

A existência de divergência estrutural pode ser preservada para diagnóstico; ela **não** é convertida em homologação automática.

## 7. Saída esperada

Após sucesso do launcher:

```text
RUNTIME_HANDOFF_WINDOWS_OK
Diretório do handoff: <...>
ZIP de código/config: <...zip>
SQLite separado: <...sqlite3>
Manifesto SHA-256: <hash>
Origem alterada: NÃO
V8 homologada: NÃO
```

No diretório `<label>-handoff` devem existir, entre outros:

- ZIP seguro de código/configuração;
- cópia SQLite separada;
- `RUNTIME_DATABASE_CLONE_REPORT.json`;
- `RUNTIME_HANDOFF_MANIFEST.json`.

## 8. Exportador legado de código

O fluxo anterior permanece disponível para diagnóstico isolado:

- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/export_runtime_reconciliation.py`;
- `scripts/audit_runtime_reconciliation.py`.

Porém, para remover o bloqueio B06, o **handoff único** é o caminho preferencial porque preserva na mesma fotografia a árvore versionável e uma cópia consistente do banco sem misturá-las.

## 9. Verificação após a coleta real

Antes de qualquer reconciliação ou commit:

1. conferir `RUNTIME_HANDOFF_MANIFEST.json`;
2. conferir os SHA-256;
3. confirmar ausência de banco/documentos/certificados/credenciais no ZIP de código;
4. manter a cópia SQLite fora do GitHub;
5. auditar código/configuração/identidade runtime ↔ repositório;
6. executar B35 e auditores estruturais sobre a cópia SQLite;
7. configurar/executar B49 contra banco/acervo reais;
8. inventariar módulos e suíte operacional;
9. reconciliar apenas diferenças comprovadas, preservando trabalho válido.

## 10. O que NÃO fazer

- não compactar manualmente a raiz inteira do servidor;
- não subir o SQLite operacional ao GitHub;
- não versionar documentos, uploads, certificados ou `.env`;
- não substituir a `main` inteira sem comparação;
- não apagar a fundação atual antes de inventariar diferenças;
- não usar o diretório do runtime como `OutputDir`;
- não declarar B06 resolvido somente porque o handoff foi gerado.

## 11. Critério para B06 sair de `BLOQUEADO_POR_RUNTIME`

B06 só avança quando:

1. o handoff for produzido no runtime Windows real;
2. manifesto e proteções passarem;
3. código/configuração/identidade forem comparados;
4. cópia SQLite passar pelos preflights aplicáveis;
5. a árvore operacional for reconciliada na fonte oficial;
6. a suíte original estiver preservada/versionada;
7. a árvore reconciliada iniciar e reproduzir o baseline esperado;
8. dados reais permanecerem fora do repositório.

## 12. Evidência do tooling

Launcher Windows + handoff canônico foram validados no GitHub Actions run `33445712854`:

```text
Ran 328 tests in 1.416s
OK
```

Isso valida o tooling, **não a instalação física**.

## 13. Estado atual

**B06 BLOQUEADO_POR_RUNTIME / RUNTIME_BASELINE NOT_RUN / V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
