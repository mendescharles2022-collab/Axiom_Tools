# AFX-071 — Padrões Oficiais de Interface

**Versão:** 2.0 | **Status:** Oficial | **ADS-100:** 12/08/2026

## Contrato

Toda interface Axiom usa Bootstrap 5.3, tokens AFX-072 e componentes do Framework. A tela deve responder à tarefa principal antes de apresentar contexto administrativo.

## Regras gerais

- Idioma padrão: pt-BR; siglas técnicas preservadas.
- Largura de leitura controlada; grid Bootstrap de 12 colunas.
- Hierarquia: identidade, ação principal, conteúdo, contexto, autoridade.
- Uma ação primária por contexto; ações destrutivas isoladas e confirmadas.
- Estados loading, vazio, erro, sucesso, desabilitado e sem permissão são obrigatórios.
- Tema, responsividade, impressão e teclado são requisitos de aceite, não complementos.

## Exemplo

```html
<main class="container-fluid ax-page">
  <header class="ax-page-intro"><h1>Empresas</h1><p>Gerencie os cadastros.</p></header>
  <section class="ax-panel">...</section>
</main>
```

## Boas práticas e restrições

Use texto claro, rótulos visíveis e feedback próximo à ação. Não exponha IDs, hashes, nomes de tabelas, campos vazios ou metadados internos. Não invente um componente quando houver equivalente oficial.

## Histórico

| Versão | Data | Alteração |
| --- | --- | --- |
| 1.0 | 06/08/2026 | Inicial. |
| 2.0 | 12/08/2026 | Consolidação ADS-100. |
