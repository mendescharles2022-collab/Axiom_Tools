# Axiom Tools — Lacunas, Contradições e Plano de Preservação

Data: 23/09/2026

## 1. Por que este documento existe

O histórico do Axiom Tools está dividido entre:

- chats;
- GitHub;
- branches;
- ZIPs;
- instalação Windows;
- SQLite;
- pastas reais;
- logs;
- backups;
- screenshots;
- instaladores/patches.

Nenhuma dessas fontes isoladamente contém “tudo”.

## 2. Lacuna principal: código operacional

**CONFIRMADO**

A main é fortemente documental e possui tooling de auditoria, mas src/axiom_tools não contém a árvore completa do runtime operacional que existiu no servidor.

Portanto:

- regras recuperadas dos chats precisam ser preservadas;
- runtime físico ainda é fonte necessária;
- migrar apenas o src atual perderia funcionalidade.

## 3. Divergência de branches

**CONFIRMADO**

main e audit-v8-runtime-reconciliation divergem.

Há commits exclusivos dos dois lados.

Consequência:

inventário precisa considerar:

- merge-base;
- arquivos só da main;
- arquivos só da auditoria;
- versões diferentes do mesmo documento/script.

Não “resolver” divergência por merge automático destrutivo.

## 4. V8

**CONFIRMADO**

V8:

- contém documentação e tooling úteis;
- contém contratos e regressões;
- não foi homologada;
- não pode substituir V5.6.14V7 como referência estável conhecida;
- não pode ser copiada inteira para outro produto como “versão final”.

## 5. Versões intermediárias

**LACUNA**

Muitas correções foram aplicadas por pacotes locais V5.6.14x.

Nem todo pacote/arquivo aparece pelo nome no Git.

Exemplo: determinados instaladores e patches de Upload/Processamento foram executados fisicamente e podem existir apenas em backups/temp/Downloads.

A futura coleta precisa buscar:

- ZIPs;
- PS1;
- backups;
- temp;
- app antigo;
- logs de instalação;
- nomes de versões.

## 6. Grafia

**LACUNA PARCIAL**

O histórico confirma motor/estrutura de exceções de grafia, mas a main atual não demonstra integralmente a implementação operacional original.

Necessário recuperar do runtime/backups:

- tabela/arquivo de exceções;
- algoritmo de capitalização;
- sanitização;
- regras de partículas;
- siglas;
- integrações que chamavam o motor;
- efeitos sobre nomes de pasta.

Até essa coleta, não reescrever o motor do zero afirmando equivalência.

## 7. Arquivo Digital

**LACUNA PARCIAL**

A estrutura DEC-002 está documentada.

Porém, a operação posterior criou:

- roots de entrada;
- repositório de processados;
- saída;
- vínculos cliente↔pasta;
- indexação;
- reconciliação;
- possível organização adicional por perfil/competência.

A árvore real precisa ser inventariada recursivamente para saber o que existia de fato.

## 8. Banco

**PENDENTE DE PROVA FÍSICA**

O SQLite operacional não deve ser enviado ao Git.

Para auditoria/migração:

- clonar;
- gerar schema;
- contagens;
- índices;
- triggers;
- migrations;
- relações;
- amostras anonimizadas quando necessárias;
- manifesto/hash.

Nunca importar banco legado diretamente num sistema novo.

## 9. Documentos reais

**FORA DO GIT POR DESIGN**

Não devem ser versionados:

- documentos de clientes;
- PDFs reais;
- certificados;
- credenciais;
- tokens;
- dados pessoais desnecessários;
- caches sensíveis.

Mas a estrutura, metadados e regras de manipulação precisam ser documentadas.

## 10. Logs

**LACUNA**

Logs locais podem conter:

- erros de parser;
- caminhos;
- versões;
- comportamento real;
- sequência de instalação;
- falhas de runtime.

Devem ser auditados com cuidado, removendo/evitando segredos antes de qualquer consolidação no Git.

## 11. UX

**LACUNA PARCIAL**

Conversas preservam decisões de UX que não necessariamente estão nos templates atuais da main.

Antes de redesenhar outro produto, recuperar:

- screenshots históricas;
- templates do runtime;
- CSS/JS válidos;
- críticas do usuário;
- fluxos que foram aceitos/rejeitados.

Não usar tela da V8 como canônico apenas porque é mais recente.

## 12. Motores

**LACUNA CRÍTICA**

É necessário localizar implementações reais de:

- Domínio;
- eSocial;
- e-CAC/DARF;
- FGTS Digital;
- DAE;
- eConsignado;
- Identidade;
- Competência;
- Valores;
- Pessoas;
- cruzamento.

A documentação preserva regras, mas parser real pode conter heurísticas, regexes e tratamentos que ainda não estão inventariados.

## 13. Casos reais

**PATRIMÔNIO OBRIGATÓRIO**

Os casos de agosto/2026 não devem ser reduzidos a nomes.

Cada caso deve, quando os dados seguros estiverem disponíveis, manter:

- cenário;
- fontes;
- resultado esperado;
- falha observada;
- causa;
- regra criada;
- teste de regressão.

Sem isso, o próximo sistema repete os mesmos erros.

## 14. Contradições conhecidas

### Documentação inicial × operação posterior
Sprints AXT-001–008 descrevem evolução inicial. O runtime posterior acumulou módulos/fluxos além delas.

### Estrutura DEC-002 × Storage evoluído
DEC-002 é árvore canônica histórica; classificação posterior por perfil é evolução. Não são necessariamente equivalentes 1:1.

### V8 × versões homologadas
V8 é mais recente, mas não é mais autoritativa.

### Main × runtime
Main é rastreável; runtime é operacional. Nenhum substitui automaticamente o outro.

### Status técnico × status operacional
PROCESSADO/100% não equivale a CONFERIDO/FECHADO.

## 15. Coleta física ainda necessária

Quando houver acesso à instalação/backup completo, coletar em modo somente leitura:

1. inventário da árvore da aplicação;
2. hashes;
3. versões;
4. scripts/PS1;
5. config;
6. parsers;
7. templates/static;
8. schema SQLite;
9. contagens e índices;
10. roots configuradas;
11. inventário do arquivo digital sem copiar conteúdo sensível;
12. regras de grafia;
13. logs relevantes;
14. backups/ZIPs históricos;
15. tarefas Windows e comandos;
16. dependências Python;
17. manifests;
18. testes locais.

## 16. Classificação de cada artefato

Para cada item recuperado:

- preservar;
- incorporar;
- reescrever;
- referenciar;
- arquivar;
- descartar com justificativa.

Nunca descartar por “parecer antigo”.

## 17. Regra para Essence/Enterprise

Este patrimônio deve servir de entrada para análise.

Não significa transportar a arquitetura antiga inteira.

O destino deve:

- preservar regra de negócio válida;
- preservar casos de regressão;
- reutilizar estruturas/motores quando tecnicamente saudáveis;
- corrigir acoplamentos;
- adaptar ao canônico atual de UX/segurança;
- migrar dados com dry-run;
- manter evidência de origem.

## 18. Definição de “migração completa”

Só declarar completa quando houver:

- regra mapeada;
- código/implementação ou decisão de reescrita;
- dados migrados/conciliados;
- filesystem reconciliado;
- casos reais passando;
- outputs conferidos;
- rollback;
- operação independente do Tools antigo.

## 19. Regra final

O maior risco não é carregar “coisa velha”.

O maior risco é apagar uma regra operacional que nasceu de uma falha real e só descobrir sua importância no fechamento seguinte.

Por isso, em dúvida:

**preservar primeiro, classificar depois, implementar por último.**
