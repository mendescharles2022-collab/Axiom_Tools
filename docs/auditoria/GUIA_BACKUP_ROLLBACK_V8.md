# Guia V8 — Backup e rollback verificável

Data: 28/08/2026
Status: **tooling preparado e testado em staging / rollback real Windows ainda não homologado**

## Objetivo

Garantir que uma atualização V8 só avance quando existir caminho verificável para retornar a um conjunto coerente de:

- código controlado;
- configuração explicitamente incluída;
- banco SQLite consistente;
- versão da aplicação;
- versão do schema;
- commit/build de origem.

## Princípio

Backup não significa apenas existir uma pasta chamada `backup`.

Rollback só existe quando o conteúdo anterior pode ser:

1. identificado;
2. verificado por hash;
3. restaurado em ensaio;
4. validado estruturalmente;
5. associado à versão/schema/commit corretos.

## Ferramentas versionadas

### `scripts/create_rollback_bundle.py`

Cria bundle local somente a partir de lista explícita de arquivos controlados.

O script:

- não varre a instalação inteira;
- não sobrescreve destino existente;
- rejeita path traversal;
- copia os arquivos previstos mantendo caminhos relativos;
- cria cópia SQLite consistente usando `sqlite3.Connection.backup()`;
- executa `PRAGMA integrity_check` e `PRAGMA foreign_key_check` na cópia;
- registra tamanho e SHA-256;
- grava `ROLLBACK_MANIFEST.json` com versão, schema e commit;
- usa diretório `.partial` durante a construção e o remove em falha.

### `scripts/verify_rollback_bundle.py`

Verificação independente do bundle.

Revalida:

- hash próprio do manifesto;
- todos os arquivos controlados;
- ausência de arquivos extras;
- banco SQLite;
- `integrity_check`;
- `foreign_key_check`.

Nenhuma restauração deve iniciar se essa validação falhar.

### `scripts/restore_rollback_bundle.py`

Executa somente **ensaio de restauração em diretório novo**.

Não possui modo de sobrescrever uma instalação existente.

O ensaio:

1. verifica o bundle;
2. restaura arquivos e banco para staging;
3. confere novamente tamanho e SHA-256;
4. executa `integrity_check` e `foreign_key_check` no banco restaurado;
5. grava `RESTORE_REHEARSAL.json` com a evidência do ensaio.

## Plano explícito

O bundle exige um plano JSON com versão e lista de arquivos.

Exemplo estrutural:

```json
{
  "version": 1,
  "files": [
    {"path": "app/src/axiom_tools/app.py", "role": "code"},
    {"path": "config/app.ini", "role": "config"}
  ]
}
```

O plano final da instalação real somente será produzido depois da reconciliação do runtime.

Não deve ser criado a partir de suposição sobre a árvore atual reduzida do GitHub.

## Fluxo obrigatório antes da atualização real

1. reconciliar runtime ↔ GitHub;
2. identificar versão/schema/commit atualmente instalados;
3. gerar plano explícito dos arquivos controlados;
4. criar bundle de rollback;
5. verificar bundle independentemente;
6. executar ensaio de restauração em staging;
7. auditar o banco restaurado;
8. somente então autorizar a etapa de atualização;
9. manter o bundle preservado até a homologação física final.

## O que o tooling atual não faz

Ainda não está autorizado a:

- substituir arquivos da instalação oficial;
- parar/iniciar os serviços Windows;
- restaurar sobre `E:\Programas\Axiom_Tools`;
- alterar o banco operacional;
- executar rollback físico do servidor.

Esses pontos dependem da árvore reconciliada, do plano real e de homologação Windows.

## Cobertura automatizada

### `test_rollback_bundle.py`

8 testes aprovados.

### `test_restore_rollback_bundle.py`

6 testes aprovados.

Total da família rollback: **14 testes aprovados**.

## Critério para B41

B41 permanece **não homologado** enquanto faltar:

- plano real da instalação reconciliada;
- bundle criado a partir do runtime real;
- ensaio com a cópia real do banco;
- instalação Windows controlada;
- rollback físico código + banco + configuração;
- smoke após rollback;
- prova de retorno à versão/schema anteriores.

O tooling reduz o risco e torna o teste reproduzível, mas não substitui a execução física final.
