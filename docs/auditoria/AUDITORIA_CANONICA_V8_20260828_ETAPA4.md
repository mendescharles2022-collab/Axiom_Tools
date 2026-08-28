# Auditoria canônica V8 — Etapa 4

Data: 28/08/2026
Status: **auditoria em andamento / sem pacote final liberado**

## 1. Escopo desta etapa

Esta etapa aprofunda dois pontos:

1. semântica real do Extrato Mensal da Domínio, com base em documentos reais disponíveis;
2. identificação de comportamentos legados da V4/V7 que ficaram incorporados na implementação e agora entram em conflito com a arquitetura V8.

## 2. Achado novo — `Situação: Trabalhando` não define natureza do vínculo

No Extrato Mensal de `P DA SILVA CARMO`, competência 08/2026, a pessoa aparece na linha individual como:

- `Situação: Trabalhando`;
- `Vínculo: Diretor`;
- rubrica `PRO-LABORE`;
- base INSS R$ 2.000,00;
- base FGTS R$ 0,00;
- valor FGTS R$ 0,00.

Na seção agregada `Situações`, o mesmo relatório informa:

- `No. Empregados: 0`;
- `Trabalhando: 0`;
- `No. Contribuintes: 1`.

### Regra canônica

O motor não pode interpretar `Situação: Trabalhando` da linha individual como sinônimo de empregado celetista.

A natureza da pessoa deve considerar, em conjunto:

- prefixo/tipo da linha (`Empr.` x `Contr.`);
- `Vínculo`;
- rubricas;
- contadores agregados `No. Empregados` e `No. Contribuintes`;
- bases de FGTS e INSS.

Diretor/contribuinte com pró-labore e base FGTS zero não cria expectativa de FGTS apenas porque sua situação textual individual é `Trabalhando`.

## 3. Confirmação com segundo Extrato — empregado e contribuinte coexistem

No Extrato de `2A PECAS E MANUTENCAO LTDA`, competência 07/2026, existem simultaneamente:

- dois empregados celetistas (`Empr.` / `Vínculo: Celetista`);
- um contribuinte/diretor (`Contr.` / `Vínculo: Diretor` / pró-labore).

A seção agregada confirma:

- `No. Empregados: 2`;
- `Trabalhando: 2`;
- `No. Contribuintes: 1`;
- base FGTS R$ 4.319,69;
- valor FGTS R$ 345,57.

O pró-labore do diretor compõe INSS, mas não compõe FGTS.

### Consequência

O motor Domínio precisa representar pessoas por categoria de vínculo, e não apenas por status textual de atividade.

## 4. Achado novo — campo `Contribuintes` do resumo financeiro não é fonte autoritativa do INSS de contribuinte

No Extrato de `P DA SILVA CARMO`, a seção `INSS FGTS, PIS e ISS` mostra:

- `Salário contribuição contribuintes: 2.000,00`;
- desconto de INSS na linha do diretor: R$ 220,00;
- `Total INSS: 220,00`;
- porém a linha agregada `Contribuintes: 0,00` permanece zerada.

Na página seguinte, `Apuração Tributos Federais` registra corretamente:

- `INSS Segurado(Folha): 220,00`;
- `Saldo à recolher: 220,00`.

Portanto, uma leitura baseada apenas na linha financeira chamada `Contribuintes` produziria falso zero.

### Regra canônica para DARF esperada

Para o Extrato Mensal Domínio, a fonte principal do valor federal esperado deve ser:

`Apuração Tributos Federais -> Saldo à recolher`

A composição anterior deve ser preservada como detalhamento/explicação, mas não substituir o saldo final da apuração.

Isso é especialmente necessário em competências com:

- salário-família;
- salário-maternidade;
- compensações DCOMP;
- retenções;
- múltiplas categorias de segurados;
- pró-labore/contribuintes.

## 5. Regra de consolidação federal ganha evidência direta do próprio Extrato Domínio

Os Extratos reais exibem aviso expresso de que os tributos federais são consolidados entre matriz e filiais.

Isso reforça a regra já validada no caso Jair Ferreira Camargo:

- valores federais repetidos em Extratos de estabelecimentos/matrículas não devem ser somados automaticamente;
- a unidade de consolidação federal pode ser superior à unidade documental;
- FGTS continua exigindo composição própria por inscrição/matrícula quando os componentes forem economicamente distintos.

### Consequência arquitetural

A Conferência deve possuir duas noções distintas:

- `identidade documental/origem`;
- `unidade de consolidação da obrigação`.

Uma não pode ser usada como substituta da outra.

## 6. Hierarquia de campos esperada no motor Domínio

### Para FGTS mensal

Priorizar:

1. `Valor do FGTS` agregado;
2. bases e valores por pessoa para explicação;
3. FGTS rescisório em campos próprios, sem misturar com mensal;
4. múltiplos Extratos somente após classificar se são reemissão, sucessão ou unidades distintas.

### Para federal/DARF

Priorizar:

1. `Apuração Tributos Federais -> Saldo à recolher`;
2. detalhamento dos encargos/deduções;
3. valores individuais/rubricas apenas como evidência de composição.

### Para população de trabalhadores

Priorizar:

1. tipo da linha (`Empr.` / `Contr.`);
2. vínculo;
3. totais `No. Empregados` / `No. Contribuintes`;
4. situação individual como estado operacional, não como categoria jurídica do vínculo.

## 7. Achado de transição — parte dos defeitos atuais são regras antigas, não acidentes

### Regra V7 atualmente superada — fechados dentro do `Ciclo atual`

A V5.6.14V7 determinava explicitamente que a Central de Conferência, no escopo `Ciclo atual`, exibisse empresas liberadas + fechadas, excluindo apenas adiadas.

A V8 mudou o contrato: a mesa de trabalho deve mostrar trabalho vivo; fechados pertencem ao histórico/snapshot.

Portanto, a presença atual de `FECHADA` no escopo não deve ser tratada como simples regressão acidental. É comportamento legado da V7 que precisa ser removido de forma consciente, incluindo atualização de testes antigos.

### Regra V7 atualmente superada — `PRONTA` exibida diretamente como `Em conferência`

A V7 também determinou que `PRONTA` fosse apresentada como `Em conferência`.

A arquitetura V8 posterior estabeleceu que cliente sem evidência documental processada não deve ser antecipado para esse estágio; antes disso o estado correto é `Aguardando processamento` ou `Em processamento`.

### Regra V7 atualmente superada — decisão manual global pode concluir o ciclo

A V7 permitia que uma decisão manual global `Conferido/Justificado` concluísse o cliente.

Os 28 casos reais demonstraram que essa granularidade é insuficiente. Na V8, justificativa precisa existir por fonte/obrigação e o estado agregado deve ser derivado.

### Regra V4 atualmente superada — retificação dentro do mesmo escopo da Conferência

A V5.6.14V4 colocava empresas em `RETIFICACAO` dentro do escopo de Conferência/Auditoria.

Na V8, retificação continua pertencendo ao ciclo de controle, mas deve possuir fluxo próprio e não contaminar a mesa normal de trabalho da chamada corrente.

## 8. Consequência para testes

Antes de corrigir código, a suíte precisa classificar testes em três grupos:

1. **contrato V8 vigente** — preservar e expandir;
2. **teste de comportamento legado V4/V7 agora superado** — atualizar deliberadamente;
3. **falha ambiental/expectativa visual antiga** — não usar para dirigir regra de negócio.

Nenhum teste antigo deve impedir a V8 apenas por codificar uma decisão que já foi substituída por contrato posterior aprovado.

Ao mesmo tempo, não se deve simplesmente apagar testes: cada expectativa alterada precisa apontar qual regra V8 a substituiu.

## 9. Regressões obrigatórias acrescentadas

1. Diretor/pró-labore com `Situação: Trabalhando` e zero empregados não pode gerar expectativa de FGTS.
2. Empresa com empregados + diretor deve separar corretamente empregado e contribuinte.
3. Linha financeira `Contribuintes: 0,00` não pode zerar DARF se `Saldo à recolher` federal for positivo.
4. DARF esperada deve refletir deduções/compensações do saldo final, e não soma ingênua de rubricas.
5. Federal de matriz/filial não pode ser somado por repetição documental.
6. FGTS deve continuar compondo por unidade quando houver componentes distintos.
7. Testes V7 que exigem fechados em `Ciclo atual` devem ser migrados para o contrato V8.
8. Testes V4/V7 que colocam retificação na mesa normal devem ser migrados para fluxo próprio de retificação.
9. Decisão manual global não pode concluir fontes não avaliadas.
10. `PRONTA` não deve virar visualmente `Em conferência` antes de o cliente alcançar de fato esse estágio.

## 10. Estado ao final da Etapa 4

A auditoria confirma que a V8 exige não apenas correção de funções isoladas, mas migração explícita de semântica entre versões.

O risco principal agora é aplicar correções corretas e a suíte antiga tentar revertê-las por estar defendendo contratos V4/V7.

Próxima etapa recomendada:

- montar mapa de testes legados x contratos V8;
- identificar no pacote canônico quais testes afirmam comportamentos superados;
- separar correções funcionais reais das atualizações legítimas de expectativa;
- continuar a regressão do motor Domínio com documentos reais.
