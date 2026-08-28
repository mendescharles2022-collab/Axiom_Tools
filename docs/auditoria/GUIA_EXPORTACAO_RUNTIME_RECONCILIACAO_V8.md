# Guia — Exportação segura do runtime para reconciliação V8

Data: 28/08/2026  
Status: **ferramenta preparada / execução e validação Windows pendentes**

## 1. Objetivo

Gerar uma cópia **somente de código/testes controlados** da instalação operacional do Axiom Tools para reconciliar o runtime com o repositório oficial.

O procedimento não substitui a instalação, não altera o banco e não move documentos.

Script:

`scripts/export_runtime_reconciliation.ps1`

## 2. Comando padrão

Executar em PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File "<CAMINHO_DO_REPOSITORIO>\scripts\export_runtime_reconciliation.ps1" -Root "E:\Programas\Axiom_Tools"
```

Se a raiz operacional estiver em outro local, alterar somente o parâmetro `-Root`.

Opcionalmente, definir uma saída separada:

```powershell
powershell -ExecutionPolicy Bypass -File "<CAMINHO_DO_REPOSITORIO>\scripts\export_runtime_reconciliation.ps1" -Root "E:\Programas\Axiom_Tools" -OutputDir "E:\Programas\Axiom_Tools\temp"
```

## 3. O que o script procura

A exportação usa whitelist e tenta copiar, quando existirem:

- `app\src`;
- `app\tests`;
- `app\scripts`;
- `app\migrations`;
- `app\alembic`;
- `scripts`;
- `app\pyproject.toml`;
- requirements controlados;
- entrypoints Python diretamente na raiz e em `app`.

Ele não faz espelhamento cego da instalação.

## 4. Conteúdo proibido

O exportador remove/bloqueia conteúdo com risco de dados reais ou segredos, incluindo:

- SQLite/DB;
- documentos e uploads;
- certificados e chaves privadas;
- `.env`;
- arquivos com nomes de token/senha/credencial;
- logs;
- backups;
- temporários;
- caches;
- `.venv`;
- `__pycache__`;
- arquivos compactados preexistentes;
- junction/symlink/reparse point dentro das origens copiadas.

Também faz varredura textual básica para possível segredo hardcoded.

Se encontrar conteúdo suspeito, a exportação deve **falhar** em vez de silenciosamente publicar esse material.

## 5. Saída esperada

Ao concluir:

```text
EXPORT_V8_OK
Stage: <pasta temporária>
ZIP:   <arquivo .zip>
SHA256: <hash>
Arquivos: <quantidade>
A raiz operacional não foi modificada.
```

Dentro do ZIP devem existir:

- código/testes exportados;
- `RECONCILIATION_MANIFEST.csv` com SHA-256 por arquivo;
- `RECONCILIATION_INFO.txt` com resumo da coleta.

## 6. Verificação antes de usar o ZIP

Antes de qualquer commit de reconciliação:

1. conferir `RECONCILIATION_INFO.txt`;
2. conferir a lista de arquivos do ZIP;
3. confirmar ausência de banco/documentos/certificados/credenciais;
4. comparar o manifesto com a árvore operacional;
5. inventariar módulos V8 presentes;
6. identificar testes e scripts de migração;
7. somente depois iniciar a importação controlada para o GitHub.

## 7. O que NÃO fazer

- não compactar manualmente a raiz inteira do servidor;
- não copiar `data`, `database`, documentos, uploads, logs ou backups para o GitHub;
- não versionar certificados;
- não versionar `.env`;
- não substituir a `main` inteira de uma vez sem comparação;
- não apagar a fundação atual antes de inventariar diferenças;
- não declarar B06 resolvido apenas porque o ZIP foi gerado.

## 8. Critério para B06 sair de `BLOQUEADO_POR_RUNTIME`

B06 só avança quando:

1. o ZIP seguro for produzido;
2. a árvore exportada for auditada;
3. o código operacional for reconciliado na fonte oficial;
4. a suíte original estiver versionada;
5. a árvore reconciliada iniciar e reproduzir o baseline esperado;
6. dados reais permanecerem fora do repositório.

## 9. Estado atual

A ferramenta foi criada e revisada estaticamente no repositório.

O ambiente usado nesta auditoria não possui PowerShell disponível para executar o script; portanto a validação sintática/funcional final do `.ps1` permanece obrigatória no Windows antes de confiar na exportação produzida.
