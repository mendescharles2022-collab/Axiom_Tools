# Auditoria canônica V8 — Etapa 51

Data: 31/08/2026  
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Auditoria dos bloqueadores de dados, estado, segurança e concorrência:

- B34 — `classificacao_inativacao` string/Enum;
- B35 — foreign keys/invariantes;
- B36 — migração do estado global antigo para decisão por fonte;
- B37 — máquinas de estado misturadas;
- B38 — autenticação/CSRF nas mutações;
- B39 — seleção manual por IDs;
- B40 — concorrência lógica.

A análise usa os deltas materializados V/V4/V8A/V8B/V8F2 e os contratos canônicos existentes.

## 2. B34 — fronteira Enum está correta na view recuperada, mas o contrato do repositório continua estrito

No código recuperado do módulo Clientes:

`ClassificacaoInativacao` é um `Enum` de string com valores como:

- `BAIXADA`;
- `TRANSFERIDA`;
- `ENCERRAMENTO_ATENDIMENTO`;
- `SEM_MOVIMENTO`;
- `OUTRO`.

`ClienteRepository` serializa o campo usando:

```python
cliente.classificacao_inativacao.value
```

Logo o repositório espera um objeto `ClassificacaoInativacao`, não uma string crua.

A view de inativação recuperada faz corretamente:

```python
classificacao_raw = request.form.get("classificacao", "").strip().upper()
classificacao = ClassificacaoInativacao(classificacao_raw)
service.inativar_cliente(... classificacao=classificacao ...)
```

Esse caminho Web está coerente e deve ser preservado.

Entretanto a auditoria anterior registrou uma falha de suíte envolvendo representação string/Enum. Os deltas não contêm a implementação completa do serviço de Clientes nem a suíte operacional que produziu essa falha.

Consequentemente a conclusão segura é:

- o formulário Web recuperado **não é a origem óbvia do problema**;
- o repositório continua com contrato estrito de Enum;
- algum consumidor de serviço/teste pode ainda passar string crua;
- a correção deve normalizar a fronteira no domínio/serviço ou comprovar que todos os chamadores entregam Enum.

### Estado

B34 permanece **CONFIRMADO_RUNTIME / ponto exato do chamador pendente**.

Não aplicar correção especulativa apenas no repositório sem recuperar a suíte que falhou.

## 3. B35 — schema possui FKs úteis, mas integridade lógica permanece muito além delas

### 3.1 Fechamento mensal

`fechamento_mensal_cliente` possui:

```sql
FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
UNIQUE(competencia,cliente_id)
```

`fechamento_mensal_historico` usa:

```sql
FOREIGN KEY(cliente_id) REFERENCES clientes(id) ON DELETE SET NULL
```

`fechamento_cliente_perfil` também possui FK para `clientes`.

Isso é patrimônio válido.

### 3.2 Relações sem FK declarada nos schemas recuperados

Não foi encontrada FK explícita, nos deltas V4/V8B, entre:

- `fechamento_mensal_cliente.competencia` e `fechamento_mensal.competencia`;
- `fechamento_mensal_versao.cliente_id` e `clientes.id`;
- `fechamento_mensal_versao` e o controle mensal correspondente;
- `fechamento_mensal_retificacao` e `clientes/fechamento_mensal_cliente`;
- `base_versao` e a versão efetivamente existente.

Isso não implica corrupção; significa apenas que essas relações dependem de invariantes lógicas e não de FK física.

### 3.3 Invariantes já implementadas no `main`

A Etapa 41 já registrou quatro regressões para duas regras comprovadas:

- FECHADA sem versão é inválida;
- `versao_atual` precisa apontar para versão existente.

Esses testes continuam válidos como infraestrutura.

### 3.4 Gap restante

Ainda faltam executar no banco real reconciliado:

```sql
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

mais invariantes de:

- competência órfã;
- retificação/base de versão;
- chamada/status/movimento;
- documentos vigentes;
- saídas sem versão autorizadora;
- obrigações por fonte.

### Estado

B35 permanece **EM_CORRECAO / teste real do banco pendente**.

Nenhuma corrupção foi declarada nesta etapa.

## 4. B36 — não existe ainda modelo por fonte para onde migrar a decisão global

A implementação recuperada mantém `processamento_conferencia_manual` com uma decisão por:

```text
competencia + cliente_id
```

usando estados globais como:

- `CONFERIDO`;
- `JUSTIFICADO`;
- `PENDENTE`.

Não existe no schema recuperado uma estrutura equivalente ao contrato V8:

```text
competencia + cliente_id + obrigacao + componente
```

Portanto a migração B36 ainda não pode ser considerada implementada.

Mais importante: como algumas decisões legadas podem ter sido tomadas apenas para DARF, copiar o status global para DARF + FGTS + eConsignado criaria informação falsa.

A migração correta precisa classificar:

- decisão com fonte identificável -> converter;
- decisão global ambígua -> preservar como legado/revisão;
- nunca fabricar estados finais por obrigação sem evidência.

### Estado

B36 permanece **CONTRATO_OBRIGATORIO / PRONTO_PARA_CORRIGIR após schema B05/B18**.

## 5. B37 — mistura de máquinas continua confirmada

A recuperação reforça evidências anteriores:

### Ciclo mensal

`STATUS` do Closing ainda traduz:

```python
"PRONTA": "Em conferência"
```

mesmo que V8A tenha criado uma mitigação visual mais inteligente em uma tela.

### Documento

`PROCESSADO` continua sendo estado técnico usado por serviços de saída e dossiê.

### Sessão técnica

A auditoria do ZIP canônico já confirmou persistência `COM_PENDENCIAS` versus apresentação `PROCESSAMENTO_CONCLUIDO` a 100%.

### Consulta externa

Estados MTE/Dataprev continuam pertencendo a fotografia externa, enquanto a Conferência deriva outro estado de negócio.

### Retificação

`RETIFICACAO` ainda aparece em conjuntos comuns da Conferência/Monitor.

### Estado

B37 permanece **CONFIRMADO_RUNTIME / PRONTO_PARA_CORRIGIR**, integrando as correções B02/B03/B07/B09/B10/B11/B18/B26.

## 6. B38 — evidência de autenticação e tokens CSRF melhorou substancialmente

Foi executada inspeção estática nos deltas materializados.

### 6.1 Decorators de autenticação

Rotas POST encontradas e protegidas por `@login_required` ou `@admin_required` imediatamente no bloco da rota:

- V8A: **13/13**;
- V4: **36/36**;
- V8F2: **30/30**.

Não foi encontrada rota POST sem proteção de autenticação nesses três deltas.

### 6.2 Formulários POST materializados

Formulários HTML com `method="post"` encontrados:

- V8A: 16;
- V4: 15;
- V8F2: 3.

Nos formulários materializados inspecionados, todos incluem `csrf_token`.

Isso demonstra que a implementação operacional preservou o padrão de inclusão de token nas superfícies recuperadas.

### 6.3 Limite

Os deltas não contêm a inicialização completa da extensão CSRF/Flask-WTF nem toda a árvore Web.

Logo ainda falta provar na árvore reconciliada que:

- token ausente/inválido é realmente rejeitado no servidor;
- não existem rotas mutáveis fora dos deltas sem proteção;
- endpoints máquina-a-máquina possuem política própria;
- autorização de negócio ocorre além do login.

### Classificação

B38 permanece formalmente **TESTE_PENDENTE_RUNTIME**, mas a nova evidência reduz fortemente a hipótese de regressão generalizada de autenticação/CSRF.

O foco da correção deve migrar para **autorização de negócio e transação**, não para reescrever a fundação de login que já está presente.

## 7. B39 — IDs recebidos continuam sendo seleção, não autorização

A Etapa 45 já confirmou bypass de autorização em Impressão/Entregas.

Neste bloco o mesmo padrão aparece no Closing:

```python
def _ids():
    return [int(x) for x in request.form.getlist("cliente_id") if str(x).isdigit()]
```

As rotas entregam esses IDs para funções de negócio.

As funções verificam se existe uma linha `competencia + cliente_id`, mas não necessariamente se o estado atual permite a ação solicitada.

Exemplo `fechar_clientes(...)`:

- aceita IDs selecionados;
- carrega linha atual;
- registra versão;
- atualiza para `FECHADA`;
- não recebe como pré-condição os estados por obrigação que autorizaram o fechamento.

Assim, mesmo fora do tema de saída, fica reforçada a regra:

**ID enviado pelo front nunca é autorização de negócio.**

### Estado

B39 permanece **CONFIRMADO_RUNTIME / PRONTO_PARA_CORRIGIR**.

## 8. B40 — concorrência lógica possui falhas concretas de compare-and-set

Este é o achado mais forte do bloco.

### 8.1 `_alterar(...)`

Fluxo atual:

1. lê `old` por `competencia + cliente_id`;
2. calcula destino;
3. executa:

```sql
UPDATE fechamento_mensal_cliente
SET status=?, chamada=?, ...
WHERE competencia=? AND cliente_id=?
```

O `WHERE` não inclui:

- status lido;
- chamada lida;
- revisão/versão;
- `atualizado_em` esperado.

Uma decisão concorrente pode ser sobrescrita por snapshot obsoleto.

### 8.2 `sincronizar_resultados_conferencia(...)`

A função primeiro lê a linha e exige que naquele instante esteja `PRONTA`.

Depois:

1. registra versão fechada;
2. executa `UPDATE ... SET status='FECHADA'` apenas por `competencia + cliente_id`.

Entre a leitura e o UPDATE, outra requisição pode ter adiado o cliente ou iniciado retificação.

O UPDATE obsoleto ainda seria capaz de gravar `FECHADA` porque não repete `AND status='PRONTA'` nem verifica `rowcount`.

Esse cenário é diretamente compatível com o risco do caso T L.

### 8.3 `fechar_clientes(...)`

Também lê estado e posteriormente atualiza por `competencia + cliente_id`, sem compare-and-set.

### 8.4 `marcar_movimento_competencia(...)`

Lê movimento/status, pode criar versão e depois grava o novo estado sem condição sobre o estado original lido.

### 8.5 `abrir_proxima_chamada(...)`

Atualiza `chamada_atual` e depois libera em massa:

```sql
WHERE competencia=? AND status='ADIADA' AND chamada<=?
```

O predicado de cliente é mais seguro que um UPDATE irrestrito, mas a operação não usa uma revisão esperada/idempotency key para impedir avanço repetido por retry/duplo clique.

### 8.6 Consequência

A aplicação possui histórico, mas histórico não impede lost update.

A correção deve usar compare-and-set/transição versionada, por exemplo:

```sql
UPDATE ...
SET ...
WHERE competencia=?
  AND cliente_id=?
  AND status=?
  AND chamada=?
```

seguido de validação de `rowcount`.

Quando `rowcount == 0`, recarregar estado e responder conflito em vez de registrar sucesso.

### Estado

B40 permanece **CONTRATO_OBRIGATORIO**, agora com falha concreta de concorrência identificada nos serviços recuperados.

## 9. Achado adicional — retificação bloqueia saída mesmo sem mudança, por desenho V4

`avaliar_cliente(...)` V4 retorna:

```text
mudou=False, bloquear_saida=True
```

quando o snapshot atual tem o mesmo hash da versão fechada ou quando o delta calculado fica vazio.

O validador V4 exige explicitamente esse comportamento para repetição idêntica.

No worker, saída automática só ocorre quando:

```python
not retificacao.get("bloquear_saida")
```

Portanto uma nova ingestão materialmente idêntica em cliente fechado pode bloquear a saída automática daquele processamento mesmo sem abrir retificação.

Isso não cria B51; reforça a necessidade de reconciliar B03/B04/B17 e distinguir:

- bloquear saída porque existe mudança material;
- não gerar nova saída automática por duplicidade/reemissão;
- manter o fechamento vigente autorizado.

A semântica final deve ser explicitada na correção para não transformar prudência documental em bloqueio global artificial.

## 10. Síntese

- B34: caminho Web usa Enum corretamente; chamador que gerou a regressão ainda precisa ser recuperado;
- B35: FKs parciais válidas, invariantes lógicas e banco real ainda pendentes;
- B36: decisão por fonte ainda não existe para migração segura do legado;
- B37: mistura de máquinas permanece;
- B38: autenticação/tokens CSRF nos deltas estão substancialmente preservados;
- B39: IDs continuam sendo seleção, não autorização;
- B40: compare-and-set ausente em transições críticas, com risco concreto de lost update.

Nenhum bloqueador é promovido para `CORRIGIDO_TESTADO` ou `CORRIGIDO_HOMOLOGADO`.

A V8 permanece **NÃO HOMOLOGADA**.

## 11. Próxima frente

Prosseguir para os bloqueadores operacionais e de entrega final:

- B41 — backup/rollback;
- B42 — proveniência de build;
- B43 — Pendências orientada por PROC;
- B44 — relatório A4 retrato;
- B45 — escala >600;
- B46 — Monitor duplicado/confuso;
- B47 — Sintegra;
- B48 — limpeza/retention;
- B49 — banco ↔ filesystem;
- B50 — hash ≠ obrigação.
