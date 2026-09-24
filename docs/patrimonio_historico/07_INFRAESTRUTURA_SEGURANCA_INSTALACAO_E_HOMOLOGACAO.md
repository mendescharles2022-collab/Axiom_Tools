# Axiom Tools — Infraestrutura, Segurança, Instalação e Homologação

Data: 23/09/2026

## 1. Ambiente operacional histórico

**IMPLEMENTAÇÃO OBSERVADA / HOMOLOGADO EM ETAPAS**

Instalação histórica principal:

    E:\Programas\Axiom_Tools

Componentes observados:

- backend interno;
- gateway;
- app;
- data;
- scripts;
- backups;
- SQLite;
- tarefas/serviços Windows em fases do projeto.

Portas históricas:

- backend: 5201;
- gateway: 5200.

O gateway foi usado para acesso na rede enquanto backend permanecia interno.

## 2. Tarefas Windows

**IMPLEMENTAÇÃO OBSERVADA**

Nomes usados:

- Axiom Tools Backend;
- Axiom Tools Gateway.

Em uma fase, scripts iniciavam as tarefas.  
Em outra, houve falha de Register-ScheduledTask por acesso negado e foi adotado modo direto sem recriar a tarefa.

Lição permanente:

**não assumir que a tarefa agendada aponta para a instalação correta.**

Foi detectado risco de tarefa antiga carregar outro runtime/caminho.

## 3. Data dir

**IMPLEMENTAÇÃO OBSERVADA**

Houve configuração explícita de data-dir dentro da instalação, com dados separados do código.

Princípio permanente:

- código pode ser substituído/atualizado;
- dados operacionais, banco e acervo não podem depender da pasta descartável do build.

## 4. SQLite

**DECISÃO HISTÓRICA APROVADA**

Regras recuperadas:

- persistência local;
- WAL quando apropriado;
- proteção de concorrência;
- migrations aditivas;
- backup consistente;
- integrity_check;
- foreign_key_check quando aplicável;
- comparação de contagens antes/depois;
- nunca substituir banco real por banco “novo vazio” durante upgrade.

Banco não é o arquivo documental; arquivos ficam no filesystem e banco guarda índice/estado/metadados.

## 5. Atualização segura

**DECISÃO HISTÓRICA APROVADA**

Antes de upgrade:

- backup integral de app/config necessários;
- backup/clonagem consistente do banco;
- preservar documentos/certificados/configurações;
- registrar versão;
- validar origem/destino.

Depois:

- migrations;
- validação de saúde;
- contagens;
- testes;
- verificação de serviços/portas;
- rollback se falhar.

Nenhuma atualização deve apagar acervo físico.

## 6. Pacotes/instaladores

**HISTÓRICO OPERACIONAL**

O projeto utilizou:

- ZIPs de atualização;
- instaladores PowerShell;
- patches menores;
- validações após aplicação;
- backups automáticos com timestamp.

A preferência operacional consolidada foi **um pacote claro por atualização**, contendo payload, instalador e validação, evitando sequência confusa de remendos.

## 7. Segurança documental

**CANÔNICO**

Proibido no fluxo automático normal:

- deletar original;
- sobrescrever arquivo existente sem regra;
- renomear/mover legado apenas por estética;
- destruir pasta ao excluir cadastro;
- limpar evidência de auditoria;
- apagar versão anterior de retificação.

Conflito bloqueia somente a ação incompatível e preserva conteúdo.

## 8. Segurança de portais

**CANÔNICO**

Não:

- contornar CAPTCHA;
- burlar MFA;
- armazenar segredo de forma insegura;
- simular confirmação humana;
- executar ação governamental clandestina.

Sim:

- abrir portal;
- auxiliar navegação;
- receber download;
- indexar;
- comparar;
- registrar evidência;
- retomar pipeline local.

## 9. Usuários e auditoria

**DECISÃO HISTÓRICA APROVADA**

Operação em servidor/navegador deve utilizar usuários individuais e rastreabilidade.

Eventos relevantes precisam registrar, conforme aplicável:

- usuário;
- data/hora;
- operação;
- módulo;
- objeto afetado;
- resultado;
- contexto/IP quando disponível.

Não guardar senha em texto.

## 10. Uploads

**DECISÃO HISTÓRICA APROVADA**

Uploads/importações precisam validar:

- extensão;
- tipo;
- tamanho;
- integridade;
- hash;
- associação;
- duplicidade.

Falha de validação não pode resultar em perda do arquivo original.

## 11. Backup e rollback

**DECISÃO HISTÓRICA APROVADA**

Rollback não pode ser “resetar tudo”.

Deve restaurar:

- aplicação/versão;
- banco;
- configuração necessária;

sem destruir arquivos que foram preservados.

Toda alteração estrutural relevante precisa ter caminho de retorno comprovável.

## 12. Main ≠ runtime

**CANÔNICO ATUAL**

A main não espelha integralmente o runtime operacional histórico.

O próprio README do repositório registra essa limitação.

Consequências:

- código da main sozinho não prova funcionamento;
- docs sozinhos não provam implementação;
- testes do tooling não provam runtime corrigido;
- migração exige reconciliação.

## 13. Branch de auditoria

**FATO DO REPOSITÓRIO**

Existe branch:

    audit-v8-runtime-reconciliation

Ela diverge da main.

Portanto, inventário futuro precisa inspecionar as duas e o merge-base, não apenas main.

## 14. B06 — reconciliação runtime↔GitHub

**PROVISÓRIO V8 / TOOLING VALIOSO**

A auditoria produziu cadeia segura para:

- exportar runtime por whitelist;
- manter origem read-only;
- clonar SQLite;
- gerar hashes;
- consumir em staging;
- comparar runtime↔repo;
- produzir plano;
- exigir revisão humana;
- aceitar baseline;
- materializar staging isolado;
- verificar novamente o staging.

Esse desenho é patrimônio reutilizável mesmo sem a V8 ter sido homologada.

## 15. B01–B50

**PROVISÓRIO V8 / REGRESSÃO**

O rastreador final registrou:

- 46 itens em correção;
- 4 bloqueados por runtime físico;
- 0 corrigidos homologados.

Bloqueados pelo runtime físico:

- B05;
- B06;
- B45;
- B49.

Logo, não existe base para afirmar que “a V8 ficou pronta”.

## 16. Casos C01–C28

**PROVISÓRIO V8 / PATRIMÔNIO DE TESTE**

Foram mapeados 28 casos reais de agosto/2026 para bloqueadores.

Regra:

um caso só pode passar quando os bloqueadores associados estiverem efetivamente corrigidos na árvore operacional reconciliada.

## 17. Homologação

**DECISÃO HISTÓRICA APROVADA**

Critério de qualidade não é “instalou sem erro”.

Homologação precisa combinar:

- runtime correto;
- banco correto;
- migrations;
- testes;
- regressões reais;
- estado do filesystem;
- segurança;
- benchmark quando relevante;
- build identificável;
- backup;
- rollback;
- operação Windows.

## 18. Gate final V8

**PROVISÓRIO V8**

O gate formal exigia cumulativamente:

- 50/50 bloqueadores homologados;
- 28/28 casos PASS;
- release READY;
- build verificável;
- evidências externas.

Isso nunca foi atingido.

## 19. Integridade banco↔filesystem

**DECISÃO HISTÓRICA APROVADA / PENDENTE DE PROVA FÍSICA**

Auditoria de snapshot encontrou milhares de registros com caminho/hash coerentes, mas raízes reais estavam fora do ZIP.

Portanto:

- metadado coerente não comprova arquivo existente;
- hash armazenado não comprova hash físico sem ler o arquivo;
- reconciliação precisa montar/acessar a raiz real.

## 20. Performance

**DECISÃO HISTÓRICA APROVADA**

Benchmark deve usar volume representativo da operação, não banco minúsculo artificial.

O objetivo é validar:

- consultas;
- paginação;
- lotes;
- workers;
- concorrência;
- uso de memória;
- throughput.

## 21. Regra de preservação

O Axiom Tools é patrimônio técnico e operacional.

Mesmo que outro sistema assuma suas funções, não arquivar/apagar o legado antes de:

- inventário completo;
- migração rastreável;
- regressão;
- independência do runtime;
- backup histórico final.
