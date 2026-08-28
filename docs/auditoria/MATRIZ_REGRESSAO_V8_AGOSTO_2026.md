# Matriz de regressão V8 — competência 08/2026

Data: 28/08/2026
Status: **critério de auditoria / execução de regressão ainda pendente sobre a implementação canônica**

Esta matriz transforma os casos reais discutidos com o escritório em resultados objetivos de regressão. Nenhuma correção deve ser considerada concluída apenas por remover visualmente uma pendência.

## Casos 1 a 28

| # | Cliente | Mecanismo principal | Resultado esperado |
|---|---|---|---|
| 1 | 307 Looks Ltda | Reprocessamento / retificação | Arquivo novo ou alterado deve ser versionado, promovido somente após validação e provocar recomposição da Conferência. Estado antigo fica no histórico. |
| 2 | Alex Douglas de Andrade | Rescisão + reprocessamento | FGTS mensal do vínculo tratado na rescisão deve ficar `NAO_APLICAVEL`; DARF previdenciária continua exigível e documento adicionado depois precisa ser incorporado. |
| 3 | Casa das Carnes e Panificadora Lago Azul | Justificativa por fonte | DARF = `IMPEDIDA_EXTERNAMENTE` por procuração expirada. A decisão não pode resolver FGTS/eConsignado ou marcar o cliente inteiro como conferido. |
| 4 | Comercial Faria Ltda | Múltiplas evidências de FGTS | Compor FGTS mensal + recolhimento rescisório/antecipado economicamente distinto; não exigir uma única guia e não duplicar reemissões. |
| 5 | Construtora & Empreendimentos Messias | Descoberta/vínculo | GFD existente deve ser redescoberta, lida, identificada, vinculada e incorporada na Conferência; ocorrência deve apontar o estágio exato se falhar. |
| 6 | D A F Castro | eConsignado contextual | Retorno da API deve ser associado corretamente ao cliente/competência e comparado contrato a contrato com o Extrato; divergência falsa deve desaparecer. |
| 7 | D&L Alimentos | eConsignado residual | Sem vínculo ativo/remuneração/FGTS em agosto, retorno residual da API vira observação a confirmar, não bloqueio automático. |
| 8 | Delfino Pereira Ribeiro | Produtor rural PF / GFD | Descoberta e vínculo de GFD devem funcionar com CPF/CAEPF e perfil rural PF. Guia existente não pode permanecer como ausência genérica. |
| 9 | Denes Mariano de Castro | Saldo previdenciário zero | INSS menos salário-família/deduções = zero deve produzir DARF `NAO_APLICAVEL`, sem pendência por ausência de guia. |
| 10 | Elenice Batista Santos Silva | MEI / DAE | Perfil MEI exige DAE como referência. Não criar expectativa mensal de GFD autônoma; separar componentes federal e FGTS do DAE. |
| 11 | Eloim Transportes | Descoberta/vínculo de Extrato | Extrato Domínio presente deve chegar à Conferência pela cadeia descoberta → leitura → identidade → competência → persistência → composição. |
| 12 | Empório Frios Itapaci | Rescisão + eConsignado | Separar parcela mensal, garantias/rescisão e recolhimentos correlatos. Mudança material em cliente fechado cria retificação, nunca alteração silenciosa. |
| 13 | Empresa Funerária Itapax | Descoberta/vínculo GFD | Ausência sem causa operacional confirmada deve ser tratada como provável falha técnica de descoberta/leitura/vínculo até validação física. |
| 14 | GL Auto Center | Afastamento + eConsignado | Afastamento por acidente mantém FGTS aplicável. Pagamento direto comunicado explica ausência de desconto do consignado sem criar divergência. |
| 15 | Gold Pallace Hotel | Afastamento integral | Sem remuneração, pró-labore e bases: DARF e FGTS ficam `NAO_APLICAVEL`; cliente não pode ser classificado como incompleto por falta de guia. |
| 16 | J Bernardes / Odonto Art | Reprocessamento documental | DARF/FGTS adicionadas depois devem ser ingeridas e a Conferência recalculada; estado anterior não pode permanecer congelado. |
| 17 | Jair Ferreira Camargo | Multi-Extrato / rural | Extratos 449/450 preservados por matrícula. Federal R$ 511,43 conta uma vez. FGTS R$ 129,68 + R$ 259,36 = R$ 389,04. |
| 18 | Larissa B Maia | Sem empregados / pró-labore | FGTS zero é `NAO_APLICAVEL`; DARF previdenciária R$ 178,31 batida deve permitir conclusão sem expectativa artificial adicional. |
| 19 | Lourenconi & Modesto | Inconsistência entre fontes | Diferença de R$ 230,91 deve ficar `DIVERGENTE — requer confirmação`, após confronto por contrato/empregado/identificador; sistema não escolhe fonte vencedora sozinho. |
| 20 | Luriel Ferreira Malheiros | MEI / DAE | Mesma regra MEI: DAE é referência normal e GFD autônoma não é expectativa padrão. |
| 21 | Marcos Augusto Pimentel Daibert | Afastamento integral rural PF | Afastamento INSS + remuneração/bases zeradas = DARF/FGTS `NAO_APLICAVEL`, sem incompletude artificial. |
| 22 | Maria Virginia S Souto | Justificativa por fonte / saída | DARF = `IMPEDIDA_EXTERNAMENTE` por procuração revogada. Outras fontes permanecem independentes. Competências posteriores devem respeitar saída do ciclo. |
| 23 | Ponto Kent | Deduções previdenciárias | INSS R$ 893,45 - salário-família R$ 135,08 = DARF R$ 758,37; FGTS Domínio/GFD R$ 722,15. Ambos devem bater e concluir. |
| 24 | Predileta | Responsabilidade Fiscal + rescisão | DARF sob responsabilidade Fiscal não bloqueia fechamento do DP quando parametrizada, mas não libera FGTS/eConsignado. Rescisão exige análise contextual de garantias/consignado. |
| 25 | Ribeiro e Nascimento Art Vidros | eConsignado + rescisão | Separar parcela mensal, garantias usadas e recolhimento rescisório; não comparar totais cegamente. |
| 26 | S S Santos Empreendimentos | Evolução de evidência | Cliente pode evoluir de `sem dados` para `dados disponíveis`; novos relatórios/guias invalidam o estado operacional antigo e recompõem a Conferência. |
| 27 | T L Empreendimentos Agrícolas | Chamada mensal | Cliente de 2ª chamada fica fora do universo da 1ª e aparece como `Aguardando 2ª chamada`. Mudança deve ser persistida e auditável imediatamente. |
| 28 | Wilmar Ferreira Pires | Faltas integrais | Faltas em todos os dias + remuneração/base zerada = obrigações `NAO_APLICAVEL`, com explicação, e não pendência. |

## Controle adicional — P DA SILVA CARMO

Documento real disponível: `21537-Extrato Mensal.pdf`, competência 08/2026.

O Extrato mostra simultaneamente:

- uma linha individual com `Situação: Trabalhando`;
- `Vínculo: Diretor`;
- rubrica de pró-labore;
- `No. Empregados: 0`;
- `No. Contribuintes: 1`;
- base FGTS R$ 0,00;
- valor FGTS R$ 0,00;
- saldo federal a recolher R$ 220,00.

### Regressão esperada

O motor não pode inferir empregado apenas porque a linha individual contém `Situação: Trabalhando`.

Deve considerar a natureza do vínculo e os totais do relatório:

- contribuinte/diretor com pró-labore;
- zero empregados;
- FGTS `NAO_APLICAVEL`/valor esperado zero;
- obrigação federal esperada de R$ 220,00.

Este caso passa a ser controle explícito contra falsa expectativa de FGTS por interpretação superficial do campo `Situação`.

## Regras de aceite da matriz

1. Cada caso deve ter fixture/evidência reproduzível ou cenário de teste equivalente.
2. A regressão deve validar estado por fonte e estado agregado do cliente.
3. Reprocessamento deve preservar versão vigente até promoção do candidato.
4. Testes de composição precisam cobrir documento duplicado, reemissão e unidade/matrícula distinta.
5. `PROCESSADO` nunca deve ser usado como sinônimo de `CONFERIDO` ou `FECHADO`.
6. Ações de Impressão, Entregas e Saídas automáticas precisam passar pelo mesmo gate de backend.
7. Abrir a Conferência deve ser operação de leitura sem efeito colateral.
8. Nenhum caso pode ser considerado resolvido apenas por ocultar a ocorrência na interface.
9. A regressão completa deve rodar antes de qualquer pacote final da V8.
