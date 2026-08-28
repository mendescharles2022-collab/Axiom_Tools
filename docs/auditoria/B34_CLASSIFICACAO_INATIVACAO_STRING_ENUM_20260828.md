# B34 — Classificação de inativação: contrato Enum/string

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: árvore canônica recuperada e reconciliada em auditoria.

## Falha confirmada

O serviço podia receber `classificacao_inativacao` como string em algumas fronteiras, enquanto o repositório assumia sempre uma instância de `ClassificacaoInativacao` e acessava `.value` diretamente.

Isso permitia `AttributeError` durante persistência e deixava o contrato interno inconsistente.

## Correção

### Serviço

`ClienteService.inativar_cliente()` aceita:

- `ClassificacaoInativacao`;
- string canônica;
- string em caixa diferente, normalizada;
- `None`.

String inválida é rejeitada com `ValueError` antes de qualquer mutação de estado do cliente.

### Repositório

A serialização de `classificacao_inativacao` ficou defensiva:

- Enum → `.value`;
- string válida → normalização + validação;
- vazio/None → `NULL`;
- string inválida → `ValueError`.

O repositório não depende mais cegamente da existência do atributo `.value`.

## Fixture legado corrigido

O teste legado `test_service.py` passava `"teste"` como terceiro argumento posicional de `inativar_cliente`, embora essa posição corresponda a `classificacao`. O fixture foi corrigido para `usuario="teste"`.

Durante a regressão ampla também foi mantida a expectativa canônica da máscara CAEPF `000.000.000/000-00`; um teste legado que esperava 14 dígitos crus havia ficado incompatível com a própria implementação/documentação de máscaras.

## Evidência de regressão

Teste específico versionado:

`runtime_overlay/app/tests/modules/test_inactivation_classification_v8.py`

Cobre:

1. Enum válido;
2. string canônica;
3. string minúscula;
4. string inválida rejeitada antes da mutação;
5. proteção defensiva do repositório.

Resultados na árvore auditada:

- B34 específico: **5/5 PASS**;
- regressão não-web acumulada: **398/398 PASS**;
- failures: 0;
- errors: 0.

## Evidência de código

- patch: `docs/auditoria/patches/B34_CLASSIFICACAO_INATIVACAO_STRING_ENUM.patch`;
- regressão: `runtime_overlay/app/tests/modules/test_inactivation_classification_v8.py`.

## Estado

B34: `CORRIGIDO_TESTADO`.

A homologação Windows/runtime final continua pendente e não é inferida destes testes.
