# Auditoria canônica V8 — Etapa 53

Data: 31/08/2026  
Status: **auditoria em andamento / C01–C28 NÃO EXECUTADOS COMO REGRESSÃO FINAL / V8 NÃO HOMOLOGADA**

## 1. Escopo

Após concluir a revisão diagnóstica B01–B50 na Etapa 52, esta etapa liga formalmente os 28 casos reais de 08/2026 aos bloqueadores que precisam ser resolvidos para cada resultado ser confiável.

Foi criado:

`config/regression_case_blocker_map_v8_202608.json`

com dependências mínimas C01–C28 + controle P DA SILVA CARMO.

## 2. Regra de governança

Um caso real não pode receber `PASS` apenas porque a interface mostra o número/status esperado.

`PASS` exige que o mecanismo causal relevante também esteja coberto.

Exemplo Jair/C17:

não basta a tela exibir FGTS R$ 389,04.

A regressão precisa provar que:

- os dois Extratos continuam preservados;
- as matrículas permanecem distintas;
- federal R$ 511,43 foi consolidado uma única vez;
- FGTS R$ 129,68 e R$ 259,36 foram classificados como componentes aditivos;
- não houve soma por coincidência/ordem de arquivo;
- reemissão equivalente não duplicaria a obrigação.

Por isso C17 depende de B12/B13/B16/B17/B50.

## 3. Nenhum C01–C28 está apto a PASS final nesta fotografia

O estado formal continua:

- PASS: `0/28`;
- FAIL final executado: `0/28`;
- regressão integrada final: ainda não executada na árvore reconciliada.

Os patches recuperados permitem avaliar implementação parcial, mas não substituem execução do caso real/fixture equivalente.

## 4. Casos com correção parcial já encontrada

### FGTS zero — B19

A correção V8F2 beneficia diretamente, entre outros:

- C09 Denes;
- C15 Gold Pallace;
- C18 Larissa B Maia;
- C21 Marcos Augusto;
- C28 Wilmar.

Porém esses casos também dependem de deduções/afastamentos/identidade e, portanto, não podem ser promovidos apenas pela nova regra de FGTS zero.

### eConsignado — B26

A correção V8F2 que impede `CONFERIDO` sem fonte de recolhimento beneficia principalmente:

- C06 D A F Castro;
- C19 Lourenconi & Modesto.

Mas ainda faltam associação/contexto por contrato, fotografia/idempotência e divergência contextual completa.

### Saldo federal autoritativo — B30

A Conferência já consome `saldo_total_apuracao_dominio`, o que é base correta para:

- C09 Denes;
- C18 Larissa;
- C23 Ponto Kent;
- controle P DA SILVA CARMO.

O parser Domínio integral ainda precisa provar que o campo é extraído com a semântica correta.

## 5. Casos dominados por reprocessamento/descoberta

Dependem fortemente de B01/B15/B49 e não devem ser testados apenas por estado final da tela:

- C01 307 Looks;
- C05 Construtora & Empreendimentos Messias;
- C11 Eloim Transportes;
- C16 J Bernardes / Odonto Art;
- C26 S S Santos Empreendimentos.

Prova mínima inclui cadeia física/indexação, preservação da versão vigente, nova evidência e recomposição da Conferência.

## 6. Casos dominados por decisão/aplicabilidade por fonte

Dependem de B18 e regras específicas de obrigação:

- C03 Casa das Carnes/Lago Azul;
- C10 Elenice/MEI;
- C14 GL Auto Center;
- C20 Luriel/MEI;
- C22 Maria Virginia;
- C24 Predileta;
- C25 Ribeiro e Nascimento.

Enquanto a decisão manual continuar global por cliente, esses casos não possuem regressão confiável de isolamento entre DARF, FGTS e eConsignado.

## 7. Casos dominados por composição multi-documento

- C04 Comercial Faria;
- C12 Empório Frios;
- C17 Jair;
- C25 Ribeiro e Nascimento.

Dependem da separação entre:

- identidade física;
- identidade documental;
- identidade econômica;
- mensal/rescisório/antecipado/reemissão/unidade distinta.

A atual estratégia “último documento do tipo” impede homologação.

## 8. Casos dominados por identidade PF/CAEPF

- C08 Delfino Pereira Ribeiro;
- C17 Jair Ferreira Camargo;
- C21 Marcos Augusto Pimentel Daibert.

O cadastro suporta múltiplas inscrições, mas o matching operacional completo ainda precisa ser recuperado/reconciliado.

## 9. Casos dominados pelo ciclo/chamada

C27 T L depende obrigatoriamente de:

- B07 — universo operacional único;
- B08 — regressão específica da 2ª chamada;
- B40 — transição com compare-and-set/concorrência.

A prova não pode ser apenas “T L aparece na chamada 2”.

Deve sobreviver a:

- abertura de telas;
- sincronização da Conferência;
- processamento de outros clientes;
- restart;
- colisão de escrita;
- avanço explícito para a chamada 2.

## 10. Casos que exigem parser/contexto ainda não recuperado integralmente

Entre outros:

- C09/C23 — deduções previdenciárias;
- C14/C15/C21/C28 — afastamentos/faltas;
- C08/C17/C21 — identidade rural;
- controle P DA SILVA CARMO — Diretor ≠ empregado.

Esses casos não devem ser “corrigidos” na Conference para compensar parser errado. A origem precisa estar correta.

## 11. Validador C01–C28 atual

`validate_regression_results.py` já garante:

- exatamente 28 casos no registry;
- IDs/números válidos e únicos;
- hash canônico do registry;
- status limitado a PASS/FAIL/NOT_RUN/BLOCKED;
- PASS somente com alguma evidência;
- modo final somente com 28/28 PASS.

Essa infraestrutura é válida.

## 12. Lacuna adicional de evidência

O validador atual verifica que um `PASS` possui pelo menos uma string em `evidence`, mas não valida semanticamente se a evidência cobre os bloqueadores/mecanismos associados ao caso.

O novo mapa de dependências deve ser usado na próxima evolução do gate para impedir evidência genérica do tipo:

`"tela conferida manualmente"`

quando o caso exige, por exemplo, prova de:

- versão preservada;
- matrícula;
- composição;
- estado por fonte;
- transição concorrente;
- vínculo físico.

Isso não invalida o validador atual; define sua próxima camada.

## 13. Estado

O diagnóstico dos casos reais está agora vinculado formalmente ao diagnóstico B01–B50.

Nenhum C é promovido a PASS.

A V8 permanece **NÃO HOMOLOGADA / PACOTE FINAL NÃO AUTORIZADO**.

## 14. Próxima frente

1. fortalecer o gate C01–C28 com o mapa de dependências;
2. continuar corrigindo tooling B06/B42 que independe do runtime;
3. reconciliar a árvore operacional integral assim que os bytes do runtime canônico estiverem acessíveis;
4. executar correções e então gerar evidência real caso a caso.
