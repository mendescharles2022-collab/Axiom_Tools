# Auditoria canônica V8 — Etapa 50

Data: 31/08/2026  
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Auditoria dos bloqueadores de parser e competência:

- B29 — Diretor ≠ empregado;
- B30 — federal autoritativo;
- B31 — competência/proveniência;
- B32 — IRRF por competência de pagamento;
- B33 — dezembro/13º e calendário versionado.

A análise confronta os contratos canônicos com os deltas operacionais materializados até V8F2, especialmente `central.py`, `conference.py`, `motors/ecac_engine.py` e o validador V8F2.

## 2. B29 — o defeito permanece confirmado historicamente, mas o parser Domínio integral não está nos deltas recuperados

O contrato do Extrato Domínio exige classificar pessoas usando, em conjunto:

- prefixo/tipo da linha (`Empr.` / `Contr.`);
- campo `Vínculo`;
- rubricas;
- totais de empregados/contribuintes;
- bases de FGTS/INSS;
- situação apenas como estado operacional.

A regressão real P DA SILVA CARMO prova que `Situação: Trabalhando` não pode transformar diretor/contribuinte em empregado celetista.

Nos deltas V8 materializados nesta sessão, o especialista `motors/dominio_engine.py` e a implementação integral de `_dados_extrato(...)` não estão presentes. `central.py` apenas os importa da instalação-base.

Consequentemente esta etapa não possui evidência nova suficiente para afirmar:

- que o parser atual continua errando Diretor;
- ou que já foi corrigido.

O consumidor `conference.py` depende de campos já extraídos pelo Domínio, portanto uma classificação errada a montante continua capaz de contaminar FGTS/quantidade de funcionários.

### Estado

B29 permanece **CONFIRMADO_RUNTIME / INSPEÇÃO do parser Domínio completo pendente**.

Não promover nem rebaixar o bloqueador por ausência do arquivo-base nos deltas.

## 3. B30 — o consumidor da Conferência já usa corretamente o saldo federal autoritativo

No V8B/V8F2, `_check_darf_folha(...)` prioriza:

```python
total_esperado = exd.get("saldo_total_apuracao_dominio")
```

A montagem da linha também expõe:

- composição detalhada;
- IRRF folha;
- PIS folha;
- SENAR/Funrural;
- deduções;
- saldo final esperado.

Isso está alinhado com o contrato canônico:

`Apuração Tributos Federais → Saldo à recolher`

é o valor agregado autoritativo para o batimento federal do Extrato Domínio.

### Limite

O parser Domínio integral que preenche `saldo_total_apuracao_dominio` não está nos deltas materializados.

Logo há duas camadas distintas:

1. **consumo na Conferência** — coerente com a regra canônica;
2. **extração do Extrato** — ainda precisa ser provada no parser real e nos fixtures P DA SILVA CARMO / 2A Peças / Denes / Ponto Kent.

### Classificação

B30 deve ser registrado como:

**consumidor implementado corretamente / parser e regressão canônica ainda pendentes**.

Nenhuma promoção para `CORRIGIDO_TESTADO` ou `CORRIGIDO_HOMOLOGADO`.

## 4. B31 — houve avanço real de proveniência, porém ainda existe perda de informação no armazenamento central

### 4.1 Especialista e-CAC V8F2

`motors/ecac_engine.py` retorna competência juntamente com método de obtenção.

Exemplos recuperados:

- `Competência MM/AAAA` -> `DOCUMENTO`;
- `PA MM/AAAA` -> `DOCUMENTO`;
- `Período de Apuração MM/AAAA` -> `DOCUMENTO`;
- `Período de Apuração agosto/2026` -> `PERIODO_APURACAO_MES_EXTENSO`;
- `Período de Apuração 31/07/2026` -> `PERIODO_APURACAO`;
- fallback legado -> `DOCUMENTO` quando encontra competência.

O resultado do motor grava:

```python
"competencia": comp,
"competencia_metodo": comp_metodo,
```

Esse é patrimônio válido e deve ser preservado.

### 4.2 Validador V8F2

O validador possui regressão direta para:

```text
Período de Apuração agosto/2026 -> 08/2026
```

Também verifica que o reforço contextual e-CAC mantém a competência `08/2026`.

Isso prova que o delta V8F2 contém uma melhoria funcional concreta na leitura temporal do DARF.

### 4.3 Persistência central

`processamento_arquivo` continua possuindo coluna principal `competencia`, sem colunas dedicadas visíveis nos deltas para:

- `competencia_origem`;
- regra/calendário utilizado;
- versão da regra;
- confiança temporal;
- evidência temporal.

`central.py` preserva `competencia_metodo` dentro de `dados_json`, em `_analise`, mas isso não equivale ao modelo completo de proveniência exigido pelo contrato.

Além disso, `_capturar_competencia_generica(...)` retorna apenas a competência e não o método de captura.

No caminho legado de `_classificar_texto(...)`, DARF/FGTS podem usar essa função genérica e inserir apenas `competencia` no dicionário.

### 4.4 Hierarquia de força

Não foi recuperada nos deltas uma função central que compare explicitamente força temporal, por exemplo:

```text
DOCUMENTO_EXPLICITO > FONTE_ESTRUTURADA > CONTEXTO > CALENDARIO_INFERIDO
```

O reprocessamento V8F2 também não possui, no código recuperado, um compare-and-promote específico para impedir degradação de uma competência forte para inferência mais fraca.

### Estado

B31 permanece **CONTRATO_OBRIGATORIO / parcialmente implementado**.

Preservar:

- `competencia_metodo` dos motores especialistas;
- reconhecimento ampliado de PA no e-CAC.

Completar:

- proveniência persistente estruturada;
- ranking de força;
- regra de conflito;
- proteção contra degradação no reprocessamento;
- regressões cross-motor.

## 5. B32 — a semântica de IRRF por competência de pagamento continua sem prova de implementação

O contrato temporal comprova por documentos reais que o Extrato Domínio possui simultaneamente:

- IRRF conforme competência do cálculo;
- IRRF conforme competência do pagamento;
- aviso de que IRRF utiliza competência de pagamento.

Nos deltas recuperados, `conference.py` apenas recebe/agrega valores já extraídos do Extrato e classifica receitas DARF como `IRRF_FOLHA`.

Não existe nesses deltas evidência de que o parser Domínio:

- extraia as duas colunas separadamente;
- persista `competencia_calculo` e `competencia_pagamento`;
- selecione a dimensão de pagamento para confronto fiscal;
- trate férias/IRRF em competência distinta corretamente.

Também não existe no V8F2 uma regressão específica de IRRF cálculo x pagamento.

### Estado

B32 permanece corretamente classificado como **TESTE_PENDENTE_RUNTIME**.

Não transformar risco documental em defeito confirmado sem recuperar/testar o parser Domínio integral.

## 6. B33 — calendário eSocial configurável existe, mas a cobertura do 13º ainda não está comprovada

### 6.1 Patrimônio já existente

Os deltas V/V2/V8C mostram uma área própria de calendário eSocial:

```text
GET  /processamento/calendario-esocial
POST /processamento/calendario-esocial/regra
POST /processamento/calendario-esocial/excecao
POST /processamento/calendario-esocial/excecao/<competencia>/excluir
```

A regra padrão permite configurar:

- ativo;
- dia de início;
- dia de fim.

A exceção permite configurar por competência:

- competência;
- data inicial;
- data final;
- tipo;
- observação;
- ativo.

`processamento_config` também possui defaults:

```text
esocial_dia_inicio = 25
esocial_dia_fim = 9
esocial_calendario_ativo = 1
```

Portanto o sistema já possui uma fundação real de calendário configurável e exceções por competência. Isso deve ser preservado.

### 6.2 Módulo-base ausente

O arquivo `modules/processing/calendar_esocial.py` é importado pelos deltas, mas não está contido nos pacotes materializados desta etapa.

Assim ainda não foi possível verificar:

- schema interno das exceções;
- versionamento formal das regras;
- lógica exata de virada entre meses;
- precedência documento explícito x calendário;
- comportamento específico dezembro/13º;
- testes anuais.

### 6.3 Lacuna concreta nos fallbacks recuperados

Os fallbacks de competência presentes em `central.py` e no especialista e-CAC V8F2 usam regex explícito de meses `01–12`.

Por exemplo, `_capturar_competencia_generica(...)` aceita:

```text
(0[1-9]|1[0-2])/AAAA
```

O especialista e-CAC também trabalha explicitamente com `01–12` em seus padrões principais.

A configuração de `competencia_ativa`, entretanto, aceita `01–13/AAAA`.

Isso demonstra uma assimetria real:

- a camada operacional reconhece a existência da competência 13;
- os fallbacks temporais recuperados não a tratam explicitamente.

O fallback legado do motor e-CAC não está materializado, portanto não é possível afirmar que todo documento `13/AAAA` falha; apenas que a cobertura explícita V8F2 recuperada não prova esse caso.

### Estado

B33 permanece **CONTRATO_OBRIGATORIO / implementação parcial**.

Patrimônio a preservar:

- calendário eSocial configurável;
- exceções por competência;
- parâmetros 25→09.

Pendências:

- recuperar `calendar_esocial.py`;
- provar dezembro e 13º;
- versionar regras/exceções de forma auditável;
- assegurar precedência da competência explícita;
- criar regressões 12/AAAA, 13/AAAA e virada anual.

## 7. Síntese do bloco

- B29: parser Domínio integral ausente dos deltas; não atribuir correção especulativa;
- B30: consumidor federal da Conferência já está coerente;
- B31: `competencia_metodo` é avanço real, mas proveniência estruturada e ranking de força ainda faltam;
- B32: continua teste pendente, sem prova de coluna temporal correta do IRRF;
- B33: calendário configurável existe e deve ser preservado; 13º/versionamento ainda não comprovados.

Nenhum bloqueador é promovido para corrigido/testado/homologado.

A V8 permanece **NÃO HOMOLOGADA**.

## 8. Próxima frente

Prosseguir com banco/dados e máquinas de estado:

- B34 — `classificacao_inativacao` string/Enum;
- B35 — foreign keys/invariantes;
- B36 — migração do estado global antigo para decisões por fonte;
- B37 — máquinas de estado misturadas;
- B38 — autenticação/CSRF nas mutações;
- B39 — seleção manual por IDs;
- B40 — concorrência lógica.
