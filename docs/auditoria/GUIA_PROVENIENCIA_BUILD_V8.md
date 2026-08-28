# Guia operacional — Proveniência de build V8

Data: 28/08/2026  
Status: **tooling implementado/testado / integração final com runtime pendente**

## 1. Objetivo

Garantir que qualquer pacote chamado de release V8 possa responder objetivamente:

- qual release é;
- qual schema acompanha a release;
- qual commit originou o payload;
- qual árvore Git foi usada;
- quais arquivos integram o pacote;
- qual SHA-256 corresponde a cada arquivo;
- qual identidade canônica autorizou o build;
- se o payload foi alterado depois da geração.

## 2. Fonte canônica

Arquivo:

`config/release_identity.toml`

Estado atual intencional:

```toml
state = "UNRELEASED"
release_version = ""
schema_version = ""
```

Enquanto estiver assim, **o build final deve falhar**.

Não preencher release/schema apenas para “fazer o script passar”.

A mudança para `READY` só ocorre depois que:

1. runtime estiver reconciliado com GitHub;
2. baseline/suíte original forem conhecidos;
3. schema alvo estiver definido;
4. build estiver efetivamente pronto para homologação.

## 3. Geração do manifesto

Ferramenta:

`scripts/generate_build_provenance.py`

Exemplo de uso quando a identidade estiver `READY`:

```powershell
python scripts\generate_build_provenance.py `
  --repo-root . `
  --payload-root .\dist\Axiom_Tools_V8
```

Saída padrão dentro do payload:

`BUILD_PROVENANCE.json`

O comando oficial **não recebe release/schema pela linha de comando**. Esses valores vêm apenas da identidade canônica.

## 4. O que o gerador exige

- repositório Git válido;
- working tree limpa;
- identidade de release em `READY`;
- release/schema válidos;
- payload não vazio;
- ausência de banco real;
- ausência de certificados/chaves;
- ausência de `.env`/credenciais;
- ausência de possível segredo hardcoded;
- ausência de symlink no payload versionado.

## 5. Conteúdo do `BUILD_PROVENANCE.json`

Inclui, entre outros:

- `produto`;
- `versao_release`;
- `commit_sha`;
- `commit_short`;
- `source_ref`;
- `data_hora_build_utc`;
- `schema_version`;
- `python_target`;
- `plataforma_target`;
- `working_tree_clean`;
- `release_identity_source`;
- `release_identity_sha256`;
- `payload_file_count`;
- `payload_manifest_sha256`;
- lista de arquivos com tamanho + SHA-256;
- `hash_manifesto`.

O manifesto não faz hash de si próprio; `hash_manifesto` cobre o conteúdo lógico do manifesto sem autorreferência.

## 6. Verificação independente

Ferramenta:

`scripts/verify_build_provenance.py`

### Verificar somente o pacote

```powershell
python scripts\verify_build_provenance.py `
  --payload-root .\dist\Axiom_Tools_V8
```

Essa verificação confirma:

- hash do próprio manifesto;
- todos os arquivos declarados;
- tamanho e SHA-256;
- ausência de arquivo extra;
- ausência de arquivo faltante;
- ausência de conteúdo sensível/proibido.

### Verificar pacote + fonte Git

```powershell
python scripts\verify_build_provenance.py `
  --payload-root .\dist\Axiom_Tools_V8 `
  --repo-root .
```

Além do payload, confirma:

- commit atual = commit registrado no build;
- working tree atual limpa;
- identidade canônica existente;
- hash da identidade = hash registrado no build;
- release/schema/Python/plataforma = identidade canônica.

## 7. Comportamentos que bloqueiam o build/verificação

Exemplos:

- `state = UNRELEASED`;
- Git sujo;
- commit fonte diferente;
- arquivo alterado depois do build;
- arquivo extra inserido no payload;
- banco SQLite dentro do pacote versionado;
- certificado/chave privada;
- segredo hardcoded detectado;
- identidade canônica alterada depois da geração;
- edição manual do `BUILD_PROVENANCE.json`;
- caminho duplicado ou inseguro no manifesto.

## 8. Integrações ainda pendentes de B42

O tooling central está implementado/testado, mas B42 só termina quando a árvore operacional reconciliada passar a consumir essa identidade em:

- metadata/versionamento da aplicação;
- `/health`;
- logs de inicialização;
- instalador;
- relatório técnico do pacote;
- backup/rollback;
- tela/footer quando a versão for exibida.

## 9. Regra final

Nenhum ZIP pode ser chamado de `V8 final` sem:

1. identidade canônica `READY`;
2. `BUILD_PROVENANCE.json` gerado;
3. verificação do payload aprovada;
4. verificação contra a fonte Git aprovada;
5. schema compatível;
6. pacote originado da mesma árvore testada.
