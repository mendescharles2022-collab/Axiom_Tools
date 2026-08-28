# Contrato V8 — Máquinas de estado separadas

Data: 28/08/2026
Status: **contrato canônico de auditoria / implementação pendente de consolidação**

## 1. Problema confirmado

A base auditada apresenta mistura semântica entre estados técnicos e estados de negócio.

Exemplos confirmados:

- persistência de sessão pode registrar `COM_PENDENCIAS`, enquanto camada visual converte 100% para `PROCESSAMENTO_CONCLUIDO`;
- `PROCESSADO` é utilizado em saída como se fosse validado;
- V7 mapeava `PRONTA` visualmente para `Em conferência` mesmo antes de verificar estágio documental;
- eConsignado pode mostrar `CONFERIDO` apesar de fontes incompatíveis/ausentes;
- decisão global antiga conseguia concluir cliente inteiro.

A V8 precisa separar máquinas de estado independentes.

## 2. Regra central

Nunca reutilizar o mesmo status para responder perguntas diferentes.

Exemplos:

```text
O worker terminou?                 -> status técnico da sessão
O PDF foi lido?                    -> status técnico do documento
A obrigação bateu?                 -> status da obrigação
O cliente encerrou o mês?          -> status do ciclo mensal
A API respondeu?                   -> status da consulta externa
Existe mudança após fechamento?    -> status de retificação
Pode imprimir/entregar?            -> autorização derivada, não status técnico
```

## 3. Máquina A — sessão técnica de processamento

Estados canônicos sugeridos:

```text
NAO_INICIADA
PROCESSANDO
PAUSADA
CONCLUIDA
CONCLUIDA_COM_FALHA_TECNICA
INTERROMPIDA
CANCELADA
```

Regras:

- percentual indica percurso técnico;
- 100% não significa conferência concluída;
- divergência contábil/documental não transforma sessão em `COM_PENDENCIAS`;
- falha técnica real pode coexistir com percentual 100% percorrido.

## 4. Máquina B — documento/processamento individual

Estados conceituais:

```text
DESCOBERTO
EM_LEITURA
PROCESSADO
REVISAO_TECNICA
FALHA_TECNICA
CANDIDATO
REJEITADO
VIGENTE
ARQUIVADO/HISTORICO
```

O vocabulário final pode ser ajustado ao schema, mas deve distinguir:

- sucesso técnico;
- necessidade de revisão;
- candidato de reprocessamento;
- versão vigente.

`PROCESSADO` não autoriza saída.

## 5. Máquina C — obrigação/fonte na Conferência

Estados mínimos:

```text
PENDENTE
CONFERIDA
DIVERGENTE
NAO_APLICAVEL
JUSTIFICADA
IMPEDIDA_EXTERNAMENTE
EM_REVISAO
RETIFICACAO
```

Exemplos de fontes/obrigações:

- DARF/federal;
- FGTS mensal;
- FGTS rescisório/composição;
- DAE MEI;
- eConsignado;
- eSocial/S-1299 quando aplicável.

Decisão é por obrigação, não por cliente inteiro.

## 6. Máquina D — ciclo mensal do cliente

Estados de negócio devem refletir estágio agregado real, por exemplo:

```text
AGUARDANDO_PROCESSAMENTO
EM_PROCESSAMENTO
EM_CONFERENCIA
PENDENTE_CONFERENCIA
ADIADA_PROXIMA_CHAMADA
SEM_MOVIMENTO
FECHADA
RETIFICACAO_DETECTADA
EM_RETIFICACAO
RETIFICADA
```

O estado agregado é derivado do contexto mensal e das obrigações aplicáveis.

Ele não deve ser obtido apenas traduzindo um status técnico de documento.

## 7. Máquina E — consulta externa

Cada integração tem resultado próprio.

Exemplo eConsignado:

```text
NAO_CONSULTADA
EM_CONSULTA
COM_CONSIGNADO
SEM_CONSIGNADO
SEM_PROCURACAO
ERRO_TECNICO
```

Esses estados não são conclusão da obrigação na Conferência.

`COM_CONSIGNADO` ainda precisa de cruzamento.

## 8. Máquina F — retificação

Estados conceituais:

```text
NAO_APLICAVEL
CANDIDATA
EM_ANALISE
REJEITADA_SEM_MUDANCA
PENDENTE
CONCLUIDA
```

A versão anterior permanece vigente até promoção/conclusão válida.

Enquanto houver retificação material pendente, saída final fica bloqueada.

## 9. Autorização de saída

Não criar um status genérico `VALIDADO` baseado em documento.

A autorização deve ser função derivada:

```text
pode_sair(cliente, competencia) =
    ciclo == FECHADA
    AND sem_retificacao_material_pendente
    AND documento_pertence_ao_cliente_competencia
    AND documento_eh_tipo_de_saida_permitido
```

## 10. Transições, não atribuições soltas

Mudança de estado deve passar por funções de domínio que validem transição.

Evitar SQL espalhado como:

```sql
UPDATE ... SET status='X'
```

em views/workers sem regra central.

Cada transição crítica deve registrar:

- estado anterior;
- estado novo;
- evento/causa;
- usuário/job;
- data/hora;
- correlação.

## 11. Estados derivados na UI

A interface pode usar rótulos amigáveis, mas sem inventar outra verdade persistente.

Exemplo:

```text
status técnico = CONCLUIDA
label = Processamento concluído
```

Não manter `status` no banco dizendo uma coisa e `status_operacional` calculado dizendo outra coisa para o mesmo conceito.

## 12. Caso Monitor de Execução

Defeito confirmado:

- persistência grava sessão como `COM_PENDENCIAS` quando há documentos em `REVISAO`;
- `listar_sessoes()` / `status_sessao()` podem mostrar `PROCESSAMENTO_CONCLUIDO` aos 100%.

Correção:

- remover `COM_PENDENCIAS` como mistura de resultado técnico com Conferência;
- sessão termina `CONCLUIDA` ou `CONCLUIDA_COM_FALHA_TECNICA`;
- documentos em revisão são contagem técnica separada;
- divergências de batimento ficam na Conferência.

## 13. Regressões obrigatórias

1. sessão 100% + divergência contábil = sessão concluída, cliente ainda pendente na Conferência;
2. documento `PROCESSADO` + cliente não FECHADA = saída bloqueada;
3. eConsignado `COM_CONSIGNADO` + fontes incompatíveis = obrigação não `CONFERIDA`;
4. DARF justificada + FGTS pendente = cliente não FECHADA;
5. cliente adiado = fora da chamada atual mesmo que documentos estejam processados;
6. nova evidência em FECHADA = retificação candidata sem alterar versão vigente;
7. abrir Conference não provoca transição;
8. rótulo visual não altera estado persistido.

## 14. Migração

Antes de remover/renomear estados antigos:

- inventariar valores existentes no banco;
- mapear semanticamente cada valor;
- não converter ambiguidades silenciosamente;
- preservar histórico original quando necessário;
- atualizar testes e relatórios.

## 15. Critério de aceite

A V8 não estará homologada enquanto uma mesma coluna/status puder significar simultaneamente 'worker terminou', 'documento foi lido', 'cliente está conferido' ou 'pode entregar'.
