# Auditoria canônica V8 — Etapa 49

Data: 31/08/2026  
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Auditoria concentrada no eConsignado:

- B24 — fora do orquestrador;
- B25 — universo excessivo;
- B26 — falso `CONFERIDO`;
- B27 — retorno residual;
- B28 — idempotência/retry.

Foram confrontados o contrato canônico e os deltas preservados até o V8F2.

## 2. Limite do material recuperado

Os deltas materializados possuem:

- rotas Web de eConsignado;
- template do painel;
- integração da Conferência com `processamento_consignado_snapshot`;
- validações do V8F2.

Entretanto, nenhum dos deltas materializados contém o arquivo:

`modules/processing/consignados.py`

As views importam esse módulo da instalação-base, mas os pacotes incrementais não o substituem.

Logo as funções internas de criação do universo, consulta oficial, persistência de job e retry não podem ser reatribuídas linha a linha nesta etapa.

## 3. B24 — separação do orquestrador permanece explícita até o V8F2

No `documents_views.py` V8F2 existe fluxo dedicado:

```text
GET  /processamento/consignados
POST /processamento/consignados/config
POST /processamento/consignados/sincronizar
GET  /processamento/consignados/status
```

A sincronização executa:

```python
job_id = criar_job_consignados(conexao, competencia=competencia)
lancar_job_consignados(Path(current_app.instance_path), job_id)
```

Portanto o eConsignado continua nascendo de comando/rota própria e de job próprio.

Não há, nos deltas V8 recuperados, evidência de que essa consulta tenha sido incorporada como Etapa 0 obrigatória ao mesmo comando/orquestrador que processa Domínio → eSocial → e-CAC → FGTS.

Esse desenho coincide com a falha já registrada no contrato canônico.

### Estado

B24 permanece **CONFIRMADO_RUNTIME / PRONTO_PARA_CORRIGIR**.

## 4. B25 — 840 x 339 permanece confirmado pela evidência canônica; causa interna ainda depende do módulo ausente

O contrato canônico registra para 08/2026:

- 840 empregadores consultados no job eConsignado;
- 339 clientes participantes do Fechamento Mensal;
- `clientes_consulta()` derivando universo do cadastro histórico/situação, e não diretamente da competência/chamada.

Na view V8F2, o comando de sincronização entrega ao job apenas a `competencia`.

Não passa pela rota:

- chamada atual;
- conjunto de clientes liberados;
- IDs do universo mensal;
- movimento mensal.

Isso é consistente com a implementação-base descrita pela auditoria, mas o corpo de `criar_job/clientes_consulta` não está nos deltas para verificar se algum filtro interno posterior foi acrescentado.

### Conclusão segura

O defeito 840 x 339 continua como evidência canônica válida. A causa histórica já registrada é o universo cadastral excessivo, porém a comprovação de uma eventual correção posterior exige recuperar `consignados.py` da árvore operacional completa.

### Estado

B25 permanece **CONFIRMADO_RUNTIME / INSPEÇÃO da implementação-base pendente**.

## 5. B26 — V8F2 contém uma correção funcional real contra falso `CONFERIDO`

No V8F2, `_check_econsignado(...)` passou a separar:

- previsão/contrato MTE/Dataprev;
- referência local de desconto (`dominio` ou `comunicado`);
- fonte de recolhimento (`fgts`).

A função declara explicitamente que retorno positivo do MTE/Dataprev não prova recolhimento.

Regras recuperadas:

```text
nenhuma fonte -> NAO_APLICAVEL
falta referência local OU falta recolhimento -> AGUARDANDO_FONTES
fontes presentes + diferença <= tolerância -> CONFERIDO
fontes presentes + diferença > tolerância -> DIVERGENTE
```

Isso corrige o mecanismo que podia transformar presença de contrato oficial em conclusão prematura.

### Validador V8F2

`VALIDAR_14V8F2.py` possui duas verificações diretas:

```python
_check_econsignado(100, 100, None, None) -> AGUARDANDO_FONTES
_check_econsignado(100, 100, None, 100) -> CONFERIDO
```

Diferentemente do caso FGTS zero, essas verificações não dependem de encontrar fixture no banco: são chamadas diretas da função.

### Limite

Nesta sessão o validador não foi executado dentro da instalação canônica reconciliada, e o `main` não contém a árvore operacional para regressão integrada D A F Castro.

### Classificação

B26 deve ser registrado como:

**correção implementada no V8F2 + checagem funcional embutida no validador / regressão integrada e homologação pendentes**.

Não promover para `CORRIGIDO_TESTADO` ou `CORRIGIDO_HOMOLOGADO`.

## 6. B27 — retorno residual ainda pode virar pendência cega por falta de contexto de vínculo/remuneração

No V8F2, `_mte_cliente(...)` agrega `processamento_consignado_snapshot` por:

- competência;
- cliente_id; ou
- inscrição do empregador como fallback.

A agregação calcula:

- quantidade de contratos;
- quantidade de trabalhadores;
- soma de `valor_parcela`.

Não existe nessa função filtro por:

- vínculo ativo na competência;
- admissão/desligamento;
- remuneração;
- afastamento;
- rescisão;
- contrato residual;
- compatibilidade trabalhador × folha.

Depois, `_check_econsignado(...)`, quando há contrato oficial mas faltam fontes locais/recolhimento, retorna `AGUARDANDO_FONTES`.

Assim a correção de B26 evita falso `CONFERIDO`, mas um retorno residual ainda pode gerar pendência operacional apenas pela existência do snapshot oficial.

Para D&L e casos equivalentes, o contrato exige que ausência de vínculo/remuneração compatível transforme o retorno residual em observação/confirmação, não em bloqueio cego.

### Estado

B27 permanece **CONTRATO_OBRIGATORIO / PRONTO_PARA_CORRIGIR**.

## 7. B28 — idempotência/retry não pode ser declarada nesta etapa

As regras de B28 exigem provar que:

- reexecução não duplica contratos/resultados;
- erro de API não apaga fotografia válida anterior;
- nova execução cria fotografia/versionamento auditável;
- universo/chamada usados no job permanecem vinculados à fotografia.

A implementação dessas operações está justamente no módulo `processing/consignados.py`, ausente dos deltas recuperados.

As views apenas:

- criam o job;
- lançam o job;
- registram `ERRO` no job se o lançamento falhar;
- consultam o último job.

Isso não permite concluir como snapshots anteriores são preservados ou substituídos.

### Estado

B28 permanece **CONTRATO_OBRIGATORIO / INSPEÇÃO do runtime completo pendente**.

## 8. Síntese

- B24: fluxo separado confirmado até V8F2;
- B25: excesso 840 x 339 permanece evidência canônica; implementação-base ausente dos deltas;
- B26: **correção real encontrada no V8F2**, sem homologação integrada;
- B27: falta cruzamento de vínculo/remuneração antes de transformar retorno residual em pendência;
- B28: não atribuir defeito/correção sem recuperar o job completo.

A V8 permanece **NÃO HOMOLOGADA**.

## 9. Próxima frente

Prosseguir com parser/competência:

- B29 — Diretor ≠ empregado;
- B30 — federal autoritativo;
- B31 — competência/proveniência;
- B32 — IRRF competência de pagamento;
- B33 — dezembro/13º e calendário versionado.
