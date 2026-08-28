# Testes

Testes automatizados do Axiom Tools ficam nesta pasta.

## Cobertura atual no repositório

A árvore operacional completa V7/V8 ainda não foi reconciliada, portanto esta pasta ainda não representa a suíte do runtime instalado.

Já existe, porém, cobertura automatizada para a infraestrutura de reconciliação, proveniência de build e auditoria estrutural SQLite.

### `test_audit_runtime_reconciliation.py`

**9 testes aprovados.**

Cobre classificação `SAME/CHANGED/RUNTIME_ONLY/REPO_ONLY`, manifesto SHA-256, adulteração, tentativa de `../`, arquivo extra, caminho duplicado, conteúdo sensível e segredo embutido.

### `test_export_runtime_reconciliation.py`

**9 testes aprovados.**

Cobre whitelist, exclusão de banco/documentos, manifesto, ZIP, segredo hardcoded, label, symlink/reparse point, layouts `app/src`/`src` e saída recursiva.

### `test_reconciliation_pipeline_e2e.py`

**3 testes versionados, aguardando execução comprovada.**

Cenários:

1. exportação + ZIP + auditoria sem divergência;
2. divergência runtime × repositório;
3. adulteração posterior ao manifesto.

### `test_generate_build_provenance.py`

**12 testes aprovados.**

Cobre Git limpo, commit/ref, identidade canônica `READY/UNRELEASED`, release/schema, payload sensível, segredo hardcoded, hashes e políticas de release.

### `test_verify_build_provenance.py`

**9 testes aprovados.**

Cobre verificação de payload, arquivos extras/alterados, hash do manifesto, commit fonte, identidade canônica, caminhos/JSON duplicados.

### `test_audit_sqlite_baseline.py`

**7 testes aprovados.**

Cobre:

- banco estruturalmente íntegro;
- FK quebrada detectada mesmo quando criada com enforcement desligado;
- auditoria sem mutação dos bytes do banco;
- rejeição de arquivo não-SQLite;
- opção sem `COUNT(*)` por tabela;
- relatório sem caminho absoluto da base;
- hash de schema estável em base inalterada.

## Contagem atual

- auditor de reconciliação: 9 aprovados;
- exportador do runtime: 9 aprovados;
- gerador de proveniência: 12 aprovados;
- verificador do build: 9 aprovados;
- auditor SQLite baseline: 7 aprovados;
- pipeline E2E de reconciliação: 3 versionados, execução ainda não comprovada.

**Total definido: 49 testes.**  
**Total aprovado nas execuções controladas: 46 testes.**

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
python -m unittest tests/test_audit_sqlite_baseline.py -v
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
- migração e invariantes lógicas SQLite;
- autenticação/CSRF/autorização;
- banco ↔ filesystem;
- regressão dos 28 casos de 08/2026.

## Princípio

Nenhum bloqueador V8 muda para `CORRIGIDO_HOMOLOGADO` apenas porque o código foi alterado. A transição exige teste objetivo e evidência no runtime/build correto.
