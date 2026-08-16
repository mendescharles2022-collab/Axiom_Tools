# AFX-033 — Arquitetura Oficial de Temas

**Versão:** 2.0 | **Status:** Oficial

Os únicos modos globais são claro, escuro e automático. “Temas” por categoria de imagem ou por produto são proibidos. A identidade do produto entra por `--ax-system-primary`; tokens semânticos permanecem compartilhados.

```html
<html lang="pt-BR" data-theme="auto" data-system="tables">
```

O modo automático segue `prefers-color-scheme`; escolha explícita do usuário prevalece e é persistida. Componentes consomem apenas tokens `--ax-*`. Logos usam variantes clara/escura adequadas ao fundo. Contraste WCAG AA é obrigatório em todas as combinações.

Wallpapers de login são conteúdo de branding do produto, não temas. Sua troca não pode alterar layout, paleta funcional ou componentes.
