# Auditoria canônica V8 — Etapa 8

Data: 28/08/2026
Status: **auditoria em andamento / nenhum pacote final liberado**

## 1. Escopo

Esta etapa auditou a coerência operacional e visual dos três módulos centrais da V8:

- Fechamento Mensal;
- Processamento de Arquivos;
- Central de Conferência.

Também consolidou os requisitos de relatórios/impressão A4 e revisou os limites da evidência recuperada da árvore instalada.

## 2. Arquitetura aprovada confirma papéis distintos

A arquitetura V8 oficial determina:

### Fechamento Mensal

- abre a competência uma única vez;
- define composição mensal;
- controla movimento e chamadas;
- acompanha o ciclo;
- não executa processamento técnico;
- não possui fluxo normal de `Fechar selecionadas`.

### Processamento

- herda competência/chamada;
- recebe/descobre/processa documentos;
- executa motores técnicos;
- mantém sessões/fila/hash/cache/checkpoints;
- pendências desta tela são técnicas.

### Conferência

- recebe trabalho que realmente chegou ao estágio de análise;
- concentra divergências, ausências e justificativas;
- deve permitir anexar, reprocessar, registrar ocorrência, resolver/justificar e ver documentos na própria mesa.

## 3. `Fechar selecionadas`

V7 já havia removido explicitamente `Fechar selecionadas`.

A arquitetura V8 mantém a regra: fechamento é consequência das obrigações aplicáveis satisfeitas/justificadas.

Nesta rodada não foi recuperado o template atual integral com evidência de reintrodução do botão.

Classificação:

`REGRESSAO PREVENTIVA / NÃO CONFIRMADA NO TEMPLATE ATUAL`.

Não registrar como defeito atual sem prova.

## 4. Estado `Em conferência` antecipado — confirmado como problema de arquitetura/interface

A arquitetura V8 registra expressamente que a interface ainda pode exibir estados antecipados de `Em conferência`.

Regra correta:

- sem evidência processada -> `Aguardando processamento`;
- sessão em execução -> `Em processamento`;
- evidência suficiente para análise -> `Em conferência`;
- divergência -> pendente/divergente;
- chamada futura -> aguardando chamada;
- fechado -> fora da mesa viva;
- mudança material posterior -> retificação.

A regra antiga V7 `PRONTA => Em conferência` está superada pela V8.

## 5. Aba Pendências do Processamento — defeito confirmado

O status operacional V8F2 registra que a aba ainda não abre de forma operacionalmente clara já filtrada pela competência ativa.

O usuário ainda precisa lidar com PROC/chaves técnicas para isolar o ciclo corrente.

Isso viola o princípio de competência única herdada.

Correção contratual:

- competência ativa como filtro primário automático;
- PROC como filtro técnico secundário;
- `Competência não identificada` em exceção própria;
- histórico de outras competências somente por consulta explícita.

## 6. Pendência técnica x pendência de negócio

Processamento não deve exibir como pendência técnica:

- DARF ausente esperada;
- FGTS divergente;
- eConsignado divergente;
- procuração expirada;
- obrigação não aplicável;
- composição rescisória.

Esses itens pertencem à Conferência.

Pendências técnicas válidas incluem:

- arquivo ilegível;
- cliente não identificado;
- competência não identificada;
- erro de extração;
- falha de motor;
- arquivo corrompido/bloqueado.

## 7. Conferência como mesa de resolução

A interface final precisa permitir, na ocorrência/ficha do cliente:

- ver fontes independentes;
- abrir documentos;
- anexar documento faltante;
- reprocessar;
- registrar evidência/ocorrência;
- justificar por fonte;
- marcar não aplicável quando válido;
- registrar impedimento externo;
- mover para chamada futura;
- marcar sem movimento mensal quando válido;
- consultar histórico.

Essas ações não devem exigir sair da Conferência e navegar por vários módulos para resolver uma ocorrência comum.

## 8. Mesa viva não é histórico

A auditoria estrutural já confirmou que a Conferência atual mistura `PRONTA`, `FECHADA` e `RETIFICACAO` no escopo amplo.

A V8 define:

- mesa padrão = trabalho vivo da chamada corrente;
- fechados = histórico/consulta;
- retificações = fluxo próprio;
- chamada futura = fora da mesa corrente;
- competências anteriores = histórico explícito.

Contadores da mesa não podem incluir esses universos silenciosamente.

## 9. Relatório de pendências A4 — falha funcional confirmada

O status V8F2 registra relatório ultrapassando a largura imprimível do A4 retrato.

A correção ainda precisa de homologação visual real.

Foi criado contrato específico exigindo:

- A4 retrato dentro da área imprimível;
- quebra controlada de texto;
- tabela compacta;
- cabeçalhos repetíveis;
- sem sidebar/topbar/botões na impressão;
- máscaras centralizadas;
- estado por fonte;
- preview real no Windows/navegador.

## 10. Evidência da árvore instalada

Trechos recuperados da instalação real confirmam:

- `web/templates/closing/index...` existe e exibe cabeçalho/tabs/KPIs;
- `web/templates/conference/index...` existe;
- `processing/central.py` consulta Fechamento Mensal;
- `closing/service.py` mantém status/chamadas/histórico.

Porém os trechos recuperados não contêm conteúdo integral suficiente para afirmar:

- todos os botões hoje presentes no template;
- todos os parâmetros da aba Pendências;
- todas as ações hoje presentes na ocorrência da Conferência;
- o CSS final do relatório A4.

Esses pontos permanecem `INSPECAO DIRETA DO ZIP/RUNTIME`.

## 11. Contratos criados nesta etapa

- `CONTRATO_INTERFACE_OPERACIONAL_V8.md`;
- `CONTRATO_RELATORIOS_IMPRESSAO_V8.md`;
- este documento.

## 12. Regressões obrigatórias acrescentadas

1. abrir competência somente no Fechamento;
2. Processamento herda competência e chamada;
3. aba Pendências abre no ciclo corrente sem PROC manual;
4. pendência técnica não mistura divergência de negócio;
5. estado `Em conferência` só aparece após estágio real;
6. `Fechar selecionadas` não reaparece no fluxo normal;
7. Conference padrão mostra apenas trabalho vivo;
8. fechado não volta à mesa sem retificação;
9. retificação possui fluxo próprio;
10. ocorrência pode ser resolvida sem sair da Conferência;
11. justificativa é por fonte;
12. relatório de pendências cabe em A4 retrato sem corte;
13. preview/impressão real é parte da homologação.

## 13. Estado ao final da Etapa 8

A interface operacional está conceitualmente bem delimitada, mas ainda não homologada no runtime canônico.

A próxima frente da auditoria deve aprofundar:

- segurança transacional das escritas críticas;
- duplicação de regras entre módulos;
- monólitos `central.py`/views;
- CSRF/autorização em ações de mutação;
- migração/schema dos novos estados por fonte e reprocessamento versionado;
- testes que precisarão ser substituídos porque defendem comportamento legado V7.

Nenhum pacote V8 deve ser liberado antes da regressão integral.
