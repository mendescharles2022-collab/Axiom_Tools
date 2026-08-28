# Auditoria canônica V8 — Etapa 5

Data: 28/08/2026
Status: **auditoria em andamento / sem pacote final liberado**

## 1. Escopo

Esta etapa consolidou dois contratos transversais que afetam diretamente o resultado da Central de Conferência:

- semântica do parser do Extrato Mensal Domínio;
- identidade cadastral/documental e unidade de consolidação das obrigações.

Também foi feita busca adicional por evidências reais de GFD, DARF e DAE na biblioteca disponível nesta sessão. Nenhuma guia concreta correspondente aos casos auditados foi recuperada nessa busca; por isso não são feitas afirmações novas sobre o conteúdo/parser dessas guias nesta etapa.

## 2. Parser Domínio — dois fixtures reais confirmados

Foram usados dois Extratos reais:

### P DA SILVA CARMO — 08/2026

- zero empregados;
- um contribuinte;
- diretor com pró-labore R$ 2.000,00;
- INSS R$ 220,00;
- FGTS R$ 0,00;
- saldo federal a recolher R$ 220,00.

A linha individual informa `Situação: Trabalhando`, mas isso não transforma o diretor em empregado.

### 2A Peças e Manutenção Ltda — 07/2026

- dois empregados celetistas;
- um contribuinte/diretor;
- FGTS agregado R$ 345,57;
- federal a recolher R$ 518,44.

O diretor participa da apuração previdenciária, mas não da base de FGTS.

## 3. Campo federal autoritativo

Os documentos demonstram que a linha financeira intermediária `Contribuintes` pode estar zerada mesmo quando há INSS de contribuinte e saldo federal positivo.

Assim, a fonte principal para o valor federal esperado deve ser:

`Apuração Tributos Federais -> Saldo à recolher`

A composição detalhada permanece necessária para explicação, deduções e diagnóstico.

## 4. IRRF — risco registrado, ainda não defeito confirmado

O Extrato distingue:

- IRRF conforme competência do cálculo;
- IRRF conforme competência do pagamento.

E o próprio aviso do relatório informa que o IRRF utiliza a competência de pagamento.

Como o código integral do parser/conferência não foi recuperado na biblioteca desta sessão, não há prova de que a implementação atual esteja errada nesse ponto.

Classificação correta neste estágio:

`RISCO DE REGRESSAO A TESTAR`.

O teste deve impedir associação automática do IRRF à competência de cálculo apenas por causa do cabeçalho do Extrato.

## 5. Identidade — contrato cadastral já existia antes da V8

A AXT-003 já definiu:

### PF

- CPF = documento principal;
- CAEPF = inscrição vinculada 1:N;
- PF pode possuir dois ou mais CAEPFs;
- múltiplos CAEPFs não criam múltiplos clientes.

### PJ

- CNPJ identifica o estabelecimento;
- matriz e filial são estabelecimentos distintos e relacionados;
- mesma raiz não é duplicidade.

Portanto, a V8 não precisa inventar uma nova camada de identidade. Precisa reutilizar e propagar a existente para Processamento e Conferência.

## 6. Evidência Jair Ferreira Camargo

A carga real já registra duas inscrições para Jair:

- CAEPF `10127380100149`;
- CAEPF `10127380100230`;

ambas associadas ao CPF principal sugerido `10127380191`.

Isso confirma o modelo esperado:

```text
1 cliente PF
1 CPF principal
2 inscrições CAEPF
2 origens documentais possíveis
```

O erro observado nos Extratos 449/450, portanto, deve ser tratado como falha de propagação/vínculo de identidade entre Cadastro -> Processamento -> Conferência, e não como necessidade de duplicar clientes.

## 7. Identidade documental e consolidação são coisas diferentes

Para cada documento, a V8 deve guardar a inscrição/origem específica.

Depois, por obrigação, decidir a unidade de consolidação.

### Jair

Federal:

- R$ 511,43 repetido nas duas origens;
- resultado consolidado = R$ 511,43.

FGTS:

- R$ 129,68 + R$ 259,36;
- resultado consolidado = R$ 389,04.

O sistema não pode usar uma regra global de soma por cliente ou por inscrição.

## 8. Achado arquitetural consolidado

A V8 precisa manter, separadamente:

```text
cliente_id
identidade principal
inscricao documental de origem
documento
obrigacao
unidade/grupo de consolidacao
natureza econômica do componente
```

Esse desenho também impede que uma perda de CAEPF durante reprocessamento pareça apenas queda de confiança: é regressão de identidade e deve impedir promoção automática do candidato.

## 9. Guias GFD/DARF/DAE — estado desta rodada

A busca da biblioteca por guias reais de agosto não recuperou arquivos utilizáveis dos casos auditados.

Consequentemente:

- não foi inventado contrato de campos de GFD/DARF/DAE sem evidência;
- regras já validadas por casos reais permanecem vigentes;
- o batimento ponta a ponta Extrato -> guia continua requisito de regressão;
- quando as guias/fontes estiverem novamente acessíveis, devem ser confrontadas com os contratos de parser e consolidação já definidos.

## 10. Novos critérios de regressão

1. diretor/contribuinte não vira empregado por `Situação: Trabalhando`;
2. pró-labore pode compor federal sem compor FGTS;
3. `Contribuintes: 0,00` não anula saldo federal positivo;
4. federal esperado usa `Saldo à recolher` como referência final do Extrato;
5. IRRF por competência de pagamento deve possuir teste específico;
6. PF com dois CAEPFs continua um único cliente;
7. documento mantém CAEPF de origem;
8. perda da inscrição de origem em reprocessamento bloqueia promoção do candidato;
9. PJ matriz/filial continua em cadastros distintos, relacionados;
10. consolidação varia por obrigação e não funde identidade cadastral.

## 11. Documentos canônicos produzidos nesta linha da auditoria

- `AUDITORIA_CANONICA_V8_20260828_ETAPA3.md`;
- `MATRIZ_REGRESSAO_V8_AGOSTO_2026.md`;
- `DIVERGENCIA_REPOSITORIO_BASE_CANONICA_20260828.md`;
- `AUDITORIA_CANONICA_V8_20260828_ETAPA4.md`;
- `MAPA_TRANSICAO_REGRAS_V4_V7_PARA_V8.md`;
- `CONTRATO_PARSER_EXTRATO_DOMINIO_V8.md`;
- `CONTRATO_IDENTIDADE_CONSOLIDACAO_V8.md`;
- este documento.

## 12. Estado ao final da Etapa 5

A auditoria permanece aberta.

Os contratos funcionais estão ficando suficientemente objetivos para impedir correções pontuais por cliente.

Ainda não existe evidência para declarar corrigidos:

- reprocessamento destrutivo;
- recuperação 449/450;
- composição multi-GFD;
- decisão por fonte;
- gate único de saída;
- eConsignado limitado ao ciclo;
- Conference read-only;
- regressão integral dos 28 casos;
- falha `classificacao_inativacao` string/Enum;
- restauração/homologação visual Sintegra.

Nenhum pacote V8 deve ser liberado antes dessas verificações.
