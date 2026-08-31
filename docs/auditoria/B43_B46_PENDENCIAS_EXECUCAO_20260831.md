# B43/B46 — Pendências orientadas por competência e uma única execução ao vivo

Data: 31/08/2026
Branch: `audit-v8-runtime-reconciliation`
Base: snapshot operacional recuperado `Axiom_Tools(20260828-175237).zip`.

## B43 — Pendências

Problema confirmado no runtime recuperado:

- a rota já possuía fallback para `competencia_ativa`, porém a interface mantinha PROC/chave como filtro principal;
- links da tela de Execução abriam Pendências com `chave=PROC...`, tornando a chave técnica o eixo operacional;
- o usuário precisava lidar com PROC para chegar ao recorte de competência.

Correção aplicada na cópia canônica:

- título passa a `Pendências técnicas`;
- competência em foco é exibida explicitamente;
- filtro principal começa por competência;
- busca, motivo e paginação permanecem no primeiro nível;
- PROC e origem são movidos para `Filtros avançados`;
- links da Execução para Pendências passam `competencia=competencia_execucao`, não `chave=detalhe.chave`;
- remover filtros avançados preserva a competência em foco.

A rota mantém o comportamento já correto de assumir `competencia_ativa` quando o parâmetro não é informado.

## B46 — uma única verdade técnica de execução

Problema confirmado:

- a sessão técnica podia ser exibida como `COM_PENDENCIAS` apenas porque existiam documentos em `REVISAO`;
- isso misturava estado da execução com estado documental e reforçava a percepção de múltiplos monitores;
- `Monitor de Execução`, `Monitor automático` e `Auditoria` apareciam como conceitos visuais concorrentes.

Correção aplicada:

- revisão documental não altera mais o estado técnico da sessão;
- sessão 100% sem erro técnico = `PROCESSAMENTO_CONCLUIDO`, mesmo quando há documentos para revisão;
- sessão 100% com erro técnico = `PROCESSAMENTO_CONCLUIDO_COM_ERROS`;
- sessão em andamento com erro técnico = `COM_ERROS`;
- persistência da sessão não grava mais `COM_PENDENCIAS` por causa de revisão documental;
- a tela ao vivo passa a se chamar simplesmente `Execução`;
- a Auditoria passa a se apresentar como `Auditoria técnica`, explicitamente histórica;
- o Dashboard troca `Monitor automático` por `Conexões automáticas` para não criar um segundo conceito de monitor.

## Evidência

Teste versionado:

`runtime_overlay/app/tests/modules/test_pending_execution_ux_v8.py`

Resultado na cópia canônica:

- 8/8 testes específicos PASS;
- `queue.py` compilado com `py_compile`;
- patch local contra o snapshot canônico: SHA-256 `2da77a080a8e457a2764bf3d2883d120832c53d1fda64a366f093fc54f8b9913`.

## Critério alcançado

B43 e B46 podem ser classificados como `CORRIGIDO_TESTADO` na cópia canônica recuperada.

Ainda não são `CORRIGIDO_HOMOLOGADO`: validação visual real no Windows/browser e promoção da árvore reconciliada continuam pendentes.
