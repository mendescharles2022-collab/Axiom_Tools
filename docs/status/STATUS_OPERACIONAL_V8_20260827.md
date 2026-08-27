# Status Operacional V8 — 27/08/2026

Status atual: **V5.6.14V8F2 NÃO HOMOLOGADA**  
Natureza: correção parcial com falhas funcionais críticas ainda abertas.  
Competência operacional em uso: **08/2026**.

## 1. Decisão operacional imediata

Enquanto as correções estruturais continuam, as pendências restantes da competência 08/2026 serão resolvidas manualmente para não impedir a rotina do escritório. Os documentos já conferidos podem ser impressos e entregues normalmente; as pendências serão tratadas caso a caso até a correção definitiva dos motores e da Conferência.

Esta contingência manual **não homologa a V8F2** e não deve ser interpretada como solução técnica das falhas abaixo.

## 2. Pontos efetivamente resolvidos

- Monitor de Execução passou a usar a competência operacional `08/2026` em vez de `Múltiplas`.
- Sessões tecnicamente concluídas passaram a exibir `100% · Processamento concluído`, separando progresso técnico de pendências da Conferência.
- Foi criada a ação `Reprocessar pendências e divergências — 08/2026`.
- O reprocessamento seletivo preserva clientes já resolvidos em vez de reprocessar indiscriminadamente toda a competência.
- Backend 5201 e Gateway 5200 foram validados no runtime real.

## 3. Falhas críticas ainda abertas

### 3.1 Identificação e vínculo de documentos

- `MMT Empreendimentos Ltda.pdf` continua como `Cliente não identificado`, 0% e sem competência operacional aplicada corretamente após reprocessamento.
- `Alex Douglas de Andrade.pdf` continua como `Cliente não identificado`, 0% e sem competência operacional aplicada corretamente após reprocessamento.
- Extratos Domínio como `449-Extrato Mensal.pdf` e `450-Extrato Mensal.pdf` chegam a reconhecer tipo e competência `08/2026`, mas permanecem sem cliente identificado.
- O fallback por nome do arquivo e o reforço de identidade do e-CAC ainda não estão produzindo o efeito esperado no fluxo real de reprocessamento.

### 3.2 Reprocessamento incompleto da cadeia documental

O botão de reprocessamento executa e informa quantidades de documentos/clientes processados, mas ainda não garante a cadeia completa:

`descoberta nas conexões → leitura/OCR → identificação → competência → motor especialista → persistência → cruzamento → atualização da Conferência`.

Há casos em que a Conferência continua exibindo ausência/divergência mesmo depois do documento existir e do reprocessamento ter sido executado.

### 3.3 DARF / e-CAC

- Alex Douglas continua com `DARF AUSENTE INESPERADO` na Conferência apesar da existência da DARF real da competência 08/2026.
- A associação entre documentos órfãos do e-CAC e o cliente/competência ainda não está atualizando a Conferência de forma confiável.
- A ausência de DARF por motivo administrativo, como falta de procuração ativa, ainda precisa de resolução mensal auditável na própria ocorrência, sem obrigar envio inexistente.

### 3.4 FGTS Digital

- Persistem empresas com FGTS Domínio preenchido e FGTS Digital ausente após reprocessamento, sem comprovação de que todas as guias existentes nas conexões foram redescobertas e vinculadas.
- O sistema ainda pode exigir FGTS Digital quando `FGTS Domínio = R$ 0,00`.
- Caso Alex Douglas: continua sendo cobrado FGTS Digital mesmo com valor mensal Domínio igual a zero e contexto de rescisão já discutido.
- Regras de FGTS rescisório e composição de múltiplas evidências ainda não estão homologadas no fluxo real.

### 3.5 MEI / DAE

- A regra aprovada de que cliente cadastrado como **MEI não recebe cobrança mensal genérica de FGTS Digital autônoma** ainda não está resolvida.
- Caso real: **Elenice Batista Santos Silva 21582084149**, cadastrada como MEI, continua sendo tratada pela lógica genérica de FGTS/DARF na Conferência.
- O perfil MEI ainda não está prevalecendo de forma confiável sobre heurísticas genéricas de incidência.

### 3.6 eConsignado

- Persistem falsos estados `CONFERIDO` com fontes ausentes ou valores incompatíveis.
- Caso real: **D A F Castro Ltda** apresenta MTE/Dataprev, Domínio, Comunicado e FGTS Digital incompletos/incompatíveis e mesmo assim o bloco pode aparecer como `CONFERIDO`.
- A regra correta continua sendo: resultado positivo no MTE/Dataprev exige cruzamento com as demais fontes aplicáveis; ausência de fonte necessária não pode resultar em `CONFERIDO`.

### 3.7 Chamadas do fechamento

- Já foi identificado cliente enviado para 2ª chamada que continuou sendo cobrado na Conferência da 1ª chamada.
- Essa falha permanece aberta até nova validação funcional comprovando exclusão imediata da chamada atual.

### 3.8 Filtro da aba Pendências

- A aba ainda não abre de forma operacionalmente clara já filtrada pela competência ativa.
- O usuário ainda precisa lidar com PROC/chaves técnicas para isolar o ciclo corrente.
- A regra desejada permanece: competência ativa como filtro principal; PROC limitada automaticamente à competência; `Competência não identificada` como exceção visível separada.

### 3.9 Impressão de relatórios

- Foi identificado relatório de pendências ultrapassando a largura imprimível do papel A4 em modo retrato.
- A correção deve garantir A4 retrato, largura máxima da área imprimível, quebra controlada de texto, tabela compacta e cabeçalhos repetidos.
- O ajuste criado ainda precisa de homologação visual em preview/impressão real.

## 4. Casos de regressão obrigatórios

As próximas correções devem ser validadas, no mínimo, contra estes casos reais:

1. **MMT Empreendimentos Ltda** — identificação do DARF, cliente e competência.
2. **Alex Douglas de Andrade** — DARF real deve alimentar Conferência; FGTS mensal zero não pode gerar ausência artificial; contexto rescisório deve ser respeitado.
3. **449/450 Extrato Mensal** — tipo e competência já reconhecidos; falta resolver vínculo de cliente.
4. **Elenice Batista Santos Silva 21582084149** — MEI deve usar regra específica/DAE e não cobrança genérica de GFD.
5. **D A F Castro Ltda** — eConsignado não pode ficar conferido com fontes ausentes/incompatíveis.
6. **Casa das Carnes e Panificadora Lago Azul Ltda** — ausência de DARF por falta de procuração deve ser justificável mensalmente e auditável.
7. **Cliente em 2ª chamada** — deve desaparecer das expectativas/divergências da 1ª chamada.
8. **FGTS rescisório** — múltiplas guias/evidências devem compor o valor da competência sem falsa divergência.

## 5. Critério para a próxima homologação

A V8 só poderá avançar para homologação quando o reprocessamento provar, no runtime real, que consegue percorrer a cadeia completa e atualizar automaticamente a Conferência, sem correção manual de vínculo para casos que os documentos já permitem identificar.

A validação deve comprovar:

- identificação de cliente e competência;
- leitura nativa/OCR fallback quando realmente necessário;
- uso correto do motor especialista;
- descoberta de documentos novos/alterados nas conexões;
- recomposição dos cruzamentos;
- atualização imediata da Conferência;
- respeito a MEI/DAE, chamadas, FGTS zero/rescisório e eConsignado;
- ausência de falsos `CONFERIDO` e falsas pendências;
- impressão A4 retrato sem corte.

Validação de instalador, backend ou gateway sozinha **não constitui homologação funcional**.

## 6. Avaliação da V8F2

A V8F2 trouxe melhorias reais de infraestrutura e interface, porém aproximadamente metade dos problemas operacionais relevantes ainda permanece aberta. Portanto, o estado canônico é:

> **V5.6.14V8F2 — NÃO HOMOLOGADA; implementação parcial, com falhas críticas em motores, vínculo, reprocessamento e Conferência.**
