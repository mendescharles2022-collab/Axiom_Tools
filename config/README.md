# Configuração

Arquivos de exemplo e definições de configuração controlada do Axiom Tools ficam nesta pasta.

Configurações locais contendo caminhos reais, credenciais ou dados sensíveis não devem ser versionadas. Quando necessário, criar modelos seguros como `*.example` para documentar opções disponíveis.

## Identidade canônica de release

`release_identity.toml` é a fonte canônica da identidade de uma release/build controlada.

Enquanto a V8 não estiver reconciliada e homologável, o arquivo permanece deliberadamente:

```toml
state = "UNRELEASED"
release_version = ""
schema_version = ""
```

Consequência: `scripts/generate_build_provenance.py` deve bloquear a geração de manifesto de build final.

Quando a árvore operacional estiver reconciliada e a release estiver efetivamente pronta, este arquivo será atualizado uma única vez com:

- `state = "READY"`;
- `release_version`;
- `schema_version`;
- `python_target`;
- `platform_target`.

A política de release mantém `require_clean_git = true`.

O objetivo é impedir que versão/schema sejam digitados manualmente em cada etapa do build e acabem divergindo entre código, pacote, instalador e relatório técnico.
