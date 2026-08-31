# Auditoria canônica V8 — Etapa 47

Data: 31/08/2026  
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Continuação da reconstrução operacional sobre deltas preservados, com foco em:

- B12 — Multi-Extrato;
- B13 — federal x FGTS rural/múltiplas matrículas;
- B14 — múltiplas GFD/FGTS;
- B15 — descoberta → vínculo;
- B16 — identidade PF/CAEPF;
- B17 — deduplicação lógica.

Foram confrontados principalmente V1, V3A/V4, V8B e V8F2 com os contratos canônicos de parser, composição FGTS e deduplicação.

## 2. B12 — a Conferência reduz múltiplos Extratos a um único documento

No `conference.py` do V8F2 existe:

```python
def _ultimo_tipo(emp, tipo):
    itens = [...]
    processados = [x for x in itens if x.status == 'PROCESSADO']
    return (processados or itens)[-1]
```

Na montagem de cada cliente:

```python
extr = _ultimo_tipo(emp, 'EXTRATO_MENSAL')
```

Toda a expectativa de folha/federal/FGTS Domínio usada depois é derivada somente de `extr`.

Consequência: se o mesmo cliente possui dois Extratos economicamente necessários — por exemplo, matrículas/unidades distintas — a Conferência escolhe um deles e descarta o outro da composição operacional, embora ambos continuem presentes no dossiê.

Isso é exatamente incompatível com o caso Jair e com o contrato canônico de composição.

### O defeito também alcança versionamento/retificação

`closing/retification.py` V4 repete a mesma estratégia:

```python
def _latest(rows, tipo):
    ...

extr = _latest(rows, 'EXTRATO_MENSAL')
```

O snapshot fechado registra folha/federal/FGTS Domínio com base em um único Extrato.

Logo B12 não afeta apenas a tela da Conferência: pode produzir snapshot de fechamento materialmente incompleto.

### Estado

B12 permanece **CONFIRMADO_RUNTIME / PRONTO_PARA_CORRIGIR**.

## 3. B13 — o modelo atual não consegue expressar Jair corretamente

O contrato canônico determina, para múltiplas matrículas/unidades:

- preservar identidade documental por inscrição;
- não somar federal consolidado repetido;
- permitir FGTS aditivo quando as matrículas representam componentes econômicos distintos.

O desenho recuperado não possui essa composição dimensional na Conferência:

1. escolhe um único Extrato;
2. lê `saldo_total_apuracao_dominio` desse Extrato;
3. lê `fgts_total` desse mesmo Extrato;
4. compara esses valores a um único DARF/uma única GFD também escolhidos por `_ultimo_tipo`.

Portanto não existe, nesse caminho, estrutura capaz de produzir simultaneamente:

- federal consolidado uma única vez;
- FGTS somado por matrículas distintas;
- proveniência por Extrato/matrícula.

O caso Jair exige exatamente essa diferença entre **unidade de consolidação federal** e **componentes de FGTS**.

### Retificação agrava o risco

O snapshot V4 também reduz Extrato/GFD a `_latest`, de modo que uma segunda matrícula pode parecer simples substituição/alteração do “último documento” em vez de componente aditivo da mesma competência.

### Estado

B13 permanece **CONFIRMADO_RUNTIME / PRONTO_PARA_CORRIGIR**.

## 4. B14 — GFD também é reduzida a uma única evidência

No V8F2:

```python
gfd = _ultimo_tipo(emp, 'GUIA_FGTS_DIGITAL')
fgts_gfd = gd.get('fgts_total')
```

Não há, nessa composição da Conferência:

- classificação mensal;
- rescisória;
- antecipada;
- reemissão;
- substitutiva;
- complementar;
- matrícula/unidade distinta;
- relação econômica entre duas guias.

O snapshot de retificação V4 igualmente usa apenas:

```python
gfd = _latest(rows, 'GUIA_FGTS_DIGITAL')
```

Isso prova que múltiplas GFD não são compostas conforme natureza econômica na cadeia auditada.

A correção não deve simplesmente somar todas: precisa implementar o contrato de classificação antes da soma.

### Estado

B14 permanece **CONTRATO_OBRIGATORIO / PRONTO_PARA_CORRIGIR**, com implementação atual comprovadamente insuficiente para a composição exigida.

## 5. B15 — Conference depende exclusivamente do que já foi indexado em `processamento_arquivo`

`dossie_competencia(...)` V4 começa sua composição consultando:

```sql
FROM processamento_arquivo p
WHERE p.competencia=?
  AND COALESCE(p.documento_vigente,1)=1
```

A partir dessas linhas ele constrói:

- `documentos`;
- `dominio`;
- `esocial`;
- `ecac`;
- `fgts`;
- `guias`;
- pendências.

A Central de Conferência consome esse dossiê.

Portanto um arquivo fisicamente existente, mas que não chegou corretamente a `processamento_arquivo` com:

- competência;
- cliente_id;
- tipo;
- vigência;

não pode aparecer na Conferência apenas por existir no acervo físico.

Isso explica a natureza do B15 como falha de cadeia **descoberta → ingestão → identidade → competência → vínculo → dossiê**, e não como simples erro de renderização da Conference.

### Limite desta etapa

Os deltas recuperados não trazem a implementação integral de descoberta/arquivamento físico. Assim, esta etapa não atribui o ponto exato da perda de guias/extratos históricos a uma rotina específica.

### Estado

B15 permanece **CONFIRMADO_RUNTIME / INSPEÇÃO da origem física ainda necessária**.

## 6. B16 — cadastro 1:N de inscrições existe, mas a cadeia recuperada de processamento não prova consumo equivalente

O V1 confirma patrimônio válido no cadastro:

`cliente_inscricoes_v2` possui:

- `cliente_id`;
- `tipo`;
- `numero`;
- `principal`;
- estado/situação/origem;
- `UNIQUE(cliente_id,tipo,numero)`;
- índice por `numero`.

Esse schema suporta múltiplas inscrições por cliente, incluindo CAEPF/CNO/CEI e demais tipos tratados pela camada de cadastro.

No V8F2, entretanto, `_inserir_generico(...)` tenta identificar cliente usando, em essência:

```python
documento_contribuinte or cnpj or cpf
```

seguido de `_buscar_cliente(...)` importado do motor Domínio.

Os arquivos recuperados não incluem o corpo de `_buscar_cliente(...)`. Portanto não é correto afirmar nesta etapa qual consulta interna ele executa.

Também não foi recuperado, na Central V8F2, um caminho explícito que passe `cliente_inscricoes_v2.numero`/CAEPF como dimensão persistida da composição.

### Conclusão segura

A assimetria estrutural está confirmada:

- cadastro já possui identidade 1:N por inscrição;
- a camada recuperada da Central trabalha prioritariamente com documento principal/cliente_id e não expõe a inscrição documental como dimensão de composição;
- o corpo responsável pelo matching final não está disponível nos deltas, portanto a causa exata do vínculo PF/CAEPF permanece dependente da árvore canônica reconciliada.

### Estado

B16 permanece **CONFIRMADO_RUNTIME / INSPEÇÃO da função de identidade completa pendente**.

## 7. B17 — deduplicação atual é física e ainda estreita; não há fingerprint lógico/econômico recuperado

No V8F2, `_inserir_generico(...)` calcula SHA-256 e considera duplicado somente quando encontra simultaneamente:

```text
origem_id igual
caminho_origem igual
sha256 igual
```

Isso já é mais estreito que uma identidade física global: o mesmo conteúdo redescoberto por origem/caminho diferente pode não cair nessa condição.

Mais importante: nenhuma implementação recuperada em V4/V8F2 contém os conceitos exigidos pelo contrato:

- fingerprint documental lógico;
- grupo de equivalência;
- `REEMISSAO_EQUIVALENTE`;
- `VERSAO_SUCESSORA`;
- `UNIDADE_DISTINTA`;
- `COMPONENTE_ADITIVO`;
- relação indeterminada antes de compor valores.

### Retificação confirma a limitação

O V4 não classifica relação documental antes de gerar snapshot. Ele escolhe `_latest` para Extrato, DARF e GFD e compara valores agregados.

Isso pode confundir:

- reemissão equivalente com sucessora;
- segunda matrícula com substituição;
- duas GFD aditivas com duplicidade;
- documento materialmente igual com bytes diferentes.

### Estado

B17 permanece **CONTRATO_OBRIGATORIO / PRONTO_PARA_CORRIGIR**.

## 8. Raiz comum B12–B17

A estrutura atual preserva vários documentos no dossiê, mas a Conferência e o snapshot colapsam cedo demais para “o último documento do tipo”.

O desenho canônico deve mudar a unidade de composição para:

1. todas as evidências vigentes da obrigação;
2. identidade física;
3. identidade documental lógica;
4. identidade econômica/componente;
5. consolidação somente depois dessa classificação;
6. proveniência de cada componente usado no fechamento.

Isso preserva o patrimônio já existente e elimina a necessidade de regras especiais para Jair/Leosmar/GFD múltiplas.

## 9. Estados

Nenhum bloqueador é promovido para corrigido/testado/homologado.

- B12: confirmado no Conference e snapshot;
- B13: composição atual incapaz de representar federal consolidado + FGTS aditivo por matrícula;
- B14: composição multi-GFD ausente;
- B15: cadeia depende do índice `processamento_arquivo`; origem física exata ainda pendente;
- B16: cadastro 1:N preservado; matching de processamento completo ainda precisa da árvore reconciliada;
- B17: hash físico sem camada lógica/econômica recuperada.

A V8 permanece **NÃO HOMOLOGADA**.

## 10. Próxima frente

Prosseguir com os bloqueadores de aplicabilidade por fonte:

- B18 — decisão por fonte;
- B19 — FGTS zero;
- B20 — MEI/DAE;
- B21 — deduções previdenciárias;
- B22 — afastamentos/faltas;
- B23 — DARF sob responsabilidade Fiscal/impedimento RFB.
