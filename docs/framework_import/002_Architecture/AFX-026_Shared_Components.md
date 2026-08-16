# AFX-026 — Arquitetura de Componentes Compartilhados

**Versão:** 2.0 | **Status:** Oficial

Todo componente visual existe uma vez no Framework e é distribuído como pacote versionado. Sistemas consumidores importam templates, CSS, JavaScript, ícones e tokens; não copiam nem bifurcam arquivos.

## Camadas

1. Tokens: cor, tipografia, espaço, raio, sombra e movimento.
2. Primitivos: botão, campo, badge, ícone e superfície.
3. Compostos: card, modal, tabela, paginação, busca e alertas.
4. Padrões: shell, dashboard, fluxo de formulário e Ficha Técnica.
5. Identidade: logo, nome, ícone e `--ax-system-primary` fornecidos pelo produto.

O pacote segue versionamento semântico. Correções compatíveis são patch; novos componentes, minor; quebra de contrato, major e migração documentada. É proibida customização local que altere comportamento compartilhado.
