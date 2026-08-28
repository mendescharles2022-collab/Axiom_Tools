# Contrato V8 — Universo operacional canônico

Data: 28/08/2026
Status: **achado estrutural confirmado / implementação pendente**

## 1. Achado confirmado na instalação real

A inspeção da árvore instalada mostrou consultas diretas a `fechamento_mensal_cliente` em múltiplas camadas:

- `modules/processing/central.py` por volta da linha 726;
- `modules/processing/operations...` por volta das linhas 343 e 383;
- `web/views/documents_views.py` por volta das linhas 1097 e 1107;
- além das próprias funções de `modules/closing/service.py`.

Isso comprova que o conceito de 'cliente pertencente ao ciclo/escopo' está replicado em pontos diferentes.

Os valores exatos de todos os `status IN (...)` não ficaram integralmente visíveis na saída PowerShell preservada; por isso este documento não inventa quais status cada trecho utiliza.

O defeito estrutural, porém, já está comprovado: **mais de uma camada decide diretamente o universo operacional a partir da tabela de fechamento**.

## 2. Risco real

Quando Fechamento, Processamento, Conferência, eConsignado, Pendências, Impressão e Entregas reproduzem filtros próprios, uma alteração de regra pode ser aplicada em um ponto e esquecida em outro.

Sintomas já observados são compatíveis com isso:

- cliente de 2ª chamada ainda cobrado na 1ª;
- fechados aparecendo na mesa viva da Conferência;
- eConsignado consultando universo muito maior que o ciclo;
- Impressão/Entregas com gates diferentes;
- Processamento e telas documentais com consultas próprias ao fechamento.

## 3. Princípio canônico

Somente o domínio de Fechamento deve decidir a composição mensal e as transições de chamada/status.

Os demais módulos devem consumir funções/serviços públicos do domínio de Fechamento, sem reproduzir SQL de composição mensal.

## 4. Universos distintos por finalidade

Não existe um único conjunto chamado genericamente 'clientes do ciclo'. Devem existir conjuntos semânticos explícitos.

### 4.1 Universo da competência

Todos os clientes participantes da composição mensal, inclusive históricos de estados.

Uso: Fechamento Mensal e relatórios administrativos.

### 4.2 Universo liberado da chamada atual

Clientes com movimento e efetivamente liberados para a chamada corrente.

Uso:

- Processamento normal;
- eConsignado Etapa 0;
- descoberta de documentos da chamada.

Não inclui:

- chamada futura;
- sem movimento;
- fora do ciclo;
- fechado histórico, salvo fluxo de retificação.

### 4.3 Universo em conferência

Clientes que já possuem evidência processada suficiente para alcançar a mesa de Conferência e ainda requerem conclusão/resolução.

Uso: Central de Conferência normal.

Não inclui automaticamente todo cliente `PRONTA` só por status cadastral do ciclo.

### 4.4 Universo de retificação

Clientes previamente fechados com mudança material candidata.

Uso: fluxo próprio de retificação.

Não mistura com a mesa normal da chamada.

### 4.5 Universo autorizado de saída

Clientes efetivamente `FECHADA`, sem retificação material pendente, na competência da saída.

Uso obrigatório:

- Impressão;
- Entregas;
- saídas automáticas.

## 5. API sugerida de domínio

A nomenclatura pode variar, mas o conceito deve equivaler a:

```python
closing_scope.competencia(competencia)
closing_scope.liberados_chamada_atual(competencia)
closing_scope.em_conferencia(competencia)
closing_scope.em_retificacao(competencia)
closing_scope.autorizados_saida(competencia)
closing_scope.pode_processar(competencia, cliente_id)
closing_scope.pode_sair(competencia, cliente_id)
```

Nenhuma dessas funções deve depender de filtro visual recebido da tela.

## 6. SQL fora do domínio Closing

Consultas diretas à tabela `fechamento_mensal_cliente` fora de `modules/closing` devem ser inventariadas.

Regra de migração:

- leitura operacional de composição/status deve migrar para a fachada canônica;
- consultas de relatório/histórico podem existir quando justificadas, mas não devem decidir autorização/transição de negócio;
- qualquer exceção deve ser documentada.

## 7. T L Empreendimentos Agrícolas

A árvore instalada contém pelo menos dois pontos de mutação em `closing/service.py`:

- atualização individual de status/chamada por volta da linha 150;
- atualização para `status='PRONTA'` e nova chamada por volta da linha 205, próxima da atualização de `chamada_atual`.

A saída preservada não mostra nome de função nem condição completa. Portanto ainda não é possível afirmar qual trecho causou o retorno indevido da T L para chamada 1.

Regressão obrigatória:

1. adiar T L da chamada 1 para chamada 2;
2. confirmar persistência imediata de `ADIADA`/estado equivalente e chamada 2;
3. abrir Fechamento, Processamento, Conferência e Pendências;
4. executar sincronizações/recalculos permitidos;
5. confirmar que nenhuma rotina obsoleta retorna o cliente para chamada 1;
6. avançar globalmente para chamada 2;
7. somente nesse evento o cliente passa a `PRONTA`/liberada para a chamada 2;
8. histórico deve mostrar a sequência completa.

## 8. Regressões de escopo

### Cenário A — próxima chamada

Cliente adiado não aparece em Processamento, eConsignado ou Conferência da chamada anterior.

### Cenário B — fechado

Cliente fechado não reaparece na mesa viva apenas porque a tela foi aberta.

### Cenário C — retificação

Nova mudança material em fechado entra no universo de retificação, não no ciclo comum.

### Cenário D — sem movimento

Cliente sem movimento mensal fica fora do Processamento normal e não gera expectativa de guias incompatíveis.

### Cenário E — saída

Somente `autorizados_saida()` podem chegar a Impressão/Entrega/saída automática, mesmo com IDs manuais.

## 9. Critério de aceite

A V8 não estará homologada enquanto múltiplos módulos continuarem mantendo regras próprias e potencialmente divergentes para responder 'este cliente pertence a este estágio da competência?'.
