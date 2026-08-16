# AFX-079 — Acessibilidade

**Versão:** 2.0 | **Status:** Oficial

Meta mínima: WCAG 2.2 nível AA. Contraste de texto normal ≥ 4,5:1; texto grande ≥ 3:1; componentes e foco ≥ 3:1. Toda função opera por teclado, possui nome acessível e ordem de foco coerente.

Obrigatórios: link “Pular para o conteúdo”, landmarks semânticos, `lang="pt-BR"`, foco visível, labels, mensagens associadas, legendas/alternativas, redução de movimento e alvos de toque de ao menos 44×44 px.

```css
:focus-visible { outline: 3px solid var(--ax-focus); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { *,*::before,*::after { scroll-behavior:auto!important; animation:none!important; transition:none!important; } }
```

É proibido comunicar estado só por cor, remover outline sem substituto, criar `div` clicável sem semântica, travar zoom ou ocultar conteúdo essencial de leitor de tela.
