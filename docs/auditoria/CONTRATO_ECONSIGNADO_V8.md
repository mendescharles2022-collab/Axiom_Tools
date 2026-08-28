# Contrato canônico V8 — eConsignado

Data: 28/08/2026
Status: **contrato de auditoria / implementação ainda não homologada**

## 1. Evidência da base canônica

Na competência 08/2026, o job eConsignado auditado consultou 840 empregadores, com 19 `COM_CONSIGNADO`, 684 `SEM_CONSIGNADO`, 137 `SEM_PROCURACAO`, zero erros e 58 contratos.

O Fechamento Mensal da mesma competência possui 339 clientes participantes do ciclo.

A função `clientes_consulta()` da base auditada deriva o universo do cadastro histórico/situação e não diretamente da composição mensal/chamada.

Também foi confirmado que o processamento principal e a consulta eConsignado são fluxos separados: `/processamento/processar` enfileira conexões, enquanto `/processamento/consignados/sincronizar` cria e lança job próprio.

Portanto existem duas falhas estruturais confirmadas:

1. eConsignado não é etapa obrigatória do orquestrador mensal;
2. o universo consultado é maior que o universo operacional da competência/chamada.

## 2. Posição no fluxo

O eConsignado é a Etapa 0 do processamento mensal:

`Competência aberta -> eConsignado -> Domínio -> eSocial -> e-CAC/DARF -> FGTS Digital -> Conferência`

A fotografia MTE/Dataprev deve estar disponível antes dos documentos para servir de referência no cruzamento posterior.

## 3. Universo canônico do job

O job deve nascer da composição mensal vigente do Fechamento Mensal.

Entram apenas empregadores elegíveis para a chamada operacional corrente, respeitando:

- competência ativa;
- chamada liberada;
- movimento mensal aplicável;
- perfil cadastral;
- deduplicação matriz/filial quando a consulta oficial for por raiz/empregador;
- exclusão de chamada futura;
- exclusão de `Sem movimento` quando a regra mensal determinar não aplicabilidade;
- exclusão de clientes fora do ciclo.

O cadastro mestre serve para identidade e parametrização, não para definir sozinho o universo mensal.

## 4. Status de consulta não é status de Conferência

A consulta oficial deve possuir resultado próprio, separado da conclusão da Conferência.

Resultados de consulta mínimos:

- `COM_CONSIGNADO`;
- `SEM_CONSIGNADO`;
- `SEM_PROCURACAO`;
- `ERRO_TECNICO`.

Semântica:

- `SEM_CONSIGNADO` = resultado válido da fonte oficial;
- `SEM_PROCURACAO` = impedimento/informação auditável, não erro técnico do motor;
- `ERRO_TECNICO` = falha de conexão/API/execução;
- resultado anterior válido nunca deve ser apagado por uma falha técnica posterior.

Nenhum desses estados equivale sozinho a `CONFERIDA`.

## 5. Estado da obrigação eConsignado

A Conferência deriva o estado da obrigação somente após contextualizar a fotografia oficial com as demais fontes aplicáveis.

Estados de negócio possíveis seguem o contrato por fonte da V8, como:

- `CONFERIDA`;
- `DIVERGENTE`;
- `JUSTIFICADA`;
- `NAO_APLICAVEL`;
- `IMPEDIDA_EXTERNAMENTE`;
- `PENDENTE`;
- `RETIFICACAO`.

## 6. Cruzamento contextual obrigatório

Resultado positivo no MTE/Dataprev precisa ser confrontado com, conforme aplicabilidade:

- vínculo ativo;
- data de admissão/desligamento;
- remuneração na competência;
- Extrato Domínio;
- eSocial;
- comunicado de pagamento direto;
- afastamento;
- rescisão;
- garantias do consignado;
- FGTS mensal/rescisório quando relevante;
- identificador do contrato;
- duplicidades/repetições do retorno oficial.

## 7. Casos reais obrigatórios

### D A F Castro

Falha confirmada na V8F2: bloco pode aparecer `CONFERIDO` com MTE/Dataprev, Domínio, Comunicado e FGTS Digital incompletos/incompatíveis.

Regressão: fonte necessária ausente ou incompatível impede `CONFERIDA`.

### D&L Alimentos

Sem vínculo ativo/remuneração/FGTS em agosto, retorno residual deve virar observação a confirmar e não bloqueio automático.

### GL Auto Center

Afastamento por acidente mantém FGTS aplicável. Comunicado de pagamento direto pode justificar ausência de desconto normal do consignado.

### Empório Frios Itapaci / Predileta / Ribeiro e Nascimento Art Vidros

Com rescisão, separar parcela mensal, garantias e efeitos rescisórios antes de comparar totais.

### Lourenconi & Modesto

Diferença não explicada entre fontes deve permanecer `DIVERGENTE — requer confirmação`; o sistema não escolhe automaticamente qual fonte está errada.

## 8. Idempotência e fotografia

Cada job deve preservar:

- competência;
- chamada;
- universo consultado;
- horário;
- identificador/versão da consulta quando disponível;
- resultado por empregador;
- contratos retornados;
- erros técnicos;
- vínculo com o ciclo que o originou.

Reexecução deve criar nova fotografia/versionamento sem destruir resultado anterior válido.

## 9. Regressões mínimas

1. job da 1ª chamada não consulta cliente adiado para 2ª;
2. cliente `Sem movimento` não entra quando mensalmente não aplicável;
3. `SEM_CONSIGNADO` não vira erro;
4. `SEM_PROCURACAO` não vira falha técnica;
5. erro de API não apaga fotografia válida anterior;
6. `COM_CONSIGNADO` não gera `CONFERIDA` automaticamente;
7. D A F Castro não fica conferida com fontes incompatíveis/ausentes;
8. retorno residual D&L não bloqueia sozinho;
9. rescisão separa parcela mensal de garantias;
10. job nasce do mesmo comando/orquestrador da competência.

## 10. Critério de homologação

O eConsignado só será homologado quando, no runtime real, a execução mensal provar que:

- usa o universo correto da competência/chamada;
- roda como Etapa 0 do fluxo;
- preserva fotografias anteriores;
- diferencia resultado de consulta de conclusão de negócio;
- não produz falsos `CONFERIDO`;
- alimenta a Conferência por fonte, de forma contextual e auditável.
