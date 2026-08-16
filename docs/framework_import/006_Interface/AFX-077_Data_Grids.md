# AFX-077 — Tabelas, Pesquisa, Filtros e Paginação

**Versão:** 2.0 | **Status:** Oficial

## Tabelas e grids

Tabelas são usadas para comparação; cards, para exploração. Cabeçalhos são claros, ordenação é anunciada, ações ficam na última coluna e códigos nunca aparecem sem descrição.

```html
<div class="table-responsive"><table class="table align-middle">
  <thead><tr><th scope="col">Código</th><th scope="col">Descrição</th><th scope="col">Situação</th></tr></thead>
  <tbody>...</tbody>
</table></div>
```

## Pesquisa e filtros

Pesquisa simples aceita código, nome, descrição e sinônimo. Pesquisa avançada aparece sob demanda e mostra filtros ativos removíveis. A ausência de resultados explica como revisar a consulta.

## Paginação

Padrões: 10, 25, 50 e 100 registros; padrão 25. Exibir página atual, total de páginas, total de resultados, anterior/próxima e janela curta de páginas. Filtros e tamanho sobrevivem à navegação.

No celular, preservar comparação essencial com rolagem sinalizada ou transformar cada linha em bloco sem perder rótulos. Na impressão, repetir cabeçalhos e evitar cortar linhas.
