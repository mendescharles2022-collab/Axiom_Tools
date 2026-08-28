# Guia V8 — Auditoria de segurança das rotas

Data: 28/08/2026
Status: **tooling estático preparado / validação dinâmica do runtime ainda pendente**

## Objetivo

Criar inventário reproduzível das rotas web da árvore operacional reconciliada e localizar sinais que merecem revisão antes da homologação.

## Ferramenta

`scripts/audit_route_security.py`

A ferramenta analisa Python via AST e inventaria funções com decorators de rota Flask.

Ela registra:

- arquivo e linha;
- função;
- caminho da rota quando literal;
- métodos HTTP;
- decorators presentes;
- markers de autenticação configurados;
- presença de marker `csrf.exempt` configurado;
- classificação de rota mutante.

## Política

Exemplo seguro versionado:

`config/route_security_policy.example.json`

A política é configurável porque a árvore operacional pode usar decorators diferentes de uma versão para outra.

Não se deve concluir que uma rota está desprotegida apenas porque não usa exatamente `login_required`.

## Achados estáticos

A ferramenta marca para revisão:

- rota mutante sem marker de autenticação reconhecido pela política;
- rota marcada como exceção de CSRF;
- erro de parse em arquivo Python.

Esses achados são **sinais de inspeção**, não sentença automática.

## Limite importante

A análise estática NÃO comprova:

- proteção global de autenticação;
- Flask-WTF/CSRFProtect configurado globalmente;
- wrappers/decorators criados dinamicamente;
- autorização por perfil/permissão;
- validação de escopo do cliente/competência;
- transação/rollback da mutação;
- proteção contra escrita obsoleta;
- comportamento real de sessão/cookies.

Esses pontos continuam exigindo teste dinâmico no runtime reconciliado.

## Execução futura

Exemplo:

```powershell
.venv\Scripts\python.exe scripts\audit_route_security.py `
  --root app\src `
  --policy config\route_security_policy.json `
  --output temp\ROUTE_SECURITY_AUDIT.json
```

A política real só deve ser criada depois de inspecionar os decorators efetivamente utilizados pelo runtime.

## Regressão dinâmica obrigatória para B38

Depois da reconciliação:

1. inventariar todas as rotas mutantes;
2. confirmar proteção de autenticação;
3. confirmar autorização de perfil/permissão;
4. confirmar CSRF nas mutações browser-based;
5. testar usuário anônimo;
6. testar usuário autenticado sem permissão;
7. testar request sem token CSRF quando aplicável;
8. testar escopo inválido de cliente/competência;
9. confirmar transação/rollback em falha;
10. confirmar ausência de mutação parcial;
11. confirmar log/auditoria da ação.

## Estado de B38

B38 permanece **INSPECAO_PENDENTE**.

O tooling estático está implementado e coberto por 8 testes, mas nenhuma rota V8 operacional foi homologada por essa ferramenta enquanto a árvore completa do runtime não estiver reconciliada.
