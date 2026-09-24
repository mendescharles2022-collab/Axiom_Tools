# Axiom Tools — Fechamento, Conferência, Regras de DP e Casos Reais

Data: 23/09/2026

## 1. Separação obrigatória

**DECISÃO HISTÓRICA APROVADA**

### Fechamento Mensal
Abre competência e acompanha o ciclo.

### Processamento
Executa trabalho técnico sobre documentos.

### Central de Conferência
Decide se as evidências explicam corretamente a obrigação.

Nenhum dos três deve duplicar o papel dos outros.

## 2. Competência única

**DECISÃO HISTÓRICA APROVADA**

A competência é aberta uma vez no Fechamento Mensal.

Processamento, Conferência, Impressão e Entregas herdam esse contexto.

Processamento não deve pedir uma nova “abertura” de competência.

Consultas históricas não trocam silenciosamente a competência ativa.

## 3. Universo operacional

**DECISÃO HISTÓRICA APROVADA**

A competência cria uma composição mensal sem alterar cadastro mestre.

Situações:

- Com movimento;
- Sem movimento;
- Fora do ciclo/não aplicável;
- Chamada futura/impedido.

Fluxo automático normal trabalha somente com clientes:

- pertencentes ao universo;
- com movimento;
- liberados na chamada atual.

Cliente cadastrado no Tools não participa automaticamente de todo fechamento.

## 4. Quantitativo do DP

**DECISÃO HISTÓRICA APROVADA**

Regra:

    quantidade inicial + admissões − desligamentos = quantidade a transportar

Essa informação deve ser preservada por competência e cliente.

A carteira de fechamento quantitativo é relevante para clientes com empregados.

Sem movimento pode registrar zero sem simular movimentação inexistente.

## 5. Chamadas

**DECISÃO HISTÓRICA APROVADA**

Chamadas sucessivas:

- 1ª;
- 2ª;
- 3ª;
- seguintes, sem limite artificial.

Motivos recuperados:

- aguardando registro/admissão;
- rescisão pendente;
- decisão administrativa;
- aguardando cartão de ponto/apontamento;
- procuração/acesso impedido;
- outro motivo documentado.

Mudança de chamada registra:

- usuário;
- data/hora;
- chamada anterior;
- nova chamada;
- motivo;
- observação.

## 6. Estados do ciclo

**DECISÃO HISTÓRICA APROVADA**

Estados coerentes com estágio real:

- Aguardando processamento;
- Em processamento;
- Em conferência;
- Pendente/Divergente;
- Sem movimento;
- Próxima chamada/Impedida;
- Fechada;
- Retificação detectada;
- Retificação em conferência;
- Retificada.

Cliente sem documento processado não deve aparecer antecipadamente como Em conferência.

## 7. Fechamento automático

**DECISÃO HISTÓRICA APROVADA**

Não existe necessidade operacional de “Fechar selecionadas” como mecanismo normal.

Fluxo:

    competência aberta
      → composição/chamada
      → processamento
      → conferência
      → fontes aplicáveis satisfeitas ou justificadas
      → FECHADO

Fechado registra versão e data/hora.

## 8. Central de Conferência como mesa de resolução

**DECISÃO HISTÓRICA APROVADA**

Sem sair da ficha/ocorrência, permitir:

- marcar Sem movimento nesta competência;
- justificar ausência;
- alterar/justificar chamada quando autorizado;
- anexar documento;
- reprocessar documento;
- registrar ocorrência;
- registrar evidência manual;
- ver documentos;
- resolver/justificar;
- recalcular resultado.

Anexo feito na ocorrência herda cliente, competência e contexto.

## 9. Estados por fonte

**DECISÃO HISTÓRICA APROVADA**

Conferência deve poder avaliar separadamente:

- Domínio;
- eSocial;
- DARF/federal;
- FGTS;
- DAE;
- eConsignado;
- outras fontes aplicáveis.

Uma fonte justificada não transforma todas as outras em justificadas.

## 10. Expectativa documental

**DECISÃO HISTÓRICA APROVADA**

Não cobrar toda fonte de todo cliente.

Aplicabilidade deriva de:

- perfil cadastral;
- situação da competência;
- pessoas/movimentações;
- evidências;
- regime/tipo;
- regras normativas.

Exemplos:

- MEI: DAE específico, sem expectativa mensal genérica de FGTS Digital autônomo;
- doméstico: DAE;
- eConsignado: somente com evidência/aplicabilidade;
- produtor rural: regras específicas;
- sem movimento: reduz expectativas mensais sem alterar cadastro permanente.

## 11. FGTS e rescisões

**DECISÃO HISTÓRICA APROVADA**

O motor precisa distinguir:

- FGTS mensal;
- FGTS rescisório;
- FGTS rescisório antecipado;
- multa rescisória;
- recolhimentos em documentos diferentes;
- competência do desligamento;
- valores de garantia vinculados a consignado quando existirem.

Não considerar divergência apenas porque o valor não está em uma única guia.

A composição correta pode exigir soma de múltiplas evidências.

## 12. Consignado em rescisão

**DECISÃO HISTÓRICA APROVADA**

Casos reais mostraram que consignado não pode ser tratado como uma única parcela mensal.

Separar:

- parcela ordinária;
- ajuste por rescisão;
- garantia/FGTS;
- valores não calculados inicialmente e inseridos depois;
- evidências que chegam em reprocessamento.

## 13. Rural / múltiplas matrículas

**CANÔNICO ESPECÍFICO**

Caso Jair Ferreira Camargo consolidou a regra:

- DARF federal repetido entre matrículas do mesmo contribuinte não é somado em duplicidade;
- FGTS individualizado por matrícula é aditivo;
- comparar uma única apuração federal consolidada;
- somar parcelas de FGTS aplicáveis;
- preservar detalhamento por matrícula.

Essa regra é genérica e não hardcode do cliente.

## 14. Funrural, SENAR e INCRA

**DECISÃO HISTÓRICA APROVADA**

Empregador/produtor rural deve ser identificado pelo cadastro e cenário, não apenas pelo nome/CNAE.

Separar cenários:

- Produtor Rural PF — comercialização;
- Produtor Rural PF — opção pela folha;
- Segurado Especial;
- Produtor Rural PJ;
- Agroindústria.

Regras históricas registradas em trabalho correlato:

- SENAR 0,20% em cenários previstos;
- opção pela folha é regra específica do PRPF;
- R-2055 e indicador de opção precisam ser tratados conforme cenário;
- INCRA/Funrural/SENAR não devem ser lançados por heurística genérica;
- vigência e fonte normativa importam.

O Tools deve consumir regra normativa versionada, não números espalhados nos parsers.

## 15. DARF emitida pelo Fiscal

**DECISÃO HISTÓRICA APROVADA — CASO REAL**

Em alguns clientes a DARF é emitida pela equipe fiscal, consolidando impostos fiscais com parcela previdenciária.

Consequência:

- DP não deve gerar “pendência” apenas porque não emitiu a DARF;
- fonte deve registrar responsabilidade/fluxo;
- conferência usa a DARF real quando disponível;
- FGTS continua sob rotina do DP quando assim definido.

## 16. Casos reais de agosto/2026 preservados

### Afastamento integral pelo INSS
**CASO REAL / REGRA DE REGRESSÃO**

Cliente/produtor rural com funcionário integralmente afastado, sem valores no mês.

Não cobrar guia inexistente apenas porque o cliente costuma ter obrigação. Aplicabilidade deve reconhecer ausência de base no mês.

### Procuração revogada
**CASO REAL / REGRA DE REGRESSÃO**

Cliente saiu do escritório e a revogação da procuração foi descoberta ao tentar operar o eSocial/e-CAC.

O sistema deve representar impedimento externo/administrativo, e não “guia zero”, “erro de motor” ou ausência injustificada.

### Cliente com rescisão
**CASO REAL / REGRA DE REGRESSÃO**

Rescisão modifica expectativas de FGTS e consignado. O sistema deve procurar evidências rescisórias e não comparar tudo como mensal ordinário.

### Ribeiro e Nascimento
**CASO REAL / REGRA DE REGRESSÃO**

Ocorrência envolveu consignados e garantias na rescisão.

Falha observada: primeiro processamento não calculou valores; depois guias/relatórios foram incluídos, mas o reprocessamento não releu/recompôs corretamente.

Regressão obrigatória:

- nova evidência precisa participar do reprocessamento;
- não reutilizar snapshot incompleto como se estivesse atual;
- recompor consignado/garantia e recalcular conferência.

### T L Empreendimentos Agrícolas
**CASO REAL / REGRA DE REGRESSÃO**

Empresa configurada para 2ª chamada entrou indevidamente na 1ª.

Regra: universo operacional/chamada precisa ser soberano em todos os motores e consultas.

### Funcionário com faltas em toda a competência
**CASO REAL / REGRA DE REGRESSÃO**

Funcionário com apontamento de faltas em todos os dias pode resultar em ausência de valores e guias.

O sistema não pode concluir automaticamente que documento está faltando sem interpretar base/remuneração.

### P da Silva Carmo
**CASO DE AUDITORIA**

Exemplo que expôs erro de classificação de pessoa: diretor/pró-labore não deve inflar contagem de empregados/FGTS por aparecer como “Trabalhando”.

## 17. Sem movimento

**DECISÃO HISTÓRICA APROVADA**

Sem movimento é condição mensal.

Pode ser marcado na Conferência com justificativa/evidência apropriada.

Não altera o cadastro permanente para “cliente sem movimento”.

Sem movimento também não pode ser usado como atalho automático para esconder falha de processamento.

## 18. Justificativas

**DECISÃO HISTÓRICA APROVADA**

Categorias recuperadas:

- sem movimento;
- afastamento integral;
- admissão pendente;
- rescisão pendente;
- FGTS rescisório recolhido antecipadamente;
- documento ainda não emitido;
- compensação/suspensão;
- ausência de incidência;
- próxima chamada;
- impedimento de procuração/acesso;
- outro motivo documentado.

Justificativa registra operador, momento e contexto.

## 19. Retificação inteligente

**DECISÃO HISTÓRICA APROVADA**

Cliente/competência já fechado recebe nova evidência:

- idêntica → já conhecida;
- complementar sem impacto material → mantém fechamento;
- alteração material → candidata de retificação;
- histórico anterior preservado;
- comparação Vn → Vn+1;
- saídas automáticas bloqueadas enquanto a retificação material não for concluída.

## 20. Gate de saída

**DECISÃO HISTÓRICA APROVADA**

Impressão, entrega e geração de pacote não podem usar seleção manual para burlar Conferência.

Toda saída passa por um gate único baseado em estado real da competência/fonte/versão.

Seleção manual serve para escolher entre itens autorizados, não para autorizar item inválido.

## 21. Regra de não cobrança indevida

O sistema deve explicar por que esperava cada obrigação.

Se não consegue explicar a aplicabilidade com cadastro, movimentação, regra normativa ou evidência, deve pedir revisão — não fabricar pendência.
