# Contrato V8 — Transações e segurança das mutações operacionais

Data: 28/08/2026
Status: **contrato de auditoria / verificação integral no código canônico pendente**

## 1. Escopo

A V8 possui mutações críticas que podem alterar fechamento, documentos, histórico e saídas.

Incluem:

- reprocessar arquivo;
- anexar documento;
- justificar/resolver ocorrência;
- marcar sem movimento;
- mover cliente de chamada;
- fechar/concluir obrigação;
- concluir retificação;
- inativar/reativar cliente;
- gerar impressão/entrega;
- aplicar atualização cadastral externa.

Essas ações precisam de proteção de rota, CSRF quando aplicável, autorização de backend, transação e histórico consistente.

## 2. Baseline anterior

A AXT-003 já exigia para ações cadastrais:

- transação;
- rollback em falha;
- SQL parametrizado;
- proteção de rota;
- autorização administrativa no backend;
- CSRF para POSTs persistentes/destrutivos.

A Auditoria Operacional V4 registrou, naquela fotografia, 56 rotas de negócio e nenhuma rota sem `login_required`/`admin_required`.

Essas garantias devem ser preservadas e ampliadas para os módulos V8.

## 3. Limite da evidência atual

O código integral das rotas V8 não está sincronizado no `main` atual e não foi recuperado integralmente da biblioteca desta sessão.

O `pyproject.toml` do `main` possui `dependencies = []`, embora o runtime real conhecido use Flask/Flask-WTF/Waitress e outras dependências.

Consequência:

- não é possível afirmar, só a partir do `main`, que CSRF está ausente ou presente nas rotas V8;
- não é possível homologar proteção de todas as rotas pela fotografia V4;
- a verificação deve ser executada na árvore operacional reconciliada.

Classificação atual:

`SEGURANCA V8 — REVALIDACAO OBRIGATORIA`.

## 4. Regra transacional

Uma mutação de negócio deve terminar em um dos estados:

```text
COMPLETA E CONSISTENTE
ou
SEM EFEITO PERSISTENTE
```

Não aceitar estado parcial.

Exemplo de reprocessamento:

Errado:

1. apagar versão vigente;
2. tentar nova leitura;
3. falhar;
4. deixar banco degradado.

Correto:

1. preservar vigente;
2. criar candidato;
3. processar candidato;
4. validar;
5. promover atomicamente;
6. recalcular projeções afetadas;
7. registrar histórico.

## 5. Escopo da transação de reprocessamento

A promoção do candidato deve ser atômica no que diz respeito a:

- versão vigente/candidata;
- pessoas/itens relacionados;
- vínculo de cliente;
- competência;
- inscrição/origem;
- dados extraídos;
- histórico da promoção;
- marcação para recálculo da Conferência.

Falha antes da promoção mantém a versão vigente intacta.

Falha depois de iniciar a promoção deve fazer rollback da unidade transacional ou deixar mecanismo idempotente de recuperação comprovado.

## 6. Transição de chamada

Mover cliente para próxima chamada deve ser transacional entre:

- estado atual;
- nova chamada;
- motivo/impedimento;
- histórico.

Não gravar `chamada=2` sem histórico, nem histórico de chamada 2 mantendo projeção em chamada 1.

Preferir compare-and-set para impedir snapshot obsoleto de sobrescrever decisão recente.

## 7. Decisão/justificativa por fonte

Registrar uma justificativa deve, na mesma unidade lógica:

- gravar fonte/obrigação;
- motivo;
- observação/evidência;
- usuário/data/hora;
- recalcular estado da obrigação;
- recalcular estado agregado do cliente.

Falha no recálculo não pode deixar uma decisão gravada com projeção silenciosamente contraditória sem mecanismo de recuperação.

## 8. Fechamento e versão

Quando todas as obrigações conclusivas permitirem fechamento:

- atualizar estado `FECHADA`;
- registrar data/hora;
- registrar versão/snapshot;
- registrar histórico.

Esses elementos devem ser coerentes entre si.

Abrir a Conferência não pode executar essa transação.

## 9. Retificação

Detectar mudança material deve preservar o fechamento anterior e criar candidata/retificação de forma atômica.

Concluir retificação deve:

- validar candidata;
- criar nova versão;
- atualizar estado corrente;
- manter versão anterior;
- liberar saída apenas depois da conclusão.

## 10. Autenticação e autorização

Todas as rotas internas V8 permanecem autenticadas.

A autorização relevante deve existir no backend, não somente na UI.

Exemplos:

- ação administrativa de cliente;
- override/contingência futura;
- conclusão de retificação;
- configuração que altera regra do ciclo;
- ações destrutivas ou de alto impacto.

## 11. CSRF

Toda mutação disparada por navegador via cookie/sessão deve usar proteção CSRF compatível com a arquitetura Flask adotada.

Abrange, conforme rota final:

- POST de mudança de chamada;
- sem movimento;
- justificativa/resolução;
- reprocessamento;
- anexo;
- inativação/reativação;
- configurações;
- impressão/entrega quando a ação gera estado persistente.

Endpoints internos máquina-a-máquina, se existirem, devem usar autenticação própria e não serem simplesmente isentos sem justificativa.

## 12. Idempotência

Ações sujeitas a duplo clique, retry de navegador ou repetição de worker devem ser idempotentes ou possuir chave de operação.

Casos principais:

- anexar/processar mesmo arquivo;
- promover candidato;
- mover chamada;
- concluir retificação;
- gerar lote;
- gerar entrega.

Repetição não pode criar:

- duas versões idênticas;
- dois históricos contraditórios;
- valores dobrados;
- duas entregas silenciosas.

## 13. Erro e feedback

Falha de mutação deve:

- registrar log técnico;
- gerar referência/correlação quando aplicável;
- retornar mensagem operacional acionável;
- não expor traceback;
- não afirmar sucesso antes do commit real.

## 14. Auditoria de rotas obrigatória na árvore final

Antes da homologação, inventariar todas as rotas V8 e classificar:

```text
GET leitura
POST mutação
permissão/autenticação
CSRF
autorização adicional
serviço chamado
transação
histórico gerado
```

Nenhuma rota POST deve permanecer sem classificação.

## 15. Regressões obrigatórias

1. POST sem autenticação é recusado;
2. POST com CSRF ausente/inválido é recusado quando aplicável;
3. falha de reprocessamento não remove vigente;
4. falha em mudança de chamada não deixa histórico/projeção divergentes;
5. duplo clique em `Resolver` não duplica evento;
6. retry de conclusão de retificação não cria duas versões;
7. seleção direta de ID não burla autorização de saída;
8. erro após início da transação causa rollback;
9. mensagem de sucesso só aparece após persistência concluída;
10. GET da Conferência não produz mutação.

## 16. Critério de homologação

A segurança transacional só será considerada homologada após auditoria da árvore operacional reconciliada e execução dos testes acima no mesmo código que será empacotado.
