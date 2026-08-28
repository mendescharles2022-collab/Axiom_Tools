# Contrato V8 — Identidade cadastral, documental e consolidação de obrigações

Data: 28/08/2026
Status: **contrato de auditoria / regressão obrigatória antes da homologação V8**

## 1. Problema

A auditoria dos casos de agosto demonstrou que o Axiom Tools precisa distinguir conceitos que hoje podem ser confundidos durante Processamento e Conferência:

- cliente;
- pessoa/entidade jurídica principal;
- estabelecimento;
- inscrição vinculada;
- identidade do documento;
- unidade de consolidação da obrigação.

O caso Jair Ferreira Camargo é a evidência principal: uma mesma pessoa física possui duas inscrições CAEPF, dois Extratos documentais e componentes de FGTS distintos, enquanto a obrigação federal é consolidada.

## 2. Contrato cadastral já aprovado na AXT-003

A modelagem cadastral anterior já definiu corretamente:

### Pessoa Física

- CPF = identidade principal do cliente;
- CAEPF = inscrição vinculada;
- IE = inscrição vinculada;
- um PF pode possuir 0..N CAEPF;
- um PF pode possuir 0..N IE;
- possuir dois CAEPFs não cria dois clientes.

### Pessoa Jurídica

- CNPJ = identidade operacional do estabelecimento;
- matriz e filial são estabelecimentos/clientes distintos;
- mesma raiz CNPJ não é duplicidade;
- relação matriz/filial deve ser preservada.

A V8 não deve substituir esse contrato. Deve propagá-lo para documentos, processamento e conferência.

## 3. Evidência real — Jair Ferreira Camargo

A carga inicial do Axiom Tools contém duas linhas para Jair:

- CAEPF `10127380100149`;
- CAEPF `10127380100230`.

Ambas têm como CPF principal sugerido:

`10127380191`.

Logo, o resultado cadastral esperado é:

```text
cliente PF = Jair Ferreira Camargo
CPF principal = 101.273.801-91
inscricoes CAEPF = [10127380100149, 10127380100230]
```

Não são dois clientes independentes.

## 4. Três níveis de identidade obrigatórios

### 4.1 Identidade cadastral

Quem é o cliente no Axiom Tools.

Exemplos:

- PF: CPF;
- PJ: CNPJ do estabelecimento.

### 4.2 Identidade documental

A qual inscrição/unidade o documento pertence.

Pode incluir:

- CAEPF;
- CNPJ de filial;
- matrícula;
- CNO;
- CEI;
- estabelecimento Domínio;
- outra inscrição reconhecida.

Dois documentos podem pertencer ao mesmo cliente e manter identidades documentais distintas.

### 4.3 Unidade de consolidação da obrigação

Nível em que determinado valor deve ser comparado/consolidado.

Essa unidade depende da obrigação e não pode ser inferida apenas do `cliente_id`.

## 5. Consolidação é específica por obrigação

O mesmo conjunto de documentos pode ter unidades de consolidação diferentes.

### Exemplo Jair

Dois Extratos de CAEPFs distintos pertencem ao mesmo cliente PF.

#### Federal

- saldo R$ 511,43 aparece em ambos;
- representa a mesma apuração consolidada;
- resultado esperado: R$ 511,43 uma única vez.

#### FGTS

- CAEPF A: R$ 129,68;
- CAEPF B: R$ 259,36;
- componentes economicamente distintos;
- resultado esperado: R$ 389,04.

Portanto:

```text
mesmo cliente != somar tudo
inscricoes diferentes != obrigações sempre independentes
```

A natureza da obrigação define a composição.

## 6. Regras para PF + múltiplos CAEPF

1. identificar primeiro o CPF principal;
2. vincular cada CAEPF ao mesmo `cliente_id` PF;
3. preservar CAEPF de origem em cada documento;
4. permitir múltiplos documentos da mesma competência por CAEPF;
5. consolidar apenas no estágio da obrigação;
6. nunca escolher apenas o "último Extrato" do cliente;
7. nunca transformar inscrição secundária em novo cliente automaticamente.

## 7. Regras para PJ matriz/filial

A modelagem é diferente da PF.

Cada CNPJ de estabelecimento permanece cliente/estabelecimento operacional distinto, relacionado pela raiz/matriz.

A Conferência deve poder formar um `grupo de consolidação` quando a obrigação assim exigir, sem fundir os cadastros.

Exemplo real já existente na carga:

- Agropecuária J. Guedes Ltda — CNPJ matriz `29.697.676/0001-68`;
- filial `29.697.676/0002-49`;
- mesma raiz, cadastros de estabelecimentos distintos e relacionados.

## 8. Grupo de consolidação não é grupo cadastral genérico

É proibido criar uma única regra do tipo:

`mesma raiz/mesmo CPF -> somar valores`.

O sistema deve responder separadamente:

1. quais documentos pertencem à mesma entidade/grupo;
2. quais documentos representam a mesma obrigação;
3. quais componentes são aditivos;
4. quais valores são repetição/consolidação já realizada na origem.

## 9. Chave lógica de composição

Cada evidência financeira deve carregar, quando disponível:

```text
cliente_id
competencia
fonte
obrigacao
inscricao_origem
tipo_inscricao
estabelecimento_origem
natureza_recolhimento
periodo_apuracao
identificador_documental
grupamento_consolidacao
valor
```

O `grupamento_consolidacao` deve ser calculado conforme a obrigação, não usado como identidade cadastral.

## 10. Federal

Para federal/DARF:

- respeitar indicação de consolidação do Extrato Domínio;
- evitar soma de saldo repetido entre unidades quando a apuração já vier consolidada;
- preservar cada documento que comprovou o mesmo saldo;
- comparar a guia e-CAC/DARF contra a obrigação consolidada correta.

## 11. FGTS

Para FGTS:

- manter origem por inscrição/matrícula;
- distinguir mensal, rescisório e antecipado;
- somar apenas componentes economicamente distintos;
- detectar reemissão/duplicidade antes da soma;
- permitir guia consolidada confrontada com múltiplos componentes de origem.

## 12. eConsignado

O universo e a consolidação de eConsignado também não devem duplicar consultas por estabelecimento quando a fonte governamental opera em nível de empregador/CPF/CNPJ raiz aplicável.

A regra específica deve preservar:

- identidade do contrato;
- trabalhador;
- empregador consultado;
- estabelecimento/vínculo quando disponível;
- deduplicação de retorno.

Não reutilizar automaticamente a regra de federal ou FGTS.

## 13. Interface da Conferência

A ficha do cliente deve conseguir mostrar:

```text
Cliente: Jair Ferreira Camargo
CPF: 101.273.801-91

Origem CAEPF A
- Extrato ...
- FGTS R$ 129,68

Origem CAEPF B
- Extrato ...
- FGTS R$ 259,36

Consolidação
- Federal esperado: R$ 511,43 (não somado)
- FGTS esperado: R$ 389,04 (soma das unidades)
```

Assim o usuário enxerga a origem e a regra usada, em vez de receber um único número opaco.

## 14. Relação com reprocessamento

Quando uma nova leitura perder a inscrição de origem, isso deve ser considerado regressão de identidade relevante.

Um candidato de reprocessamento que transforme:

```text
cliente + CAEPF conhecido
```

em:

```text
cliente desconhecido / inscrição desconhecida
```

não pode substituir silenciosamente a versão vigente.

Esse é exatamente o padrão observado nos Extratos 449/450 de Jair.

## 15. Regressões obrigatórias

1. dois CAEPFs de um mesmo CPF não criam dois clientes PF;
2. documentos de CAEPFs distintos permanecem individualizados;
3. Jair federal = R$ 511,43 uma vez;
4. Jair FGTS = R$ 389,04 por soma das duas inscrições;
5. perda de CAEPF em reprocessamento impede promoção automática do candidato;
6. dois CNPJs da mesma raiz continuam estabelecimentos distintos;
7. mesma raiz CNPJ não é duplicidade cadastral;
8. grupo de consolidação não funde clientes/estabelecimentos;
9. regra de composição deve variar por obrigação;
10. interface deve exibir origem das parcelas consolidadas.

## 16. Conclusão

A modelagem cadastral necessária para resolver o caso Jair já havia sido prevista corretamente desde a AXT-003.

O defeito arquitetural da V8 está na ligação entre essa identidade e as camadas de Processamento/Conferência.

A correção deve reutilizar `cliente + inscrições vinculadas + relação matriz/filial`, e não criar uma segunda modelagem paralela de identidade dentro dos motores documentais.
