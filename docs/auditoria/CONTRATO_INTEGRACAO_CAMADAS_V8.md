# Contrato V8 — Integração entre camadas

Data: 28/08/2026
Status: **contrato de auditoria / obrigatório para regressão**

## 1. Motivo

A auditoria operacional anterior do Axiom Tools já encontrou defeitos em que cada peça existia isoladamente, mas o fluxo real estava quebrado:

- extensão de schema existia, mas não era inicializada;
- view tentava persistir campos que o repository não suportava;
- providers existiam, mas não eram registrados no service;
- cadastro PF gravava, porém a ficha seguinte quebrava por dependência desconectada.

Naquela auditoria, o problema só apareceu quando o fluxo foi testado de ponta a ponta.

A V8 apresenta novamente sinais de integração parcial entre camadas.

## 2. Princípio

Uma funcionalidade não está implementada porque seus arquivos/classes existem.

Ela só está implementada quando o caminho completo funciona:

```text
schema/migração
  -> repository/persistência
  -> service/regra de negócio
  -> orquestrador/job
  -> view/endpoint
  -> template/ação
  -> efeito persistido
  -> recálculo downstream
  -> auditoria
  -> regressão
```

## 3. Fechamento Mensal

Testar integração completa:

```text
abrir competência
-> criar composição
-> persistir movimento/chamada
-> expor universo canônico
-> Processamento herdar escopo
-> Conferência herdar estágio
-> saída herdar FECHADA
```

Não basta a tabela existir ou a tela exibir o status.

## 4. Mudança de chamada

Fluxo obrigatório:

```text
POST válido
-> transição no service Closing
-> UPDATE atômico
-> histórico
-> universo da chamada recalculado
-> Processamento deixa de incluir
-> eConsignado deixa de incluir
-> Conferência deixa de cobrar
-> UI reflete sem regra paralela
```

Caso de regressão: T L Empreendimentos Agrícolas.

## 5. Reprocessamento

Fluxo obrigatório:

```text
documento vigente
-> criar candidato
-> leitura/classificação/identidade/competência
-> persistir candidato
-> comparar com vigente
-> promover ou rejeitar
-> recompor obrigações afetadas
-> recalcular Conferência
-> retificação se competência já fechada
-> manter histórico
```

Caso de regressão: Jair 449/450.

## 6. Documento novo descoberto nas conexões

Fluxo obrigatório:

```text
arquivo físico
-> descoberta
-> hash
-> ingestão
-> leitura nativa/OCR fallback
-> identidade
-> competência
-> especialista
-> persistência
-> vínculo ao cliente
-> composição
-> Conferência
```

Casos reais: Construtora & Empreendimentos Messias, Eloim Transportes, J Bernardes/Odonto Art e outros.

## 7. eConsignado

Fluxo obrigatório:

```text
competência/chamada
-> universo canônico
-> job criado com escopo persistido
-> consulta oficial
-> normalização/idempotência
-> contratos/fotografia
-> cruzamento com Domínio/vínculo/rescisão/afastamento
-> estado por obrigação
-> Conferência
```

Não basta endpoint de sincronização funcionar isoladamente.

## 8. Gate de saída

Fluxo obrigatório:

```text
solicitação de impressão/entrega/saída
-> resolver competência/cliente
-> gate canônico Closing
-> confirmar FECHADA
-> confirmar ausência de retificação pendente
-> validar documento pertence à versão autorizada
-> gerar saída
-> registrar lote/entrega/versão
```

A listagem da tela não substitui o gate do serviço.

## 9. Clientes + fontes externas

Fluxo obrigatório:

```text
consulta RFB/SEFAZ
-> provider
-> normalização
-> diff
-> prévia Atual x Externo
-> confirmação humana
-> repository
-> histórico/auditoria
-> ficha atualizada
```

Ausência de um estágio não deve ser escondida por preenchimento direto na view.

## 10. Banco e inicialização

Toda tabela/índice/coluna criada para V8 deve:

- fazer parte da inicialização/migração oficial;
- ser idempotente;
- funcionar em banco vazio;
- funcionar em cópia de banco existente;
- ser validada por `integrity_check`;
- não depender de uma rota específica ser aberta para criar schema acidentalmente.

## 11. Contrato de interface de serviços

Views/templates não devem duplicar regra do domínio.

Workers/jobs não devem importar funções internas aleatórias para contornar a fachada do módulo.

Cada domínio crítico deve ter API pública pequena e estável.

Exemplos:

- `closing_scope` para universos/gates;
- serviço de reprocessamento candidato;
- serviço de composição de obrigações;
- serviço de integração eConsignado;
- serviço de saídas.

## 12. Testes de integração obrigatórios

Para cada funcionalidade crítica, possuir pelo menos um teste que atravesse várias camadas e valide o efeito final.

Exemplos:

1. `adiar cliente -> desaparece da Conferência/Processamento da chamada atual`;
2. `anexar DARF faltante -> motor -> vínculo -> Conferência deixa de acusar ausência`;
3. `reprocessamento pior -> candidato rejeitado -> vigente preservado`;
4. `cliente FECHADA -> impressão permitida`; cliente PRONTA -> bloqueada no backend;
5. `nova evidência material em FECHADA -> RETIFICACAO -> saída bloqueada`;
6. `MEI -> DAE -> nenhuma expectativa genérica de GFD`;
7. `consulta eConsignado -> somente clientes da chamada -> cruzamento contextual`.

## 13. Testes isolados continuam necessários

Unitários continuam importantes para:

- parsers;
- normalizadores;
- máscaras;
- validators;
- regras de composição.

Mas unitário verde não substitui integração.

## 14. Critério de homologação

Uma entrega V8 não pode ser considerada pronta com a justificativa 'o método existe', 'a tabela existe', 'a tela abre' ou 'o endpoint respondeu'.

O efeito de negócio completo precisa ser reproduzível e testado de ponta a ponta.
