# Contrato V8 — Invariantes de banco e orfandade

Data: 28/08/2026
Status: **contrato de auditoria / nenhuma orfandade declarada sem execução no banco canônico**

## 1. Fundamento

A fundação do Axiom Tools já utiliza SQLite com:

- foreign keys habilitadas;
- WAL;
- `busy_timeout=10000`;
- `synchronous=NORMAL`.

Versões anteriores também registraram `PRAGMA integrity_check = ok` em validações.

Isso é necessário, mas não suficiente para homologar a V8.

## 2. Distinção importante

### Integridade física/estrutural

`PRAGMA integrity_check` detecta problemas estruturais do arquivo SQLite.

### Integridade referencial

`PRAGMA foreign_key_check` verifica violações de foreign keys declaradas.

### Integridade lógica de negócio

Exige queries específicas, mesmo quando o banco não possui foreign key para todas as relações históricas/versionadas.

A V8 precisa dos três níveis.

## 3. Regra de auditoria

Não declarar 'banco íntegro' somente porque `integrity_check = ok`.

O relatório final deve apresentar separadamente:

```text
integrity_check
foreign_key_check
invariantes_logicas
```

## 4. Invariantes — Clientes

Verificar, conforme schema real:

- inscrição vinculada aponta para cliente existente;
- relação matriz/filial aponta para estabelecimentos existentes;
- histórico de cliente pode preservar referência histórica mesmo após exclusão cadastral conforme política definida;
- cliente inativo continua com documentos/pasta preservados;
- documento principal normalizado permanece único conforme tipo.

## 5. Invariantes — Fechamento Mensal

Para cada `fechamento_mensal_cliente`:

- competência de controle existe;
- cliente existe ou há política explícita de preservação histórica para cadastro excluído;
- chamada é válida para a competência;
- status é compatível com chamada/movimento;
- `versao_atual` aponta para versão existente quando aplicável;
- `FECHADA` possui snapshot/versionamento correspondente;
- `RETIFICACAO` possui candidato/registro de retificação coerente;
- `ADIADA`/próxima chamada não pertence ao universo liberado da chamada anterior.

## 6. Invariantes — Versões e retificações

- versão base existe;
- numeração de versão é monotônica por cliente + competência;
- somente uma versão é vigente;
- candidato não substitui vigente antes da promoção;
- retificação concluída gera nova versão vigente;
- retificação pendente bloqueia saída;
- snapshot histórico não é apagado por reprocessamento.

## 7. Invariantes — Processamento documental

Cada documento/registro vigente deve manter, quando aplicável:

- arquivo físico/hash correspondente;
- cliente válido ou estado explícito `NÃO_IDENTIFICADO`;
- competência válida ou estado explícito de revisão;
- tipo documental;
- versão vigente/candidato identificável;
- origem/conexão;
- proveniência dos campos críticos.

Não admitir estado ambíguo em que `cliente_id` foi perdido mas o documento continua sendo usado silenciosamente na Conferência.

## 8. Pessoas extraídas

Registros de pessoas extraídas devem apontar para a versão/documento de processamento correspondente.

Ao rejeitar candidato:

- pessoas do candidato não podem contaminar a versão vigente;
- registros candidatos podem permanecer para auditoria, claramente versionados/isolados.

Ao promover:

- conjunto promovido torna-se vigente de forma atômica.

## 9. Obrigações por fonte

Para cada obrigação mensal:

- cliente + competência existem;
- fonte/tipo é válido;
- estado pertence ao vocabulário canônico;
- decisão manual aponta para obrigação específica;
- justificativa possui usuário/data/hora quando necessária;
- `CONFERIDA` possui evidência suficiente segundo sua regra;
- `NAO_APLICAVEL` possui causa/regra explicável;
- obrigação não pode possuir simultaneamente estados finais conflitantes.

## 10. eConsignado

- job aponta para competência;
- escopo de clientes do job é persistido ou reproduzível;
- resultado aponta para job/cliente correto;
- contrato não fica duplicado por retry idempotente;
- retorno residual não cria obrigação final sem cruzamento contextual;
- fotografia anterior válida permanece referenciável.

## 11. Saídas

Cada lote/entrega/saída final deve apontar, direta ou indiretamente, para:

- competência;
- cliente;
- documento(s);
- versão de fechamento que autorizou a saída;
- usuário/job gerador;
- data/hora.

Não deve existir saída final de cliente sem versão FECHADA correspondente, salvo contingência externa explicitamente fora do sistema.

## 12. Auditoria/histórico

Eventos de mutação crítica devem ter entidade identificável.

Verificar eventos órfãos que apontem para IDs inexistentes sem snapshot/nome histórico suficiente para interpretação.

A exclusão cadastral administrativa não pode tornar o histórico incompreensível.

## 13. Arquivo físico x banco

Executar auditoria bidirecional amostral/automatizada:

### Banco -> filesystem

Documento persistido aponta para arquivo existente, salvo estado explícito de arquivo indisponível/legado.

### Filesystem -> banco

Arquivos gerenciados em conexões/acervo que deveriam estar indexados não permanecem indefinidamente invisíveis ao banco sem ocorrência técnica.

Isso é especialmente importante para os casos de guia existente mas não descoberta/vinculada.

## 14. Queries de homologação

Na árvore/schema reconciliados, a suíte deve executar:

```sql
PRAGMA integrity_check;
PRAGMA foreign_key_check;
```

Além de queries próprias para cada invariante lógica.

Resultados precisam constar no relatório da versão.

## 15. Migração

Executar invariantes:

1. antes da migração, na cópia baseline;
2. depois da migração em cópia;
3. depois da instalação no banco operacional, antes da liberação geral.

Comparar contagens relevantes antes/depois e justificar diferenças esperadas.

## 16. Proibição

Não 'corrigir' órfãos automaticamente apagando registros durante migração sem regra de negócio e backup.

Qualquer saneamento deve:

- preservar histórico;
- registrar quantidade;
- explicar causa;
- ter rollback.

## 17. Estado atual

Não foi executado `foreign_key_check` no banco canônico nesta sessão porque o ZIP/banco operacional não está disponível localmente.

Portanto este documento registra uma lacuna de validação e o contrato de homologação, **não a existência de corrupção ou registros órfãos**.
