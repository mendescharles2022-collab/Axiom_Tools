# Axiom Tools — UX, Telas, Impressão, Entregas e Relatórios

Data: 23/09/2026

## 1. Filosofia de UX

**DECISÃO HISTÓRICA APROVADA**

A interface deve acompanhar a rotina real e reduzir cliques.

Princípios recuperados:

- telas compactas;
- evitar “telões” com controles que não têm utilidade imediata;
- não exigir seleção manual de centenas de clientes;
- busca e filtros estáveis;
- paginação;
- estado visual coerente com o backend;
- abrir detalhe sem perder o contexto;
- ações próximas do objeto/ocorrência;
- histórico separado da operação corrente;
- status técnicos separados de status operacionais;
- não duplicar módulos com o mesmo papel.

## 2. Shell e navegação

**CANÔNICO HISTÓRICO**

A camada visual previa:

- cabeçalho;
- menu lateral;
- área central;
- identificação do usuário/ambiente;
- Dashboard;
- temas;
- atalhos.

A navegação operacional amadureceu para áreas como:

- Fechamento Mensal;
- Processamento;
- Conferência;
- Repositório/Arquivo do Cliente;
- Entregas;
- Impressão;
- Conexões;
- Parâmetros;
- Auditoria/Relatórios.

A divisão pode mudar em produto futuro, mas as responsabilidades não devem ser recombinadas de forma confusa.

## 3. Processamento de Arquivos

**DECISÃO HISTÓRICA APROVADA**

A tela deve privilegiar:

- competência/chamada herdadas;
- upload;
- fila atual;
- sessão;
- progresso técnico;
- pendências técnicas;
- histórico sob demanda;
- monitor;
- ação de reprocessamento.

Ações de upload/processamento devem ficar próximas da fila e habilitar/desabilitar conforme existência/seleção de arquivos.

Upload deve suportar:

- arrastar e soltar;
- múltiplos arquivos;
- múltiplos arrastos;
- ZIP quando previsto;
- renomeação assistida quando apropriada;
- associação contextual.

## 4. Preview documental

**DECISÃO HISTÓRICA APROVADA**

Ao selecionar linha/documento:

- abrir preview embutido;
- preferencialmente painel lateral;
- não obrigar nova guia;
- linha selecionada destacada;
- checkbox reservado para seleção em lote, não para “abrir”;
- painel com espaço suficiente para leitura.

Ações recuperadas:

- Abrir;
- Baixar;
- Imprimir/Salvar PDF;
- Copiar link;
- Voltar/fechar preview sem perder filtros.

Preview não altera original.

## 5. Fila versus Histórico

**DECISÃO HISTÓRICA APROVADA**

Fila mostra operação corrente.

Depois de sessão concluída:

- pode desaparecer da fila visual;
- continua persistida;
- aparece em Histórico mediante contexto/chave.

Não misturar meses e sessões antigas na tela diária.

## 6. Monitor

**DECISÃO HISTÓRICA APROVADA**

Visualização em tempo real deve permitir entender:

- cliente;
- arquivo;
- bloco;
- etapa;
- percentual;
- motor;
- competência;
- arquivamento;
- resultado/saída.

O monitor é leitura operacional. Abrir monitor não dispara mutação.

## 7. Fechamento Mensal

**DECISÃO HISTÓRICA APROVADA**

Tela de Fechamento deve ser simples:

- abrir competência;
- listar clientes do universo;
- mostrar chamada;
- mostrar estado;
- permitir filtros;
- mostrar contagens;
- abrir movimento/detalhe do cliente;
- histórico por competência.

Não deve conter controles de upload/processamento.

Não deve exigir marcação manual de todos os clientes para iniciar fluxo normal.

## 8. Central de Conferência

**DECISÃO HISTÓRICA APROVADA**

É a mesa de resolução.

Na mesma ficha:

- ver expectativa por fonte;
- ver documentos;
- ver valores;
- anexar documento;
- reprocessar;
- justificar;
- marcar sem movimento;
- registrar ocorrência;
- resolver;
- ver histórico.

A crítica histórica mais forte foi justamente evitar mandar o usuário “sair da Conferência” para resolver o que a Conferência identificou.

## 9. Pendências

**DECISÃO HISTÓRICA APROVADA**

Separar:

### Pendência técnica
Arquivo ilegível, parser falhou, cliente não identificado, extração impossível.

### Pendência de conferência
Documento faltante, valor divergente, fonte não aplicável, justificativa necessária.

Não usar “Com pendências” como status genérico de sessão 100% processada.

## 10. Busca, filtros e paginação

**DECISÃO HISTÓRICA APROVADA**

Listagens grandes devem oferecer:

- pesquisa;
- filtros;
- ordenação;
- paginação;
- quantidade por página;
- seleção múltipla quando houver ação em lote.

No histórico do Tools apareceram opções como 10/25/50/100.  
O ecossistema Axiom posterior também adotou padrões como 25/50/100/200/Todos.

Isso é uma evolução de UI: o número exato deve seguir o canônico visual vigente do produto destino, mas a necessidade de paginação/busca é permanente.

## 11. Densidade visual

**DECISÃO HISTÓRICA APROVADA**

Evitar:

- cards enormes para pouca informação;
- excesso de espaços;
- tabelas com poucas linhas por tela;
- botões desalinhados;
- ações repetidas em várias áreas;
- status sem explicação.

Preferir:

- informação compacta;
- hierarquia clara;
- cor como apoio semântico, não decoração excessiva;
- detalhes sob demanda;
- ação principal evidente;
- botões alinhados e consistentes.

## 12. Repositório / Arquivo do Cliente

**DECISÃO HISTÓRICA APROVADA**

Central documental precisa permitir navegação por:

- cliente;
- CPF/CNPJ;
- tipo;
- competência;
- datas;
- valores;
- protocolo;
- hash.

Arquivo pode ser localizado pela árvore física ou pelo índice.

Varredura recursiva deve trazer arquivos existentes para a visão sem exigir novo upload.

## 13. Impressão

**CANÔNICO / DECISÃO HISTÓRICA APROVADA**

Recursos:

- seleção por competência;
- seleção por cliente;
- seleção por tipo;
- versão vigente por padrão;
- ordenação A–Z;
- agrupamento por empresa;
- pré-visualização;
- PDF consolidado temporário/derivado;
- múltiplos arquivos quando desejado;
- relatório de lote;
- impressão controlada.

Impressão não sobrescreve original.

## 14. Bloqueio de impressão

**DECISÃO HISTÓRICA APROVADA**

Documento/cliente não autorizado pela Conferência/Fechamento não entra na saída apenas porque foi marcado manualmente.

Gate de backend é soberano.

Retificação material aberta deve bloquear saída automática da versão anterior como se ainda fosse vigente.

## 15. Centro de Impressão × Central de Entregas

**DECISÃO HISTÓRICA APROVADA**

Separação aceita:

### Centro de Impressão
Clientes de retirada presencial, office-boy e outras rotinas físicas.

### Central de Entregas
Clientes eletrônicos, como e-mail/WhatsApp/portal, conforme configuração.

A mesma documentação pode alimentar ambas, mas o fluxo de saída e auditoria é diferente.

## 16. Organização das saídas

**DECISÃO HISTÓRICA APROVADA**

Para clientes eletrônicos, estrutura central por cliente → ano → mês/competência.

Formatos:

- arquivos individuais;
- PDF único;
- ZIP;
- grupos por categoria;
- configuração personalizada.

Originais são copiados/referenciados; não movidos para “Saída”.

## 17. DARF e FGTS

**DECISÃO HISTÓRICA APROVADA**

Padrão operacional posteriormente preferido:

- DARF e FGTS eletrônicos separados;
- unificação opcional/parametrizável por cliente;
- não impor PDF único para todos.

Também deve ser possível gerar lotes gerais por tipo:

- geral DARF;
- geral FGTS;
- por empresa;
- individuais;
- consolidados quando solicitado.

## 18. Contracheques e pró-labore

**DECISÃO HISTÓRICA APROVADA**

Para entrega eletrônica, podem ser agrupados por empresa.

A forma final pode ser:

- individuais;
- pacote;
- PDF consolidado;
- ZIP;

conforme parâmetro do cliente/fechamento.

## 19. Presencial/office-boy

**DECISÃO HISTÓRICA APROVADA**

Clientes de entrega física devem cair naturalmente no Centro de Impressão após autorização.

Não exigir que o usuário monte manualmente a carteira de impressão todo mês.

## 20. Relatórios

**DECISÃO HISTÓRICA APROVADA**

Relatórios operacionais devem ser:

- filtráveis;
- exportáveis;
- imprimíveis quando aplicável;
- auditáveis;
- capazes de operar em volumes grandes.

Relatórios de fechamento precisam explicar:

- cliente;
- competência;
- estado;
- fonte;
- divergência;
- justificativa;
- versão.

Houve regra de validação A4/retrato na auditoria V8. Esse material é útil como contrato de regressão, mas deve ser confrontado com o padrão visual atual antes de reutilização.

## 21. UX de erro

**DECISÃO HISTÓRICA APROVADA**

Erro deve responder:

- o que aconteceu;
- em qual arquivo/cliente/fonte;
- se é técnico ou operacional;
- o que está bloqueado;
- o que o usuário pode fazer.

Evitar status genérico que force o operador a “adivinhar” o problema.

## 22. Regra de continuidade

A interface deve sempre tentar manter o usuário no contexto em que o problema apareceu.

Exemplo clássico:

    Conferência encontrou ausência
      → anexar ali mesmo
      → processar
      → recalcular
      → atualizar a ocorrência

Não:

    Conferência → sair → Upload → procurar cliente → escolher competência → processar → voltar → procurar ocorrência.
