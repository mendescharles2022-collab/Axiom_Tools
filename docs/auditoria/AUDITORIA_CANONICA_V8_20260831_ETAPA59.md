# Auditoria canônica V8 — Etapa 59

Data: 31/08/2026  
Status: **B41 em correção / readiness de rollback implementada e testada / rollback físico Windows pendente / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 59 consolidou os componentes de rollback já existentes em um único gate de prontidão, sem sobrescrever instalação real.

Novo script:

`scripts/build_rollback_readiness_preflight.py`

Fluxo do ensaio:

`inventariar origem → criar bundle → verificar bundle → restaurar em staging → auditar banco restaurado via B35 → provar origem inalterada`

## 2. Cobertura mínima obrigatória

O plano de rollback precisa conter pelo menos os papéis:

- `code`;
- `config`.

O SQLite é incluído obrigatoriamente pelo bundle.

Plano que cobre apenas código é rejeitado antes do ensaio.

Isso corrige uma fraqueza observada no instalador V8F2, cujo backup prático estava limitado aos arquivos alterados e não representava o conjunto completo código + configuração + banco.

## 3. Fotografia da origem

Antes e depois do ensaio são registrados, para cada arquivo planejado:

- path relativo;
- role;
- tamanho;
- `mtime_ns`;
- SHA-256.

Também é registrada a fotografia do SQLite.

`ready_for_windows_rehearsal` só pode ficar verdadeiro se a origem permanecer idêntica durante a operação.

## 4. Bundle

O preflight reutiliza:

`scripts/create_rollback_bundle.py`

O bundle contém:

- arquivos de código/configuração previstos no plano;
- cópia SQLite consistente obtida pela API de backup do sqlite3;
- versão da aplicação;
- versão de schema;
- commit de origem;
- hashes individuais;
- hash próprio do manifesto.

## 5. Verificação

O bundle é validado por:

`scripts/verify_rollback_bundle.py`

A verificação confirma:

- manifesto íntegro;
- ausência de extras/faltantes;
- hashes/tamanhos dos arquivos;
- hash/tamanho do banco;
- `integrity_check`;
- `foreign_key_check`.

## 6. Ensaio de restauração

O preflight chama:

`scripts/restore_rollback_bundle.py`

A restauração ocorre exclusivamente em um diretório de staging novo.

Não há overwrite da instalação.

Depois da cópia, todos os hashes são conferidos novamente e o SQLite restaurado passa por `integrity_check` e `foreign_key_check`.

## 7. Integração com B35

O SQLite restaurado é submetido ao:

`scripts/build_database_homologation_preflight.py`

Assim, o rollback não é considerado pronto apenas porque o arquivo SQLite foi copiado corretamente.

As invariantes lógicas confirmadas também precisam permanecer válidas no banco restaurado.

Um bundle tecnicamente íntegro, mas contendo estado lógico inválido, não recebe `ready_for_windows_rehearsal=true`.

## 8. Proteções

- diretório de trabalho existente não é sobrescrito;
- staging parcial é removido em falha;
- arquivo ausente no plano bloqueia antes da criação do bundle;
- origem é comparada antes/depois;
- banco original não é substituído;
- restauração ocorre somente em staging;
- não para/inicia serviços;
- não altera portas;
- não executa rollback físico Windows.

## 9. Regressões adicionadas

Foram adicionados seis testes cobrindo:

1. bundle + verificação + restore + B35 válidos;
2. plano sem configuração recusado;
3. banco restaurado logicamente inválido bloqueando readiness;
4. work-dir existente nunca sobrescrito;
5. arquivos e banco de origem permanecem inalterados;
6. arquivo de origem ausente aborta e limpa staging parcial.

## 10. Marco CI

Run:

`33440693101`

Commit:

`9b593623c78ef2f5d636fde42ce03cc5a8c094bf`

Python:

`3.12.14`

Resultado:

```text
Ran 228 tests in 3.134s
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
- ID `9776107830`;
- SHA-256 `07f86f83627bcc0ecce17a4ed9ed7a7ccf9d92489408bf50fc6feecb06c88d43`.

## 11. Impacto sobre B41

B41 permanece `EM_CORRECAO`.

A prontidão genérica em staging agora prova:

- cobertura mínima código + configuração + banco;
- bundle verificável;
- restauração reproduzível;
- banco restaurado estrutural e logicamente auditável;
- origem intacta.

Ainda faltam para homologação:

1. plano real completo da instalação;
2. identidade instalada real;
3. serviços/processos/locks Windows;
4. ensaio com paths/configuração reais;
5. rollback físico da instalação e banco como conjunto coerente;
6. smoke pós-rollback;
7. evidência no gate `ROLLBACK_WINDOWS`.

## 12. Limite importante

`ready_for_windows_rehearsal=true` não significa `ROLLBACK_WINDOWS=PASS`.

A etapa comprova que o material necessário é recuperável em staging; ainda não comprova troca física segura da instalação em Windows.

## 13. Estado geral

**V8 NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO.**
