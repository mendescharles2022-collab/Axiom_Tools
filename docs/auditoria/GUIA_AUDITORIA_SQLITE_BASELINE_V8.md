# Guia operacional — Auditoria SQLite baseline V8

Data: 28/08/2026  
Status: **tooling implementado/testado / execução no banco operacional ainda pendente**

## 1. Objetivo

Auditar uma cópia/base SQLite do Axiom Tools sem executar qualquer migração ou correção.

Ferramenta:

`scripts/audit_sqlite_baseline.py`

Ela usa apenas o módulo nativo `sqlite3` do Python e abre o banco em modo somente leitura.

## 2. O que é verificado

### Integridade estrutural

- `PRAGMA integrity_check`;
- `PRAGMA foreign_key_check`;
- `PRAGMA user_version`;
- `PRAGMA application_id`;
- journal mode;
- page size/count/freelist;
- encoding;
- inventário de tabelas, índices, views e triggers;
- definições de foreign keys;
- hash canônico do schema;
- contagem de registros por tabela, salvo quando explicitamente desabilitada.

### O que NÃO é concluído automaticamente

O relatório marca as invariantes lógicas V8 como:

`NOT_EVALUATED`

Isso é intencional.

`integrity_check = ok` e `foreign_key_check` vazio não provam, por exemplo:

- fechamento `FECHADA` com versão válida;
- ausência de duas retificações abertas concorrentes;
- decisão manual corretamente segmentada por fonte;
- vínculo correto cliente/CPF/CAEPF;
- consistência de chamada mensal;
- ausência de órfãos lógicos que não dependem de FK física.

Essas regras serão implementadas quando o schema operacional estiver reconciliado.

## 3. Execução

### Auditoria completa

```powershell
python scripts\audit_sqlite_baseline.py `
  --database "C:\copia\axiom_tools.sqlite3" `
  --output "C:\copia\auditoria_sqlite_v8.json"
```

### Base muito grande

Para evitar `COUNT(*)` em todas as tabelas:

```powershell
python scripts\audit_sqlite_baseline.py `
  --database "C:\copia\axiom_tools.sqlite3" `
  --output "C:\copia\auditoria_sqlite_v8.json" `
  --skip-row-counts
```

## 4. Códigos de saída

- `0` — `integrity_check` e `foreign_key_check` aprovados;
- `2` — banco inválido, ausente ou erro operacional;
- `3` — divergência estrutural/FK detectada.

Código `0` NÃO significa homologação funcional V8; significa apenas que os checks estruturais implementados passaram.

## 5. Segurança

O auditor:

- usa URI SQLite `mode=ro`;
- ativa `PRAGMA query_only=ON` na conexão;
- não executa `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, `DROP` ou migração;
- não grava caminho absoluto do banco no JSON;
- só escreve o arquivo de relatório indicado pelo usuário.

## 6. Testes já aprovados

A suíte `tests/test_audit_sqlite_baseline.py` cobre:

1. banco íntegro;
2. FK quebrada criada com enforcement desligado;
3. prova de que a auditoria não altera os bytes do banco;
4. rejeição de arquivo não-SQLite;
5. auditoria sem contagens;
6. relatório sem caminho absoluto do banco;
7. hash de schema estável em base inalterada.

**7 testes aprovados em execução controlada.**

## 7. Uso na migração V8

A ordem obrigatória quando a cópia real estiver disponível será:

1. auditar baseline pré-migração;
2. preservar relatório e hash de schema;
3. executar migração somente na cópia;
4. auditar novamente;
5. comparar schema, FKs e contagens esperadas;
6. executar invariantes lógicas V8;
7. somente depois considerar atualização do banco real.

## 8. Estado dos bloqueadores

- B35 — FKs/invariantes: tooling estrutural em implementação/teste; invariantes lógicas dependem do runtime reconciliado;
- B05 — migração V8: continua bloqueada até existir schema/cópia operacional reconciliados;
- B41 — rollback: continua dependente do pacote e banco reais de homologação.
