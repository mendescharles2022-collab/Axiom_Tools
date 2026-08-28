# Auditoria canônica V8 — Etapa 29

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 29 aprofundou B14 — múltiplas evidências de FGTS e contexto rescisório.

## 2. Evidência disponível

O status V8F2 já registra que:

- Alex Douglas continua com cobrança de FGTS Digital mesmo com FGTS mensal Domínio igual a zero e contexto rescisório;
- regras de FGTS rescisório e composição de múltiplas evidências ainda não foram homologadas no fluxo real.

Os casos operacionais de agosto também exigem tratamento para múltiplas evidências, rescisão e garantias.

## 3. Contrato criado

Foi criado `docs/architecture/CONTRATO_COMPOSICAO_FGTS_V8.md`.

A regra canônica diferencia:

- FGTS mensal;
- rescisório;
- antecipado por rescisão;
- substitutivo;
- reemissão;
- complementar;
- evidência de unidade/matrícula distinta.

## 4. Regra central

`mais de um arquivo` não significa `mais de uma obrigação econômica`.

Antes da soma, o motor precisa classificar a relação entre as evidências.

Reemissões/substituições equivalentes não podem dobrar valor; componentes economicamente distintos podem compor.

## 5. Casos obrigatórios

A regressão deverá cobrir, no mínimo:

- Alex Douglas de Andrade;
- Comercial Faria;
- Empório Frios Itapaci;
- Predileta;
- Ribeiro e Nascimento Art Vidros;
- Jair Ferreira Camargo como controle de composição por matrícula sem rescisão.

## 6. Retificação

Novo componente econômico ou alteração material em cliente fechado cria retificação candidata.

Reemissão equivalente sem mudança material não deve criar retificação artificial.

## 7. Estado do bloqueador

B14 permanece `CONTRATO_OBRIGATORIO` e não homologado no runtime.

B17/B50 continuam necessários para deduplicação lógica antes da composição.

Nenhum item foi marcado como corrigido.

## 8. Próxima frente

Validar a semântica temporal de IRRF/competência de pagamento sem promover risco ainda não comprovado a defeito confirmado.
