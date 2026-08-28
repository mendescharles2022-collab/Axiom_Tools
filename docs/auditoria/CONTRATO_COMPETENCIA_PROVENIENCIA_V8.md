# Contrato V8 — Competência e proveniência temporal

Data: 28/08/2026
Status: **contrato de auditoria / regressão integral pendente**

## 1. Princípio central

Competência é dado de negócio. Data do arquivo, data de upload e data de processamento são apenas evidências auxiliares.

O sistema não pode deslocar documento entre competências silenciosamente por causa do relógio do filesystem.

## 2. Hierarquia de determinação

A competência deve ser determinada pela evidência mais forte disponível, nesta ordem conceitual:

1. competência/período de apuração explicitamente declarado no documento;
2. competência retornada de forma estruturada pela fonte oficial/integração;
3. contexto explícito herdado de uma ocorrência/anexo dentro de cliente + competência já definidos;
4. competência inferida por calendário configurado para o tipo/fonte;
5. revisão humana quando as evidências forem insuficientes ou conflitantes.

Nunca usar data de criação/modificação do PDF como fonte autoritativa isolada.

## 3. Proveniência obrigatória

Toda competência persistida deve indicar sua origem lógica, por exemplo:

```text
DOCUMENTO_EXPLICITO
FONTE_ESTRUTURADA
CONTEXTO_OCORRENCIA
CALENDARIO_INFERIDO
DECISAO_MANUAL
```

E guardar, quando aplicável:

- valor da competência;
- fonte;
- regra/calendário utilizado;
- versão da regra;
- data/hora da determinação;
- confiança;
- evidência textual/estruturada de suporte.

## 4. Calendário configurável

Quando o tipo documental realmente exigir inferência, a regra padrão do calendário operacional deve ser configurável.

Regra de referência aprovada para o fluxo mensal: a janela de uma competência pode compreender do dia 25 do próprio mês da competência até o dia 09 do mês seguinte.

Exemplo conceitual:

```text
competência 08/2026
janela padrão: 25/08/2026 até 09/09/2026
```

Essa regra é fallback de inferência, não substitui competência explícita no documento.

## 5. Dezembro e 13º salário

Dezembro e 13º possuem janelas/exceções próprias e devem ser configuráveis por exercício.

Não espalhar datas especiais em condicionais hardcoded pelos parsers.

O motor deve consultar um calendário versionado, capaz de registrar exceções anuais.

## 6. Contexto de anexos na Conferência

Documento anexado diretamente de uma ocorrência deve herdar como contexto candidato:

- cliente;
- competência;
- fonte/obrigação da ocorrência.

Mas a leitura do documento ainda deve validar conflito material.

Se o PDF declarar competência diferente da ocorrência:

- não sobrescrever silenciosamente;
- marcar conflito de competência;
- exigir resolução antes de promoção/vínculo definitivo.

## 7. Reprocessamento

Reprocessar não pode degradar competência forte para inferida.

Exemplo:

```text
vigente: 08/2026 — DOCUMENTO_EXPLICITO
candidato: 07/2026 — CALENDARIO_INFERIDO
```

O candidato deve ser rejeitado ou encaminhado à revisão, nunca promovido automaticamente apenas por nova leitura de menor qualidade.

## 8. Retificação

Documento novo de competência fechada deve ser comparado com a versão fechada daquela competência.

Não usar a competência operacional atualmente aberta para remapear um documento que declara período anterior.

Mudança material gera candidato de retificação da competência correta.

## 9. Fontes específicas

### Domínio

Usar competência/tipo de cálculo declarados no Extrato quando disponíveis.

### DARF/e-CAC

Usar período de apuração/competência fiscal declarada no documento/retorno.

### FGTS Digital

Usar competência declarada na guia/arquivo e natureza mensal/rescisória separadamente.

### eSocial

Quando o documento/retorno não trouxer competência suficiente, calendário configurado pode ser usado como fallback, mantendo proveniência da inferência.

### eConsignado

A consulta nasce vinculada à competência/chamada que originou o job. Retorno não deve migrar para outra competência por data de execução da API.

## 10. Conflitos

Quando duas evidências fortes divergirem:

- não escolher silenciosamente;
- manter ambas como evidência;
- classificar `CONFLITO_COMPETENCIA`;
- impedir saída final até resolução quando a divergência for material.

## 11. Regressões obrigatórias

1. competência explícita vence data do arquivo;
2. competência explícita vence inferência de calendário;
3. anexo da ocorrência herda contexto, mas conflito explícito é detectado;
4. reprocessamento não degrada `DOCUMENTO_EXPLICITO` para `CALENDARIO_INFERIDO`;
5. documento anterior em competência fechada entra na retificação correta;
6. janela padrão mensal é versionada/configurável;
7. dezembro e 13º usam exceções próprias por exercício;
8. eConsignado permanece na competência do job;
9. arquivo sem evidência suficiente vai para revisão, não recebe competência fabricada;
10. toda competência exibida pela Conferência consegue explicar sua origem.

## 12. Critério de aceite

Nenhum motor especialista está homologado enquanto puder produzir competência sem proveniência ou sobrescrever uma evidência temporal mais forte por heurística mais fraca.
