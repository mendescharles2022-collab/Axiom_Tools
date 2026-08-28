# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Cobertura atual no repositório

A árvore operacional completa V7/V8 ainda não foi reconciliada, portanto esta pasta ainda não representa a suíte do runtime instalado.

Já existe, porém, cobertura automatizada para a ferramenta de reconciliação:

- `test_audit_runtime_reconciliation.py`
  - classifica arquivos `SAME`, `CHANGED`, `RUNTIME_ONLY` e `REPO_ONLY`;
  - valida o manifesto SHA-256 do export do runtime;
  - detecta adulteração de arquivo após o manifesto;
  - detecta conteúdo proibido como banco SQLite dentro do export.

Executar com Python padrão:

```bash
python -m unittest tests/test_audit_runtime_reconciliation.py -v
```

A suíte foi validada em 28/08/2026 com 3 testes aprovados.

## Cobertura obrigatória após reconciliação do runtime

Quando a árvore operacional for trazida para o repositório, a suíte deverá incorporar os testes existentes do runtime e ampliar cobertura para:

- reprocessamento candidato/versionado;
- promoção/rejeição de candidato;
- Conference GET somente leitura;
- gate único de Impressão/Entregas;
- universo por competência/chamada;
- 2ª chamada e concorrência lógica;
- aplicabilidade DARF/FGTS/DAE;
- multi-Extrato e multi-GFD;
- identidade CPF/CNPJ/CAEPF/matrícula;
- eConsignado contextual e idempotente;
- retificação/versionamento;
- migração e invariantes SQLite;
- autenticação/CSRF/autorização;
- banco ↔ filesystem;
- regressão dos 28 casos de 08/2026.

## Princípio

Nenhum bloqueador V8 muda para `CORRIGIDO_HOMOLOGADO` apenas porque o código foi alterado. A transição exige teste objetivo e evidência no runtime/build correto.
