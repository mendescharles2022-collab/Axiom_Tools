# Contrato V8 — Autenticação, sessão e mutações críticas

Data: 28/08/2026
Status: **contrato de auditoria / verificação direta do runtime ainda pendente**

## 1. Fundamento

A AXT-002 já estabeleceu login, sessão, logout e proteção das telas internas como requisitos de base.

As rotas criadas posteriormente pela V8 não podem ficar abaixo desse piso apenas por terem sido adicionadas depois.

## 2. Escopo de mutações críticas

Exigem autenticação válida e proteção contra requisição indevida, no mínimo:

- abrir competência;
- alterar movimento mensal;
- adiar para próxima chamada;
- reverter/avançar chamada;
- anexar documento;
- reprocessar documento;
- promover/rejeitar candidato;
- justificar/resolver obrigação;
- concluir retificação;
- inativar/reativar/excluir cadastro;
- gerar impressão;
- gerar entrega;
- disparar saída automática;
- sincronizar eConsignado;
- aplicar dados externos do Sintegra/SEFAZ.

## 3. Regras

Toda mutação deve:

- exigir usuário autenticado;
- validar sessão no backend;
- possuir proteção CSRF ou mecanismo equivalente apropriado ao tipo de endpoint;
- validar autorização de negócio no servidor, não apenas esconder botão;
- registrar usuário, data/hora, entidade, ação, resultado e correlação quando aplicável;
- rejeitar parâmetros fora do universo autorizado, mesmo se enviados manualmente.

## 4. GET somente leitura

Rotas GET de consulta não devem executar mutações de negócio.

Isso reforça o achado já confirmado da Central de Conferência: abrir a tela não pode sincronizar fechamento, criar histórico ou alterar status.

## 5. Seleção por IDs

Qualquer POST que receba IDs de clientes/documentos deve intersectar a seleção recebida com o universo autorizado calculado no backend.

Aplica-se especialmente a:

- Impressão;
- Entregas;
- ações em lote;
- reprocessamentos;
- mudanças de chamada;
- operações administrativas.

IDs fornecidos pelo navegador nunca são prova de autorização.

## 6. Sessão e concorrência

Mutações longas não devem depender de sessão HTTP aberta até o fim do processamento.

Quando houver worker/job:

- a autorização é validada no momento da criação do job;
- o job registra quem o solicitou;
- a execução usa escopo persistido e auditável;
- expansão posterior do universo não deve ocorrer silenciosamente.

## 7. Erros

Erro de autorização, CSRF ou sessão:

- não pode produzir mutação parcial;
- deve retornar resposta clara;
- deve gerar log/auditoria suficiente;
- não deve revelar segredos, tokens ou stack trace ao usuário final.

## 8. Regressões mínimas

1. acesso não autenticado às telas internas é rejeitado;
2. POST sem proteção adequada é rejeitado;
3. ID manual de cliente fora do gate de impressão não gera arquivo;
4. ID manual fora do gate de entrega não gera saída;
5. cliente em 2ª chamada não pode ser recolocado na 1ª por POST obsoleto sem transição válida;
6. GET da Conferência não altera banco;
7. job eConsignado mantém o universo autorizado da competência/chamada;
8. aplicação de dados SEFAZ exige revisão/confirmação e usuário autenticado.

## 9. Estado de evidência

A árvore `main` atual não espelha integralmente o runtime V8. Por isso, ausência de dependência ou decorator no repositório reduzido não é, isoladamente, prova de falha de segurança na instalação.

A verificação final deve ocorrer sobre a árvore reconciliada que será empacotada.
