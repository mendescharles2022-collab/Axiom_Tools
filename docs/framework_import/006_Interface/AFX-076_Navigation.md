# AFX-076 — Navegação Oficial

**Versão:** 2.0 | **Status:** Oficial

## Componentes

Sidebar, topbar, breadcrumb, tabs, dropdown e paginação formam um único sistema. Sidebar organiza áreas; breadcrumb informa localização; tabs alternam visões equivalentes; dropdown reúne ações relacionadas.

```html
<nav aria-label="Navegação estrutural">
  <ol class="breadcrumb"><li class="breadcrumb-item"><a href="/">Início</a></li>
    <li class="breadcrumb-item active" aria-current="page">Empresas</li></ol>
</nav>
```

O item atual usa `aria-current`. A pesquisa global permanece disponível na topbar desktop e no fluxo móvel. O menu móvel usa offcanvas, prende foco e fecha com Escape. Não misturar ações destrutivas com navegação, não depender só de ícones e não duplicar a mesma árvore em lugares concorrentes.
