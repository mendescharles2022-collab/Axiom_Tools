# Contrato V8 — Elegibilidade e composição mensal

Data: 28/08/2026
Status: **contrato obrigatório de auditoria / implementação ainda não homologada**

## 1. Achado de evolução

Há três momentos documentais diferentes:

### V6

A abertura da competência foi definida como inclusão automática de `todos os clientes ativos` na 1ª chamada.

### Runtime posterior

O `closing/service.py` preservado em evidência real contém regra/comentário indicando que classificação `NAO_SE_APLICA` fica fora do fechamento mensal.

### V8

A arquitetura aprovada afirma que estar cadastrado no Axiom Tools não significa participar automaticamente do fechamento mensal.

Conclusão: a regra de elegibilidade evoluiu e precisa existir em um serviço canônico explícito, não como filtro implícito espalhado pelo código.

## 2. Princípio

A composição de uma competência é um **snapshot de elegibilidade mensal**.

Ela deve responder, para cada cliente avaliado:

```text
participa = SIM/NAO
motivo = <regra objetiva>
fonte_da_regra = <cadastro/configuracao/data efetiva>
avaliado_em = <data/hora>
```

## 3. Cadastro não é composição

O cadastro mestre representa a carteira completa e o acervo.

A composição mensal representa apenas os clientes elegíveis para aquele ciclo do Departamento Pessoal.

Portanto:

```text
cliente ATIVO
não implica automaticamente
cliente PARTICIPANTE
```

sem passar pela regra canônica de elegibilidade.

## 4. Critérios mínimos de entrada

O serviço deve considerar, conforme os campos realmente existentes na implementação reconciliada:

- situação interna e vigência cadastral;
- classificação permanente que indique participação ou não no fechamento;
- data efetiva de inativação/reativação;
- perfil operacional relevante ao DP;
- exclusões explícitas como `NAO_SE_APLICA`;
- decisão administrativa válida prevista pela arquitetura.

Não inferir participação pela existência de pasta ou documento.

## 5. Abertura da competência

Ao abrir a competência:

1. executar serviço único de elegibilidade;
2. gerar composição mensal;
3. registrar participantes e motivo de inclusão;
4. quando útil para auditoria, registrar também motivo dos não participantes sem criar linha operacional ativa desnecessária;
5. participantes liberados iniciam na 1ª chamada/estado correspondente;
6. composição passa a ser a fonte do universo dos módulos dependentes.

## 6. Sincronização após abertura

Mudanças cadastrais posteriores à abertura não reescrevem silenciosamente a composição.

Deve existir rotina canônica de sincronização que:

- identifica delta de elegibilidade;
- explica cliente adicionado/removido/proposto;
- respeita data efetiva;
- preserva clientes já processados/fechados;
- registra histórico;
- não cria duplicidade.

## 7. Inativação após abertura

Inativar cliente depois que ele já entrou na composição:

- não o apaga silenciosamente da competência;
- o ciclo existente deve ser resolvido conforme realidade operacional;
- competências futuras respeitam a data efetiva.

## 8. Reativação após abertura

Reativação não inclui silenciosamente o cliente em competência já aberta.

A inclusão deve ocorrer por sincronização canônica, se temporalmente aplicável, com histórico.

## 9. Próxima chamada

Chamada não altera elegibilidade da competência.

Cliente em 2ª chamada:

- continua participante da competência;
- fica fora apenas do universo operacional da 1ª chamada;
- motivo e chamada permanecem auditáveis.

## 10. Sem movimento

`Sem movimento nesta competência` também não significa não participante.

É condição mensal dentro da composição e altera expectativas, não a existência histórica do cliente no ciclo.

## 11. NAO_SE_APLICA

A classificação permanente `NAO_SE_APLICA`, quando vigente no cadastro/configuração, exclui o cliente da composição mensal normal.

Essa decisão deve ser distinguida de:

- `Sem movimento` mensal;
- próxima chamada;
- impedimento temporário;
- obrigação específica `NAO_APLICAVEL` dentro de um cliente participante.

São quatro conceitos diferentes.

## 12. Consumidores obrigatórios

O mesmo universo de composição deve ser consumido por:

- Processamento;
- eConsignado;
- Conference;
- Pendências técnicas contextualizadas;
- fechamento automático;
- Impressão/Entregas via gate;
- relatórios da competência.

Nenhum consumidor deve reconstruir elegibilidade consultando diretamente `clientes` com regra própria.

## 13. Contagens explicáveis

Toda tela que exibir contagem de ciclo deve ser reconciliável:

```text
total carteira
- inativos/não vigentes
- NAO_SE_APLICA/outros não elegíveis
= participantes da competência
```

Depois:

```text
participantes
= chamada atual + chamadas futuras + fechados + retificação + demais estados internos válidos
```

A soma deve fechar sem clientes fantasma.

## 14. Evidência de agosto

A auditoria registrou 339 clientes participantes em 08/2026 enquanto a carteira total era muito maior.

A composição real demonstra que já existe algum filtro de elegibilidade além de simples existência cadastral.

A regra completa do runtime ainda precisa ser inspecionada no ZIP/código reconciliado; não será inferida apenas pela contagem.

## 15. Regressões mínimas

1. cliente ativo + elegível entra na nova competência;
2. cliente `NAO_SE_APLICA` não entra no ciclo normal;
3. inativo fora da vigência não entra;
4. cliente de 2ª chamada continua participante, mas fora da 1ª;
5. sem movimento continua participante da competência;
6. inativação posterior não apaga composição já existente;
7. reativação não altera competência antiga;
8. sincronização pós-abertura é idempotente;
9. todos os módulos recebem a mesma lista para a mesma chamada;
10. contagens das telas reconciliam com a composição;
11. eConsignado não consulta universo maior que o da competência/chamada aplicável;
12. motivo de inclusão/exclusão é auditável.

## 16. Relação com bloqueadores

Principalmente B07, B08, B24, B25, B37, B40 e B45.
