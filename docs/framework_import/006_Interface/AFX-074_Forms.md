# AFX-074 — Formulários Oficiais

**Versão:** 2.0 | **Status:** Oficial

## Componentes

Input, textarea, select, checkbox, radio, switch e upload usam label persistente, ajuda opcional, erro inline e associação programática. Altura mínima dos controles: 44 px.

```html
<div class="mb-3">
  <label class="form-label" for="company-name">Razão social</label>
  <input class="form-control" id="company-name" name="company_name" required
         aria-describedby="company-name-help company-name-error">
  <div id="company-name-help" class="form-text">Conforme cadastro oficial.</div>
  <div id="company-name-error" class="invalid-feedback">Informe a razão social.</div>
</div>
```

## Boas práticas

- Um conceito por campo; máscara não substitui validação.
- Obrigatoriedade indicada no label e para tecnologias assistivas.
- Preservar valores após erro; foco vai ao primeiro erro no envio.
- Switch apenas para estado binário com efeito imediato compreensível.
- Upload informa tipos, tamanho, progresso, sucesso e falha.

## Restrições

Não usar placeholder como label, select para sim/não sem motivo, campos desabilitados para dados que precisam ser enviados, nem validação somente por cor.
