# AFX-073 — Layout Oficial

**Versão:** 2.0 | **Status:** Oficial

## Estrutura

O shell padrão contém sidebar, topbar/navbar, workspace, conteúdo principal e footer. A sidebar representa navegação estrutural; a topbar reúne menu móvel, pesquisa global e ações pessoais. O conteúdo usa `container-fluid`, largura útil máxima de 1600 px e espaçamento externo de 24 px no desktop.

```html
<div class="ax-shell">
  <aside class="ax-sidebar">...</aside>
  <div class="ax-workspace"><header class="ax-topbar">...</header>
    <main id="main-content" class="ax-content">...</main><footer class="ax-footer">...</footer>
  </div>
</div>
```

## Padrões

- Sidebar desktop: 272 px, recolhível para 72 px; móvel em offcanvas.
- Topbar: mínimo 64 px e posição sticky quando não ocultar conteúdo.
- Grid: 12 colunas; gutters de 24 px; cards iguais somente quando comparáveis.
- Dashboard: introdução, KPIs, conteúdo prioritário, atividade/contexto.
- Hero: permitido para orientação e descoberta, nunca antes de uma resposta urgente.
- Impressão remove navegação, ações, sombras e fundos dispensáveis.

## Restrições

Não criar layouts diferentes por sistema, dashboards ornamentais, cards vazios ou scroll horizontal da página. A cor do sistema aparece em ações e acentos, não como tinta derramada no prédio inteiro.
