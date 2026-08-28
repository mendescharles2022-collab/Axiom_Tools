# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Cobertura atual no repositório

A árvore operacional completa V7/V8 ainda não foi reconciliada, portanto esta pasta ainda não representa a suíte do runtime instalado.

Já existe, porém, cobertura automatizada para a infraestrutura de reconciliação.

### `test_audit_runtime_reconciliation.py`

Cobertura atual:

- classifica `SAME`, `CHANGED`, `RUNTIME_ONLY` e `REPO_ONLY`;
- valida o manifesto SHA-256;
- detecta adulteração após geração do manifesto;
- rejeita `../`/saída da raiz;
- detecta arquivo extra fora do manifesto;
- detecta caminho duplicado no manifesto;
- detecta banco/arquivo sensível no export;
- detecta segredo embutido em arquivo textual;
- aceita placeholder explicitamente falso de teste.

**9 testes automatizados aprovados** na revisão local da auditoria.

### `test_export_runtime_reconciliation.py`

Cobertura atual:

- whitelist de código/testes/configuração controlada;
- exclusão de banco e documentos;
- manifesto cobrindo exatamente o payload;
- bloqueio de segredo hardcoded;
- label inseguro;
- conteúdo do ZIP;
- symlink/reparse point;
- suporte a `src/` na raiz além de `app/src`;
- bloqueio de diretório de saída dentro da própria árvore exportada.

**9 testes automatizados aprovados** na revisão local da auditoria.

### `test_reconciliation_pipeline_e2e.py`

Três cenários ponta a ponta foram versionados:

1. `runtime → export ZIP → extração → auditoria` sem divergência;
2. divergência real entre runtime e repositório retorna código específico de diferença;
3. adulteração do pacote após o manifesto é rejeitada antes da comparação.

Esses **3 testes end-to-end estão versionados, mas a execução automática no GitHub Actions ainda não foi comprovada**. O workflow `.github/workflows/reconciliation-tests.yml` existe, porém commits feitos pela integração não produziram run automático no momento da auditoria.

## Contagem atual

- 18 testes da infraestrutura já aprovados nas revisões executadas;
- 3 testes end-to-end adicionais versionados e aguardando execução comprovada;
- total atual definido: **21 testes de reconciliação**.

## Execução

Suíte de reconciliação:

```bash
python -m unittest discover -s tests -p "test_*reconciliation*.py" -v
```

Testes isolados:

```bash
python -m unittest tests/test_audit_runtime_reconciliation.py -v
python -m unittest tests/test_export_runtime_reconciliation.py -v
python -m unittest tests/test_reconciliation_pipeline_e2e.py -v
```

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
