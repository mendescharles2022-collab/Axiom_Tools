# Contrato V8 — Enriquecimento cadastral por fontes externas

Data: 28/08/2026
Status: **contrato de auditoria / implementação integrada ainda não homologada**

## 1. Objetivo

Definir como o Cadastro de Clientes deve consumir RFB, SEFAZ GO/Sintegra e demais fontes externas sem misturar dados oficiais com decisões internas do escritório e sem sobrescrever silenciosamente informações válidas.

## 2. Princípio central — fontes têm papéis diferentes

O Axiom Tools deve separar:

- **situação interna do cliente**: decisão operacional do escritório (`ATIVO`, `INATIVO` etc.);
- **situação cadastral RFB**: estado federal conhecido na última consulta;
- **situação cadastral estadual**: estado da inscrição estadual na fonte estadual;
- **validação local de IE**: verificação matemática/formal;
- **conferência externa da IE**: confirmação cadastral no portal estadual.

Nenhuma dessas dimensões deve sobrescrever automaticamente outra.

Exemplo válido:

```text
Situação interna: Ativo
Situação RFB: Baixada
Situação IE GO: Suspensa
```

O sistema deve expor a divergência; não decidir sozinho que o cliente deve ser inativado.

## 3. RFB

A arquitetura anterior já determinou que dados RFB sejam tratados como retrato externo, com fonte e data/hora da consulta.

Regras preservadas:

- consulta sob demanda ou conforme configuração explícita;
- atualização diferencial;
- revisão humana antes de aplicar campos sensíveis;
- ausência de campo na fonte não deve virar valor negativo inventado;
- falha de provider não apaga retrato anterior válido;
- situação RFB jamais inativa automaticamente o cadastro interno.

## 4. SEFAZ GO / Sintegra

Para Goiás, a consulta pública atual permite CCE/IE, CNPJ ou CPF e não apresenta CAPTCHA visível no formulário validado em 28/08/2026.

Estratégia:

1. tentativa de consulta direta por adaptador isolado;
2. normalização do resultado;
3. comparação `Atual × SEFAZ GO`;
4. confirmação humana;
5. fallback assistido no navegador se a consulta direta for bloqueada ou mudar.

Não assumir API oficial estável sem documentação própria.

## 5. Validação local da IE não é conferência cadastral

O validador local deve responder apenas sobre formato/DV e suporte da UF.

Estados locais possíveis incluem:

- `VALIDA_LOCALMENTE`;
- `DV_DIVERGENTE`;
- `FORMATO_INVALIDO`;
- `NAO_INFORMADA`;
- `NAO_SUPORTADA`.

Uma IE com DV matematicamente correto pode:

- pertencer a outro contribuinte;
- estar baixada;
- estar suspensa;
- ter sido substituída;
- estar desatualizada no cadastro interno.

Portanto não exibir simplesmente `IE válida` quando apenas o DV foi testado.

## 6. Evidência da carga inicial

A carga inicial preparada para o Axiom Tools registrou, entre outros indicadores:

- 981 linhas na relação original;
- 887 CNPJs válidos detectados;
- 25 CPFs válidos;
- 69 candidatos a CAEPF;
- 274 registros com IE informada;
- 241 IEs com DV local conferindo;
- 29 IEs com DV local divergente;
- 4 placeholders `10.000.000-0`.

A decisão já documentada para IE com DV divergente é:

`preservar valor original -> marcar pendência -> conferir no Sintegra -> manter/corrigir/remover`.

Nunca calcular um novo DV e sobrescrever o número automaticamente.

## 7. Hierarquia por campo

A origem deve ser preservada por campo.

### Identidade principal

- CPF/CNPJ interno normalizado identifica o cliente/estabelecimento;
- divergência do documento retornado pela fonte bloqueia aplicação automática.

### Razão social / nome fantasia

- fonte externa pode propor atualização;
- usuário revisa a diferença;
- nome legal/original anterior permanece no histórico.

### Endereço

- RFB e SEFAZ podem ter retratos diferentes;
- sistema deve informar fonte e data;
- não mesclar pedaços de endereços de fontes distintas sem regra explícita.

### CNAE

- preservar fonte;
- RFB e SEFAZ podem ter escopos/tempos de atualização distintos;
- não substituir automaticamente conjunto de CNAEs por uma fonte mais pobre.

### Inscrição Estadual

- IE pertence à coleção de inscrições do cliente;
- UF explícita;
- validação local e conferência externa são estados separados;
- histórico de inclusão, edição, remoção e conferência obrigatório.

## 8. Ausência na fonte

`campo ausente` não significa `campo deve ser apagado`.

Ao receber resposta parcial:

- manter dado atual;
- registrar `não retornado nesta fonte` quando necessário;
- só remover campo por decisão explícita ou evidência oficial inequívoca apresentada ao usuário.

## 9. Conflito entre fontes

Conflitos devem gerar comparação explicável, não arbitragem silenciosa.

Exemplo:

```text
Campo: Nome fantasia
Cadastro atual: X
RFB: Y
SEFAZ GO: Z
```

O usuário decide qual valor aplicar ao cadastro operacional, mantendo os retratos externos separados.

## 10. Auditoria obrigatória

Toda aplicação de diferença deve registrar:

- cliente;
- campo;
- valor anterior;
- valor novo;
- fonte externa;
- data/hora da consulta;
- usuário que aplicou;
- data/hora da aplicação.

Para IE, preservar eventos específicos como:

- `IE_ADICIONADA`;
- `IE_EDITADA`;
- `IE_REMOVIDA`;
- `IE_VALIDADA_LOCALMENTE`;
- `IE_CONFERIDA_SINTEGRA`;
- `IE_MARCADA_DIVERGENTE`.

## 11. Regressões obrigatórias

1. situação RFB `Baixada` não inativa cliente automaticamente;
2. situação estadual não altera situação interna automaticamente;
3. DV local correto não marca IE como cadastralmente confirmada;
4. DV divergente não autocorrige IE;
5. campo ausente na fonte não apaga valor interno;
6. documento retornado incompatível bloqueia aplicação;
7. falha SEFAZ não vira `IE inexistente`;
8. falha RFB não apaga último retrato válido;
9. atualização diferencial preserva histórico;
10. RFB e SEFAZ mantêm metadados de fonte independentes;
11. consulta direta GO e fallback produzem o mesmo modelo normalizado;
12. matriz/filial e múltiplas inscrições não são tratadas como duplicidade apenas por compartilharem raiz/identidade principal.

## 12. Critério de homologação

O enriquecimento cadastral só estará homologado quando o usuário puder consultar, comparar e aplicar dados de fontes externas sem que qualquer fonte externa passe a controlar silenciosamente a situação operacional interna do cliente.
