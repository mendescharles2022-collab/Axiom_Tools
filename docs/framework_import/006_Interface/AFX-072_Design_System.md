# AFX-072 — Design System Oficial do Ecossistema Axiom

**Versão:** 2.0  
**Status:** Oficial e normativo  
**Consolidação:** ADS-100, 12/08/2026

## Autoridade

Este documento, em conjunto com AFX-071 a AFX-080, é a única fonte oficial de identidade visual, UX, UI e componentes do Ecossistema Axiom. Sistemas consumidores não podem manter documentação visual superior, paralela ou divergente. O Axiom Tables foi fonte técnica temporária nesta consolidação; após a absorção, deixa de ser referência normativa.

## Princípios

1. Uma experiência, vários produtos.
2. A resposta procurada vem antes dos metadados.
3. Componentes existem uma vez no Framework e são consumidos pelos sistemas.
4. A individualidade limita-se a nome, logotipo, cor predominante, ícone e conteúdo funcional.
5. Tema claro, escuro, responsividade, impressão e acessibilidade pertencem ao mesmo contrato.
6. Bootstrap 5.3 é a fundação de interface; customizações usam tokens, não sobrescritas casuais.
7. Cor nunca é o único meio de transmitir estado.

## Tokens oficiais

```css
:root {
  --ax-font-sans: Inter, "Segoe UI", Roboto, Arial, sans-serif;
  --ax-font-mono: "Cascadia Code", Consolas, monospace;
  --ax-space-1: .25rem; --ax-space-2: .5rem; --ax-space-3: .75rem;
  --ax-space-4: 1rem; --ax-space-5: 1.5rem; --ax-space-6: 2rem;
  --ax-radius-sm: .375rem; --ax-radius-md: .625rem; --ax-radius-lg: 1rem;
  --ax-shadow-sm: 0 1px 2px rgb(15 23 42 / .08);
  --ax-shadow-md: 0 10px 30px rgb(15 23 42 / .12);
  --ax-bg: #f6f8fb; --ax-surface: #ffffff; --ax-surface-2: #f0f3f7;
  --ax-border: #d8dee8; --ax-text: #172033; --ax-text-muted: #667085;
  --ax-success: #198754; --ax-warning: #b7791f; --ax-danger: #c53030;
  --ax-info: #0b7285; --ax-focus: #7c3aed;
  --ax-primary: var(--ax-system-primary, #334155);
  --ax-primary-hover: color-mix(in srgb, var(--ax-primary), #000 14%);
  --ax-disabled-bg: #e9edf3; --ax-disabled-text: #98a2b3;
}
[data-theme="dark"] {
  --ax-bg: #0c111b; --ax-surface: #151c28; --ax-surface-2: #1d2635;
  --ax-border: #344054; --ax-text: #f2f4f7; --ax-text-muted: #a8b2c1;
  --ax-shadow-sm: 0 1px 2px rgb(0 0 0 / .35);
  --ax-shadow-md: 0 14px 34px rgb(0 0 0 / .38);
}
```

### Tipografia

- Corpo: 16 px, altura de linha mínima 1,5.
- Texto auxiliar: 14 px; nenhum texto funcional abaixo de 12 px.
- H1: `clamp(1.75rem, 3vw, 2.5rem)`; H2: 1,5 rem; H3: 1,25 rem.
- Peso 600 para títulos e ações; 400 para leitura; 700 apenas para números ou ênfase curta.
- Códigos técnicos usam fonte monoespaçada quando isso melhora a distinção.

## Identidade cromática dos sistemas

As cores abaixo são **provisórias**, salvo homologação posterior registrada no Framework. Até lá, podem ser usadas como `--ax-system-primary`, preservando todos os tokens semânticos.

| Sistema | Cor predominante | HEX | RGB | HSL | Situação |
| --- | --- | --- | --- | --- | --- |
| Enterprise | Verde esmeralda | `#0F8A5F` | 15, 138, 95 | 159°, 80%, 30% | Provisória |
| Tables | Azul cobalto | `#2457C5` | 36, 87, 197 | 221°, 69%, 46% | Provisória |
| Registry | Laranja | `#D96C16` | 217, 108, 22 | 26°, 82%, 47% | Provisória |
| Company | Dourado | `#B88716` | 184, 135, 22 | 42°, 79%, 40% | Provisória |
| Certificates | Vermelho rubi | `#B32645` | 179, 38, 69 | 347°, 65%, 43% | Provisória |
| Convention | Roxo | `#6F42C1` | 111, 66, 193 | 261°, 50%, 51% | Provisória |
| Time | Azul ciano | `#0787A5` | 7, 135, 165 | 191°, 92%, 34% | Provisória |
| Extractor | Roxo escuro | `#4C2A85` | 76, 42, 133 | 262°, 52%, 34% | Provisória |
| Contacts | Turquesa | `#078C85` | 7, 140, 133 | 177°, 90%, 29% | Provisória |
| Payroll | Verde oliva | `#667A1E` | 102, 122, 30 | 73°, 61%, 30% | Provisória |
| Manage | Bordô | `#7A2948` | 122, 41, 72 | 337°, 50%, 32% | Provisória |
| Medicine | Vermelho médico | `#C43D3D` | 196, 61, 61 | 0°, 54%, 50% | Provisória |
| Nexus | Grafite | `#3F4652` | 63, 70, 82 | 218°, 13%, 28% | Provisória |

Novos sistemas herdam grafite como fallback e não recebem cor definitiva sem homologação. Tons Light, Dark e Accent são derivados em 12%, 18% e 24% por mistura perceptual; não se substituem Success, Warning, Danger e Info pela cor do produto.

## Biblioteca oficial de componentes

| Família | Componentes oficiais |
| --- | --- |
| Estrutura | app shell, container, grid, sidebar, navbar/topbar, footer, breadcrumb |
| Conteúdo | hero, page intro, cards, KPIs, widgets, painéis, Fichas Técnicas, timeline |
| Dados | tabela, data grid, busca, busca avançada, filtros, paginação, estado vazio |
| Formulários | label, input, textarea, select, checkbox, radio, switch, upload |
| Ações | botão primário, secundário, contorno, textual, ícone, download |
| Estado | badge, alerta, toast, modal, progresso, skeleton, erro inline |
| Utilidade | tooltip, popover, avatar, dropdown, tabs, accordion |

Cada componente deve possuir descrição, objetivo, exemplo, código de uso, boas práticas e restrições no documento especializado correspondente. Componentes ausentes exigem evolução do Framework antes de implementação local.

## Fichas Técnicas

O Framework incorpora a gramática da Biblioteca ATB-600 sem incorporar conteúdo específico do Tables:

1. Identidade: título e código/competência quando aplicável.
2. Resumo: até três linhas.
3. Resposta principal: primeiro bloco técnico, visível sem abas ou modal.
4. Contexto: aplicação, relações, exceções e observações úteis.
5. Autoridade: fonte, vigência, fundamento e histórico.

Campos vazios, IDs internos, hashes e metadados administrativos não são apresentados. Um produto pode definir tipos de ficha próprios, mas deverá registrá-los no Framework antes de desenvolver a tela.

```html
<article class="ax-sheet" aria-labelledby="sheet-title">
  <header class="ax-sheet__header">
    <p class="ax-eyebrow">Ficha Técnica</p>
    <h1 id="sheet-title">Código — título</h1>
    <p class="ax-summary">Resumo objetivo.</p>
  </header>
  <section class="ax-sheet__answer" aria-label="Resposta principal">...</section>
  <section class="ax-sheet__context">...</section>
  <footer class="ax-sheet__authority">Fonte e vigência</footer>
</article>
```

## Estados obrigatórios

- Hover: reforça interatividade sem deslocar conteúdo.
- Focus: anel de 3 px com `--ax-focus` e afastamento de 2 px.
- Active: reduz contraste/luminosidade em relação ao hover.
- Disabled: aparência e semântica desabilitadas; não usar apenas opacidade.
- Loading: preservar dimensões, anunciar carregamento e impedir duplo envio.
- Empty: explicar ausência e oferecer próxima ação quando existir.
- Error: mensagem próxima à origem, linguagem acionável e preservação dos dados digitados.

## Branding e ativos

Cada produto mantém somente seus ativos de identidade: logo horizontal, vertical/compacto, claro, escuro, monocromático, ícone, favicon e apple-touch-icon. Arquivos compartilhados pertencem ao Framework. O slogan oficial é: **“Axiom — Tecnologia com propósito. Inteligência em movimento.”**

A tela de login usa imagem em tela inteira e painel legível, responsivo e acessível. Categorias temáticas de wallpapers não fazem parte do contrato; cada produto aponta para sua pasta oficial de backgrounds. Glassmorphism só é permitido quando contraste e legibilidade forem comprovados.

## Restrições

- Proibido duplicar componente, CSS ou template oficial em repositório consumidor.
- Proibido usar o Tables como fonte normativa após a ADS-100.
- Proibido criar identidade visual própria além dos cinco elementos autorizados.
- Proibido esconder informação essencial em hover, tooltip, modal ou aba secundária.
- Proibido mostrar seções vazias, conteúdo repetido ou cards decorativos.

## Histórico

| Versão | Data | Alteração |
| --- | --- | --- |
| 1.0 | 06/08/2026 | Documento inicial. |
| 2.0 | 12/08/2026 | ADS-100: consolidação integral, tokens, paleta, biblioteca e absorção técnica do Tables. |
