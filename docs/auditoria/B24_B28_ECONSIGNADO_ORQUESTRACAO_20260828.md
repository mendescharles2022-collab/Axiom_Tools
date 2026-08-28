# B24–B28 — eConsignado: orquestração, universo, contexto e retry

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## B24 — eConsignado dentro do orquestrador

O job deixa de operar como rotina paralela sem contexto do fechamento. A competência e a chamada são herdadas do Fechamento Mensal, e a conclusão do job dispara o recálculo explícito da Conference.

## B25 — universo excessivo

A consulta passa a usar o universo canônico da chamada atual com movimento.

Fixture real 08/2026:

- universo histórico anterior: aproximadamente 840 empregadores consultados;
- universo operacional V8: 30 clientes na chamada atual com movimento;
- `clientes_consulta()` e `clientes_chamada_atual_ids()` produzem o mesmo conjunto de 30 clientes.

O job persiste:

- chamada;
- escopo (`CICLO`);
- SHA-256 do escopo congelado;
- total de empregadores.

## B26 — falso CONFERIDO

Conference e painel eConsignado passam a usar o mesmo avaliador contextual. O retorno da API não é, sozinho, conclusão da Conferência.

Fixtures reais:

- D A F Castro (cliente 205): `DIVERGENTE`, diferença R$ 591,86;
- D&L Alimentos (cliente 212): `RETORNO_RESIDUAL`, R$ 603,38;
- GL Auto Center (cliente 362): `PAGAMENTO_DIRETO_JUSTIFICADO`, diferença R$ 0,00;
- Lourenconi & Modesto (cliente 524): `DIVERGENTE`, diferença R$ 230,91.

O painel e a Conference exibem o mesmo estado contextual para esses casos.

## B27 — retorno residual / falha externa

A promoção do snapshot oficial passou a ser conservadora:

- `COM_CONSIGNADO`: substitui a fotografia oficial atomicamente;
- `SEM_CONSIGNADO`: fotografia conclusiva vazia, pode limpar o snapshot anterior;
- `SEM_PROCURACAO`: não apaga snapshot bom;
- `NAO_DISPONIVEL`: não apaga snapshot bom;
- erro técnico: não apaga snapshot bom.

Falha durante a promoção executa rollback e preserva o snapshot anterior.

## B28 — idempotência / retry

Retry cria novo job auditável, mantendo o job original intacto. O novo job referencia `retry_de_job_id` e reaproveita somente alvos elegíveis para nova tentativa.

O job original não é reaberto nem sobrescrito.

## Evidência de testes

Teste versionado:

`runtime_overlay/app/tests/modules/test_econsignado_orchestration_v8.py`

Resultados na árvore canônica corrigida:

- 9/9 testes específicos PASS;
- regressão não-web acumulada: 375/375 PASS;
- 0 failures;
- 0 errors;
- 0 skips.

Hashes da árvore testada:

- `consignados.py`: `c9e5232c936804bc68ca56ed21018dffeda7f2bee98d686f781e27d754bb3f70`
- `consignado_sync_worker.py`: `f8517bc2f4a6054ef69e564b40475cd19c0a394bde307639ea65b8a72e2fc1ae`
- `conference.py`: `c466c8be692db514e34f34d006071d931407745959f7c996d0ef9397c136b433`
- teste específico: `389edbe170d2e2103cb15177dee2fa68962b1643760a32ac20d6acfcc71699b8`

## Estado

B24, B25, B26, B27 e B28 podem ser classificados como `CORRIGIDO_TESTADO` na cópia canônica recuperada.

Ainda não são `CORRIGIDO_HOMOLOGADO`: falta promoção da árvore reconciliada, execução Windows/runtime e homologação final da V8.
