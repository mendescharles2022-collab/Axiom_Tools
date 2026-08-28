# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Cobertura atual no repositório

A árvore operacional completa V7/V8 ainda não foi reconciliada, portanto esta pasta ainda não representa a suíte do runtime instalado.

Já existe, porém, cobertura automatizada para a infraestrutura de reconciliação e proveniência de build.

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

**9 testes automatizados aprovados.**

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

**9 testes automatizados aprovados.**

### `test_reconciliation_pipeline_e2e.py`

Três cenários ponta a ponta foram versionados:

1. `runtime → export ZIP → extração → auditoria` sem divergência;
2. divergência real entre runtime e repositório retorna código específico de diferença;
3. adulteração do pacote após o manifesto é rejeitada antes da comparação.

Esses **3 testes end-to-end estão versionados, mas a execução automática no GitHub Actions ainda não foi comprovada**. O workflow `.github/workflows/reconciliation-tests.yml` existe, porém commits feitos pela integração não produziram run automático no momento da auditoria.

### `test_generate_build_provenance.py`

Cobertura atual:

- commit Git e branch/ref;
- árvore limpa obrigatória no caminho oficial;
- modo interno de diagnóstico para árvore suja;
- bloqueio de banco/arquivo sensível no payload;
- bloqueio de segredo hardcoded;
- hash do payload muda quando conteúdo muda;
- manifesto não faz hash de si próprio;
- payload vazio bloqueado;
- identidade textual inválida bloqueada;
- release `UNRELEASED` bloqueia build final;
- identidade `READY` fornece release/schema/python/plataforma ao build;
- política não pode desligar `require_clean_git`.

**12 testes automatizados aprovados.**

### `test_verify_build_provenance.py`

Cobertura atual:

- build válido passa com payload + fonte Git;
- payload adulterado é rejeitado;
- arquivo extra no payload é rejeitado;
- edição direta do manifesto quebra o hash próprio;
- caminho duplicado em `files` é rejeitado;
- commit fonte divergente é rejeitado;
- identidade canônica alterada depois do build é rejeitada;
- manifesto fora do payload é rejeitado;
- chave JSON duplicada é rejeitada.

**9 testes automatizados aprovados.**

## Contagem atual

- 9 testes do auditor de reconciliação — aprovados;
- 9 testes do exportador — aprovados;
- 12 testes do gerador de proveniência — aprovados;
- 9 testes do verificador de build — aprovados;
- 3 testes end-to-end de reconciliação — versionados, aguardando execução comprovada.

**Total definido: 42 testes.**  
**Total já aprovado nas execuções controladas: 39 testes.**

## Execução

Suíte completa do tooling V8:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Testes isolados:

```bash
python -m unittest tests/test_audit_runtime_reconciliation.py -v
python -m unittest tests/test_export_runtime_reconciliation.py -v
python -m unittest tests/test_reconciliation_pipeline_e2e.py -v
python -m unittest tests/test_generate_build_provenance.py -v
python -m unittest tests/test_verify_build_provenance.py -v
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
