# Auditoria canônica V8 — continuação de 28/08/2026

Base auditada: ZIP integral entregue em 27/08/2026, tratado como base canônica operacional.

Status: **auditoria em andamento / sem pacote final gerado**.

## Achados estruturais confirmados nesta etapa

### 1. Reprocessamento destrutivo

A função `reprocessar_arquivo()` em `modules/processing/central.py` fotografa o estado anterior e, em seguida, exclui os registros de `processamento_item_pessoa` e `processamento_arquivo` antes de saber se a nova leitura ficará melhor.

Isso permite regressão de identidade, competência, tipo, status e completude.

Evidência real no banco: os Extratos `449-Extrato Mensal.pdf` e `450-Extrato Mensal.pdf` de Jair Ferreira Camargo possuíam snapshots anteriores com `cliente_id=826`, competência `08/2026`, status `PROCESSADO` e confiança/completude de 100%. Após reprocessamentos de 27/08, os registros vigentes ficaram em `REVISAO`, 90%, sem cliente vinculado.

Correção obrigatória: reprocessamento deve ser candidato/versionado. Resultado pior não pode substituir uma versão válida.

### 2. Conferência escolhe somente um Extrato Mensal

`conference.py` usa `_ultimo_tipo(emp, "EXTRATO_MENSAL")`. Logo, mesmo que dois Extratos válidos sejam corretamente associados ao mesmo cliente/competência, somente um deles é considerado na conferência.

Isso é incompatível com clientes com múltiplas matrículas/inscrições.

#### Regra confirmada para múltiplas matrículas rurais

Caso Jair Ferreira Camargo:

- Extrato 449: FGTS R$ 129,68; saldo federal consolidado R$ 511,43.
- Extrato 450: FGTS R$ 259,36; saldo federal consolidado R$ 511,43.
- GFD consolidada: R$ 389,04.

Regra aprovada:

- **DARF / tributos federais:** não somar os dois saldos de R$ 511,43; é a mesma apuração consolidada repetida em matriz/filial.
- **FGTS:** somar os componentes das matrículas: R$ 129,68 + R$ 259,36 = R$ 389,04.
- Preservar a origem por matrícula no detalhamento.

O motor deve distinguir duplicidade/repetição federal de componente aditivo de FGTS.

### 3. Há outro grupo real com múltiplos Extratos que não pode ser tratado igual ao Jair

Leosmar Teodoro de Sousa possui dois Extratos vigentes em 08/2026 com os mesmos valores centrais: saldo federal R$ 224,73, INSS R$ 224,73 e FGTS R$ 0,00.

Isso demonstra que a regra não pode ser `havendo dois Extratos, somar FGTS` indiscriminadamente. É necessário primeiro classificar os documentos como:

- duplicidade/reemissão equivalente; ou
- unidades/matrículas distintas com composição aditiva.

### 4. Conferência possui efeito colateral de fechamento

`conferencia_competencia()` chama `sincronizar_resultados_conferencia()` durante a própria montagem da tela.

Assim, uma operação de leitura/consulta pode alterar `fechamento_mensal_cliente`, criar versão de fechamento e histórico.

Regra arquitetural: consultar a Central de Conferência deve ser somente leitura. Fechamento automático deve ocorrer como consequência explícita de evento concluído de processamento/resolução, não de abrir a tela.

### 5. Escopo CICLO inclui clientes já FECHADOS

`clientes_conferencia_ids()` inclui:

- PRONTA da chamada atual;
- FECHADA;
- RETIFICACAO.

Isso mistura trabalho vivo com histórico fechado e permite que clientes fechados reapareçam na conferência comum. Fechados devem permanecer no snapshot/histórico; nova evidência material deve criar retificação.

### 6. Centro de Impressão não possui bloqueio canônico de conferência no servidor

`printing_views.py` inicia `conferencia_filtro` vazio. Sem filtro, `_clientes_conferencia()` retorna `None`, portanto a listagem e a geração de lote não ficam obrigatoriamente restritas a clientes conferidos/fechados.

A seleção manual de IDs em `printing.service` também não valida fechamento/conferência por si só.

Regra aprovada: **o servidor deve liberar impressão operacional somente para documentos de clientes conferidos/justificados e fechados**, independentemente do filtro visual escolhido.

A contingência manual realizada em 27/08 permanece registrada como externa ao Tools.

### 7. Saídas automáticas usam PROCESSADO como sinônimo de validado

`processing/output.py` interpreta `somente_validados` como `row.status == 'PROCESSADO'`.

O worker chama `gerar_saidas_documento()` imediatamente após processar/arquivar um documento.

Isso viola a arquitetura V8: `PROCESSADO` significa apenas sucesso técnico do motor. Não significa conferido, fechado ou autorizado para saída.

Correção obrigatória: existindo Fechamento Mensal para a competência, saída final deve depender de cliente FECHADO e ausência de retificação pendente.

### 8. Central de Entregas protege a listagem, mas não todas as ações POST

A tela usa por padrão o escopo de clientes fechados quando há controle mensal. Porém rotas individuais e selecionadas chamam diretamente `gerar_cliente()` sem revalidar no servidor se o cliente pertence ao conjunto fechado.

Regra: ações individuais, selecionadas e em lote devem usar o mesmo gate canônico de fechamento.

### 9. Duplicidades de lógica permanecem no código

Foram encontrados helpers/regras repetidos entre `conference.py` e `operations.py`, incluindo `_money`, `_cmp`, `_ultimo_tipo` e uma implementação antiga de `_check_darf_folha` que já não é usada pelo fluxo canônico.

Além disso, `central.py` (~93 KB / mais de 2 mil linhas) e `documents_views.py` (~73 KB / mais de 1,7 mil linhas) concentram responsabilidades demais.

Simplificação aprovada: remover regras mortas/duplicadas e separar responsabilidades sem alterar rotas/funcionalidades aprovadas.

### 10. Suíte atual apresenta falhas reais e testes obsoletos/ambientais

A execução da suíte do ZIP canônico encontrou sete falhas visíveis nesta rodada.

Falha funcional real confirmada:

- inativação de cliente: `classificacao_inativacao` pode chegar como string e o repositório assume sempre Enum (`.value`).

Outras falhas são de ambiente Windows/biblioteca nativa ou expectativas antigas de interface/máscara e devem ser classificadas antes de alterar produção.

## Estado do fechamento de agosto no banco canônico

O perfil mensal possui 339 clientes participantes do ciclo. Entre eles, no snapshot auditado:

- 283 FECHADA com movimento;
- 13 FECHADA sem movimento;
- 30 PRONTA com movimento;
- 1 PRONTA sem movimento;
- 7 RETIFICACAO sem movimento;
- 5 ADIADA para 2ª chamada.

T L Empreendimentos Agrícolas aparece no banco canônico como `PRONTA`, chamada 1, apesar da regra operacional informada de que deveria estar na 2ª chamada. Não há persistência válida dessa decisão no snapshot auditado; a correção deve atingir o fluxo de gravação/auditoria da chamada, não apenas esconder o cliente por filtro.

## Critérios adicionais de regressão

Antes do pacote final:

1. reprocessar não pode piorar identidade/completude;
2. 449/450 devem recuperar Jair com histórico seguro;
3. DARF de Jair deve ser considerada uma única apuração federal consolidada;
4. FGTS de Jair deve somar as duas matrículas e bater R$ 389,04;
5. Leosmar não pode ter duplicidade de Extrato somada indevidamente;
6. abrir Conferência não pode escrever no fechamento;
7. cliente FECHADO não retorna ao CICLO sem retificação;
8. Impressão/Entregas/Saídas devem bloquear no servidor qualquer cliente não autorizado;
9. PROCESSADO não pode significar CONFERIDO;
10. mudança para próxima chamada deve ser persistida e auditável imediatamente.
