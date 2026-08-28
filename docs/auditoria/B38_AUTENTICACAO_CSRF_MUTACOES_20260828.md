# B38 — Autenticação, CSRF e auditoria de mutações

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`

## Inventário estático da árvore reconciliada

O scanner AST percorreu os blueprints reais da aplicação e identificou:

- 182 rotas declaradas;
- 125 rotas com método mutável (`POST`, `PUT`, `PATCH` ou `DELETE`);
- 0 rotas mutáveis internas sem `login_required` ou `admin_required`;
- login/logout tratados como fronteira da própria sessão.

Os decorators também foram confrontados diretamente:

- `login_required` exige `session['usuario']`;
- `admin_required` exige sessão e perfil `administrador`, respondendo 403 quando o perfil não autoriza.

## CSRF

A árvore utiliza `CSRFProtect` global:

- `csrf = CSRFProtect()`;
- `csrf.init_app(app)`.

Não foi encontrado `csrf.exempt`/`csrf_exempt` na árvore reconciliada.

A inspeção dos templates encontrou:

- 111 formulários POST;
- 111/111 com token CSRF;
- 0 formulários POST sem token.

O teste foi tornado propositalmente não-vazio: falha se não localizar pelo menos a quantidade de rotas/mutações/formulários observada nesta auditoria.

## Auditoria transversal de mutações

Foi acrescentado um identificador de correlação por requisição (`X-Axiom-Request-ID`) e um `after_request` para registrar toda mutação HTTP.

O evento transversal registra:

- usuário da sessão, por meio da auditoria existente;
- método e rota;
- endpoint;
- status HTTP;
- sucesso/bloqueio;
- request ID;
- nomes dos campos de formulário.

Não são persistidos valores do formulário, evitando captura acidental de senha, token ou conteúdo sensível.

Falha ao registrar a auditoria é enviada ao logger do runtime e não converte uma resposta já válida em novo erro HTTP.

## Evidência de teste

Teste versionado:

`runtime_overlay/app/tests/security/test_route_security_static_v8.py`

Cobertura:

1. inventário real e não-vazio de rotas;
2. autenticação de todas as mutações internas;
3. implementação real dos decorators de sessão/admin;
4. CSRF global sem exemptions;
5. inventário real e não-vazio de formulários POST;
6. token CSRF em todos os formulários POST;
7. auditoria transversal e correlação sem captura de valores.

Resultado específico B38: **5/5 PASS**.

Regressão não-web acumulada após B38/B39: **406/406 PASS**.

## Limitação corretamente preservada

O ambiente Linux desta auditoria não possui Flask/Flask-WTF instalados. Portanto não foi fabricado um ensaio HTTP dinâmico.

O comportamento HTTP/CSRF real deverá ser repetido na homologação Windows sobre o mesmo build empacotado. Essa limitação não altera a evidência estática de que o código reconciliado não possui mutação interna sem autenticação nem exemption de CSRF.

## Estado

B38: `CORRIGIDO_TESTADO` na árvore reconciliada.

Não homologado no Windows.
