# Protocolo executável — Segurança e autorização das mutações V8

Data: 28/08/2026
Status: **protocolo de homologação / execução pendente na árvore runtime reconciliada**

## 1. Objetivo

Verificar, rota por rota, que toda mutação V8 possui proteção técnica e autorização de negócio coerentes.

Este protocolo complementa `CONTRATO_AUTENTICACAO_MUTACOES_V8.md` e não pressupõe falha onde o código runtime ainda não foi inspecionado.

## 2. Inventário obrigatório de rotas mutantes

Construir lista a partir da árvore final e classificar pelo menos:

- método HTTP;
- rota/endpoint;
- módulo;
- ação de negócio;
- autenticação exigida;
- autorização de negócio exigida;
- proteção CSRF ou mecanismo equivalente;
- transação/rollback;
- auditoria/histórico;
- idempotência/concurrency control;
- objeto/competência/chamada/versão afetados.

Nenhuma rota mutante pode ficar fora do inventário por ser chamada apenas via JavaScript ou worker.

## 3. Famílias mínimas

### Fechamento Mensal

- abrir competência;
- alterar movimento mensal;
- marcar/reverter sem movimento;
- adiar para próxima chamada;
- avançar/reverter chamada;
- ações administrativas em lote.

### Conferência

- justificar/resolver obrigação por fonte;
- anexar documento;
- reprocessar;
- registrar ocorrência;
- concluir/promover resolução quando aplicável.

### Retificação

- criar/promover candidato quando houver ação explícita;
- concluir retificação;
- rejeitar/descartar candidato sem apagar histórico.

### Processamento/jobs

- iniciar sessão/job;
- reprocessar item/conjunto;
- cancelar/pausar/retomar quando disponível;
- sincronizar eConsignado.

### Clientes

- editar;
- inativar;
- reativar;
- excluir administrativamente;
- aplicar diferenças RFB/SEFAZ/Sintegra.

### Saídas

- impressão individual;
- impressão selecionada/lote;
- entrega individual;
- entrega selecionada/lote;
- saídas automáticas.

## 4. Testes de autenticação

Para cada rota interna:

1. chamar sem sessão;
2. provar rejeição;
3. confirmar zero delta no banco/filesystem;
4. chamar com sessão expirada/inválida;
5. provar mesma rejeição segura.

Não basta a página anterior exigir login se o POST final aceitar chamada direta.

## 5. Testes de proteção de requisição

Para endpoints de navegador sujeitos a CSRF:

- POST válido com token/mecanismo correto funciona quando autorizado;
- ausência de token é rejeitada;
- token inválido é rejeitado;
- token de sessão diferente é rejeitado;
- rejeição não cria mutação parcial.

Endpoints máquina-a-máquina, se existirem, devem usar mecanismo apropriado e documentado, sem reutilizar exceção genérica de CSRF como bypass.

## 6. Testes de autorização de negócio

Autenticação não é autorização.

Testar parâmetros manipulados manualmente:

- cliente fora da competência;
- cliente de chamada futura;
- cliente FECHADA em ação de mesa viva;
- documento pertencente a outro cliente;
- documento de outra competência;
- versão histórica enviada como vigente;
- ID de saída fora do gate;
- retificação de outro cliente;
- job com universo maior que o permitido.

O backend deve recalcular/intersectar o universo autorizado e rejeitar inconsistências.

## 7. Concorrência e estado obsoleto

Para mutações críticas, simular:

1. request A lê revisão/estado N;
2. request B grava estado N+1;
3. request A tenta gravar baseado em N;
4. a gravação obsoleta deve ser rejeitada/reavaliada.

Aplicar especialmente a:

- chamada T L;
- decisão por fonte;
- promoção de candidato;
- conclusão de retificação;
- alteração de movimento mensal.

## 8. Transação e rollback

Provocar falha controlada depois de parte da lógica preparada e antes do commit.

Validar:

- nenhuma tabela fica parcialmente atualizada;
- arquivo físico não é movido/apagado parcialmente;
- histórico não registra sucesso inexistente;
- job/ocorrência registra falha de forma coerente;
- retry seguro é possível.

## 9. GET sem efeitos colaterais

Executar repetidamente GET/list/detail/search/filter em:

- Fechamento;
- Processamento;
- Conferência;
- Retificações;
- Clientes;
- Impressão/Entregas em modo de consulta.

Comparar banco antes/depois. Rotas GET não podem alterar negócio.

A Central de Conferência é regressão obrigatória conhecida.

## 10. Jobs longos

Ao criar job:

- validar usuário e autorização no momento da criação;
- persistir solicitante, competência, chamada e universo;
- worker não amplia o escopo com nova consulta global;
- reinício preserva escopo;
- cancelamento não deixa estado intermediário promovido.

## 11. Dados externos

### SEFAZ GO/Sintegra

- consulta pode ser somente leitura;
- aplicar diferença exige usuário autenticado e confirmação explícita;
- cliente/documento incompatível bloqueia gravação;
- campo ausente na fonte não apaga cadastro.

### eConsignado/e-CAC e integrações

Resultado externo não deve autorizar mutação fora do cliente/competência originalmente aprovados.

## 12. Saídas

Testar diretamente o serviço, sem UI:

- ID manual PRONTA → bloqueia;
- ID manual RETIFICACAO → bloqueia;
- FECHADA sem versão → bloqueia;
- FECHADA com versão vigente e sem retificação → autoriza;
- lote misto não bypassa os itens inválidos;
- saída registra versão de fechamento e solicitante.

## 13. Auditoria de logs e erros

Erros de sessão, CSRF, autorização e validação:

- não exibem stack trace/segredo/token na UI;
- geram registro diagnóstico suficiente;
- distinguem falha técnica de bloqueio de negócio;
- preservam correlation_id quando aplicável.

## 14. Evidência final

Gerar matriz:

`Rota | Método | AuthN | CSRF/Mecanismo | AuthZ negócio | Transação | Auditoria | Concorrência | PASS/FAIL`

Anexar casos de teste negativos e deltas de banco.

## 15. Critério de homologação

B38 só pode receber `CORRIGIDO_HOMOLOGADO` quando:

- inventário da árvore final estiver completo;
- todas as rotas mutantes passarem nos controles aplicáveis;
- nenhuma rota GET mutar negócio;
- bypass por IDs/estado obsoleto estiver bloqueado;
- testes rodarem sobre o mesmo build que será empacotado.
