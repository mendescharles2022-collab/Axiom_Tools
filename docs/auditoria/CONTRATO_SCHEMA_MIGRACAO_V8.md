# Contrato V8 — Schema, migração aditiva e compatibilidade

Data: 28/08/2026
Status: **contrato de auditoria / implementação e migração ainda não homologadas**

## 1. Princípio

A V8 deve evoluir o banco existente de forma aditiva, preservando:

- clientes;
- competências;
- chamadas;
- históricos;
- versões de fechamento;
- retificações;
- documentos processados;
- histórico de reprocessamento;
- documentos físicos.

Não criar um segundo banco paralelo nem um segundo mecanismo de versão incompatível com a fundação já existente.

## 2. Fundação já existente

A árvore operacional real confirma que o banco já possui estruturas de fechamento e retificação, incluindo:

- `fechamento_mensal`;
- `fechamento_mensal_cliente`;
- `fechamento_mensal_historico`;
- `fechamento_mensal_versao`;
- `fechamento_mensal_retificacao`.

A retificação existente já trabalha com snapshot/versionamento por cliente + competência.

A V8 deve reutilizar essa fundação para o estado agregado do cliente e para versões de fechamento.

## 3. Estado por fonte/obrigação

A decisão global antiga por `competencia + cliente_id` é insuficiente para a V8.

É necessária uma estrutura persistente por obrigação/fonte.

Modelo lógico mínimo:

```text
competencia
cliente_id
fonte/obrigacao
status
motivo
observacao
usuario
criado_em
atualizado_em
```

A chave lógica deve impedir duas decisões correntes concorrentes para a mesma combinação `competencia + cliente_id + fonte`.

Fontes iniciais podem incluir, conforme aplicabilidade real:

- DARF;
- FGTS;
- DAE;
- eConsignado;
- eSocial/fechamento quando usado como evidência de obrigação;
- outras fontes futuras sem alterar a chave conceitual.

## 4. Estados da obrigação

Os estados devem seguir o contrato canônico já definido:

- `PENDENTE`;
- `CONFERIDA`;
- `DIVERGENTE`;
- `JUSTIFICADA`;
- `NAO_APLICAVEL`;
- `IMPEDIDA_EXTERNAMENTE`;
- `RETIFICACAO` quando houver mudança material daquela obrigação.

O estado agregado de `fechamento_mensal_cliente` é derivado dessas obrigações e demais fatos do ciclo.

## 5. Migração da decisão manual legada — risco crítico

A tabela/estrutura legada possui decisão global por cliente/competência.

É proibido migrar uma decisão global antiga copiando automaticamente o mesmo resultado para todas as fontes.

Exemplo do erro que deve ser evitado:

```text
LEGADO: cliente = JUSTIFICADO

migração errada:
DARF = JUSTIFICADA
FGTS = JUSTIFICADA
eConsignado = JUSTIFICADA
```

Isso reproduziria o defeito histórico de uma decisão em uma fonte liberar silenciosamente todas as outras.

### Política correta

- registros legados fechados permanecem preservados como evidência histórica global;
- não alterar retrospectivamente versões fechadas apenas para encaixar o novo modelo;
- para competências abertas/em andamento, somente converter automaticamente quando a fonte puder ser determinada inequivocamente pela própria evidência registrada;
- quando não for possível determinar a fonte, manter indicação `LEGADO_GLOBAL`/equivalente apenas para auditoria e recalcular o estado atual com as evidências disponíveis;
- não usar registro legado ambíguo como autorização automática de saída na V8.

## 6. Evidências por obrigação

A Conferência precisa relacionar uma obrigação a uma ou mais evidências documentais sem duplicar o documento físico/processado.

Modelo lógico de relação:

```text
competencia
cliente_id
fonte/obrigacao
documento/processamento_id
inscricao_origem
natureza_economica
papel_da_evidencia
grupo_composicao
```

Papéis possíveis, conforme caso:

- principal;
- complementar;
- reemissão equivalente;
- sucessora;
- unidade/matrícula distinta;
- rescisória;
- antecipada;
- justificativa/anexo externo.

A relação deve apontar para o documento existente; não copiar PDF ou criar outro cadastro documental só para a Conferência.

## 7. Composição multi-documento

A estrutura deve permitir representar, por exemplo:

### Jair Ferreira Camargo

- dois Extratos com CAEPFs distintos;
- federal consolidado repetido, contado uma única vez;
- FGTS por matrícula, somado em R$ 389,04.

### Leosmar Teodoro de Sousa

- dois Extratos equivalentes/reemissões;
- não duplicar valores por haver dois arquivos.

A natureza da relação precisa existir antes do cálculo.

## 8. Reprocessamento candidato/versionado

O reprocessamento documental precisa de persistência de candidato sem destruir a versão vigente.

Não é obrigatório adotar um nome físico de tabela específico neste contrato, mas o modelo precisa representar:

```text
arquivo/documento lógico
versão vigente
candidato
origem do reprocessamento
snapshot dos dados extraídos
identidade/cliente
competência
inscrição de origem
tipo documental
hash
status técnico
completude/confiança
criado_em
promovido_em/rejeitado_em
motivo da promoção/rejeição
```

## 9. Compatibilidade com histórico de reprocessamento existente

A base canônica já possui histórico suficiente para recuperar versões boas dos Extratos 449/450.

A migração deve:

- preservar esse histórico;
- não apagar versões ruins posteriores;
- permitir eleger/recuperar a versão correta como vigente de forma auditável;
- não converter histórico em duplicidade de documento.

Se a tabela histórica atual puder ser estendida com segurança, preferir evolução à criação de uma segunda linha histórica concorrente.

## 10. Vigente x candidato

Deve existir uma forma inequívoca de saber qual versão é vigente.

Invariantes:

- no máximo uma versão vigente por documento lógico;
- candidato não participa da Conferência final enquanto não for promovido;
- candidato rejeitado permanece auditável;
- promoção é atômica;
- promoção recalcula somente os cruzamentos afetados.

## 11. Identidade e inscrições

Não duplicar identidade cadastral no schema de Conferência.

Guardar referências:

- `cliente_id`;
- inscrição/origem documental quando aplicável;
- grupo/unidade de consolidação quando necessário.

PF com múltiplos CAEPFs continua um cliente.

PJ matriz/filial continua em estabelecimentos distintos e relacionados.

## 12. Índices mínimos

A migração final deve prever índices para os caminhos críticos, por exemplo:

- obrigação por competência/cliente/fonte;
- evidência por obrigação;
- candidato/versão por documento lógico;
- consulta de vigente;
- histórico por competência/cliente/data;
- retificação por competência/status.

Os índices exatos devem ser definidos após confrontar o schema real para evitar redundância com índices já existentes.

## 13. Chaves estrangeiras e integridade

Toda nova estrutura deve manter FK/relacionamento coerente com:

- clientes;
- fechamento mensal;
- documentos/processamentos;
- usuários quando o modelo já suportar referência.

A migração precisa ser testada com `PRAGMA foreign_key_check` e `PRAGMA integrity_check` na cópia da base canônica.

## 14. Migração aditiva

Ordem segura:

1. abrir cópia do banco canônico;
2. inventariar schema/índices/contagens;
3. criar estruturas novas aditivas;
4. preservar registros legados;
5. migrar apenas dados cujo significado seja inequívoco;
6. criar marcações de legado/compatibilidade quando a semântica antiga for ambígua;
7. executar backfill necessário sem reprocessar documentos físicos;
8. rodar integrity/foreign_key checks;
9. validar casos reais;
10. somente depois aplicar no instalador real com backup/rollback.

## 15. Proibição de backfill destrutivo

Não usar migração para “corrigir” em massa o resultado dos 28 casos sem passar pelas regras canônicas.

Migração de schema não é motor de conferência.

Exemplos proibidos:

- marcar todas as obrigações de clientes fechados como `CONFERIDA` apenas porque `fechamento_mensal_cliente.status='FECHADA'`;
- copiar decisão global antiga para todas as fontes;
- transformar todo documento `PROCESSADO` em evidência conferida;
- apagar históricos de reprocessamento considerados ruins.

## 16. Histórico fechado

Competências históricas já fechadas devem permanecer legíveis mesmo se não possuírem detalhamento por fonte no formato novo.

A UI pode exibir:

`Fechamento legado — decisão agregada anterior à V8`

quando necessário.

Não fabricar detalhamento retroativo que nunca existiu.

## 17. Saídas e migração

O gate V8 não deve liberar uma competência aberta apenas porque existe um registro legado global.

Para histórico já fechado, preservar as saídas passadas.

Para novas saídas após V8, usar o estado corrente canônico e retificações.

## 18. Regressões de migração obrigatórias

1. banco vazio migra;
2. cópia do banco canônico migra;
3. contagem de clientes não cai;
4. fechamento histórico não desaparece;
5. versões/retificações existentes permanecem;
6. histórico 449/450 permanece;
7. decisão global antiga não vira justificativa de todas as fontes;
8. cliente aberto recalcula por evidências atuais;
9. candidato não participa da Conferência antes da promoção;
10. somente uma versão vigente por documento lógico;
11. `integrity_check` = ok;
12. `foreign_key_check` sem violações novas;
13. rollback restaura banco original se a migração falhar.

## 19. Critério de homologação

O schema V8 só será homologado quando a migração aditiva for reproduzível sobre cópia do banco real, sem perda de dados e sem transformar ambiguidade legada em falsa certeza por fonte.
