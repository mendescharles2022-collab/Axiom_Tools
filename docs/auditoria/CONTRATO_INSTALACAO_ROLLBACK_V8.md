# Contrato V8 — Instalação, backup e rollback

Data: 28/08/2026
Status: **contrato de auditoria / homologação pendente no Windows real**

## 1. Fundamento

A V7 foi considerada estável somente depois de instalada no servidor preservando banco, serviços, histórico e retificações. O próprio estado estável anterior também determinou que código V8 não deve ser considerado concluído sem validação integrada e pacote instalável com rollback.

A V8, portanto, não pode ter critério de atualização inferior ao da V7.

## 2. Princípio

Atualização de aplicação e migração de dados são operações distintas.

O instalador pode substituir código controladamente, mas não pode tratar banco, documentos físicos, configurações operacionais e histórico como payload descartável.

## 3. Inventário mínimo pré-instalação

Antes de alterar qualquer arquivo, o instalador deve registrar:

- versão instalada;
- versão alvo;
- raiz da aplicação;
- raiz de dados permanente;
- caminho do SQLite vigente;
- tamanho e hash do banco copiado para backup;
- versão/schema do banco quando disponível;
- serviços/processos do Axiom Tools;
- portas esperadas;
- configurações locais preservadas;
- data/hora da operação.

## 4. Backup obrigatório

Backup prévio deve incluir, no mínimo:

- banco SQLite;
- configurações locais que não estejam dentro do payload versionado;
- arquivos de estado necessários para inicialização;
- código da versão instalada suficiente para rollback;
- manifesto da atualização.

Documentos reais do escritório não devem ser recopiados em massa pelo instalador quando já vivem em repositório permanente externo à aplicação; devem apenas permanecer intocados.

## 5. Migração segura do SQLite

A migração deve ocorrer antes de liberar a nova versão para operação normal.

Regras:

1. testar migração em cópia do banco sempre que tecnicamente possível;
2. validar `PRAGMA integrity_check` na cópia migrada;
3. validar tabelas/índices essenciais;
4. executar invariantes de negócio mínimas;
5. só então migrar o banco operacional;
6. manter possibilidade de restauração do backup prévio.

Migração não pode depender do utilitário externo `sqlite3`; o módulo nativo `sqlite3` do Python é suficiente e é o caminho preferido para validações automatizadas no Windows.

## 6. Serviços e locks

Antes de substituir arquivos ou migrar banco:

- impedir novas mutações de negócio;
- encerrar/pausar workers de processamento;
- garantir que não haja transação ativa relevante;
- fechar conexões do processo que possam manter lock no SQLite;
- validar portas/processos relacionados.

Um backend parado visualmente não é prova suficiente de que todos os handles de banco foram liberados.

## 7. Ordem de atualização

Fluxo esperado:

`pré-checagem -> bloquear operação -> backup -> testar migração em cópia -> aplicar código -> migrar banco operacional -> smoke local -> iniciar serviços -> health checks -> regressão crítica -> liberar operação`

## 8. Critérios de smoke

No mínimo:

- backend inicia;
- gateway inicia;
- login abre;
- sessão funciona;
- Dashboard abre;
- Fechamento Mensal abre sem mutar dados;
- Processamento abre na competência ativa;
- Conferência abre em modo somente leitura;
- acesso a Clientes funciona;
- banco responde `integrity_check=ok`;
- nenhuma migração fica pendente silenciosamente.

## 9. Critérios de rollback

Rollback deve ser possível quando ocorrer, antes da liberação operacional:

- falha de inicialização;
- migração incompleta;
- integrity check inválido;
- regressão crítica nos fluxos mensais;
- incompatibilidade de schema;
- falha de gate de saída;
- falha de autenticação/sessão;
- perda de vínculo documental.

O rollback deve restaurar código, banco e configurações compatíveis como um conjunto coerente. Não é aceitável rebaixar apenas o código deixando schema incompatível.

## 10. Proibições

- substituir o banco por um banco vazio do pacote;
- apagar banco antigo depois de migração sem retenção de backup;
- copiar árvore de dados sobre a pasta permanente sem comparação;
- considerar `porta respondeu` como homologação funcional;
- remover backup antes de concluir regressão do pacote instalado;
- gerar pacote final a partir de árvore de código diferente da árvore testada.

## 11. Regressão obrigatória pós-instalação

Além do smoke:

- abrir competência existente sem alterar contagens;
- preservar estados FECHADA/PRONTA/RETIFICACAO/ADIADA;
- preservar histórico e versões;
- preservar documentos e hashes;
- preservar decisões manuais e ocorrências;
- preservar configurações de clientes;
- preservar eConsignado já consultado;
- preservar configuração de caminhos/conexões;
- executar amostra da matriz dos 28 casos antes da liberação total.

## 12. Critério de homologação

A V8 somente pode ser declarada instalável quando o mesmo código-fonte:

1. gerar o pacote;
2. passar pela migração em cópia realista;
3. instalar no Windows alvo;
4. iniciar serviços;
5. preservar dados;
6. passar smoke e regressões críticas;
7. comprovar rollback executável.
