# Auditoria canônica V8 — Etapa 48

Data: 31/08/2026  
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Auditoria dos bloqueadores de aplicabilidade por fonte:

- B18 — decisão por fonte;
- B19 — FGTS zero;
- B20 — MEI/DAE;
- B21 — deduções previdenciárias;
- B22 — afastamentos/faltas;
- B23 — DARF sob responsabilidade Fiscal/impedimento RFB.

A análise compara V4/V8B/V8F2 com o contrato canônico de decisão por obrigação.

## 2. B18 — decisão manual global por cliente continua ativa e pode fechar o cliente inteiro

O schema V4 de `processamento_conferencia_manual` usa chave:

```text
competencia + cliente_id
```

Campos centrais:

- `status_manual`;
- `observacao`;
- `conferido_em`.

Não existem nesse registro:

- obrigação/fonte;
- componente;
- documento/evidência da decisão;
- revisão do estado mensal.

`salvar_conferencia_manual(...)` aceita apenas estados globais:

- `CONFERIDO`;
- `JUSTIFICADO`;
- `PENDENTE`.

No V8F2, a Conferência continua lendo exatamente uma linha manual por `competencia + cliente_id`.

Mais grave: `sincronizar_resultados_conferencia(...)` V8B calcula:

```python
resultado = manual if manual in {'CONFERIDO','JUSTIFICADO'} else automatico
```

Se o manual global for `CONFERIDO` ou `JUSTIFICADO`, o cliente `PRONTA` pode ser fechado mesmo que o resultado automático contenha pendência/divergência em outra fonte.

Isso é incompatível com o contrato canônico, segundo o qual a decisão deve ser por:

`competencia + cliente_id + obrigacao + escopo_componente`.

### Estado

B18 permanece **CONTRATO_OBRIGATORIO / PRONTO_PARA_CORRIGIR** e a implementação recuperada confirma o risco que motivou o bloqueador.

## 3. B19 — correção funcional apareceu no V8F2, mas a regressão ainda não está provada

### V8B

A regra era:

```python
exibir_fgts = ... and (
    (fgts_dom is not None and abs(fgts_dom) > 0.02)
    or bool(regras['fgts_esperado'])
)
```

Consequência: mesmo quando o Extrato Domínio informava `fgts_dom = 0`, um cadastro genérico `fgts_esperado=True` podia manter a expectativa de GFD e criar ausência artificial.

### V8F2

O código foi corrigido para dar precedência à evidência da competência:

```python
base_fgts_disponivel = extr is not None and fgts_dom is not None
if base_fgts_disponivel:
    incidencia_fgts_mes = abs(fgts_dom) > 0.02
else:
    incidencia_fgts_mes = bool(gfd) or bool(regras['fgts_esperado'])
```

Assim, se existe Extrato da competência e ele traz FGTS zero, o cadastro genérico deixa de fabricar obrigação mensal.

Essa alteração é tecnicamente coerente com o contrato.

### Validador V8F2

`VALIDAR_14V8F2.py` percorre as linhas da Conferência e, para cada linha com `fgts_dominio` zero, exige:

```text
checks.fgts.status == NAO_APLICAVEL
```

Porém o teste possui uma lacuna: `zeros_validos` começa em zero e não há `assert zeros_validos > 0`.

Logo o validador pode passar sem ter encontrado qualquer fixture/cliente de FGTS zero.

Além disso, nesta sessão o validador não foi executado contra o runtime canônico.

### Classificação

B19 deve ser tratado como:

**correção implementada no delta V8F2 / regressão canônica ainda não comprovada**.

Não deve continuar descrito como se nenhuma correção existisse, mas também não pode ser promovido a `CORRIGIDO_TESTADO` ou `CORRIGIDO_HOMOLOGADO`.

## 4. B20 — MEI é detectado, mas DAE não existe na máquina de obrigações recuperada

O V8F2 detecta perfil MEI por `cliente_parametros.classificacao` e usa `perfil_mei` para impedir expectativa genérica de FGTS Digital.

Isso é patrimônio válido.

Entretanto a Conferência recuperada não contém modelo de obrigação `DAE`.

A pesquisa no módulo de Processamento V8F2 não encontrou:

- parser/obrigação DAE;
- check DAE;
- estado específico DAE;
- composição DAE.

O fluxo sempre cria `checks['inss']` usando `_check_darf_folha(...)`, inclusive para perfil MEI; apenas o FGTS é suprimido por `perfil_mei`.

Portanto o MEI ainda passa pela máquina genérica de DARF federal em vez de possuir sua obrigação própria DAE eSocial.

### Estado

B20 permanece **CONFIRMADO_RUNTIME / PRONTO_PARA_CORRIGIR**.

## 5. B21 — V8F2 alinha a comparação federal ao saldo final, mas parser/fixtures ainda precisam provar a cadeia

`_check_darf_folha(...)` V8F2 prioriza:

```python
total_esperado = exd['saldo_total_apuracao_dominio']
```

Quando esse saldo existe:

- saldo zero + DARF ausente -> `NAO_APLICAVEL_ZERO` ou ausência justificada;
- saldo positivo + DARF ausente -> `DARF_AUSENTE_INESPERADO`;
- DARF presente -> comparação pelo total final.

O código também expõe campos de dedução como salário-família e salário-maternidade para a linha da Conferência.

Esse desenho está coerente com a regra canônica de que o saldo final do Domínio deve prevalecer sobre soma bruta de INSS.

### Limites

O delta V8F2 não contém o parser Domínio integral responsável por preencher:

- `saldo_total_apuracao_dominio`;
- `apuracao_federal_detalhada`;
- justificativas/deduções.

O validador V8F2 também não possui fixture explícita Denes/Ponto Kent ou assert de dedução levando saldo a zero.

### Classificação

B21 possui **implementação de consumo coerente no Conference**, mas permanece `CONTRATO_OBRIGATORIO / teste de parser + casos reais pendente`.

Não promover estado.

## 6. B22 — suporte a afastamento foi incorporado, mas depende de motor não recuperado e não cobre toda a regra de obrigação

O V8F2 chama:

```python
justifica_ausencia_total(regras, ocorrencias)
```

Quando o afastamento justifica ausência total, o check federal pode retornar:

`AUSENCIA_JUSTIFICADA_AFASTAMENTO`.

O fechamento automático considera esse resultado como `JUSTIFICADO` quando não restam outras fontes aplicáveis no agregado.

Isso representa avanço funcional válido.

### Limites

A implementação de `justifica_ausencia_total(...)` não está presente nos deltas materializados nesta etapa.

Logo não foi possível verificar:

- tipos de afastamento aceitos;
- cobertura integral da competência;
- empregado x sócio/empregador;
- faltas em todos os dias;
- bases/remuneração zeradas;
- interação com FGTS/eConsignado;
- casos Gold/Marcos/Wilmar.

### Estado

B22 permanece **CONTRATO_OBRIGATORIO / implementação parcial recuperada, regressão real pendente**.

## 7. B23 — responsabilidade Fiscal/procuração não possui estado específico por DARF

O contrato exige que ocorrências como:

- DARF emitida pelo Fiscal;
- procuração revogada/expirada;
- impedimento RFB;

afetem a obrigação DARF, sem liberar FGTS/eConsignado por consequência.

Na implementação recuperada não existe decisão manual por fonte.

Também não foi localizado no V8F2 um estado específico equivalente a:

- `IMPEDIDA_EXTERNAMENTE` para DARF;
- `RESPONSABILIDADE_OUTRO_DEPARTAMENTO`;
- `SEM_PROCURACAO` aplicado à obrigação federal da Conferência.

A única decisão manual disponível é global por cliente.

Como demonstrado em B18, `JUSTIFICADO` global pode substituir o resultado automático do cliente inteiro e permitir fechamento.

### Consequência

Usar a decisão global para resolver apenas a DARF pode ocultar uma pendência real de FGTS/eConsignado.

### Estado

B23 permanece **CONTRATO_OBRIGATORIO / PRONTO_PARA_CORRIGIR**.

## 8. Achado adicional — fechamento manual ainda contorna derivação por obrigação

Além do fechamento automático, `fechar_clientes(...)` V8B pode registrar nova versão e colocar cliente como `FECHADA` por seleção de IDs, sem receber como pré-condição os estados individuais das obrigações.

Esse caminho deve ser reconciliado com B18/B39 durante a correção. Não cria novo bloqueador.

## 9. Síntese do bloco

- B18: defeito estrutural confirmado na decisão global;
- B19: **há correção real no V8F2**, ainda sem regressão canônica suficiente;
- B20: perfil MEI detectado, mas obrigação DAE ausente;
- B21: Conference usa saldo federal final corretamente, parser/casos reais ainda pendentes;
- B22: afastamento possui suporte parcial, motor/regressões pendentes;
- B23: impedimentos/responsabilidade DARF continuam sem decisão por fonte.

Nenhum item é promovido para `CORRIGIDO_TESTADO` ou `CORRIGIDO_HOMOLOGADO`.

A V8 permanece **NÃO HOMOLOGADA**.

## 10. Próxima frente

Prosseguir com eConsignado:

- B24 — fora do orquestrador;
- B25 — universo excessivo;
- B26 — falso CONFERIDO;
- B27 — retorno residual;
- B28 — idempotência/retry.
