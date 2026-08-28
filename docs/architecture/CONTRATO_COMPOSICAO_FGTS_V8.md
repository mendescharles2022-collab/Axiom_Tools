# Contrato V8 — Composição de FGTS mensal, rescisório, antecipado e reemissões

Data: 28/08/2026
Status: **contrato obrigatório / V8 não homologada**

## 1. Problema

A Conferência não pode presumir uma única guia de FGTS por `cliente + competência` nem somar automaticamente todas as guias encontradas.

No fluxo real podem existir:

- FGTS mensal;
- FGTS rescisório;
- recolhimento antecipado em razão da rescisão;
- reemissão/substituição da mesma obrigação;
- guias por matrículas/inscrições distintas;
- evidências complementares do mesmo fato econômico.

Portanto `quantidade de arquivos` não define `quantidade de obrigações`.

## 2. Unidade de composição

Cada evidência de FGTS precisa ser classificada antes da soma por, no mínimo:

- cliente/grupo empregador;
- competência;
- CPF/CNPJ/CAEPF e matrícula/inscrição quando disponível;
- natureza do recolhimento;
- trabalhador ou conjunto de trabalhadores quando relevante;
- identificador/número da guia quando disponível;
- data de emissão/vencimento/pagamento;
- valores/componentes;
- hash físico;
- fingerprint documental/econômico;
- relação com outra evidência.

## 3. Naturezas mínimas

A estrutura deve conseguir representar, conforme evidência disponível:

- `MENSAL`;
- `RESCISORIO`;
- `ANTECIPADO_RESCISAO`;
- `SUBSTITUTIVO`;
- `REEMISSAO`;
- `COMPLEMENTAR`;
- `INDETERMINADO`.

A nomenclatura interna pode variar, mas a semântica não pode ser perdida.

## 4. Relações entre documentos

Antes de compor valores, classificar a relação entre evidências, reutilizando o contrato de deduplicação documental:

- idêntico físico;
- reemissão equivalente;
- versão sucessora/substitutiva;
- componente complementar;
- unidade/matrícula distinta;
- componente aditivo;
- relação indeterminada.

`Hash diferente` não prova obrigação diferente.

## 5. Regra de soma

Somar apenas componentes economicamente distintos que pertencem à mesma conferência agregada.

Não somar:

- reemissão da mesma guia;
- guia substituída junto com sua sucessora como se ambas fossem devidas;
- duplicata física/lógica;
- valores repetidos sem identidade econômica distinta comprovada.

Somar quando houver evidência de componentes distintos, por exemplo:

- FGTS mensal + componente rescisório realmente separado;
- matrículas/inscrições diferentes com obrigação aditiva comprovada;
- recolhimentos complementares que juntos explicam o valor esperado.

## 6. Rescisão

A presença de rescisão muda o contexto, mas não autoriza regra simplista `FGTS mensal = não aplicável` para todos os casos.

O motor deve determinar por trabalhador/obrigação:

- qual parcela pertence ao mensal;
- qual parcela pertence ao rescisório;
- se houve antecipação;
- se o valor mensal já foi absorvido por recolhimento rescisório conforme a evidência;
- se existem garantias/eConsignado relacionadas que precisam de cruzamento separado.

## 7. Casos de regressão obrigatórios

### Alex Douglas de Andrade

O contexto rescisório deve explicar a expectativa de FGTS da competência sem criar ausência artificial de GFD mensal quando o valor mensal aplicável for zero/absorvido pelo tratamento rescisório.

### Comercial Faria

Múltiplas evidências de FGTS devem ser compostas conforme natureza econômica, sem exigir uma única guia e sem duplicar reemissões.

### Empório Frios Itapaci

Separar FGTS mensal, efeitos rescisórios e componentes associados ao eConsignado/garantias quando aplicáveis.

### Predileta

Composição de FGTS permanece independente da regra administrativa da fonte DARF e deve tratar corretamente evidências rescisórias.

### Ribeiro e Nascimento Art Vidros

Separar parcela mensal, rescisão e garantias; não comparar totais agregados cegamente.

### Jair Ferreira Camargo

Embora não seja um caso de rescisão, permanece controle de composição por inscrição: FGTS de matrículas distintas pode ser aditivo enquanto o federal repetido não é.

## 8. Estado da obrigação

A obrigação FGTS só pode ficar `CONFERIDA` quando a composição de componentes aplicáveis explicar integralmente o valor esperado dentro da tolerância/regra definida.

Se a relação entre duas guias for ambígua, o estado deve permanecer `DIVERGENTE`/revisão, nunca somar por conveniência.

## 9. Retificação

Em cliente já fechado:

- reemissão equivalente sem mudança material não cria retificação;
- substituição com mesmo fato econômico e sem mudança material preserva fechamento, atualizando apenas relação documental quando permitido;
- novo componente econômico ou alteração de valor material cria retificação candidata;
- versão anterior permanece intacta.

## 10. Saídas

A saída final deve usar apenas as evidências pertencentes à versão vigente do fechamento.

Guia substituída/reemitida não pode fazer o lote incluir simultaneamente documentos incompatíveis sem ação histórica explícita.

## 11. Regressão técnica mínima

Cobrir fixtures para:

1. uma GFD mensal única;
2. mensal + rescisória aditivas;
3. mensal + reemissão equivalente — não somar;
4. guia substituída + sucessora — considerar apenas a vigente conforme relação;
5. duas matrículas aditivas;
6. duas evidências equivalentes com hashes diferentes;
7. relação indeterminada — revisão, sem soma automática;
8. novo componente em cliente FECHADO — retificação candidata;
9. reemissão sem mudança material — sem retificação artificial.

## 12. Critério de homologação

B14 só pode ser liberado quando os casos reais e fixtures provarem que a V8 distingue corretamente `mais de um arquivo` de `mais de uma obrigação econômica` e produz composição auditável por origem/documento/componente.
