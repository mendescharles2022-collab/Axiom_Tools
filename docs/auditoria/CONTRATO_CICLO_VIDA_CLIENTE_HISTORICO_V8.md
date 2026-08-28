# Contrato V8 — Ciclo de vida do cliente e preservação histórica

Data: 28/08/2026
Status: **contrato obrigatório de auditoria / implementação ainda não homologada**

## 1. Problema transversal

O módulo Clientes nasceu com regras corretas para sua etapa:

- ATIVO/INATIVO;
- inativação preserva cadastro, histórico, pasta e documentos;
- reativação preserva identidade;
- Administrador pode excluir definitivamente o cadastro sem apagar o filesystem.

Posteriormente, Fechamento Mensal, processamento, retificações e saídas passaram a manter histórico operacional por `cliente_id`.

A exclusão administrativa do cadastro mestre não pode destruir ou tornar órfã a história mensal já produzida.

## 2. Princípio

Separar definitivamente:

```text
CADASTRO MESTRE ATUAL
!=
PARTICIPACAO EM UMA COMPETENCIA
!=
IDENTIDADE HISTORICA DE FECHAMENTO
!=
PASTA/DOCUMENTOS FISICOS
```

## 3. Inativação cadastral

Inativar cliente:

- mantém o registro mestre;
- preserva CPF/CNPJ/inscrições;
- preserva histórico;
- preserva pasta e documentos;
- registra data/hora, motivo e usuário;
- altera elegibilidade de competências futuras conforme data efetiva;
- não apaga nem reescreve competências já abertas/fechadas.

## 4. Competência já aberta

Se o cliente for inativado depois de a competência já possuir composição mensal:

- não remover silenciosamente o cliente da composição;
- não apagar evidências já processadas;
- não marcar automaticamente `SEM_MOVIMENTO`;
- não fechar automaticamente apenas pela inativação.

O ciclo corrente precisa ser resolvido conforme a realidade operacional da competência.

Exemplo de cenário real:

- cliente em processo de saída do escritório;
- procuração revogada antes da conclusão da competência;
- a fonte DARF pode ficar `IMPEDIDA_EXTERNAMENTE`;
- demais obrigações continuam avaliadas separadamente;
- competências posteriores respeitam a saída/inativação efetiva.

## 5. Competências futuras

Cliente inativo não entra automaticamente em novas composições posteriores à data efetiva de inativação, salvo ação explícita e auditável de inclusão excepcional.

A regra deve usar data efetiva, não apenas o estado atual consultado hoje, para evitar reescrever o passado.

## 6. Reativação

Reativar cliente:

- reutiliza o mesmo cadastro/identidade;
- preserva período anterior de inatividade;
- não recria cliente duplicado;
- não altera retroativamente competências antigas;
- torna o cliente elegível para competências futuras conforme regra temporal;
- inclusão em competência já aberta precisa seguir rotina canônica de sincronização e gerar histórico.

## 7. Exclusão administrativa do cadastro mestre

A exclusão real do cadastro continua sendo uma capacidade administrativa, mas precisa respeitar histórico operacional já consolidado.

### Sem histórico mensal/operacional dependente

Pode remover o cadastro conforme regra administrativa, preservando filesystem/documentos físicos.

### Com histórico mensal/fechamentos/saídas

A implementação não pode usar `CASCADE DELETE` que apague:

- fechamento mensal histórico;
- versões de fechamento;
- retificações;
- decisões por fonte;
- auditoria;
- saídas/entregas/impressões históricas;
- proveniência documental necessária.

A identidade histórica precisa sobreviver por solução explícita, por exemplo:

- snapshot imutável de identidade dentro das entidades históricas; e/ou
- entidade histórica/tombstone desacoplada do cadastro mestre.

A escolha física do schema deve ser feita na implementação reconciliada, mas a garantia funcional é obrigatória.

## 8. Dados mínimos da identidade histórica

Históricos que dependam da existência futura do cliente devem preservar, conforme aplicável:

- antigo `cliente_id`/identificador de origem;
- nome/razão social vigente no momento;
- CPF/CNPJ principal;
- inscrições relevantes;
- tipo PF/PJ/perfil relevante;
- competência;
- versão de fechamento;
- data do snapshot.

Mudança posterior do nome cadastral não deve reescrever a identificação exibida em um snapshot antigo.

## 9. Renomeação/alteração cadastral

Alterar nome, endereço, inscrição ou outros dados atuais:

- atualiza cadastro mestre;
- não reescreve snapshots históricos já fechados;
- documentos físicos não são renomeados automaticamente apenas por edição cadastral;
- nova competência usa os dados atuais válidos.

## 10. Exclusão versus inativação

A UI deve distinguir claramente:

- `Inativar` — preserva cadastro e impede participação futura normal;
- `Excluir cadastro` — remove o registro mestre sob autorização administrativa, mas não destrói o passado operacional nem o acervo físico.

Não usar ícone/termo que faça inativação parecer exclusão física de documentos.

## 11. Integridade referencial

Antes da exclusão do mestre, o backend deve verificar dependências e aplicar a estratégia histórica prevista.

Depois da operação:

- `PRAGMA foreign_key_check` deve continuar limpo;
- consultas de fechamentos históricos devem abrir normalmente;
- versões e saídas antigas devem continuar legíveis;
- documentos físicos permanecem acessíveis conforme política de acervo.

## 12. Regressões mínimas

1. inativar cliente não apaga pasta nem documentos;
2. inativar cliente não remove fechamento antigo;
3. inativar durante competência aberta não apaga o cliente do ciclo silenciosamente;
4. competência futura não inclui inativo fora da vigência;
5. reativar não cria novo cliente;
6. reativar não altera competência histórica;
7. excluir cadastro sem dependência não apaga filesystem;
8. excluir cadastro com fechamento histórico preserva snapshot/versões/saídas;
9. nenhum FK fica órfão após exclusão;
10. alterar nome atual não reescreve nome congelado no fechamento antigo;
11. cliente em saída com impedimento externo continua resolvendo a competência corrente por fonte;
12. histórico registra inativação, reativação e exclusão administrativa.

## 13. Severidade

Esta é uma **lacuna arquitetural transversal** revelada pela evolução do produto.

A regra antiga de exclusão cadastral continua válida somente se for conciliada com a preservação obrigatória do histórico mensal introduzido depois.

## 14. Relação com bloqueadores

Relaciona-se a B34, B35, B41, B48 e B49 e deve entrar na homologação do módulo Clientes integrado ao Fechamento.
