# Auditoria canônica V8 — Etapa 56

Data: 31/08/2026  
Status: **tooling B49 bidirecional implementado/testado / execução real ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 56 atacou a lacuna técnica restante do B49 no repositório.

Antes desta etapa existia apenas auditoria:

`banco → filesystem`

Isso detectava, por exemplo:

- banco apontando para arquivo ausente;
- tamanho divergente;
- SHA-256 divergente;
- caminho inseguro;
- symlink/reparse indevido.

Faltava a direção inversa:

`filesystem → banco`

Essa direção é necessária para identificar arquivo físico existente que nunca entrou no índice/persistência do Tools.

## 2. Novo auditor reverso

Foi criado:

`scripts/audit_filesystem_db_index.py`

Características:

- banco aberto em modo read-only;
- `PRAGMA query_only=ON` herdado da base;
- authorizer bloqueia INSERT/UPDATE/DELETE/DDL/PRAGMA mutável;
- roots precisam ser explicitamente fornecidos;
- glob absoluto/path traversal é recusado;
- caminhos do banco precisam resolver dentro da raiz autorizada;
- junction/symlink/reparse point não é tratado como arquivo gerenciado normal;
- saída usa caminhos relativos e não precisa expor raiz física real.

Achado principal:

`UNINDEXED_FILE`

Significado:

> o arquivo existe fisicamente na raiz gerenciada, mas não foi retornado pela consulta SQL que representa o índice do banco.

Isso é evidência técnica; não aciona exclusão, movimentação ou vínculo automático.

## 3. Regressões do auditor reverso

Foram adicionados sete testes cobrindo:

1. arquivo indexado passa;
2. arquivo não indexado é detectado;
3. subpasta relativa é reconciliada corretamente;
4. path inseguro vindo do banco é sinalizado;
5. glob com traversal é rejeitado;
6. tentativa de SQL de escrita é bloqueada e o banco permanece inalterado;
7. SHA-256 pode ser calculado opcionalmente para arquivo não indexado.

## 4. CI intermediário

Run:

`33438950270`

Commit:

`31cc3d18654c699e77d8fbbe1117fd695997f51b`

Resultado:

```text
Ran 185 tests in 1.104s
OK
```

Preflight permaneceu corretamente bloqueado em:

- 0/50 B homologados;
- 0/28 C PASS;
- mapa causal 28/28;
- 1/10 evidências PASS.

## 5. Executor bidirecional único

Depois do auditor reverso, foi criado:

`scripts/audit_db_filesystem_bidirectional.py`

O executor reúne numa única operação:

- `database_to_filesystem`;
- `filesystem_to_database`.

O relatório separa:

- achados banco → filesystem;
- achados filesystem → banco;
- erros SQL;
- quantidade total de achados.

Nenhuma das duas direções escreve no banco.

## 6. Regressões do executor bidirecional

Foram adicionados quatro testes:

1. banco/acervo coerentes passam;
2. arquivo ausente e arquivo não indexado são distinguidos no mesmo relatório;
3. execução não altera o SQLite;
4. SQL mutável na direção reversa é recusado.

## 7. Marco CI da etapa

Run:

`33439050816`

Commit:

`54fa9c798fc0e5edd633d7e337b5e03143a05019`

Python:

`3.12.14`

Resultado:

```text
Ran 189 tests in 1.052s
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

- nome: `v8-release-preflight`;
- ID: `9775507384`;
- SHA-256: `e812bfce93067067c97c189583dbf2d693e8bd03be88251c6ed6165d74bd2bf9`.

## 8. Impacto sobre B49

A lacuna de tooling genérico bidirecional está fechada no repositório.

B49 continua `BLOQUEADO_POR_RUNTIME`, porque ainda faltam:

1. schema real para definir consultas de índice;
2. roots reais do acervo;
3. execução contra cópia real do banco e acervo;
4. classificação das ocorrências encontradas;
5. integração futura com ocorrência técnica automática sem alterar/acoplar arquivo silenciosamente.

## 9. Casos reais beneficiados

O B49 é especialmente relevante para regressões em que o documento existe fisicamente, mas a Conferência não o encontra, incluindo os cenários de descoberta/vínculo representados na matriz C01–C28.

O auditor não conclui a causa de negócio; ele localiza precisamente a quebra entre persistência e acervo.

## 10. Estado

**B49: tooling implementado/testado, execução real pendente.**

**V8: NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
