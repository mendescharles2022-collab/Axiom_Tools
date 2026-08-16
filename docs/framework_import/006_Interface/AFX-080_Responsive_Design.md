# AFX-080 — Responsividade e Impressão

**Versão:** 2.0 | **Status:** Oficial

Breakpoints seguem Bootstrap: xs <576, sm ≥576, md ≥768, lg ≥992, xl ≥1200, xxl ≥1400. O projeto é mobile-first.

- Até 767 px: uma coluna, sidebar offcanvas, ações empilhadas, tabelas adaptadas.
- 768–1199 px: conteúdo prioritário em largura total; complementos em até duas colunas.
- ≥1200 px: largura controlada; painéis e textos não são esticados por preencher espaço.
- Ordem visual e semântica coincidem; conteúdo nunca desaparece apenas por falta de largura.

```css
@media print {
  .ax-sidebar,.ax-topbar,.ax-footer,.ax-no-print { display:none!important; }
  .ax-workspace { margin:0!important; }
  .ax-panel,.ax-sheet { box-shadow:none; border-color:#bbb; break-inside:avoid; }
  a[href]::after { content:""; }
}
```

Testes mínimos: 360, 768, 1024 e 1440 px, zoom 200%, orientação, teclado e impressão A4. Nenhuma rolagem horizontal global é aceita.
