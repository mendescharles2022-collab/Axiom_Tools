# Auditoria canônica V8 — Etapa 46

Data: 31/08/2026  
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Continuação da auditoria sobre os deltas operacionais preservados, agora concentrada em:

- B07 — universo operacional duplicado;
- B09 — fechados permanecem na mesa viva;
- B10 — retificação misturada ao ciclo;
- B11 — estado antecipado no pipeline.

A análise utiliza principalmente V4, V7, V8A, V8B e V8F2, sem promover esses deltas a runtime canônico completo.

## 2. B07 — duplicação do universo operacional confirmada novamente e com predicados recuperados

O contrato canônico já registrava SQL direto contra `fechamento_mensal_cliente` em várias camadas. Os pacotes recuperados agora permitem ver predicados concretos.

### 2.1 `modules/processing/central.py` — V8B/V8F2

`_aplicar_competencia_trabalho(...)` consulta diretamente:

```sql
SELECT 1
FROM fechamento_mensal_cliente
WHERE competencia=?
  AND cliente_id=?
  AND status IN ('FECHADA','RETIFICACAO')
LIMIT 1
```

Essa consulta decide se documento de competência diferente da ativa pode ser aceito como potencial retificação.

Logo o Processing mantém uma regra própria de composição/estado do fechamento em vez de consumir uma fachada semântica do domínio Closing.

### 2.2 `modules/processing/operations.py` — V4

`listar_auditoria(...)` e `monitor(...)`, quando filtrados por fechadas, também reproduzem SQL direto:

```sql
... cliente_id IN (
    SELECT cliente_id
    FROM fechamento_mensal_cliente
    WHERE competencia=?
      AND status IN ('FECHADA','RETIFICACAO')
)
```

Além da duplicação, o filtro denominado `FECHADAS` inclui `RETIFICACAO`, misturando conceitos diferentes.

### 2.3 `web/views/documents_views.py` — V8F2

O Monitor incorporado repete o mesmo padrão para eventos de repositório e de saída:

```sql
p.cliente_id IN (
    SELECT cliente_id
    FROM fechamento_mensal_cliente
    WHERE competencia=?
      AND status IN ('FECHADA','RETIFICACAO')
)
```

Portanto a duplicação persiste até o V8F2 materializado.

### 2.4 `modules/closing/service.py`

O próprio Closing mantém helpers como:

- `clientes_fechados_ids(...)`;
- `clientes_conferencia_ids(...)`;
- `movimentos_competencia(...)`.

Esses helpers são um início de centralização, porém coexistem com SQL de autorização/escopo reproduzido fora do domínio.

### Conclusão B07

B07 permanece **CONFIRMADO_RUNTIME / PRONTO_PARA_CORRIGIR**.

A causa está suficientemente isolada: existem múltiplas definições paralelas de universo operacional, algumas inclusive com semânticas diferentes para `FECHADAS`.

A correção deve centralizar, no domínio Closing, conjuntos semânticos separados:

- competência;
- liberados da chamada atual;
- em conferência;
- em retificação;
- autorizados para saída.

## 3. B09 — FECHADA incluída explicitamente na mesa viva

No V8B, `clientes_conferencia_ids(...)` retorna clientes quando:

```text
(status = PRONTA e chamada = chamada_atual)
OU status IN (FECHADA, RETIFICACAO)
```

Além disso, a condição de movimento permite `FECHADA`/`RETIFICACAO` mesmo fora da regra comum de movimento.

`conference.py` usa esse helper quando `escopo_fechamento='CICLO'`.

Portanto o conjunto usado para a Conferência corrente inclui explicitamente clientes já `FECHADA`.

Isso não é apenas um rótulo visual: é a composição do conjunto de entrada da Conferência.

### Consequência

Um cliente fechado continua pertencendo à projeção da mesa viva do ciclo normal, contrariando o contrato canônico:

- `FECHADA` deve permanecer em histórico/consulta;
- nova mudança material deve migrar para retificação própria;
- abrir a mesa normal não deve reintroduzir fechado como item corrente.

### Conclusão B09

B09 permanece **CONFIRMADO_RUNTIME / PRONTO_PARA_CORRIGIR** e agora possui predicado SQL completo recuperado no V8B.

## 4. B10 — RETIFICACAO incluída no mesmo conjunto da Conferência normal

O mesmo `clientes_conferencia_ids(...)` inclui `RETIFICACAO` juntamente com `PRONTA` e `FECHADA`.

Assim, embora o V4 tenha criado:

- tabela de retificações;
- snapshots/versionamento;
- aba própria de retificação no Fechamento Mensal;
- detecção de mudança material;

os clientes em `RETIFICACAO` continuam entrando pelo mesmo conjunto de escopo consumido pela Conferência normal.

Há ainda evidência histórica explícita no relatório V4 de que Central de Conferência/Auditoria passaram a considerar empresas em retificação dentro do escopo de fechamento.

### Distinção importante

O V4 avançou corretamente ao preservar versão anterior e bloquear saída durante retificação. O defeito B10 não invalida esse patrimônio.

A regressão é de **composição da mesa**:

- retificação possui máquina, fila e contexto próprios;
- não deve ser tratada como mais um estado da mesa normal da chamada corrente.

### Conclusão B10

B10 permanece **CONFIRMADO_RUNTIME / PRONTO_PARA_CORRIGIR**.

A correção deve preservar o motor de retificação válido e retirar `RETIFICACAO` de `clientes_conferencia_ids()`/escopos comuns, expondo um universo próprio.

## 5. B11 — houve mitigação visual na V8A, mas não separação completa do estado

### 5.1 Origem

V7 introduziu explicitamente:

```text
PRONTA -> Em conferência
```

O `STATUS` de `closing/service.py` passou a mapear `PRONTA` como `Em conferência`.

Isso promovia visualmente o cliente antes de existir evidência documental suficiente.

### 5.2 V8A corrigiu parte visível do problema

A V8A acrescentou `conferencia_map` e passou a derivar:

- `aguardando_processamento` — cliente `PRONTA`/com movimento que ainda não aparece no dossiê processado;
- `em_conferencia_real` — cliente `PRONTA`/com movimento que já aparece no dossiê.

O template passou a mostrar:

- `Aguardando processamento` sem `conf`;
- `Em conferência` apenas quando há projeção de Conferência.

Esse trabalho é válido e deve ser preservado.

### 5.3 O estado legado, porém, continua semanticamente ambíguo

Mesmo em V8B, `closing/service.py` ainda declara:

```python
STATUS = {
    "PRONTA": "Em conferência",
    ...
}
```

E `resumo(...)` continua agregando todas as linhas `PRONTA + COM_MOVIMENTO` como `prontas`, sem o domínio possuir estados persistidos/derivados explícitos equivalentes a:

- aguardando processamento;
- em processamento;
- em conferência.

A V8A resolveu parte da representação na tela do Fechamento, mas a arquitetura permanece dependente de uma combinação entre `PRONTA`, dossiê processado e lógica específica da view.

Isso mantém risco de outras superfícies traduzirem `PRONTA` de forma antecipada.

### Conclusão B11

B11 permanece **CONTRATO_OBRIGATORIO / PRONTO_PARA_CORRIGIR**, porém deve ser classificado como **parcialmente mitigado na V8A**, não como ausência total de correção.

Patrimônio a preservar:

- derivação `Aguardando processamento` versus `Em conferência` introduzida na V8A.

Pendência arquitetural:

- consolidar a máquina mensal e impedir que `PRONTA` seja uma tradução genérica para Conferência em qualquer consumidor.

## 6. Relação entre B07, B09, B10 e B11

Os quatro defeitos possuem uma raiz comum de arquitetura:

1. `fechamento_mensal_cliente.status` passou a responder perguntas demais;
2. consumidores reproduzem filtros diretamente;
3. `FECHADA` e `RETIFICACAO` foram incorporadas em conjuntos de uso genérico;
4. `PRONTA` foi usada como atalho semântico para estágio de Conferência.

A correção deve preservar dados e histórico existentes, mas criar fachadas/projeções semânticas por finalidade, sem depender de SQL ou rótulo replicado em cada tela.

## 7. Estados

Nenhum bloqueador é promovido para corrigido/testado/homologado nesta etapa.

- B07: confirmado e isolado;
- B09: confirmado com predicado completo;
- B10: confirmado com predicado completo;
- B11: mitigação visual V8A reconhecida, arquitetura ainda pendente.

A V8 permanece **NÃO HOMOLOGADA**.

## 8. Próxima frente

Prosseguir na ordem canônica com os bloqueadores de composição/documentos, priorizando:

- B12 — Multi-Extrato;
- B13 — composição rural federal x FGTS;
- B14 — múltiplas evidências de FGTS;
- B15 — descoberta → vínculo;
- B16 — identidade PF/CAEPF;
- B17 — deduplicação lógica.
