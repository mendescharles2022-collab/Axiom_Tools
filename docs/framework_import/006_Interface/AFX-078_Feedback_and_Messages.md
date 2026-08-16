# AFX-078 — Feedback, Alertas, Toasts e Modais

**Versão:** 2.0 | **Status:** Oficial

Alertas persistem enquanto exigirem leitura; toasts confirmam eventos breves; erro inline fica junto ao campo; modal interrompe apenas decisões focadas. Success, Warning, Danger e Info usam tokens semânticos e ícone/texto, nunca somente cor.

```html
<div class="alert alert-warning" role="alert"><strong>Atenção:</strong> revise a vigência.</div>
<div class="toast" role="status" aria-live="polite">Alterações salvas.</div>
```

Toasts não levam informações críticas. Modais possuem título, foco inicial, Escape, retorno de foco e ação principal inequívoca. Mensagens dizem o que ocorreu e o que fazer; códigos técnicos ficam em detalhes expansíveis, não no texto principal.
