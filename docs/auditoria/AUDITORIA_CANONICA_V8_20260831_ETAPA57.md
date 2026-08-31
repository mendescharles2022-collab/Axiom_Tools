# Auditoria canônica V8 — Etapa 57

Data: 31/08/2026  
Status: **B48 em correção / fluxo não destrutivo preparado e testado / execução real pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 57 avançou o B48 — retenção, limpeza e manutenção — sem criar rotina destrutiva sobre o acervo real.

O objetivo foi transformar o planner antigo, baseado em idade/glob, em uma cadeia controlada:

`Simular → Revisar → Confirmar → Revalidar → [Executar futuramente] → Relatório`

Nesta etapa foram implementados os quatro primeiros estágios.

**Nenhum script desta etapa apaga ou move arquivos.**

## 2. Simular

Script existente ampliado:

`scripts/plan_retention_cleanup.py`

Continua com `mode=DRY_RUN_ONLY`.

Além de raiz lógica, path relativo, idade e tamanho, candidatos agora recebem fingerprint:

- `mtime_ns`;
- SHA-256.

O fingerprint é calculado apenas para itens classificados como candidatos à revisão.

Isso evita autorizar um nome de arquivo de forma abstrata: a cadeia passa a identificar a fotografia física revisada.

## 3. Revisar

Criado:

`scripts/review_retention_plan.py`

A revisão é vinculada ao dry-run por hash canônico.

Cada candidato precisa receber exatamente uma decisão:

- `ELIGIBLE`;
- `KEEP`;
- `BLOCK`.

Categorias seguras atualmente aceitas para elegibilidade:

- `TEMPORARIO_PROCESSAMENTO`;
- `CACHE_RECONSTRUIVEL`;
- `UPLOAD_TRANSITORIO`.

Categorias protegidas não podem ser `ELIGIBLE`:

- `ORIGINAL_DOCUMENTAL`;
- `ARQUIVO_GERENCIADO`;
- `VERSAO_HISTORICA`;
- `SAIDA_FINAL`;
- `BACKUP`.

`ELIGIBLE` exige evidência não vazia.

A revisão preserva:

- regra;
- raiz autorizada;
- path relativo;
- categoria;
- motivo/evidência;
- tamanho;
- idade;
- `mtime_ns`;
- SHA-256.

Saída:

`mode=REVIEWED_NOT_AUTHORIZED`

com `execution_authorized=false`.

## 4. Confirmar

Criado:

`scripts/authorize_retention_manifest.py`

A confirmação:

- precisa apontar para o `review_sha256` exato;
- exige frase canônica `AUTORIZAR_MANIFESTO_SEM_EXECUTAR`;
- registra aprovador e referência;
- recusa referência com traversal/estrutura insegura;
- recusa categoria protegida disfarçada de elegível;
- exige raiz lógica válida;
- exige fingerprint válido.

Saída:

`mode=AUTHORIZED_MANIFEST_NOT_EXECUTED`

com:

`execution_performed=false`.

O manifesto possui seu próprio `manifest_sha256`.

## 5. Falha de CI capturada durante a autorização

Run:

`33439569866`

Conclusão:

`failure`.

A regressão `test_invalid_reference_is_rejected` mostrou que a primeira versão da validação de `reference` aceitava `../segredo`, porque a regex permitia pontos e barras sem rejeitar semanticamente traversal.

A falha foi identificada antes da conclusão do runner e corrigida no commit:

`f54541cf74c844611a04dbf558eba57bae45d182`.

A validação passou a bloquear:

- referência iniciando/terminando com `/`;
- componente `..`;
- `//`.

Run de recuperação:

`33439623526`.

Resultado:

```text
Ran 204 tests in 1.120s
OK
```

## 6. Proveniência da raiz autorizada

Durante a preparação da revalidação foi identificada outra lacuna de desenho: `rule_id + path` não era suficiente para uma futura operação segura.

A cadeia passou a preservar também a chave `root` desde o plano até o manifesto.

Sem raiz autorizada válida, item elegível é recusado.

## 7. Revalidar antes da execução

Criado:

`scripts/revalidate_retention_manifest.py`

O revalidador é somente leitura.

Ele verifica novamente:

- hash do manifesto;
- confirmação canônica;
- raiz fornecida;
- path relativo seguro;
- categoria executável;
- ausência de symlink/junction/reparse point;
- existência do arquivo;
- tipo arquivo;
- tamanho;
- `mtime_ns`;
- SHA-256.

Arquivo trocado depois da revisão é bloqueado mesmo quando mantém o mesmo nome e tamanho.

Saída:

`mode=PREEXECUTION_REVALIDATED_NOT_EXECUTED`

com:

- `ready_for_execution=true/false`;
- `execution_performed=false`;
- findings específicos quando houver mudança.

## 8. Cobertura de testes

A frente B48 passou a cobrir, entre outros cenários:

- dry-run não mutável;
- fingerprint de candidato;
- raiz lógica inválida;
- categoria protegida;
- elegibilidade sem evidência;
- plano adulterado;
- candidato inexistente;
- review adulterado;
- confirmação de outra revisão;
- referência com traversal;
- item elegível sem raiz;
- item sem fingerprint;
- manifesto adulterado;
- arquivo removido depois da autorização;
- arquivo substituído por outro do mesmo tamanho;
- path traversal no manifesto;
- symlink/reparse;
- execução inexistente durante todos esses estágios.

## 9. Marco CI final da etapa

Run:

`33440070146`

Commit:

`0b980637de843fb1fbef61836da4a03b975dff2f`

Python:

`3.12.14`

Resultado:

```text
Ran 215 tests in 0.899s
OK
```

Preflight:

```text
Final OK: False
Bloqueadores homologados: 0/50
Casos PASS: 0/28
Mapa causal: 28/28
Evidências PASS: 1/10
Release READY: False
Build OK: False
```

Artifact:

- `v8-release-preflight`;
- ID `9775877239`;
- SHA-256 `bee98e0797da5549b8d63cc0f2fd092d4cc9bcac031ef3dc07bf8c753a5cf8c4`.

## 10. O que deliberadamente NÃO foi implementado

Não foi criado executor de exclusão física.

Motivo:

B48 exige prova operacional de que cada categoria é realmente transitória/reconstruível e de que o arquivo não sustenta:

- fechamento versionado;
- retificação;
- documento original;
- saída final;
- backup protegido;
- job ativo;
- evidência sem cópia segura.

Essas garantias dependem do runtime/schema/acervo reais e se relacionam com B06, B35 e B49.

Criar um `unlink()` genérico agora seria reintroduzir exatamente o risco que o contrato de retenção pretende eliminar.

## 11. Estado de B48

B48 pode avançar de `INSPECAO_PENDENTE` para `EM_CORRECAO`.

Já existe tooling testado para:

- simulação;
- revisão;
- confirmação documental;
- revalidação física pré-execução.

Pendente:

1. política real de categorias/TTL;
2. integração com estado de job/fechamento/retificação/backups;
3. execução em staging com acervo representativo;
4. executor final controlado;
5. relatório pós-execução;
6. homologação no Windows/acervo real.

## 12. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**

B48 avançou tecnicamente sem reduzir as proteções de acervo e sem qualquer exclusão real.
