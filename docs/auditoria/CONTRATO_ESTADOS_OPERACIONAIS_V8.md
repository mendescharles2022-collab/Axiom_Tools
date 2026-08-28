# Contrato V8 — Máquinas de estado operacionais

Data: 28/08/2026
Status: **contrato de auditoria / implementação ainda não homologada**

## 1. Problema confirmado

A base canônica mistura conceitos distintos de estado.

Exemplo confirmado no Monitor de Execução:

- persistência grava sessão como `COM_PENDENCIAS` quando existem documentos em `REVISAO`;
- `listar_sessoes()` / `status_sessao()` podem apresentar visualmente `PROCESSAMENTO_CONCLUIDO` quando o percentual chega a 100%.

Assim, existem duas verdades para a mesma sessão.

Em paralelo, a Conferência/Fechamento também confundem `PROCESSADO`, `PRONTA`, `Em conferência`, decisão manual e `FECHADA`.

A correção exige separar máquinas de estado, não apenas renomear rótulos.

## 2. Máquina A — sessão técnica de processamento

Representa somente execução dos motores.

Estados mínimos:

- `NAO_INICIADO`;
- `PROCESSANDO`;
- `PAUSADO` quando suportado;
- `CONCLUIDO`;
- `CONCLUIDO_COM_FALHA_TECNICA`;
- `INTERROMPIDO` / `CANCELADO` conforme suporte real.

Regras:

- 100% = todos os itens da sessão foram percorridos;
- divergência documental não muda sessão para pendente;
- documento em revisão técnica pode compor contador de pendências técnicas;
- conclusão técnica não fecha cliente.

## 3. Máquina B — ciclo mensal do cliente

Representa posição do cliente dentro da competência/chamada.

Estados conceituais esperados:

- `AGUARDANDO_PROCESSAMENTO`;
- `EM_PROCESSAMENTO`;
- `EM_CONFERENCIA`;
- `PENDENTE_CONFERENCIA` / `DIVERGENTE` como visão agregada;
- `ADIADA_PROXIMA_CHAMADA`;
- `SEM_MOVIMENTO`;
- `FECHADA`;
- `RETIFICACAO` em fluxo próprio.

O estado agregado deve ser derivado de fatos do ciclo e das obrigações, não de abertura de tela.

## 4. Máquina C — obrigação/fonte

Representa cada obrigação independente do cliente:

- DARF;
- FGTS;
- DAE;
- eConsignado;
- demais fontes futuras.

Estados mínimos:

- `PENDENTE`;
- `CONFERIDA`;
- `DIVERGENTE`;
- `JUSTIFICADA`;
- `NAO_APLICAVEL`;
- `IMPEDIDA_EXTERNAMENTE`;
- `RETIFICACAO` quando a própria obrigação possui mudança material.

A decisão em uma fonte não altera as outras.

## 5. Máquina D — resultado da consulta eConsignado

O resultado da fonte externa não pertence à máquina de Conferência:

- `COM_CONSIGNADO`;
- `SEM_CONSIGNADO`;
- `SEM_PROCURACAO`;
- `ERRO_TECNICO`.

Depois do cruzamento, a obrigação eConsignado recebe estado da Máquina C.

## 6. Derivação do estado do cliente

Exemplos:

### Fechada

Cliente fica `FECHADA` quando todas as obrigações aplicáveis estiverem em estados conclusivos válidos, como:

- `CONFERIDA`;
- `JUSTIFICADA`;
- `NAO_APLICAVEL`;
- `IMPEDIDA_EXTERNAMENTE` somente quando a regra administrativa permitir conclusão daquela fonte sem esconder outras pendências.

### Pendente

Qualquer obrigação aplicável `PENDENTE` ou `DIVERGENTE` impede fechamento normal.

### Próxima chamada

Cliente movido validamente para chamada futura sai imediatamente da mesa da chamada corrente, preservando histórico da mudança.

### Retificação

Nova evidência material em cliente `FECHADA` não devolve o cliente à mesa comum como se nunca tivesse sido fechado. Cria fluxo de retificação com snapshot anterior preservado.

## 7. `PRONTA` legado

`PRONTA` pode continuar existindo internamente durante migração, mas não deve ser traduzido cegamente para `Em conferência`.

Sem evidência processada:

`PRONTA` -> visual/operacional `AGUARDANDO_PROCESSAMENTO`.

Com execução ativa:

-> `EM_PROCESSAMENTO`.

Somente após evidência/processamento suficiente para análise:

-> `EM_CONFERENCIA`.

## 8. Eventos que podem alterar estado

Estados devem mudar por evento explícito e auditável, como:

- competência aberta;
- cliente liberado/adiado em chamada;
- sessão iniciada/concluída;
- documento novo processado;
- candidato de reprocessamento promovido;
- obrigação recalculada;
- justificativa por fonte registrada;
- movimento mensal alterado;
- fechamento derivado das obrigações;
- mudança material detectada;
- retificação concluída.

Abrir/atualizar tela não é evento de negócio.

## 9. Leitura da Conferência

`GET`/consulta da Central de Conferência deve ser pura.

Não pode:

- fechar cliente;
- criar versão de fechamento;
- criar histórico de decisão;
- promover candidato;
- alterar chamada;
- alterar movimento.

A tela apenas lê a projeção atual.

## 10. Regressões obrigatórias

1. 100% técnico não fecha cliente;
2. sessão concluída com divergência de negócio continua tecnicamente concluída;
3. DARF justificada não altera FGTS;
4. cliente com uma obrigação divergente não fecha;
5. `PRONTA` sem evidência não aparece como `Em conferência`;
6. cliente de 2ª chamada sai da mesa da 1ª imediatamente;
7. abrir Conferência não altera banco de fechamento;
8. cliente fechado com nova evidência material cria retificação;
9. retificação não aparece na mesa normal da chamada;
10. resultado `SEM_CONSIGNADO` não é estado de fechamento do cliente.

## 11. Critério de homologação

A V8 só pode ser homologada quando não houver conversão implícita entre estado técnico, estado mensal, resultado de fonte externa e estado de obrigação.
