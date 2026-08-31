# Guia — Exportação segura do runtime para reconciliação V8

Data: 31/08/2026  
Status: **tooling revisado / execução Windows real ainda pendente**

## 1. Objetivo

Gerar uma cópia controlada dos artefatos versionáveis da instalação operacional do Axiom Tools para reconciliar o runtime com o repositório oficial.

A exportação pode conter:

- código-fonte;
- testes;
- scripts/migrações;
- templates/estáticos;
- arquivos de dependência;
- configuração-modelo sem segredos;
- metadata/identidade de release.

O procedimento não substitui a instalação, não altera o banco e não move documentos.

Scripts:

- `scripts/export_runtime_reconciliation.ps1`;
- `scripts/export_runtime_reconciliation.py`;
- `scripts/audit_runtime_reconciliation.py`.

## 2. Comando padrão

Executar em PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File "<CAMINHO_DO_REPOSITORIO>\scripts\export_runtime_reconciliation.ps1" -Root "E:\Programas\Axiom_Tools"
```

Se a raiz operacional estiver em outro local, alterar somente `-Root`.

Opcionalmente:

```powershell
powershell -ExecutionPolicy Bypass -File "<CAMINHO_DO_REPOSITORIO>\scripts\export_runtime_reconciliation.ps1" -Root "E:\Programas\Axiom_Tools" -OutputDir "E:\Programas\Axiom_Tools\temp"
```

## 3. Whitelist de coleta

Quando existirem, o exportador considera áreas como:

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

`config` não recebe tratamento privilegiado: entra somente porque configuração-modelo e identidade de release são necessárias à reconciliação. Todos os filtros de segurança continuam valendo dentro dessa pasta.

O script não faz espelhamento cego da instalação.

## 4. Conteúdo proibido

O exportador remove/bloqueia, inclusive dentro de `config`:

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

Também existe varredura textual para possíveis segredos hardcoded.

Se houver material suspeito, a exportação deve falhar em vez de publicá-lo silenciosamente.

## 5. Privacidade do artefato

`RECONCILIATION_INFO.txt` não deve registrar:

- caminho absoluto da instalação;
- caminho absoluto do staging;
- caminho absoluto do diretório de saída.

O relatório JSON do auditor também não deve expor `runtime_root` ou `repo_root` absolutos.

A proveniência necessária à comparação é fornecida pelo manifesto, hashes, áreas comparadas e identidade versionável — não pelo caminho físico do servidor.

## 6. Saída esperada

Ao concluir:

```text
EXPORT_V8_OK
Stage: <nome da pasta de staging>
ZIP:   <nome do arquivo .zip>
SHA256: <hash>
Arquivos: <quantidade>
```

Dentro do ZIP devem existir:

- artefatos versionáveis exportados;
- `RECONCILIATION_MANIFEST.csv` com SHA-256 por arquivo;
- `RECONCILIATION_INFO.txt` sem caminhos absolutos da instalação.

## 7. Auditoria de reconciliação

Depois de extrair o ZIP seguro, executar o auditor contra um clone controlado do repositório.

Além de código/testes/templates, o auditor compara agora:

- `app/config` ou `config` com `config` do repositório;
- `release_identity.toml` quando presente;
- `pyproject.toml` e requirements controlados.

O relatório registra se:

- configuração foi comparada;
- identidade de release foi encontrada/comparada;
- arquivos são `SAME`, `CHANGED`, `RUNTIME_ONLY` ou `REPO_ONLY`.

## 8. Verificação antes da reconciliação

Antes de qualquer commit de runtime:

1. conferir o manifesto;
2. conferir a lista do ZIP;
3. confirmar ausência de banco/documentos/certificados/credenciais;
4. confirmar que configuração exportada é apenas versionável/modelo;
5. verificar divergência de `release_identity.toml` quando existir;
6. inventariar módulos V8 e suíte operacional;
7. somente então reconciliar arquivos de forma controlada.

## 9. O que NÃO fazer

- não compactar manualmente a raiz inteira do servidor;
- não copiar `data`, banco, documentos, uploads, logs ou backups para o GitHub;
- não versionar certificados;
- não versionar `.env`;
- não publicar configuração local contendo segredo;
- não substituir a `main` inteira sem comparação;
- não apagar a fundação atual antes de inventariar diferenças;
- não declarar B06 resolvido apenas porque o ZIP foi gerado.

## 10. Critério para B06 sair de `BLOQUEADO_POR_RUNTIME`

B06 só avança quando:

1. o export seguro for produzido no runtime real;
2. manifesto e segurança passarem;
3. código/configuração/identidade forem comparados;
4. a árvore operacional for reconciliada na fonte oficial;
5. a suíte original estiver versionada;
6. a árvore reconciliada iniciar e reproduzir o baseline esperado;
7. dados reais permanecerem fora do repositório.

## 11. Estado atual

A revisão de 31/08/2026 adicionou cobertura explícita de configuração/identidade e removeu caminhos absolutos dos artefatos de export/auditoria.

A validação final do fluxo `.ps1` e a execução contra a instalação Windows real continuam obrigatórias antes de remover B06.
