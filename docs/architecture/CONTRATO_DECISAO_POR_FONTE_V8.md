# Contrato V8 — Decisão e justificativa por fonte/obrigação

Data: 28/08/2026
Status: **contrato obrigatório / V8 não homologada**

## 1. Problema

A decisão manual global por cliente/competência é insuficiente para a operação real.

Um mesmo cliente pode ter simultaneamente:

- DARF resolvida/justificada;
- FGTS pendente;
- eConsignado divergente;
- DAE não aplicável;
- FGTS rescisório em composição;
- fonte impedida externamente;
- outra obrigação normalmente exigível.

Uma decisão global pode ocultar pendência válida de outra fonte.

## 2. Chave canônica

Toda decisão manual deve ser registrada por:

`competencia + cliente_id + obrigacao + escopo_componente`

`escopo_componente` é opcional, mas obrigatório quando a própria obrigação possui componentes independentes, por exemplo FGTS mensal x rescisório.

## 3. Estados mínimos

Cada obrigação deve poder assumir, conforme o domínio:

- `PENDENTE`;
- `CONFERIDA`;
- `DIVERGENTE`;
- `JUSTIFICADA`;
- `NAO_APLICAVEL`;
- `IMPEDIDA_EXTERNAMENTE`;
- `RETIFICACAO`.

A situação agregada do cliente é derivada das obrigações; nunca o contrário.

## 4. Justificativa não altera aplicabilidade histórica sem evidência

`JUSTIFICADA` resolve uma ocorrência operacional específica.

Ela não deve:

- mudar silenciosamente o cadastro mestre;
- transformar outra fonte em não aplicável;
- criar regra permanente para competências futuras;
- apagar a evidência da pendência original.

## 5. Metadados obrigatórios da decisão

Registrar:

- obrigação/fonte;
- estado anterior;
- novo estado;
- motivo padronizado;
- observação livre quando necessário;
- usuário;
- data/hora;
- documentos/evidências vinculados;
- origem da ação;
- correlation_id;
- revisão do estado mensal utilizada na decisão.

## 6. Motivos sugeridos

Entre outros:

- sem movimento na competência;
- afastamento integral;
- ausência de incidência;
- saldo zerado por dedução/compensação;
- responsabilidade de outro departamento;
- procuração revogada/expirada;
- documento ainda não emitido;
- recolhimento rescisório antecipado;
- próxima chamada;
- pagamento direto informado;
- outro motivo documentado.

Motivo e estado não são a mesma coisa.

Exemplo: procuração expirada pode levar DARF a `IMPEDIDA_EXTERNAMENTE`, não simplesmente `CONFERIDA`.

## 7. Fechamento agregado

O cliente só pode fechar quando todas as obrigações `APLICAVEIS` estiverem em estado terminal aceitável.

Estados terminais aceitáveis, conforme regra do agregador:

- `CONFERIDA`;
- `JUSTIFICADA`;
- `NAO_APLICAVEL`;
- `IMPEDIDA_EXTERNAMENTE` quando a política operacional permitir fechamento justificado.

`DIVERGENTE`, `PENDENTE` e `RETIFICACAO` bloqueiam fechamento.

## 8. Sem movimento

`Sem movimento nesta competência` é uma decisão mensal de maior alcance, mas ainda assim precisa gerar as obrigações derivadas como `NAO_APLICAVEL` de forma explicável e auditável.

A marcação não deve ser herdada automaticamente pela próxima competência.

## 9. Migração do legado global

Decisões globais antigas não podem ser copiadas cegamente para todas as fontes.

Na migração:

- quando a fonte puder ser identificada com segurança, converter para decisão específica;
- quando não puder, preservar como decisão legada/ambígua para revisão;
- nunca fabricar justificativa de FGTS/eConsignado a partir de uma decisão originalmente tomada apenas para DARF.

## 10. Regressão mínima

1. justificar DARF e provar que FGTS permanece pendente;
2. marcar FGTS `NAO_APLICAVEL` e provar que DARF continua exigível;
3. registrar eConsignado divergente e provar que decisão de outra fonte não o fecha;
4. aplicar `Sem movimento` e provar derivação correta das obrigações daquele mês;
5. reverter `Sem movimento` e provar preservação do histórico e reabertura das expectativas;
6. repetir a mesma decisão e provar idempotência;
7. tentar decidir sobre revisão antiga e provar bloqueio de escrita obsoleta.
