# Auditoria canônica V8 — Etapa 27

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Esta etapa aprofundou B15 — descoberta/leitura/vínculo — e sua relação com B01, B12, B16 e a recomposição da Conferência.

## 2. Evidência operacional

O status V8F2 registra casos em que:

- documento foi reprocessado, mas continua sem cliente;
- tipo/competência foram reconhecidos, mas o vínculo foi perdido;
- documento real existe, mas a Conferência mantém ocorrência de ausência;
- reprocessamento não garante `descoberta → leitura → identidade → competência → persistência → cruzamento → Conferência`.

Isso demonstra que o problema não pode ser tratado apenas no parser.

## 3. Contrato criado

Foi criado `docs/architecture/CONTRATO_PIPELINE_DOCUMENTAL_V8.md`.

O pipeline passa a possuir estágios observáveis:

`DESCOBERTO → INGERIDO → LIDO → CLASSIFICADO → IDENTIFICADO → COMPETENCIA_DEFINIDA → EXTRAIDO → PERSISTIDO → VINCULADO → COMPOSTO → CONFERENCIA_RECALCULADA`

## 4. Nova regra de diagnóstico

`DOCUMENTO_AUSENTE` só pode ser emitido quando a obrigação é aplicável e a busca foi realmente concluída sem candidato compatível.

Se o arquivo existir mas falhar em qualquer estágio, a ocorrência deve apontar a causa técnica, como:

- identidade;
- competência;
- extração;
- vínculo;
- composição;
- recálculo.

## 5. Casos-mestre

### MMT Empreendimentos

Deve sair de `Cliente não identificado` ou indicar exatamente o estágio/evidência que impede identificação.

### Alex Douglas

DARF real deve percorrer a cadeia e alimentar a Conferência; o contexto de FGTS zero/rescisão é regra independente.

### Jair 449/450

Após reprocessamento candidato e recuperação segura, ambos devem chegar ao estágio `COMPOSTO`, preservando inscrição/matrícula e cliente correto.

## 6. Redescoberta x reprocessamento

A auditoria passa a exigir distinção explícita entre:

- reprocessar arquivo já indexado;
- redescobrir novos/alterados nas conexões;
- reconciliar arquivo físico sem índice;
- reavaliar órfão já persistido.

Um botão não pode alegar executar todas essas ações se o backend percorre apenas uma delas.

## 7. Banco x filesystem

A homologação exigirá auditoria bidirecional para detectar:

- físico sem índice;
- índice sem físico;
- alteração de hash;
- duplicidade física;
- órfão potencialmente vinculável.

## 8. Estado dos bloqueadores

- B15 permanece `CONFIRMADO_RUNTIME`;
- B16 permanece `CONFIRMADO_RUNTIME`;
- B49 permanece `CONTRATO_OBRIGATORIO`;
- B01 permanece `REGRESSAO_CONFIRMADA`;
- nenhum item foi marcado corrigido.

## 9. Próxima frente

Auditar aplicabilidade documental em MEI/DAE, FGTS zero, afastamento integral e saldo previdenciário zerado por deduções.
