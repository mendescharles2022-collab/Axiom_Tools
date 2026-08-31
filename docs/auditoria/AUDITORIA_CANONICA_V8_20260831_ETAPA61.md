# Auditoria canônica V8 — Etapa 61

Data: 31/08/2026  
Status: **B38 em correção / preflight estático de autenticação e autorização implementado e testado / runtime de segurança ainda pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 61 ampliou a auditoria estática de rotas para cobrir não apenas autenticação, mas também contrato explícito de autorização de negócio por rota mutável.

Novo script:

`scripts/build_security_homologation_preflight.py`

O script reutiliza:

`scripts/audit_route_security.py`

## 2. Regra de classificação

Toda rota mutável (`POST`, `PUT`, `PATCH`, `DELETE`) precisa estar classificada em uma política explícita.

Uma rota mutável descoberta no código, mas ausente da política, gera:

`UNCLASSIFIED_MUTATING_ROUTE`

Uma regra de política que não corresponde mais a nenhuma rota também bloqueia o relatório como contrato obsoleto.

## 3. Autenticação x autorização

`login_required` não é tratado como prova automática de autorização de negócio.

Cada regra define os decorators obrigatórios daquela operação.

Exemplo conceitual:

- autenticação: `login_required`;
- autorização administrativa: `admin_required`;
- outros gates de negócio: conforme a rota real exigir.

Se um decorator obrigatório não estiver presente, o preflight registra:

`MISSING_REQUIRED_DECORATOR:<decorator>`

## 4. CSRF

Rotas `csrf.exempt` não passam silenciosamente.

Por padrão, uma rota mutável com isenção CSRF gera:

`CSRF_EXEMPT_NOT_ALLOWED`

A exceção só pode ser aceita quando a regra:

- declara `allow_csrf_exempt=true`;
- contém `csrf_reason` documentado.

## 5. Revisão obrigatória da regra

A política não pode ser gerada mecanicamente e aceita sem análise.

Cada regra precisa conter:

- `reviewed=true`;
- `business_purpose`;
- `reviewer`;
- lista não vazia de `evidence`;
- decorators exigidos;
- justificativa CSRF, quando aplicável.

Regra sem revisão/evidência é rejeitada antes da auditoria.

## 6. Regressões

O B38 recebeu dez testes específicos cobrindo:

1. rota mutável classificada e protegida;
2. rota mutável não classificada;
3. ausência de decorator de autorização de negócio;
4. ausência de marcador de autenticação;
5. `csrf.exempt` não autorizado;
6. exceção CSRF explicitamente documentada;
7. regra obsoleta sem rota correspondente;
8. regra duplicada para o mesmo path/métodos;
9. revisão/evidência obrigatórias;
10. motivo obrigatório para exceção CSRF.

## 7. Marco CI

Run:

`33443352109`

Commit:

`97798a561a646ab70847c96c595a758f18ab23d6`

Python:

`3.12.14`

Resultado:

```text
Ran 245 tests in 1.225s
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

- `v8-release-preflight`;
- ID `9777080392`;
- SHA-256 `8c797da288322944bc350b81c04a8f3bcf1159ebd9b1b4e9bfdd3894b8edd5e4`.

## 8. Impacto sobre B38

B38 pode avançar de `INSPECAO_PENDENTE` para `EM_CORRECAO`.

O tooling agora consegue bloquear estaticamente:

- rota mutável sem autenticação reconhecida;
- rota mutável sem classificação;
- autorização de negócio ausente;
- exceção CSRF não documentada;
- política obsoleta ou duplicada.

Ainda faltam para homologação:

1. árvore operacional integral reconciliada por B06;
2. política real cobrindo 100% das rotas mutáveis do runtime;
3. teste dinâmico de autenticação;
4. teste dinâmico de autorização de negócio;
5. teste de CSRF real;
6. sessão/cookies/configuração real;
7. manipulação de IDs e escopo de objetos;
8. concorrência e transações quando aplicável;
9. evidência no gate `SECURITY_RUNTIME`.

## 9. Limite importante

`static_ok=true` não significa `SECURITY_RUNTIME=PASS`.

O preflight reduz a chance de rota mutável esquecida ou protegida apenas por login, mas a segurança efetiva depende do runtime reconciliado e de testes dinâmicos.

## 10. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
