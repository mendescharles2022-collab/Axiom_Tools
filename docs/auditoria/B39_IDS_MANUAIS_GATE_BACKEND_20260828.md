# B39 — IDs manuais e gate backend de saídas

Data: 28/08/2026
Branch: `audit-v8-runtime-reconciliation`

## Risco auditado

IDs enviados pelo navegador não podem funcionar como autorização para impressão ou entrega. Um usuário autenticado também não pode fabricar um POST com cliente/documento fora do universo liberado pelo Fechamento Mensal.

## Impressão

Mesmo quando `gerar_lote()` recebe `ids` explícitos, o serviço resolve os documentos e executa `exigir_documentos_autorizados()` antes de criar a saída.

Esse gate rejeita:

- documento inexistente;
- documento sem cliente;
- documento fora da competência;
- cliente fora da composição/ciclo;
- cliente não FECHADA;
- cliente sem versão vigente;
- versão inexistente/não vigente;
- retificação pendente.

A filtragem feita pela view é conveniência de interface. A autorização real permanece no serviço backend.

## Entrega

`gerar_cliente()` executa `avaliar_saida_cliente()` antes de criar pasta ou arquivo. Assim, inclusive a rota individual com `cliente_id` no path não consegue preparar entrega para cliente ainda PRONTA ou bloqueado.

O lote selecionado usa `exigir_clientes_autorizados()` antes de iterar sobre qualquer cliente; seleção mista é rejeitada como um todo, evitando saída parcial silenciosa.

## Regressão explícita contra POST adulterado

Teste versionado:

`runtime_overlay/app/tests/modules/test_manual_output_ids_v8.py`

Casos:

1. lote de documentos contendo um ID autorizado e outro não autorizado é rejeitado integralmente;
2. ID explícito de impressão para cliente PRONTA não passa pelo gate;
3. ID individual de entrega para cliente PRONTA não passa pelo gate.

O teste legado/amplo `test_output_gate_v8.py` também foi ampliado localmente com a entrega individual por ID manual.

Resultados:

- gate de saída amplo: 14 testes;
- segurança estática B38: 5 testes;
- conjunto B38+B39: 19/19 PASS;
- regressão não-web acumulada: 406/406 PASS.

## Observação de interface

Foi corrigido na árvore auditada um comentário antigo de `printing_views.py` que dizia que seleção explícita poderia incluir “qualquer cliente”. Isso nunca deve ser entendido como autorização: todo ID recebido é apenas candidato e continua sujeito ao gate backend.

## Estado

B39: `CORRIGIDO_TESTADO` na árvore reconciliada.

A homologação HTTP/Windows continua pendente para o pacote final.
