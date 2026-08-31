# Guia — Handoff seguro do runtime para reconciliação V8

Data: 31/08/2026  
Status: **handoff B06 + launcher Windows + autodiscovery SQLite conservadora testados / execução na instalação real ainda pendente**

## 1. Objetivo

Materializar uma fotografia controlada da instalação operacional do Axiom Tools para reconciliar o runtime com o repositório oficial, sem publicar dados operacionais e sem alterar a origem.

O fluxo preferencial B06 produz separadamente:

- ZIP seguro de código/configuração versionável;
- cópia SQLite consistente do banco;
- relatório estrutural da cópia;
- manifesto comum com SHA-256.

O banco **não entra** no ZIP de código.

## 2. Comando preferencial no Windows

Primeira tentativa, sem precisar localizar manualmente o banco:

```powershell
powershell -ExecutionPolicy Bypass -File "<CAMINHO_DO_REPOSITORIO>\scripts\BUILD_RUNTIME_HANDOFF_V8.ps1" `
  -RuntimeRoot "<RAIZ_OPERACIONAL_DO_AXIOM_TOOLS>" `
  -OutputDir "<DIRETORIO_EXTERNO_AO_RUNTIME>"
```

A seleção automática do banco só acontece se houver **exatamente um SQLite válido** na árvore pesquisável do runtime.

Se o tooling encontrar zero ou mais de um SQLite válido, ele interrompe a coleta e exige escolha explícita:

```powershell
powershell -ExecutionPolicy Bypass -File "<CAMINHO_DO_REPOSITORIO>\scripts\BUILD_RUNTIME_HANDOFF_V8.ps1" `
  -RuntimeRoot "<RAIZ_OPERACIONAL_DO_AXIOM_TOOLS>" `
  -Database "<CAMINHO_DO_BANCO_SQLITE_OPERACIONAL>" `
  -OutputDir "<DIRETORIO_EXTERNO_AO_RUNTIME>"
```

Regras obrigatórias:

- `OutputDir` deve ficar fora da árvore indicada em `RuntimeRoot`;
- quando `Database` for informado, o banco de origem não pode ficar dentro de `OutputDir`;
- um banco explícito precisa possuir cabeçalho SQLite válido;
- o launcher não possui drive do servidor codificado;
- não é necessário informar Python quando `.venv`, `venv`, `py.exe` ou `python.exe` puder ser localizado com segurança;
- se necessário, informar explicitamente `-PythonExe "<CAMINHO_DO_PYTHON>"`.

Opcionalmente, pode ser usado um label controlado:

```powershell
-Label "axiom-tools-runtime-v8"
```

## 3. Autodiscovery conservadora do SQLite

A descoberta automática aceita apenas arquivos `.sqlite`, `.sqlite3` ou `.db` que tenham o cabeçalho real:

`SQLite format 3`

A regra é deliberadamente conservadora:

- um único SQLite válido → `AUTO_DISCOVERED_SINGLE`;
- nenhum SQLite válido → falha e solicita `-Database`;
- dois ou mais SQLite válidos → falha, lista os candidatos relativos e solicita `-Database`;
- arquivo apenas com extensão de banco, mas conteúdo não SQLite → ignorado;
- não existe desempate automático por nome, tamanho, data, pasta ou banco “mais novo”.

A busca não segue symlinks e ignora áreas como backups, temporários, documentos, uploads, logs, certificados, caches e ambientes virtuais. Diretórios usuais de dados/banco (`data`, `database`, `db`) permanecem pesquisáveis.

## 4. O que o launcher executa

O arquivo:

`scripts/BUILD_RUNTIME_HANDOFF_V8.ps1`

chama exclusivamente o orquestrador canônico:

`scripts/build_runtime_reconciliation_handoff.py`

O launcher:

1. valida runtime, saída, label e banco quando explicitamente informado;
2. resolve o Python sem caminho de servidor hardcoded;
3. impede saída dentro do runtime;
4. impede banco explícito de origem dentro da saída;
5. deixa o Python aplicar a seleção SQLite inequívoca quando `-Database` for omitido;
6. executa o handoff;
7. exige `RUNTIME_HANDOFF_MANIFEST.json`;
8. confirma no manifesto que a origem não foi alterada;
9. confirma que o banco não entrou no ZIP de código;
10. confirma que a cópia SQLite permaneceu separada;
11. informa o banco selecionado e `database_selection`;
12. termina declarando explicitamente `V8 homologada: NÃO`.

## 5. Whitelist do ZIP de código/configuração

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

## 6. Conteúdo proibido no ZIP de código

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

## 7. Tratamento do banco

O SQLite é tratado em trilha separada.

O handoff usa o tooling de backup/cópia consistente e registra:

- nome do banco selecionado;
- método `EXPLICIT` ou `AUTO_DISCOVERED_SINGLE`;
- SHA-256 do banco de origem antes e depois;
- schema SHA-256;
- `user_version`;
- diagnóstico estrutural;
- equivalência de schema entre origem e cópia;
- cópia física separada do ZIP de código.

A existência de divergência estrutural pode ser preservada para diagnóstico; ela **não** é convertida em homologação automática.

## 8. Saída esperada

Após sucesso do launcher:

```text
RUNTIME_HANDOFF_WINDOWS_OK
Diretório do handoff: <...>
Banco selecionado: <...> [EXPLICIT|AUTO_DISCOVERED_SINGLE]
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

## 9. Exportador legado de código

O fluxo anterior permanece disponível para diagnóstico isolado:

- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/export_runtime_reconciliation.py`;
- `scripts/audit_runtime_reconciliation.py`.

Porém, para remover o bloqueio B06, o **handoff único** é o caminho preferencial porque preserva na mesma fotografia a árvore versionável e uma cópia consistente do banco sem misturá-las.

## 10. Verificação após a coleta real

Antes de qualquer reconciliação ou commit:

1. conferir `RUNTIME_HANDOFF_MANIFEST.json`;
2. conferir `database_selection` e o banco selecionado;
3. conferir os SHA-256;
4. confirmar ausência de banco/documentos/certificados/credenciais no ZIP de código;
5. manter a cópia SQLite fora do GitHub;
6. auditar código/configuração/identidade runtime ↔ repositório;
7. executar B35 e auditores estruturais sobre a cópia SQLite;
8. configurar/executar B49 contra banco/acervo reais;
9. inventariar módulos e suíte operacional;
10. reconciliar apenas diferenças comprovadas, preservando trabalho válido.

## 11. O que NÃO fazer

- não compactar manualmente a raiz inteira do servidor;
- não subir o SQLite operacional ao GitHub;
- não versionar documentos, uploads, certificados ou `.env`;
- não substituir a `main` inteira sem comparação;
- não apagar a fundação atual antes de inventariar diferenças;
- não usar o diretório do runtime como `OutputDir`;
- não escolher automaticamente entre dois bancos possíveis;
- não declarar B06 resolvido somente porque o handoff foi gerado.

## 12. Critério para B06 sair de `BLOQUEADO_POR_RUNTIME`

B06 só avança quando:

1. o handoff for produzido no runtime Windows real;
2. manifesto e proteções passarem;
3. código/configuração/identidade forem comparados;
4. cópia SQLite passar pelos preflights aplicáveis;
5. a árvore operacional for reconciliada na fonte oficial;
6. a suíte original estiver preservada/versionada;
7. a árvore reconciliada iniciar e reproduzir o baseline esperado;
8. dados reais permanecerem fora do repositório.

## 13. Evidência do tooling

Handoff, launcher Windows e autodiscovery conservadora foram validados no GitHub Actions run `33446139531`:

```text
Ran 336 tests in 1.585s
OK
```

Isso valida o tooling, **não a instalação física**.

## 14. Estado atual

**B06 BLOQUEADO_POR_RUNTIME / RUNTIME_BASELINE NOT_RUN / V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
