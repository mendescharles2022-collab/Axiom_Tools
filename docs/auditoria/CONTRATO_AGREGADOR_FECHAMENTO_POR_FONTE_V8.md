# Contrato V8 — Agregador de fechamento por fonte

Data: 28/08/2026
Status: **contrato obrigatório de auditoria / implementação ainda não homologada**

## 1. Objetivo

Definir uma única regra de backend para decidir o estado agregado de `cliente + competencia` a partir das obrigações/fontes aplicáveis.

Nenhuma view, relatório, impressão ou entrega deve recalcular essa regra por conta própria.

## 2. Entrada

O agregador recebe o conjunto de obrigações da competência, por exemplo:

- DARF/federal;
- FGTS mensal;
- FGTS rescisório/antecipado, quando aplicável;
- DAE, quando aplicável;
- eConsignado;
- outras fontes reconhecidas futuramente.

Cada obrigação deve possuir:

- aplicabilidade;
- estado;
- evidências;
- valor esperado;
- valor encontrado/composto;
- justificativa, quando houver;
- proveniência.

## 3. Estados terminais aceitáveis da obrigação

Podem contribuir para fechamento, conforme regra da fonte:

- `CONFERIDA`;
- `NAO_APLICAVEL`;
- `JUSTIFICADA`;
- `IMPEDIDA_EXTERNAMENTE`, quando a política daquela obrigação permitir conclusão administrativa.

## 4. Estados que bloqueiam fechamento

Qualquer obrigação aplicável em um destes estados bloqueia `FECHADA`:

- `PENDENTE`;
- `DIVERGENTE`;
- `EM_PROCESSAMENTO`;
- `REVISAO`;
- `ERRO_TECNICO` quando impede obtenção necessária;
- `RETIFICACAO`;
- `INDETERMINADA`;
- qualquer estado não terminal.

## 5. Regra agregada

### FECHADA

Somente quando:

1. todas as obrigações aplicáveis existem na composição;
2. todas estão em estado terminal aceitável;
3. não há retificação material pendente;
4. snapshot/versão de fechamento pode ser produzido de forma consistente.

### EM_CONFERENCIA

Quando há evidência processada suficiente para a mesa, mas ainda existe obrigação aplicável pendente/divergente/revisão.

### AGUARDANDO_PROCESSAMENTO

Quando o cliente pertence ao ciclo/chamada atual, mas ainda não há evidência técnica suficiente para conferência.

### EM_PROCESSAMENTO

Quando existe job técnico ativo sobre evidências relevantes.

### PROXIMA_CHAMADA

Quando o cliente foi adiado para chamada futura. Fica fora do universo operacional da chamada atual.

### SEM_MOVIMENTO

É condição mensal explícita que reduz expectativas conforme regra aplicável. Não significa automaticamente que nenhuma obrigação existe; o agregador deve considerar o perfil e a regra mensal.

### RETIFICACAO

Quando cliente já fechado possui mudança material candidata.

## 6. Proibições

- decisão global `Conferido` não fecha cliente se outra fonte continuar pendente;
- `PROCESSADO` de documento não fecha cliente;
- `100%` de sessão não fecha cliente;
- ausência de documento não vira `NAO_APLICAVEL` sem regra de aplicabilidade;
- uma fonte `JUSTIFICADA` não justifica as demais;
- filtro de interface não altera resultado agregado.

## 7. Casos reais

### Predileta

DARF sob responsabilidade Fiscal pode estar resolvida/justificada na fonte DARF, enquanto FGTS/eConsignado continuam independentes.

### Casa das Carnes e Lago Azul / Maria Virginia

DARF impedida por procuração não libera automaticamente outras fontes.

### Alex Douglas

FGTS mensal pode ser não aplicável pelo contexto rescisório, mantendo DARF aplicável.

### Gold Pallace / Marcos Daibert / Wilmar

Bases/remuneração zeradas explicadas podem levar obrigações específicas a `NAO_APLICAVEL`, permitindo fechamento quando nenhuma outra obrigação estiver aberta.

### MEI

DAE substitui expectativa genérica de GFD conforme perfil; o agregador usa a composição correta do cliente.

## 8. Idempotência

Recalcular o agregado com as mesmas obrigações e evidências deve produzir o mesmo estado sem criar histórico/versão duplicados.

Mudança de estado só gera evento quando houver transição real.

## 9. Evento de fechamento

Quando o resultado transicionar para `FECHADA`:

1. gerar snapshot/versionamento;
2. registrar histórico;
3. atualizar estado agregado;
4. liberar gate de saída para aquela versão.

Esses passos devem ser transacionais/atômicos.

## 10. Evento de reabertura material

Nova evidência material em cliente FECHADA não volta simplesmente para PRONTA.

Deve:

1. preservar versão vigente;
2. criar retificação candidata;
3. alterar agregado para RETIFICACAO;
4. bloquear novas saídas;
5. encaminhar ao fluxo próprio de retificação.

## 11. Regressões mínimas

1. DARF conferida + FGTS pendente -> não FECHADA.
2. DARF justificada + FGTS conferida -> FECHADA se nenhuma outra obrigação aplicável estiver aberta.
3. documento PROCESSADO sem conferência -> não FECHADA.
4. sessão 100% com divergência -> não FECHADA.
5. próxima chamada -> fora do ciclo atual.
6. todas N/A justificadas por regra legítima -> FECHADA com snapshot.
7. retificação material -> bloqueia saída.
8. recálculo idêntico -> não duplica versão/histórico.
9. decisão por uma fonte não altera outra.
10. FECHADA sempre possui versão válida.

## 12. Relação com bloqueadores

Principalmente:

- B02;
- B03;
- B04;
- B08;
- B09;
- B10;
- B11;
- B18;
- B19;
- B20;
- B22;
- B23;
- B26;
- B37.
