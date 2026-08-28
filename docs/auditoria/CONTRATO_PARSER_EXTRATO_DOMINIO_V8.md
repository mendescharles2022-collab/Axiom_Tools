# Contrato V8 — Parser do Extrato Mensal Domínio

Data: 28/08/2026
Status: **contrato de auditoria / implementação e regressão ainda não homologadas**

## 1. Objetivo

Definir de forma inequívoca quais campos do Extrato Mensal da Domínio representam identidade, população de trabalhadores, FGTS e tributos federais, evitando inferências incorretas que geram falsas pendências na Central de Conferência.

Este contrato foi derivado de documentos reais e deve orientar implementação, testes e explicabilidade da Conferência.

## 2. Princípio central

O Extrato Mensal possui campos com nomes semelhantes que representam conceitos diferentes.

O parser não pode escolher valores apenas por proximidade textual ou por uma palavra isolada.

Toda extração relevante deve guardar:

- valor extraído;
- seção de origem;
- rótulo original;
- página;
- regra de interpretação aplicada;
- unidade documental/estabelecimento quando disponível.

A Conferência deve conseguir explicar de onde veio cada valor usado no batimento.

## 3. Identidade do documento

Extrair e preservar:

- código da empresa Domínio;
- razão/nome;
- CPF/CNPJ/CAEPF exibido;
- competência;
- tipo de cálculo;
- complemento de cálculo;
- data/hora de emissão;
- filial/matrícula/origem quando disponível.

Identidade documental não define, sozinha, a unidade de consolidação da obrigação.

## 4. Classificação das pessoas

### Regra obrigatória

A categoria da pessoa deve ser determinada por conjunto de evidências, nesta ordem:

1. prefixo/tipo da linha (`Empr.` / `Contr.` ou equivalente);
2. campo `Vínculo`;
3. rubricas características;
4. totais agregados `No. Empregados` e `No. Contribuintes`;
5. bases de FGTS/INSS;
6. `Situação` como estado operacional, não como categoria jurídica.

### Proibição

Não usar `Situação: Trabalhando` como sinônimo de empregado celetista.

Uma pessoa pode estar trabalhando e ser diretor/contribuinte sem incidência de FGTS.

## 5. Fixture real A — P DA SILVA CARMO

Documento: `21537-Extrato Mensal.pdf`
Competência: 08/2026
CNPJ: 39.373.545/0001-89

### Evidência individual

- `Contr: 1 POLIANA DA SILVA CARMO`;
- `Situação: Trabalhando`;
- `Vínculo: Diretor`;
- rubrica `PRO-LABORE` R$ 2.000,00;
- desconto INSS R$ 220,00;
- base FGTS R$ 0,00;
- valor FGTS R$ 0,00.

### Evidência agregada

- `No. Empregados: 0`;
- `Trabalhando: 0`;
- `No. Contribuintes: 1`;
- `Salário contribuição empregados: 0,00`;
- `Salário contribuição contribuintes: 2.000,00`;
- `Total INSS: 220,00`;
- `Contribuintes: 0,00` na grade financeira intermediária;
- `Apuração Tributos Federais -> Saldo à recolher: 220,00`.

### Saída estruturada esperada

```text
competencia = 08/2026
empregados = 0
contribuintes = 1
fgts_base_mensal = 0,00
fgts_valor_mensal = 0,00
federal_saldo_recolher = 220,00
pessoa[0].categoria = CONTRIBUINTE
a pessoa[0].vinculo = DIRETOR
pessoa[0].pro_labore = 2.000,00
pessoa[0].inss = 220,00
pessoa[0].fgts = 0,00
```

A presença textual de `Situação: Trabalhando` não altera esse resultado.

## 6. Fixture real B — 2A Peças e Manutenção Ltda

Documento: `Extrato Mensal.pdf`
Competência: 07/2026
CNPJ: 39.538.135/0001-40

### Pessoas

- Pedro Emmanuel Araújo Silva — `Empr.`, vínculo Celetista, FGTS R$ 209,57;
- Carolina Machado Fernandes — `Empr.`, vínculo Celetista, FGTS R$ 136,00;
- Robson Alves Silveira — `Contr.`, vínculo Diretor, pró-labore R$ 1.621,00, INSS R$ 178,31, FGTS R$ 0,00.

### Agregados

- `No. Empregados: 2`;
- `Trabalhando: 2`;
- `No. Contribuintes: 1`;
- base FGTS R$ 4.319,69;
- valor FGTS R$ 345,57;
- saldo federal a recolher R$ 518,44.

### Saída estruturada esperada

```text
competencia = 07/2026
empregados = 2
contribuintes = 1
fgts_base_mensal = 4.319,69
fgts_valor_mensal = 345,57
federal_saldo_recolher = 518,44
```

O FGTS individual dos dois empregados soma R$ 345,57. O diretor não adiciona FGTS, embora participe da apuração previdenciária.

## 7. Regra autoritativa para FGTS

Para FGTS mensal, priorizar o valor agregado da seção `INSS FGTS, PIS e ISS`:

- `Base do FGTS`;
- `Valor do FGTS`.

Os valores por pessoa são detalhamento de composição e devem servir para validação/explicação.

Campos de FGTS rescisório devem permanecer separados:

- `Base FGTS Rescisório`;
- `Valor FGTS Rescisório`;
- campos de mês anterior, quando existentes.

Não somar mensal e rescisório sem primeiro classificar a natureza econômica da evidência.

## 8. Regra autoritativa para DARF/federal esperado

A fonte principal do valor federal esperado é:

`Apuração Tributos Federais -> Saldo à recolher`

Esse saldo já representa a apuração após os componentes aplicáveis, incluindo quando presentes:

- salário-família;
- salário-maternidade;
- DCOMP;
- retenções;
- diferentes categorias de segurados;
- IRRF e demais encargos reconhecidos no relatório.

### Proibições

Não usar isoladamente como total federal:

- linha `Contribuintes` da grade intermediária;
- soma bruta de descontos individuais;
- `Total INSS` quando o próprio relatório apresentar saldo final diferente;
- soma de saldos federais repetidos entre matriz/filiais.

## 9. Deduções e saldo zero

Quando `Saldo à recolher = 0,00`, o parser deve preservar a composição que levou ao zero.

A Conferência deve receber:

```text
obrigacao_federal_aplicavel = SIM
saldo_esperado = 0,00
emissao_darf_necessaria = NAO
```

Isso permite distinguir:

- obrigação inexistente;
- obrigação existente cujo saldo foi zerado por deduções/compensações.

Casos reais relacionados: Denes Mariano de Castro e situações com salário-família/compensações.

## 10. Consolidação matriz/filial

O próprio Extrato Domínio informa que os tributos federais são consolidados entre matriz e filiais.

Portanto:

- identidade documental por estabelecimento deve ser preservada;
- saldo federal repetido não deve ser automaticamente somado;
- a Conferência deve determinar a unidade de consolidação da obrigação antes da composição;
- FGTS pode continuar sendo aditivo por matrícula/unidade quando a evidência demonstrar componentes economicamente distintos.

Esse contrato é obrigatório para o caso Jair Ferreira Camargo.

## 11. IRRF — risco específico de competência

O Extrato apresenta simultaneamente quadros de:

- `IRRF conforme competência do cálculo`;
- `IRRF conforme competência do pagamento`.

O aviso do próprio relatório indica que a apuração de IRRF utiliza a competência de pagamento.

### Regra de auditoria

O parser não pode assumir que todo IRRF pertence automaticamente à competência de cálculo do cabeçalho.

Antes de transformar IRRF em expectativa de DARF por competência, a implementação deve validar qual coluna/competência corresponde ao fato gerador tratado pelo fluxo do escritório.

Neste momento isso é **risco de regressão a testar**, não defeito funcional confirmado no código.

## 12. Validação cruzada interna do Extrato

O parser deve produzir alertas técnicos quando os campos internos forem incoerentes além de tolerância definida.

Exemplos de validação:

- soma de FGTS individual dos empregados x `Valor do FGTS` agregado;
- contagem de linhas `Empr.` x `No. Empregados`;
- contagem de linhas `Contr.` x `No. Contribuintes`;
- saldo federal final x composição informada, sem recalcular legislação quando o relatório já fornece o saldo oficial da apuração.

Divergência interna deve reduzir confiança e encaminhar o documento para revisão técnica, sem inventar valor alternativo.

## 13. Proveniência obrigatória

Cada campo relevante persistido deve poder indicar sua fonte lógica.

Exemplo:

```text
federal_saldo_recolher.valor = 220,00
federal_saldo_recolher.fonte = APURACAO_TRIBUTOS_FEDERAIS_SALDO
federal_saldo_recolher.documento = 21537-Extrato Mensal.pdf
federal_saldo_recolher.pagina = 2
```

Isso torna a ficha da Conferência auditável e evita que o usuário veja apenas um número sem saber qual trecho do relatório o originou.

## 14. Regressões mínimas do parser Domínio

1. P DA SILVA CARMO: zero empregados, um contribuinte, FGTS zero, federal R$ 220,00.
2. 2A Peças: dois empregados + um contribuinte; FGTS R$ 345,57; federal R$ 518,44.
3. Diretor com `Situação: Trabalhando` nunca vira celetista apenas pelo status.
4. `Contribuintes: 0,00` não pode zerar federal quando `Saldo à recolher` for positivo.
5. Saldo federal final zero por dedução não gera ausência de DARF como erro.
6. Federal repetido entre matriz/filial não soma sem identificação de obrigação distinta.
7. FGTS individual e agregado devem bater dentro de tolerância.
8. FGTS rescisório permanece separado do mensal até composição contextual.
9. IRRF deve respeitar a semântica de competência de pagamento antes de gerar expectativa.
10. Todo valor usado pela Conferência precisa manter proveniência documental.

## 15. Critério de homologação

O motor Domínio não estará homologado apenas porque extrai os números corretos dos dois fixtures.

Também deve:

- classificar corretamente a natureza das pessoas;
- preservar origem dos valores;
- distinguir mensal/rescisório;
- suportar matriz/filial;
- tratar deduções;
- não criar obrigação por inferência superficial;
- alimentar a Conferência com dados estruturados suficientes para explicar o batimento.
