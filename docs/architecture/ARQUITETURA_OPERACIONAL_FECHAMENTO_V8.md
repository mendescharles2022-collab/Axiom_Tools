# Arquitetura Operacional — Fechamento V8

Status: **Aprovada conceitualmente / implementação em andamento**  
Data: 26/08/2026

## 1. Princípio central

Fechamento Mensal, Processamento de Arquivos e Central de Conferência têm papéis distintos e não devem duplicar responsabilidades.

## 2. Fechamento Mensal

Responsabilidade: **abrir competência e acompanhar o ciclo**.

Ao abrir uma competência, o sistema carrega os clientes ativos e passa a refletir, sem exigir seleção manual de rotina:

- aguardando documentos;
- em processamento;
- em conferência;
- pendente;
- divergente;
- sem movimento na competência;
- próxima chamada/impedida;
- fechada;
- retificação detectada/em conferência/retificada.

Não deve existir fluxo normal de `Fechar selecionadas`.

O cliente é considerado fechado quando a Central de Conferência concluir todas as expectativas aplicáveis ou registrar justificativas válidas.

## 3. Processamento de Arquivos

Responsabilidade: **infraestrutura documental**.

Deve:

- receber arquivos;
- identificar cliente e competência;
- classificar documento;
- extrair dados;
- reprocessar;
- manter fila, hash, cache e checkpoints;
- expor apenas o contexto operacional da competência aberta no Fechamento Mensal, evitando mistura visual com apurações anteriores.

Dados históricos continuam preservados e acessíveis em visão própria, mas não contaminam a operação corrente.

## 4. Central de Conferência

Responsabilidade: **mesa de trabalho do fechamento**.

A própria ficha do cliente deve permitir, quando aplicável:

- marcar `Sem movimento nesta competência`;
- justificar ausência;
- registrar próxima chamada/impedimento;
- anexar documento faltante;
- reprocessar documento existente;
- abrir documentos da empresa;
- registrar decisão manual auditável.

### Justificativas previstas

- sem movimento no mês;
- afastamento integral;
- admissão pendente;
- rescisão pendente;
- documento ainda não emitido;
- compensação/suspensão de débito;
- ausência de incidência;
- próxima chamada;
- outro motivo documentado.

## 5. Fechamento automático

Fluxo:

`Competência aberta → documentos processados → conferência → expectativas aplicáveis satisfeitas/justificadas → FECHADO`

O status fechado deve registrar data/hora e versão do fechamento.

## 6. Retificação inteligente

Quando chegam novos dados para cliente/competência já fechados:

- dados idênticos → já conhecido, sem nova versão;
- evidência complementar sem impacto material → preserva fechamento vigente;
- mudança material → cria retificação candidata versionada;
- histórico anterior nunca é apagado;
- comparação Vn → Vn+1 deve destacar deltas de valores, pessoas e documentos;
- saídas automáticas ficam bloqueadas enquanto a retificação não for concluída.

## 7. Regras de expectativa documental

A Conferência não deve cobrar indiscriminadamente todas as fontes.

- FGTS: somente quando aplicável ao perfil/evidências.
- eConsignado: somente com evidência positiva.
- Sem movimento mensal: reduz expectativas daquela competência sem alterar cadastro permanente.
- DARF: comparação pela composição aplicável, incluindo previdenciário, IRRF, PIS sobre folha, SENAR/Funrural e outros débitos reconhecidos.

## 8. Saídas

Após fechamento:

- clientes de entrega eletrônica → Central de Entregas;
- retirada/office-boy → Centro de Impressão por padrão;
- seleção manual de outros clientes permanece possível;
- DARF e FGTS eletrônicos ficam separados por padrão;
- unificação é parametrizável por cliente;
- contracheques podem ser agrupados por empresa.

## 9. Critério de conclusão da V8

A V8 só será concluída após:

- integração dos três módulos sem duplicidade;
- isolamento consistente por competência;
- anexar/reprocessar diretamente na Conferência;
- fechamento automático validado;
- retificação preservada;
- regressão sobre Domínio, eSocial, e-CAC/DARF, FGTS e eConsignado;
- pacote Windows com backup, rollback e validação funcional.
