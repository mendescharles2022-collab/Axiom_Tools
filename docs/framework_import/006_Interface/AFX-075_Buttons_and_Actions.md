# AFX-075 — Botões e Ações

**Versão:** 2.0 | **Status:** Oficial

## Hierarquia

- Primário: ação principal do contexto (`btn-primary`).
- Secundário: ação relevante concorrente (`btn-outline-secondary`).
- Textual: navegação ou ação de baixa ênfase (`btn-link`).
- Perigo: ação destrutiva (`btn-danger`), sempre textual e confirmada quando irreversível.
- Ícone: apenas com nome acessível e tooltip complementar.

```html
<div class="d-flex gap-2 justify-content-end">
  <a class="btn btn-outline-secondary" href="./">Cancelar</a>
  <button class="btn btn-primary" type="submit">Salvar empresa</button>
</div>
```

Estados hover, focus, active, loading e disabled são obrigatórios. O rótulo começa com verbo e explica o efeito. Não usar “OK”, duas ações primárias no mesmo bloco, ícone ambíguo sem texto acessível ou botão desabilitado sem explicação.
