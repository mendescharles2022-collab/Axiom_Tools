# Arquitetura Operacional — Fechamento V8

Status: **Aprovada conceitualmente / implementação em andamento**  
Data inicial: 26/08/2026  
Última atualização: 27/08/2026

## 1. Princípio central

Fechamento Mensal, Processamento de Arquivos e Central de Conferência têm papéis distintos e não devem duplicar responsabilidades.

Regra operacional: **o fluxo normal deve acontecer sozinho; intervenção humana é para exceções**.

O Axiom Tools não é apenas extrator. Ele também administra o acervo e as estruturas de pastas de clientes ativos, inativos, baixados, com movimento e sem movimento. Por isso, estar cadastrado no Tools não significa participar automaticamente do fechamento mensal.

## 2. Competência como origem única do ciclo

A competência deve ser aberta **uma única vez**, no Fechamento Mensal.

- Fechamento Mensal fica antes de Processamento de Arquivos no fluxo e na navegação.
- Processamento, Conferência, Entregas e Impressão herdam o contexto da competência operacional.
- O Processamento não deve exigir nova digitação, aplicação ou abertura da competência.
- Histórico e retificações podem consultar competências anteriores sem trocar silenciosamente a competência operacional ativa.

## 3. Fechamento Mensal e composição da competência

Responsabilidade: **abrir competência, definir o universo operacional mensal e acompanhar o ciclo**.

Ao abrir uma competência, o sistema cria a composição mensal sem alterar o cadastro mestre nem as pastas físicas.

Cada cliente pode ser classificado na competência como:

- `Com movimento`;
- `Sem movimento`;
- fora do ciclo/não aplicável, quando pertinente.

A visão operacional padrão deve privilegiar **clientes ativos com movimento**, mantendo filtros para consultar os demais.

As caixas de seleção servem para ações administrativas em lote, e não para determinar manualmente quem será processado.

### Chamadas

A competência admite chamadas sucessivas: 1ª, 2ª, 3ª e seguintes, sem limite artificial.

Clientes adiados devem registrar motivo e histórico auditável. Motivos previstos incluem:

- aguardando registro;
- rescisão pendente;
- decisão administrativa;
- aguardando apontamento do cartão de ponto;
- outro motivo documentado.

A mudança deve preservar usuário, data/hora, chamada anterior, nova chamada, motivo e observação quando houver.

Clientes `Com movimento` liberados na chamada atual entram automaticamente no contexto operacional do Processamento. Clientes em chamada futura e clientes `Sem movimento` ficam fora do processamento normal até mudança válida de estado.

### Estados do ciclo

O Fechamento deve refletir estados reais, sem antecipar a Conferência:

- aguardando processamento;
- em processamento;
- em conferência;
- pendente/divergente na conferência;
- sem movimento na competência;
- próxima chamada/impedida;
- fechada;
- retificação detectada/em conferência/retificada.

Um cliente sem evidência documental processada **não deve aparecer como `Em conferência`**. Antes disso, o estado correto é `Aguardando processamento` ou `Em processamento`, conforme o caso.

Não deve existir fluxo normal de `Fechar selecionadas`.

O cliente é considerado fechado quando a Central de Conferência concluir todas as expectativas aplicáveis ou registrar justificativas válidas.

## 4. Processamento de Arquivos

Responsabilidade: **infraestrutura documental e execução técnica**.

Deve:

- receber arquivos;
- herdar competência e chamada do Fechamento Mensal;
- identificar cliente e competência;
- classificar documento;
- extrair dados;
- reprocessar falhas técnicas;
- manter fila, hash, cache e checkpoints;
- expor apenas o contexto operacional corrente, evitando mistura visual com apurações anteriores.

Dados históricos continuam preservados e acessíveis em visão própria, mas não contaminam a operação corrente.

### Semântica das sessões de processamento — decisão de 27/08/2026

A visualização das sessões deve representar **somente o progresso técnico do processamento**, sem misturar resultado de conferência.

Regras aprovadas para atualização futura:

- nenhum arquivo processado → `0% · Processo não iniciado`;
- processamento em andamento → `X% · Processando`;
- todos os itens percorridos sem falha técnica → `100% · Processamento concluído`;
- todos os itens percorridos com falhas técnicas reais → `100% · Concluído com falhas técnicas`;
- execução interrompida → `X% · Interrompido`.

`100%` significa que o motor percorreu 100% da sessão; **não significa que os documentos estejam corretos ou que o cliente esteja fechado**.

Uma sessão tecnicamente concluída não deve aparecer como `Com pendências` apenas porque a Conferência encontrou ausência, divergência ou incompletude documental.

A aba `Pendências` do Processamento deve ser reservada a **pendências técnicas**, como arquivo ilegível, identificação impossível, erro de extração ou falha de motor. Pendências documentais, contábeis e de batimento pertencem à Central de Conferência.

Quando útil, uma sessão concluída pode informar separadamente quantos itens/clientes foram encaminhados à Conferência, sem alterar o status técnico da execução.

## 5. Central de Conferência

Responsabilidade: **mesa de trabalho do fechamento**.

A Conferência deve receber apenas clientes que efetivamente alcançaram o estágio de conferência, e não toda a composição mensal antecipadamente.

A própria ficha do cliente deve permitir, quando aplicável:

- marcar `Sem movimento nesta competência`;
- justificar ausência;
- registrar próxima chamada/impedimento;
- anexar documento faltante;
- reprocessar documento existente;
- abrir documentos da empresa;
- registrar ocorrência/evidência manual sem sair da tela;
- registrar decisão manual auditável.

A área da ocorrência deve funcionar como mesa de resolução, permitindo **Anexar documento**, **Reprocessar**, **Registrar ocorrência**, **Resolver/Justificar** e **Ver documentos** sem abandonar a Central de Conferência.

Documentos anexados a partir de uma ocorrência devem herdar cliente, competência e contexto da ocorrência, entrar no motor especialista correspondente e provocar novo cálculo automático da conferência quando o reprocessamento terminar.

### FGTS rescisório e múltiplas evidências

A conferência não deve pressupor uma única guia de FGTS por cliente/competência. Pode haver recolhimento rescisório antecipado em razão do vencimento da rescisão e, posteriormente, recolhimento mensal da competência.

O motor deve preservar cada documento individualmente e somar as evidências aplicáveis ao mesmo cliente/competência para o batimento. Divergência deve desaparecer quando a composição documental explicar integralmente o valor esperado, sem necessidade de ignorar manualmente uma diferença válida.

### Justificativas previstas

- sem movimento no mês;
- afastamento integral;
- admissão pendente;
- rescisão pendente;
- FGTS rescisório recolhido antecipadamente;
- documento ainda não emitido;
- compensação/suspensão de débito;
- ausência de incidência;
- próxima chamada;
- outro motivo documentado.

## 6. Fechamento automático

Fluxo:

`Competência aberta → composição/chamada → documentos processados → conferência → expectativas aplicáveis satisfeitas/justificadas → FECHADO`

O status fechado deve registrar data/hora e versão do fechamento.

## 7. Retificação inteligente

Quando chegam novos dados para cliente/competência já fechados:

- dados idênticos → já conhecido, sem nova versão;
- evidência complementar sem impacto material → preserva fechamento vigente;
- mudança material → cria retificação candidata versionada;
- histórico anterior nunca é apagado;
- comparação Vn → Vn+1 deve destacar deltas de valores, pessoas e documentos;
- saídas automáticas ficam bloqueadas enquanto a retificação não for concluída.

## 8. Regras de expectativa documental

A Conferência não deve cobrar indiscriminadamente todas as fontes. O **perfil cadastrado do cliente é fonte obrigatória para determinar quais documentos e cruzamentos são aplicáveis**.

- FGTS: somente quando aplicável ao perfil/evidências.
- **MEI:** quando o cadastro do cliente estiver marcado como MEI, não cobrar guia FGTS Digital autônoma no fluxo normal. O recolhimento aplicável de FGTS do empregado integra o **DAE do MEI**; a expectativa documental e o batimento devem usar DAE/regra específica do perfil MEI. A marcação MEI no cadastro deve prevalecer sobre heurísticas genéricas de incidência que hoje possam criar falsa divergência de FGTS Digital.
- **MEI com situação excepcional:** eventual evidência extraordinária deve ser tratada explicitamente, sem transformar a exceção em expectativa mensal padrão.
- eConsignado: somente com evidência positiva.
- Sem movimento mensal: reduz expectativas daquela competência sem alterar cadastro permanente.
- DARF: comparação pela composição aplicável, incluindo previdenciário, IRRF, PIS sobre folha, SENAR/Funrural e outros débitos reconhecidos.

## 9. Saídas

Após fechamento:

- clientes de entrega eletrônica → Central de Entregas;
- retirada/office-boy → Centro de Impressão por padrão;
- seleção manual de outros clientes permanece possível;
- DARF e FGTS eletrônicos ficam separados por padrão;
- unificação é parametrizável por cliente;
- contracheques podem ser agrupados por empresa.

## 10. Histórico de decisões e governança do repositório

O repositório deve permanecer atualizado como fonte de continuidade do projeto, registrando de forma rastreável:

- melhorias aprovadas;
- falhas encontradas;
- causas identificadas;
- correções e resoluções adotadas;
- decisões funcionais e arquiteturais;
- versões instaladas e homologadas;
- pendências conhecidas e melhorias futuras.

Documentação não substitui sincronização do código operacional. Sempre que houver acesso à instalação real, a árvore do repositório deve ser confrontada com ela antes de ser tratada como espelho fiel da instalação.

## 11. Situação operacional registrada em 27/08/2026

- V5.6.14T9 (24/08/2026) permanece referência histórica de baseline comprovada na competência 05/2026.
- V5.6.14V8 introduziu competência única, composição mensal e chamadas.
- V5.6.14V8A foi aplicada em 27/08/2026 com backup automático e preservação dos motores/documentos.
- Foi identificado que a interface ainda pode exibir estados antecipados de `Em conferência` e comandos técnicos que não pertencem ao fluxo normal; isso deve ser corrigido sem reescrever os motores.
- Foi identificada nomenclatura inadequada `Com pendências` nas sessões tecnicamente concluídas; a semântica aprovada está definida na seção 4 e fica registrada para atualização futura.
- Foi identificada falsa expectativa de FGTS Digital em cliente cadastrado como MEI. A correção aprovada é tornar o perfil cadastral determinante: MEI usa expectativa de DAE e não deve receber cobrança mensal genérica de guia FGTS Digital autônoma.
- Foi aprovada a evolução da ocorrência da Central de Conferência para permitir anexar, reprocessar, registrar evidências/ocorrências e resolver justificativas sem sair da tela, inclusive composição de múltiplas guias de FGTS e FGTS rescisório antecipado.

## 12. Critério de conclusão da V8

A V8 só será concluída após:

- integração dos três módulos sem duplicidade;
- competência aberta uma única vez e herdada pelos módulos;
- composição mensal e chamadas validadas operacionalmente;
- estados do ciclo coerentes com o estágio real;
- anexar/reprocessar diretamente na Conferência;
- expectativas documentais respeitando o perfil cadastral, inclusive MEI/DAE;
- fechamento automático validado;
- retificação preservada;
- regressão sobre Domínio, eSocial, e-CAC/DARF, FGTS, DAE/MEI e eConsignado;
- pacote Windows com backup, rollback e validação funcional.
