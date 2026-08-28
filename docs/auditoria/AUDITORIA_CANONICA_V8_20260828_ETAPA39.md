# Auditoria canônica V8 — Etapa 39

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 39 consolida B48, B49 e B50:

- retenção/limpeza;
- coerência banco ↔ filesystem;
- distinção entre hash físico, identidade documental e obrigação econômica.

## 2. Retenção e limpeza — B48

O contrato de retenção já estabelece que fechamento de competência não autoriza exclusão de documentos do mês.

A rotina de manutenção precisa classificar itens antes de remover e operar por fluxo equivalente a:

`Simular → revisar → confirmar → executar → relatório`

Podem expirar, conforme política:

- temporários;
- caches reconstruíveis;
- staging abandonado comprovadamente sem job ativo;
- artefatos transitórios cuja fonte canônica esteja preservada.

Não podem ser apagados automaticamente:

- originais necessários à auditoria;
- evidências de fechamento/retificação;
- único arquivo físico de documento persistido;
- backup protegido/necessário ao rollback;
- candidato ainda relevante à auditoria.

B48 permanece `CONTRATO_OBRIGATORIO`; prazos finais de retenção continuam configuração operacional, não hipótese da auditoria.

## 3. Banco ↔ filesystem — B49

A coerência deve ser bidirecional:

- banco aponta para arquivo inexistente → ocorrência explícita;
- arquivo gerenciado que deveria estar indexado mas não está → ocorrência de não indexado;
- mudança de hash → nova evidência/candidato;
- mesmo hash em outra origem → não duplicar obrigação, mas preservar origem quando relevante.

Isso se integra ao pipeline documental: arquivo existente que não chegou à Conferência é falha técnica de descoberta/ingestão/vínculo, não `DOCUMENTO_AUSENTE` genérico.

B49 permanece `CONTRATO_OBRIGATORIO` e precisa de varredura no runtime reconciliado.

## 4. Hash x obrigação — B50

Hash responde apenas à identidade física dos bytes.

A V8 precisa de três camadas:

1. hash físico;
2. fingerprint/identidade documental lógica;
3. identidade econômica da obrigação.

Regras:

- hash igual → mesmo conteúdo físico;
- hash diferente não prova obrigação diferente;
- reemissão pode ter bytes diferentes e mesmo fato econômico;
- matrículas distintas podem ter componentes aditivos;
- o mesmo par de documentos pode ser repetido em uma dimensão e aditivo em outra.

## 5. Reprocessamento

Reprocessar o mesmo arquivo físico cria nova interpretação candidata, não novo PDF por definição.

A versão vigente permanece até promoção segura.

A limpeza não pode apagar a evidência que permita auditar candidato rejeitado quando ela ainda for necessária.

## 6. Retificação

Nova evidência física/material em competência fechada:

- não reescreve documento/snapshot antigo;
- entra como nova evidência;
- passa por materialidade;
- cria retificação candidata quando necessário.

Reemissão equivalente sem mudança econômica não cria retificação artificial.

## 7. Regressões mínimas

- mesmo hash reaparece → sem duplicação econômica;
- mesmo nome com hash diferente → mudança detectada;
- hashes diferentes mas reemissão equivalente → não somar;
- unidades/matrículas distintas → composição conforme obrigação;
- arquivo físico removido/indisponível → ocorrência explícita;
- físico não indexado → reconciliação detecta;
- simulação de limpeza produz zero alteração;
- limpeza não remove documento referenciado por fechamento/retificação;
- invariantes banco ↔ filesystem permanecem válidas após manutenção.

## 8. Estado dos bloqueadores

- B48 — contrato obrigatório, não homologado;
- B49 — contrato obrigatório, inspeção runtime pendente;
- B50 — contrato obrigatório, regressão documental pendente;
- nenhum recebe `CORRIGIDO_HOMOLOGADO` nesta etapa.

## 9. Próxima frente

Revisar os bloqueadores restantes de prioridade alta contra a matriz central e identificar quais já possuem contrato completo e quais ainda carecem de prova/teste antes da fase de implementação.
