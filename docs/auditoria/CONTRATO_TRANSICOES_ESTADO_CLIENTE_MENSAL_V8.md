# Contrato V8 — Transições de estado do cliente mensal

Data: 28/08/2026
Status: **contrato obrigatório de auditoria / implementação ainda não homologada**

## 1. Objetivo

Definir uma máquina de estados única para `cliente + competência`, evitando que Fechamento, Processamento, Conferência, workers e views reescrevam estados por regras próprias.

## 2. Estados conceituais

Estados operacionais mínimos:

- `AGUARDANDO_PROCESSAMENTO`;
- `EM_PROCESSAMENTO`;
- `EM_CONFERENCIA`;
- `PENDENTE_DIVERGENTE`;
- `PROXIMA_CHAMADA`;
- `SEM_MOVIMENTO`;
- `FECHADA`;
- `RETIFICACAO`.

Estados técnicos de sessão/documento permanecem separados e não pertencem a esta máquina.

## 3. Abertura da competência

Ao abrir competência:

- criar composição mensal a partir do universo elegível;
- cliente com movimento liberado na chamada atual inicia em `AGUARDANDO_PROCESSAMENTO`;
- decisão mensal explícita `SEM_MOVIMENTO` pode produzir estado próprio conforme composição;
- cliente já designado para chamada futura inicia/permanece `PROXIMA_CHAMADA`;
- não antecipar `EM_CONFERENCIA` antes de existir evidência processada.

## 4. AGUARDANDO_PROCESSAMENTO → EM_PROCESSAMENTO

Somente quando job técnico relevante é efetivamente iniciado/reivindicado para aquele cliente/competência/chamada.

Abrir tela ou listar cliente não muda estado.

## 5. EM_PROCESSAMENTO → EM_CONFERENCIA

Quando:

- execução técnica relevante terminou;
- dados suficientes foram persistidos;
- agregador consegue montar obrigações/evidências para análise.

`100%` da sessão global não é a condição isolada; a transição é do cliente e depende das evidências daquele cliente.

## 6. EM_CONFERENCIA ↔ PENDENTE_DIVERGENTE

Pode permanecer ou alternar conforme:

- documento faltante aplicável;
- divergência de valores;
- identidade/competência em revisão;
- fonte externa necessária;
- decisão manual específica por fonte.

A resolução de uma fonte não resolve automaticamente outra.

## 7. Trabalho vivo → FECHADA

Somente pelo agregador canônico, quando todas as obrigações aplicáveis estiverem em estados terminais aceitáveis.

A transição deve atomicamente:

1. validar ausência de retificação pendente;
2. gerar snapshot/versão;
3. registrar histórico;
4. atualizar estado para `FECHADA`;
5. liberar gate de saída para a versão criada.

## 8. FECHADA → RETIFICACAO

Única transição normal após fechamento quando surgir mudança material.

É proibido voltar silenciosamente de `FECHADA` para `PRONTA`, `EM_CONFERENCIA` ou `AGUARDANDO_PROCESSAMENTO` por simples reprocessamento.

Fluxo:

```text
FECHADA Vn
 -> nova evidência
 -> comparação de materialidade
 -> MUDANCA_MATERIAL
 -> RETIFICACAO candidata Vn+1
```

Vn permanece intacta.

## 9. RETIFICACAO → FECHADA

Após resolução e validação:

- gerar Vn+1;
- concluir retificação;
- atualizar `versao_atual`;
- voltar a `FECHADA`;
- novas saídas usam Vn+1.

Tudo de forma transacional.

## 10. Próxima chamada

### Trabalho vivo → PROXIMA_CHAMADA

A decisão precisa registrar:

- chamada anterior;
- nova chamada;
- motivo;
- observação, quando houver;
- usuário;
- data/hora;
- versão/revisão do registro para proteção contra escrita obsoleta.

Ao entrar em `PROXIMA_CHAMADA`:

- sai imediatamente do universo operacional da chamada corrente;
- jobs não iniciados da chamada corrente devem ser cancelados/ignorados com segurança;
- não vira `NAO_APLICAVEL` permanente.

### PROXIMA_CHAMADA → AGUARDANDO_PROCESSAMENTO

Somente quando a chamada correspondente for aberta/avançada e o cliente continuar elegível.

O avanço da chamada deve ser a única rotina canônica autorizada a liberar em lote esses clientes.

### Proteção T L Empreendimentos Agrícolas

Após decisão válida de 2ª chamada, nenhuma sincronização, GET, worker antigo ou recálculo pode regravar o cliente como chamada 1/PRONTA.

Qualquer `UPDATE` baseado em estado antigo deve falhar por controle de versão/condição ou ser ignorado.

## 11. Sem movimento mensal

### Trabalho vivo → SEM_MOVIMENTO

Decisão mensal explícita, auditável e limitada à competência.

O motor de aplicabilidade recalcula obrigações compatíveis.

Se a composição ficar integralmente resolvida, o agregador pode gerar fechamento/versionamento correspondente sem exigir guias incompatíveis.

### SEM_MOVIMENTO → trabalho vivo

Ao reverter:

- preservar histórico da decisão anterior;
- recompor obrigações;
- retornar a `AGUARDANDO_PROCESSAMENTO`, `EM_PROCESSAMENTO` ou `EM_CONFERENCIA` conforme evidências atuais;
- não apagar documentos já existentes.

### Evidência material conflitante

Documento/movimento real incompatível com a marcação `SEM_MOVIMENTO` deve abrir revisão; não deve ser escondido para preservar o estado.

## 12. Escrita concorrente / optimistic locking

Toda mutação do estado mensal deve conhecer a revisão/versão lida.

Padrão conceitual:

```sql
UPDATE fechamento_mensal_cliente
SET ... , revisao = revisao + 1
WHERE id = ? AND revisao = ?
```

Zero linhas alteradas significa estado concorrente mais novo; a rotina deve reler e recalcular, não sobrescrever.

Isso é especialmente obrigatório para:

- mudança de chamada;
- fechamento automático;
- retificação;
- reversão de sem movimento;
- jobs/workers assíncronos.

## 13. GET é somente leitura

Nenhuma transição desta máquina pode ocorrer por:

- abrir Fechamento;
- abrir Processamento;
- abrir Conferência;
- filtrar/paginar;
- preview de Impressão/Entrega.

Transições são consequência de eventos explícitos ou conclusão de processamento/resolução.

## 14. Histórico

Toda transição real deve registrar estado anterior, novo estado, causa/evento, usuário/processo, data/hora e correlação.

Recalcular e obter o mesmo estado não cria evento duplicado.

## 15. Regressões mínimas

1. nova competência com movimento começa aguardando processamento, não em conferência;
2. abrir Conference não muda estado;
3. job iniciado muda somente cliente correspondente para processamento;
4. evidência processada leva à conferência;
5. fonte pendente impede fechamento;
6. todas fontes terminais geram FECHADA + versão;
7. FECHADA com nova mudança material vai para RETIFICACAO, nunca PRONTA;
8. retificação concluída gera Vn+1;
9. cliente movido para 2ª chamada desaparece imediatamente da 1ª;
10. worker com snapshot antigo não desfaz mudança de chamada;
11. avanço da chamada libera cliente uma única vez;
12. sem movimento é mensal e reversível;
13. reversão preserva histórico;
14. GET/paginação nunca gravam transição;
15. reexecução idempotente não duplica histórico/versionamento.

## 16. Relação com bloqueadores

Principalmente B02, B04, B08, B09, B10, B11, B37 e B40.
