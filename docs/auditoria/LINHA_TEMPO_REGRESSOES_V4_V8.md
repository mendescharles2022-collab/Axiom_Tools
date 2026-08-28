# Linha do tempo de regressões — V4 → V8

Data: 28/08/2026
Status: **apoio vinculante à auditoria e à correção V8**

## 1. Objetivo

Separar corretamente:

- garantia antiga já homologada que regrediu;
- comportamento antigo legitimamente superado pela V8;
- defeito novo introduzido/descoberto na V8;
- risco ainda não comprovado.

Isso evita tanto reintroduzir regra antiga superada quanto remover proteção que o produto já possuía.

## 2. V4 — retificação candidata/versionada

### Garantia existente

A V5.6.14V4 já implementava:

- snapshot do fechamento por cliente + competência;
- mudança material como candidata `Vn -> Vn+1`;
- versão anterior preservada;
- repetição idêntica ignorada como retificação;
- saída automática bloqueada durante retificação;
- `integrity_check` e validação em cópia do banco.

### V8 — regressão confirmada

O reprocessamento documental comum da base V8 auditada apaga registros vigentes antes de saber se a nova leitura será melhor.

Caso real: Extratos 449/450 de Jair Ferreira Camargo perderam vínculo/qualidade após reprocessamento.

### Classificação

`REGRESSAO DE GARANTIA JA EXISTENTE — CRITICA`

### Regra de correção

Estender ao reprocessamento documental o mesmo princípio candidato/versionado já comprovado na retificação V4.

## 3. V6 — Fechamento orientado por competência

### Garantias existentes

A V6 introduziu:

- competência mensal explícita;
- composição com clientes ativos;
- chamadas;
- movimento mensal separado do cadastro permanente;
- backup do banco;
- migração idempotente;
- rollback integral.

### V8

A V8 mantém o conceito de competência como origem do ciclo, mas redistribui os papéis entre Fechamento, Processamento e Conferência.

### Classificação

`GARANTIA PRESERVADA / ARQUITETURA EVOLUIDA`

## 4. V7 — chamada futura fora do ciclo corrente

### Garantia homologada

A V7 determinou que empresa em próxima chamada não fosse cobrada pela conferência do ciclo atual.

Na amostra de homologação 05/2026, empresas adiadas foram excluídas corretamente.

### V8 — regressão confirmada

T L Empreendimentos Agrícolas deveria estar na 2ª chamada, porém snapshot V8 auditado a manteve `PRONTA`, chamada 1.

### Classificação

`REGRESSAO DE GARANTIA JA EXISTENTE — ALTA`

### Correção

Transição de chamada precisa ser persistida imediatamente, auditável e consumida por todos os módulos por uma fachada canônica do domínio Closing.

## 5. V7 — saída vinculada a FECHADA

### Garantia existente

V7 registra que entregas e impressão continuam liberadas a partir do estado `FECHADA`.

V4 já bloqueava saída automática durante retificação.

### V8 — regressões confirmadas

- `processing/output.py` usa `PROCESSADO` como equivalente prático de validado;
- worker pode gerar saída imediatamente após processamento técnico;
- Centro de Impressão não aplica gate canônico obrigatório no servidor em todos os caminhos;
- Central de Entregas possui ações POST que podem chamar geração sem repetir o gate completo.

### Classificação

`REGRESSAO DE GARANTIA JA EXISTENTE — CRITICA`

### Correção

Um único gate de backend deve exigir `FECHADA` e ausência de retificação material pendente.

## 6. V7 — decisão manual global

### Regra antiga

A decisão global `Conferido/Justificado` podia concluir o ciclo do cliente.

### V8 — regra superada

Os 28 casos reais demonstraram que a decisão precisa ser por fonte/obrigação.

Exemplo: DARF impedida externamente não resolve FGTS; DARF do Fiscal não resolve eConsignado.

### Classificação

`COMPORTAMENTO LEGADO LEGITIMAMENTE SUPERADO`

### Consequência nos testes

Teste que espera decisão global fechar o cliente inteiro deve ser substituído por testes por obrigação.

Não classificar sua remoção como regressão.

## 7. V7 — PRONTA apresentada como Em conferência

### Regra antiga

V7 mapeava visualmente `PRONTA` para `Em conferência`.

### V8 — regra superada

Cliente só deve aparecer `Em conferência` depois de evidência documental processada suficiente para alcançar a mesa.

Antes disso:

- aguardando processamento;
- em processamento;
- ou chamada futura/sem movimento conforme o caso.

### Classificação

`COMPORTAMENTO LEGADO LEGITIMAMENTE SUPERADO`

## 8. V7 — fechadas no escopo padrão da Conferência

### Regra antiga

V7 usava ciclo atual exibindo liberadas + fechadas e excluindo adiadas.

### V8 — regra superada

A mesa normal passa a representar trabalho vivo.

Fechadas ficam em histórico/snapshot; mudança material entra em retificação própria.

### Classificação

`COMPORTAMENTO LEGADO LEGITIMAMENTE SUPERADO`

## 9. V3 — seleção excepcional ampla em Impressão/Entregas

### Regra antiga

A V3 permitia opções excepcionais como `Todos os eletrônicos` e, em certos modos de impressão, seleção explícita de qualquer cliente.

### Evolução V8

Com o Fechamento Mensal como controle canônico, seleção manual não pode furar o gate de autorização de saída.

A possibilidade de escolher documentos/clientes permanece, mas somente dentro do universo autorizado.

### Classificação

`REGRA PERMISSIVA ANTIGA RESTRINGIDA POR NOVO CONTROLE CANONICO`

## 10. V4 auditoria operacional — camadas desconectadas

### Histórico

A auditoria operacional anterior encontrou falhas causadas por camadas parcialmente desconectadas:

- schema existia mas não era inicializado;
- view tentava persistir campos não sustentados pelo repositório;
- providers existiam mas não eram registrados no serviço.

### V8 — padrão estrutural semelhante

A auditoria atual encontrou:

- `main` divergente da árvore operacional;
- regra de universo replicada em várias camadas;
- decisões/contratos evoluídos sem todos os consumidores acompanharem;
- Processamento, Conferência, Impressão e Entregas usando critérios parcialmente diferentes.

### Classificação

`RISCO ARQUITETURAL RECORRENTE — ALTO`

### Correção

Testes de integração precisam atravessar schema → repository → service → view → template/job/saída e não validar cada camada isoladamente.

## 11. Novo defeito V8 — reprocessamento candidato ausente

Embora derive de garantia V4, o defeito técnico específico em `reprocessar_arquivo()` é novo no fluxo documental.

Classificação complementar:

`DEFEITO NOVO QUE VIOLA GARANTIA ANTIGA`.

## 12. Novo defeito V8 — múltiplos Extratos

`conference.py` usa somente o último `EXTRATO_MENSAL`, incompatível com múltiplas matrículas/unidades.

Não há evidência de garantia equivalente anterior no produto.

### Classificação

`DEFEITO FUNCIONAL NOVO — ALTO`

## 13. Novo defeito V8 — eConsignado fora do orquestrador/universo excessivo

Job 08/2026 consultou 840 empregadores apesar de composição mensal auditada de 339 participantes.

Além disso, a consulta estava separada do comando principal de processamento.

### Classificação

`DEFEITO DE ORQUESTRACAO/ESCOPO — ALTO`

## 14. Novo defeito V8 — Conferência GET com efeito colateral

Abrir a Conferência chama sincronização capaz de alterar fechamento/histórico.

Não há justificativa arquitetural para GET de consulta produzir fechamento.

### Classificação

`DEFEITO TRANSACIONAL NOVO — CRITICO`

## 15. Regras de severidade

### Crítica

Pode:

- perder versão válida;
- liberar saída indevida;
- alterar fechamento por consulta;
- corromper histórico/estado;
- permitir resultado final incorreto sem alerta.

### Alta

Pode:

- incluir/excluir cliente no ciclo errado;
- produzir falsa divergência/conferência;
- errar composição de obrigação;
- consultar universo governamental incorreto em escala.

### Média

Impacta operação/UX/relatório, sem alterar imediatamente o resultado financeiro ou fechamento.

## 16. Regra para a correção V8

Prioridade de implementação:

1. regressões críticas de garantias antigas;
2. defeitos críticos novos;
3. regressões altas;
4. defeitos funcionais altos;
5. migração dos comportamentos legados superados;
6. desempenho/UX/relatórios;
7. refinamentos não bloqueantes.

Nenhuma correção deve reintroduzir comportamento V7 que a arquitetura V8 tenha explicitamente substituído.
