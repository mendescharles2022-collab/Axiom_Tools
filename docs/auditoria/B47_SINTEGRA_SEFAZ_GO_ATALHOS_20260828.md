# B47 — Sintegra / SEFAZ GO na ficha do cliente

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## Achado confirmado

`clients_views.py` ainda entregava `sintegra_nacional` e `sintegra_go` ao template, mas `clients/detail.html` não renderizava nenhum dos atalhos. A regressão era visual/funcional da ficha, não ausência dos parâmetros no backend.

## Correção

A área `Dados cadastrais externos` passa a exibir novamente:

- `Consultar SEFAZ GO (Sintegra Goiás)`;
- `Sintegra Nacional`;
- documento do cliente (CPF/CNPJ) usado como contexto da consulta;
- IE GO ativa, quando existente;
- atalho para `Registrar conferência da inscrição`.

O endereço GO foi normalizado para a página pública oficial `https://appasp.sefaz.go.gov.br/Sintegra/Consulta/default.asp`.

## Segurança e governança

O bloco de atalhos não possui formulário POST e não aplica dado externo.

Regras explícitas na interface:

- nenhum dado externo altera o cadastro automaticamente;
- situação cadastral oficial e situação interna do cliente continuam distintas;
- a conferência é registrada no cadastro de inscrições, preservando fonte/status/detalhe;
- links externos usam nova aba com `noopener noreferrer`.

A consulta pública oficial atual aceita CCE, CNPJ ou CPF. Não foi criada uma falsa API estável em cima de parâmetros internos não documentados do portal. A arquitetura V8 mantém a consulta direta automatizada isolável e usa o portal oficial/fluxo assistido quando a integração direta não estiver tecnicamente contratada ou estável.

## Evidência de testes

Teste versionado:

`runtime_overlay/app/tests/modules/test_sintegra_shortcuts_v8.py`

Resultado:

- 6/6 testes específicos PASS;
- template Jinja analisado sem erro;
- atalhos GO/Nacional presentes;
- links externos isolados;
- bloco sem POST/autosave;
- documento e IE GO exibidos como contexto;
- regressão não-web acumulada: 425/425 PASS;
- 0 failures / 0 errors / 0 skips.

## Estado

B47 pode ser classificado como `CORRIGIDO_TESTADO` para a regressão de atalhos e fluxo assistido seguro.

A homologação final deverá confirmar abertura do portal a partir do navegador Windows do escritório. Qualquer futura captura direta deve permanecer em adaptador isolado e nunca sobrescrever cadastro sem comparação/confirmação.
