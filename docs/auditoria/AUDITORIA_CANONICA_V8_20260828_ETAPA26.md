# Auditoria canônica V8 — Etapa 26

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 26 revisa o eConsignado contra o contrato canônico já registrado em `docs/auditoria/CONTRATO_ECONSIGNADO_V8.md`.

Nenhuma nova arquitetura paralela foi criada.

## 2. Falhas de implementação já comprovadas

### 2.1 Universo incorreto

Na competência 08/2026, o job auditado consultou 840 empregadores, enquanto o Fechamento Mensal possuía 339 participantes no ciclo.

A base auditada mostra que `clientes_consulta()` deriva o universo do cadastro histórico/situação e não diretamente da composição mensal/chamada.

Resultado: o eConsignado consulta universo maior que o operacional.

### 2.2 Fluxo separado do orquestrador

O processamento principal e a sincronização do eConsignado possuem fluxos/rotas de job separados.

Isso permite:

- universos diferentes;
- reinício fora de sincronismo;
- fotografia de eConsignado não alinhada ao mesmo ciclo que originou Domínio/eSocial/e-CAC/FGTS;
- divergência de chamada.

### 2.3 Falso `CONFERIDO`

O status operacional V8F2 registra o caso D A F Castro: fontes MTE/Dataprev, Domínio, Comunicado e FGTS Digital incompletas/incompatíveis e, ainda assim, o bloco pode aparecer como `CONFERIDO`.

Isso confirma mistura entre resultado da consulta externa e conclusão da obrigação.

## 3. Separação obrigatória de camadas

A implementação precisa possuir três níveis independentes:

1. **job/consulta externa** — execução técnica;
2. **fotografia eConsignado** — retorno oficial versionado por competência/chamada/empregador;
3. **obrigação na Conferência** — conclusão contextual após cruzamento com demais evidências.

Nenhum resultado do nível 1 ou 2 pode promover diretamente a obrigação para `CONFERIDA`.

## 4. Universo do job

O universo deve ser congelado quando o job nasce e derivado do serviço canônico do Fechamento Mensal.

Precisa preservar:

- competência;
- chamada;
- cliente/empregador;
- motivo de inclusão;
- revisão da composição mensal;
- horário de criação;
- correlation_id.

Restart não pode reconstruir o universo a partir da carteira histórica.

## 5. Fotografia externa

Cada execução deve preservar fotografia própria, sem destruir resultado anterior válido.

Falha posterior de API não substitui fotografia válida por ausência.

A fotografia deve distinguir:

- `COM_CONSIGNADO`;
- `SEM_CONSIGNADO`;
- `SEM_PROCURACAO`;
- `ERRO_TECNICO`.

## 6. Cruzamento da obrigação

A obrigação eConsignado só pode ficar `CONFERIDA` quando o contexto aplicável estiver coerente.

Confrontar, quando pertinente:

- vínculo ativo/desligamento;
- remuneração;
- afastamento;
- Extrato Domínio;
- eSocial;
- comunicado de pagamento direto;
- rescisão;
- garantias;
- FGTS mensal/rescisório;
- identificador do contrato;
- repetição/duplicidade no retorno.

## 7. Casos mínimos da regressão

- D A F Castro — fonte positiva não conclui com evidências ausentes/incompatíveis;
- D&L Alimentos — retorno residual sem vínculo/remuneração compatível não bloqueia sozinho;
- GL Auto Center — afastamento e pagamento direto tratados contextualmente;
- Empório Frios Itapaci — separar parcela mensal de garantias/rescisão;
- Predileta — mesma separação com responsabilidade de outras fontes independente;
- Ribeiro e Nascimento Art Vidros — consignado/rescisão sem comparação cega de totais;
- Lourenconi & Modesto — diferença não explicada permanece divergente para confirmação.

## 8. Regressão de chamada

Cenário obrigatório:

1. competência em chamada 1;
2. cliente adiado para chamada 2;
3. criar job eConsignado;
4. provar que o cliente não está no universo do job;
5. reiniciar worker;
6. provar que continua fora;
7. avançar chamada global para 2;
8. novo job passa a incluí-lo quando aplicável.

## 9. Critério de homologação

O eConsignado só sai de bloqueador quando no runtime reconciliado ficar provado que:

- nasce do mesmo ciclo mensal;
- usa exatamente o universo da competência/chamada;
- preserva fotografia versionada;
- retry/restart são idempotentes;
- status de consulta não é status de Conferência;
- D A F Castro e demais casos reais passam;
- nenhuma chamada futura é consultada antecipadamente.

## 10. Estado final da etapa

B24, B25 e B26 permanecem `CONFIRMADO_RUNTIME` e não corrigidos.

B27 e B28 permanecem contratos obrigatórios ainda sem homologação no runtime.
