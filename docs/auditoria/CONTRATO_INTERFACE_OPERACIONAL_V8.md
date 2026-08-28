# Contrato V8 — Interface operacional de Fechamento, Processamento e Conferência

Data: 28/08/2026
Status: **contrato de auditoria / implementação ainda não homologada**

## 1. Princípio

Fechamento Mensal, Processamento de Arquivos e Central de Conferência são três módulos com papéis distintos.

A interface não deve duplicar decisões nem obrigar o usuário a repetir contexto.

Fluxo normal:

`Fechamento Mensal -> Processamento de Arquivos -> Central de Conferência -> Saídas`

Intervenção humana concentra-se em exceções.

## 2. Fechamento Mensal

Responsabilidade exclusiva:

- abrir competência;
- formar a composição mensal;
- classificar movimento mensal;
- administrar chamadas/impedimentos;
- acompanhar o estado agregado do ciclo;
- acessar histórico e retificações em áreas próprias.

### Deve existir

- competência operacional atual claramente visível;
- ação de abrir nova competência quando permitido;
- indicadores de chamada e estados reais;
- filtros por situação/movimento/chamada;
- ações administrativas de movimento/chamada com histórico;
- acesso à aba/fluxo de retificações.

### Não deve existir no fluxo normal

- `Fechar selecionadas`;
- seleção manual para decidir quem será processado;
- reprocessamento técnico de arquivos;
- classificação manual de documento;
- repetição da competência em outros módulos como se fosse nova abertura.

Fechamento é consequência da Conferência, não botão de conveniência.

## 3. Processamento de Arquivos

Responsabilidade:

- receber/descobrir arquivos;
- executar motores;
- identificar cliente/competência;
- classificar e extrair;
- manter sessões, fila, hash, cache e checkpoints;
- tratar falhas técnicas;
- encaminhar resultado para Conferência.

### Contexto

A competência e chamada são herdadas do Fechamento Mensal.

A interface não deve pedir:

- abrir competência novamente;
- aplicar competência novamente;
- selecionar carteira manualmente para reconstruir o universo mensal.

Histórico pode consultar outras competências sem trocar silenciosamente o contexto operacional.

### Sessões

Sessão representa progresso técnico:

- `0% · Processo não iniciado`;
- `X% · Processando`;
- `100% · Processamento concluído`;
- `100% · Concluído com falhas técnicas`;
- interrupção quando aplicável.

Não usar `Com pendências` para divergência de negócio.

## 4. Aba Pendências do Processamento

O status V8F2 confirmou que a aba ainda obriga o usuário a lidar com PROC/chaves técnicas para isolar a competência corrente.

Regra V8:

- competência operacional é filtro primário automático;
- PROC/sessão é filtro técnico secundário e limitado ao ciclo corrente por padrão;
- `Competência não identificada` aparece como exceção própria;
- pendências técnicas de outras competências não contaminam a mesa atual;
- usuário pode consultar histórico explicitamente.

### Pendência técnica válida

Exemplos:

- arquivo ilegível;
- cliente não identificado;
- competência não identificada;
- erro de extração;
- motor falhou;
- arquivo bloqueado/corrompido.

### Não pertence aqui

- DARF ausente esperada;
- diferença de FGTS;
- eConsignado divergente;
- justificativa de procuração;
- obrigação não aplicável;
- composição rescisória.

Esses itens pertencem à Conferência.

## 5. Central de Conferência

Responsabilidade: mesa de trabalho das exceções e dos batimentos.

Recebe apenas clientes que efetivamente alcançaram estágio de conferência na chamada corrente.

### Ficha/ocorrência deve permitir sem sair da tela

- ver fontes/obrigações independentes;
- abrir documentos;
- anexar documento faltante;
- reprocessar documento existente;
- registrar ocorrência/evidência;
- justificar uma fonte específica;
- marcar obrigação não aplicável quando válido;
- registrar impedimento externo;
- mover para próxima chamada quando cabível;
- marcar sem movimento da competência quando válido;
- ver histórico/auditoria da resolução.

Ações devem herdar cliente + competência + fonte da ocorrência.

## 6. Conferência não é navegação de histórico misturada

Mesa padrão = trabalho vivo da chamada atual.

Não misturar na mesma lista operacional:

- clientes fechados apenas para consulta;
- retificações;
- chamada futura;
- competências anteriores.

Esses universos devem ter acesso próprio/filtros explícitos, sem contaminar contadores e pendências da mesa atual.

## 7. Estados visuais devem refletir estado real

Não apresentar `Em conferência` antes de existir evidência processada suficiente.

Exemplos:

- composição aberta, sem arquivos -> `Aguardando processamento`;
- sessão ativa -> `Em processamento`;
- evidências processadas e análise necessária -> `Em conferência`;
- obrigação divergente -> pendente/divergente;
- chamada futura -> `Aguardando 2ª chamada` (ou correspondente);
- fechado -> histórico/estado fechado, fora da mesa viva;
- mudança material posterior -> fluxo de retificação.

## 8. Navegação

Na ordem operacional, Fechamento Mensal deve preceder Processamento de Arquivos.

A interface deve deixar claro o caminho:

1. competência;
2. processamento técnico;
3. conferência;
4. impressão/entrega.

Não criar dois módulos com o mesmo papel nem atalhos que levem o usuário a administrar competência em mais de um lugar.

## 9. Comandos técnicos

A arquitetura V8 já registrou que a interface ainda pode expor comandos técnicos que não pertencem ao fluxo normal.

Regra:

- ações técnicas avançadas ficam em contexto de diagnóstico/manutenção quando realmente necessárias;
- fluxo normal apresenta ações operacionais compreensíveis;
- nenhum comando técnico deve ser exigido para isolar uma competência, reconstituir carteira ou concluir uma ocorrência comum.

## 10. Regressões obrigatórias de interface

1. competência é aberta uma única vez;
2. Processamento herda competência sem pedir reaplicação;
3. chamada futura não aparece no processamento/conferência corrente;
4. `Fechar selecionadas` não existe no fluxo normal;
5. sessão 100% não aparece `Com pendências` por divergência da Conferência;
6. aba Pendências abre filtrada pela competência operacional;
7. usuário não precisa informar PROC para enxergar o ciclo corrente;
8. competência não identificada fica em exceção visível;
9. Central mostra apenas trabalho vivo por padrão;
10. fechado não volta à mesa sem retificação;
11. retificação tem fluxo próprio;
12. ocorrência permite anexar/reprocessar/resolver sem abandonar a Central;
13. justificativa é por fonte;
14. abrir a Central não altera dados;
15. estados exibidos correspondem ao estágio real.

## 11. Evidência atual

Confirmado documentalmente:

- V7 removeu `Fechar selecionadas`;
- arquitetura V8 mantém essa remoção;
- V8F2 ainda possui problema na aba Pendências com filtro por PROC/chaves técnicas;
- arquitetura V8 registra exposição de estados antecipados e comandos técnicos fora do fluxo ideal.

Não há evidência nesta rodada de que `Fechar selecionadas` tenha sido reintroduzido no template atual; portanto isso permanece como regressão preventiva, não defeito atual confirmado.

## 12. Critério de homologação

Os três módulos só serão considerados integrados quando o usuário puder percorrer uma competência real sem repetir contexto e sem precisar conhecer identificadores técnicos internos para executar a rotina normal.
