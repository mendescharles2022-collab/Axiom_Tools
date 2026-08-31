# B49 — Banco ↔ filesystem — inspeção do snapshot

Data: 31/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: `Axiom_Tools(20260828-175237).zip`.

## Metadados auditados

No banco operacional recuperado:

- `processamento_arquivo`: 3.369 registros;
- 3.033 registros possuem `repositorio_caminho`;
- os mesmos 3.033 possuem SHA-256 de 64 caracteres;
- os mesmos 3.033 estão com `arquivamento_status = ARQUIVADO`;
- 0 caminhos de repositório com `..`, raiz absoluta indevida ou traversal detectável;
- 0 caminhos de repositório duplicados;
- 0 caminhos com SHA ausente;
- 0 SHA de repositório sem caminho correspondente.

Há 336 registros sem caminho de repositório:

- 327 `PROCESSADO` sem `arquivamento_status`;
- 7 `REVISAO`;
- 1 `FORA_COMPETENCIA`;
- 1 `PROCESSADO` com `SEM_EMPRESA`.

A maior parte dos 327 legados vem de Entrada Domínio/e-CAC/FGTS Digital e antecede a política atual de arquivamento no repositório processado.

## Limite físico

As raízes reais persistidas em `pasta_origens` são externas ao ZIP, por exemplo:

- `E:\Rotinas Automáticas Dominio\Entrada Axiom\Domínio`;
- `E:\Rotinas Automáticas Dominio\Entrada Axiom\eCAC`;
- `E:\Rotinas Automáticas Dominio\Entrada Axiom\FGTS Digital`;
- `E:\Rotinas Automáticas Dominio\Entrada Axiom\eSocial`;
- `E:\Rotinas Automáticas Dominio\Repositório Axiom\Processados`;
- `E:\Rotinas Automáticas Dominio\Saída Axiom\...`.

Essas raízes físicas não foram incluídas no ZIP canônico. Portanto não é tecnicamente honesto declarar `MISSING=0` ou validar SHA físico sem montar o `E:` do servidor.

## Ferramenta pronta

`scripts/audit_db_filesystem_links.py` já opera somente leitura, valida path traversal, symlink, existência, tamanho e SHA-256 quando a raiz física é fornecida.

## Estado

B49 permanece `INSPECAO_PENDENTE` exclusivamente para a prova física no Windows/servidor.

A camada de metadados do snapshot está coerente; nenhum saneamento automático foi executado.
