# Mapa V8 — Garantias anteriores reintroduzidas como regressão

Data: 28/08/2026
Status: **classificação de severidade da auditoria**

## 1. Objetivo

Distinguir funcionalidade nova ainda não implementada de garantia que o Axiom Tools já havia implementado/validado e que voltou a falhar no snapshot V8.

Quando uma garantia anterior comprovada é perdida, a classificação deve ser `REGRESSAO_REINTRODUZIDA`, não simples melhoria futura.

## 2. Retificação candidata e versão anterior preservada

### V5.6.14V4

Já implementava e validava:

- snapshot versionado por cliente + competência;
- dados iguais não criam retificação;
- mudança material cria candidata `Vn -> Vn+1`;
- versão fechada anterior preservada;
- saída automática bloqueada durante retificação;
- conclusão registra nova versão;
- `integrity_check` e validações em cópia, sem mutar banco oficial.

### V8 auditada

O reprocessamento documental comum ainda pode apagar a versão vigente antes de validar a nova leitura.

Caso Jair 449/450 comprova degradação real.

### Classificação

`REGRESSAO_REINTRODUZIDA / CRITICA`.

A correção deve estender a filosofia candidata/versionada já existente à leitura documental comum, e não inventar um segundo mecanismo incompatível.

## 3. Saída bloqueada durante retificação

### V4

Saída automática durante retificação foi explicitamente validada como bloqueada.

### V8 auditada

A camada de saída automática usa `PROCESSADO` como equivalente a validado e os gates de Impressão/Entregas possuem caminhos incompletos.

### Classificação

`REGRESSAO_REINTRODUZIDA / CRITICA`.

Um fluxo posterior não pode enfraquecer a garantia de V4.

## 4. Próxima chamada fora do ciclo corrente

### V7

Empresas adiadas/próxima chamada eram excluídas do ciclo atual. A validação em cópia real registrou empresas adiadas corretamente fora do escopo.

### V8 auditada

T L Empreendimentos Agrícolas permaneceu `PRONTA`, chamada 1, apesar da decisão operacional de 2ª chamada e continuou sendo cobrada.

### Classificação

`REGRESSAO_REINTRODUZIDA / ALTA`.

A correção deve atingir persistência/auditoria da mudança, não apenas filtro visual.

## 5. Sem movimento mensal separado do cadastro permanente

### V6/V7

- sem movimento é decisão da competência;
- não deve ser herdada automaticamente;
- reversão preserva histórico;
- cadastro permanente permanece separado.

### V8 auditada

A Conferência usa combinação que permite o perfil cadastral histórico marcar a empresa como sem movimento mesmo quando a composição mensal está `COM_MOVIMENTO`.

### Classificação

`REGRESSAO_REINTRODUZIDA / ALTA`.

A composição mensal deve ser soberana quando existe.

## 6. FECHADA como requisito de Entregas/Impressão

### V7 e contratos anteriores

Entregas e impressão eram vinculadas ao estado `FECHADA`/conferência.

### V8 auditada

A listagem pode aplicar filtros, porém existem caminhos diretos/IDs/serviços que não revalidam o mesmo gate.

### Classificação

`REGRESSAO_DE_ENFORCEMENT / CRITICA`.

A regra de negócio existia; faltou manter a garantia em todas as entradas de backend.

## 7. Histórico de mudança de ciclo

### V6/V7/V4

O módulo de fechamento já possui estruturas de histórico e retificação, inclusive `fechamento_mensal_historico`, `fechamento_mensal_versao` e `fechamento_mensal_retificacao`.

### V8 auditada

A decisão operacional de 2ª chamada não ficou refletida corretamente no snapshot observado.

### Classificação

`REGRESSAO_DE_PERSISTENCIA/AUDITORIA`.

Não é aceitável introduzir um novo mecanismo de chamadas que não use a fundação histórica já existente.

## 8. Regras que NÃO são simplesmente regressão

Algumas decisões V8 são evolução legítima e não devem ser confundidas com regressão:

- retirar clientes `FECHADA` da mesa normal de trabalho vivo, pois V7 os incluía intencionalmente;
- separar retificação em fluxo próprio, embora V4/V7 a incluíssem no escopo amplo da Conferência;
- substituir decisão manual global por decisão por fonte;
- deixar de traduzir `PRONTA` automaticamente para `Em conferência`.

Nesses casos, testes antigos precisam ser migrados para o novo contrato.

## 9. Critério para correção

Para regressões reintroduzidas:

1. localizar teste/garantia anterior;
2. preservar comportamento que continua válido;
3. atualizar apenas o que foi legitimamente superado pela V8;
4. adicionar regressão específica do caso real que revelou a perda;
5. impedir que nova refatoração remova a garantia novamente.

## 10. Prioridade

Ordem de severidade sugerida:

1. reprocessamento destrutivo / perda de versão;
2. bypass de saída / `PROCESSADO` como validado;
3. chamada futura ainda cobrada;
4. movimento mensal não soberano;
5. histórico/persistência incoerente.

Essas correções devem preceder refinamentos cosméticos do fluxo V8.
