# Auditoria canônica V8 — Etapa 79

Data: 31/08/2026  
Status: **PRODUTOR + CONSUMIDOR B06 TESTADOS / RUNTIME WINDOWS FÍSICO AINDA NÃO COLETADO / V8 NÃO HOMOLOGADA**

## 1. Lacuna encerrada nesta etapa

Até a Etapa 78 o Axiom Tools já possuía tooling para produzir um handoff seguro da instalação operacional e tooling separado para auditar uma árvore runtime já extraída.

Faltava, porém, a ponte canônica entre essas duas pontas.

Não existia um único fluxo que recebesse o diretório contendo `RUNTIME_HANDOFF_MANIFEST.json`, validasse os artefatos externos, extraísse o ZIP de código com segurança, validasse novamente o manifesto interno, produzisse o diff runtime ↔ repositório e executasse o preflight da cópia SQLite sem alterar a origem.

A Etapa 79 fecha essa lacuna.

## 2. Consumidor canônico Python

Novo arquivo:

`scripts/consume_runtime_reconciliation_handoff.py`

O consumidor:

- valida versão e modo do manifesto externo;
- recalcula o SHA-256 lógico do manifesto;
- exige `source_mutation_performed = false`;
- exige banco fora do ZIP de código;
- exige cópia SQLite separada;
- aceita somente nomes de arquivos simples e seguros dentro do handoff;
- valida SHA-256 do ZIP de código;
- valida SHA-256 e tamanho da cópia SQLite;
- cruza `schema_sha256` e `user_version` do relatório da cópia SQLite com o manifesto externo;
- fotografa todos os arquivos do handoff antes e depois do consumo para provar imutabilidade;
- extrai o ZIP apenas para staging separado;
- rejeita path traversal, caminhos absolutos, backslashes suspeitos, NUL e symlinks;
- limita quantidade de entradas e tamanho total descompactado do ZIP;
- executa novamente as verificações de conteúdo proibido e possíveis segredos;
- valida o manifesto interno `RECONCILIATION_MANIFEST.json`;
- executa a reconciliação runtime ↔ repositório;
- registra `SAME`, `CHANGED`, `RUNTIME_ONLY` e `REPO_ONLY` sem esconder diferenças;
- executa o preflight SQLite na cópia, nunca na origem operacional;
- grava `DATABASE_HOMOLOGATION_PREFLIGHT.json`;
- grava `RUNTIME_HANDOFF_CONSUMPTION.json`;
- mantém explicitamente `v8_homologated = false`.

O diretório de saída:

- não pode existir previamente;
- não pode ficar dentro do handoff;
- não pode ficar dentro do repositório;
- é removido se a execução falhar antes de concluir.

## 3. Regressões do consumidor

`tests/test_consume_runtime_reconciliation_handoff.py` cobre, usando o produtor real `build_runtime_reconciliation_handoff.build_handoff()`:

1. consumo válido sem mutar o handoff;
2. diferença runtime ↔ repo registrada e não escondida;
3. falha de preflight SQLite preservada como falha;
4. ZIP de código adulterado bloqueado antes da extração;
5. SQLite adulterado bloqueado;
6. hash lógico do manifesto adulterado bloqueado;
7. saída dentro do handoff bloqueada;
8. saída existente nunca sobrescrita;
9. path traversal em ZIP bloqueado;
10. symlink em ZIP bloqueado;
11. divergência entre relatório SQLite e manifesto bloqueada.

O ponto importante é que produtor e consumidor não usam formatos paralelos inventados para teste: a suíte cria o handoff pelo produtor canônico e o entrega ao consumidor canônico.

## 4. Consumidor Windows

Novo wrapper:

`scripts/CONSUME_RUNTIME_HANDOFF_V8.ps1`

O comando aceita:

- `HandoffDir`;
- `RepoRoot`;
- `OutputDir`;
- `Invariants` opcional;
- `PythonExe` opcional;
- flags de severidade `FailOnDiff` e `RequireDbOk`.

Proteções:

- `StrictMode`;
- sem drive do servidor hardcoded;
- sem `Remove-Item`, `Move-Item`, `Clear-Content` ou `Set-Content` sobre handoff/repositório;
- saída fora de handoff e repositório;
- sem sobrescrita de staging existente;
- resolução de Python por caminho explícito, `.venv\Scripts\python.exe`, `venv\Scripts\python.exe` ou comandos disponíveis;
- compatibilidade com Windows PowerShell 5.1 sem depender de `$IsWindows`;
- validação do relatório final antes de declarar sucesso do consumidor.

Marcador final do wrapper:

`RUNTIME_HANDOFF_CONSUMER_WINDOWS_OK`

## 5. CI ponta a ponta

O workflow `.github/workflows/reconciliation-tests.yml` passou a executar no mesmo smoke PowerShell:

`runtime descartável -> BUILD_RUNTIME_HANDOFF_V8.ps1 -> manifesto -> CONSUME_RUNTIME_HANDOFF_V8.ps1 -> reconciliação -> preflight SQLite`

Marcadores comprovados no mesmo run:

- `POWERSHELL_B06_SMOKE_OK`;
- `RUNTIME_HANDOFF_CONSUMPTION_OK`;
- `RUNTIME_HANDOFF_CONSUMER_WINDOWS_OK`;
- `POWERSHELL_B06_CONSUMER_SMOKE_OK`.

Também foi comprovado:

- handoff intacto após o consumo;
- preflight SQLite OK na fotografia descartável;
- diferenças runtime/repo são reportadas;
- consumidor nunca marca a V8 como homologada.

## 6. Evidência canônica da Etapa 79

GitHub Actions:

- run: `33452559940`;
- commit auditado: `9939b660d17c68c6848cb8d9cb5e24fffefd38dd`;
- Python: `3.12.14`;
- testes: `514 OK`;
- smoke produtor: `POWERSHELL_B06_SMOKE_OK`;
- smoke consumidor: `POWERSHELL_B06_CONSUMER_SMOKE_OK`;
- mapa causal: `28/28`;
- artifact: `v8-release-preflight#9780276903`;
- SHA-256 do artifact: `511d75258d3f7f28a519708d61407963ef6bf2c0ecf8b74051252464b5432e1f`.

Preflight do mesmo marco:

- bloqueadores homologados: `0/50`;
- casos C PASS: `0/28`;
- evidências externas PASS: `1/10`;
- release READY: `False`;
- build OK: `False`.

## 7. Estado correto do B06

B06 **permanece `BLOQUEADO_POR_RUNTIME`**.

A Etapa 79 não executou o fluxo contra a instalação Windows física do escritório.

Ela elimina, porém, a lacuna técnica entre coleta e análise. O procedimento físico passa a ser claramente dividido:

1. na instalação Windows real, executar o produtor `BUILD_RUNTIME_HANDOFF_V8.ps1` apontando a saída para local externo à árvore operacional;
2. transportar o diretório do handoff sem editar seus arquivos;
3. executar `CONSUME_RUNTIME_HANDOFF_V8.ps1` contra o handoff, o repositório e um staging novo;
4. revisar `RECONCILIATION.jsonl`, o resumo de reconciliação e `DATABASE_HOMOLOGATION_PREFLIGHT.json`;
5. somente depois fixar o baseline operacional e iniciar a integração das correções.

A origem operacional continua fora da área de escrita da auditoria.

## 8. Próxima lacuna

O consumidor produz um diff confiável, mas o diff ainda precisa ser transformado em um **plano revisável de reconciliação**.

A próxima etapa deve classificar `SAME`, `CHANGED`, `RUNTIME_ONLY` e `REPO_ONLY` em ações propostas, sem copiar automaticamente nenhum arquivo e sem permitir que configuração sensível seja promovida por engano.

## 9. Situação

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**

A cadeia de tooling B06 agora possui produtor e consumidor executáveis e testados. Falta a fotografia da instalação Windows física e sua reconciliação real.
