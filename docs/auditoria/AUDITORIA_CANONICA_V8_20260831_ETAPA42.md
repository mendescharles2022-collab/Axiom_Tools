# Auditoria canônica V8 — Etapa 42

Data: 31/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Continuação da auditoria canônica a partir da Etapa 41, com foco no gate B06 de reconciliação entre runtime Windows e repositório oficial e na dependência de proveniência B42.

## 2. Estado do `main` confirmado novamente

O branch `main` continua sendo uma fundação reduzida e não contém a árvore operacional integral auditada no pacote canônico.

A árvore versionada em `src/axiom_tools` permanece composta essencialmente por fundações mínimas (`core`, `modules`, `utils` e `__init__.py` dos submódulos), enquanto a implementação operacional completa de processamento, conferência, fechamento, entregas e demais componentes permanece dependente da reconciliação do runtime.

Portanto permanece correta a regra já estabelecida: B01/B02/B03 e demais correções de negócio não devem ser implementadas sobre essa fundação reduzida como se ela fosse o runtime canônico.

## 3. Novo achado — cobertura incompleta do exportador de reconciliação

O protocolo obrigatório `PROTOCOLO_RECONCILIACAO_RUNTIME_REPOSITORIO_V8.md` determina que a captura controlada do runtime considere, entre os artefatos elegíveis para versionamento:

- código-fonte;
- templates e estáticos próprios;
- testes;
- scripts/migrações;
- arquivos de configuração-modelo sem segredos;
- metadata de versão/build;
- documentação técnica aplicável.

Entretanto, `scripts/export_runtime_reconciliation.py` atualmente limita seus candidatos principalmente a:

- `app/src` e `src`;
- testes;
- scripts;
- migrations/alembic;
- templates;
- static;
- `pyproject.toml` e alguns `requirements*.txt`.

Não existe candidato explícito para `config`/`app/config`, nem mecanismo específico para capturar a identidade de release/versionamento quando ela residir fora dos caminhos já listados.

Isso cria risco de um export ser considerado tecnicamente válido, possuir manifesto e passar na auditoria de conteúdo sensível, mas ainda assim estar incompleto para a própria finalidade de B06/B42.

## 4. Lacuna de teste confirmada

`tests/test_export_runtime_reconciliation.py` valida atualmente:

- cópia da whitelist;
- exclusão de banco/documentos;
- layout `app/src` e `src`;
- integridade do manifesto;
- bloqueio de segredo hardcoded;
- proteção de label e caminho de saída;
- ZIP e reparse/symlink.

Não há regressão exigindo exportação de configuração-modelo ou metadata de identidade.

`tests/test_audit_runtime_reconciliation.py` valida manifesto, tamper, traversal, arquivos extras, conteúdo proibido e segredos, mas também não exige comparação de configuração/identidade entre runtime exportado e repositório.

## 5. Relação direta com B42

O repositório possui `config/release_identity.toml` como fonte canônica da identidade de release, atualmente em estado `UNRELEASED` e exigindo `release_version` e `schema_version` antes de um build final.

Logo, a reconciliação precisa ser capaz de detectar se o runtime possui configuração/metadata correspondente, divergente ou ausente. Sem isso, a cadeia runtime → repositório → build → instalador pode permanecer incompleta mesmo após um export aparentemente aprovado.

## 6. Classificação

Este achado:

- **não cria novo bloqueador B51**;
- reforça B06 e B42;
- invalida a afirmação de que o tooling de B06 está integralmente fechado;
- não altera nenhum bloqueador para `CORRIGIDO_TESTADO` ou `CORRIGIDO_HOMOLOGADO`.

## 7. Correção técnica autorizada pela própria auditoria

Antes de usar o exportador contra o runtime Windows, a infraestrutura de reconciliação deve ser ajustada para:

1. capturar configuração-modelo/metadata controlada de forma segura;
2. manter bloqueio de `.env`, credenciais, certificados, tokens e bancos;
3. comparar a área de configuração/identidade com o repositório;
4. adicionar testes de regressão que falhem quando essa cobertura desaparecer;
5. executar novamente a suíte canônica.

## 8. Próximo passo

Corrigir o tooling de B06/B42 no `main`, validar por testes e somente depois utilizar o exportador na instalação Windows real.

A V8 permanece **NÃO HOMOLOGADA** e nenhum pacote final está autorizado nesta etapa.
