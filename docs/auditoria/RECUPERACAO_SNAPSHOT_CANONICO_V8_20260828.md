# Recuperação do snapshot canônico V8 — 28/08/2026

## Fonte

Arquivo informado como último ZIP operacional produzido antes de qualquer alteração posterior:

`Axiom_Tools(20260828-175237).zip`

SHA-256 do ZIP:

`2b1aa80853df8597a618141f7e536e0c324ffa5dea2ea22ed026cee021fa546a`

## Diagnóstico físico do ZIP

O arquivo contém um deslocamento/concatenação interna de `301.989.888` bytes entre parte dos headers locais e o diretório central.

Consequência: leitores ZIP convencionais conseguem abrir algumas entradas e falham em outras com erro de offset/header, embora os dados da aplicação permaneçam presentes.

O diretório central final registra 20.671 entradas. A árvore operacional atual `Axiom_Tools/app/` possui 674 entradas de arquivo.

## Recuperação da árvore operacional

Foi executada recuperação determinística por entrada:

1. localizar o offset original do header local;
2. conferir assinatura `PK\x03\x04`;
3. validar o nome local contra o nome do diretório central;
4. ler o payload comprimido pelo tamanho registrado;
5. descomprimir pelo método ZIP correspondente;
6. validar tamanho final e CRC32 contra o diretório central.

Resultado:

- 674/674 arquivos da árvore `Axiom_Tools/app/` recuperados;
- 0 falhas de header local após uso do offset original;
- 0 divergências de nome;
- 0 falhas de descompressão;
- 0 divergências de tamanho;
- 0 divergências de CRC32.

## Validação do código recuperado

A árvore Python recuperada em `app/src/axiom_tools` passou por compilação sintática integral com `compileall`.

Resultado: `COMPILE_OK`.

## Banco operacional associado

Entrada:

`Axiom_Tools/data/axiom_tools.db`

Tamanho: `30.441.472` bytes.

SHA-256:

`0ede9452365f03b391f655d943ab56c5ac11f404f5f07784f0a8da159c052e04`

Validação somente leitura:

- `PRAGMA integrity_check` = `ok`;
- `PRAGMA foreign_key_check` = 0 violações;
- 66 tabelas encontradas.

O banco permanece fora do GitHub e é tratado apenas como evidência operacional do snapshot.

## Relação com V8F2

O mesmo ZIP contém `temp/V8F2_CONSOLIDADO/payload/app/`.

Nos 14 arquivos presentes nesse payload:

- todos os arquivos-fonte coincidem byte a byte com a raiz operacional recuperada;
- as únicas diferenças são cinco arquivos `.pyc`, que são artefatos compilados e não fonte canônica.

Isso reforça que a raiz recuperada corresponde à implementação final daquela sequência e não a uma versão anterior ao V8F2.

## Seleção para versionamento

Para reconciliação com o GitHub foram selecionados 432 arquivos controláveis da aplicação, totalizando 5.847.366 bytes.

Excluídos deliberadamente:

- `app/downloads/**` com pacotes históricos;
- `__pycache__` e `.pyc`;
- evidências visuais binárias históricas em `app/docs/reports/evidencias_visuais_axt002/`;
- todo `data/**`;
- certificados, credenciais, secrets, usuários, PDFs operacionais, logs, backups e temporários.

Assets binários necessários ao runtime dentro de `src/` serão reconciliados separadamente com hash e origem controlada.

## Impacto no B06

Antes desta recuperação, B06 estava `BLOQUEADO_POR_RUNTIME` porque a árvore operacional completa não estava disponível no `main`.

Com este snapshot:

- a árvore operacional foi recuperada integralmente;
- o banco foi identificado e validado;
- o runtime-fonte necessário à reconciliação está disponível;
- o `main` continua sem a pasta `app/`, portanto a reconciliação ainda precisa ser materializada antes da homologação.

Novo enquadramento correto do B06: `EM_CORRECAO` — runtime recuperado, reconciliação com o GitHub em andamento.

## Regra de segurança

A recuperação deste ZIP não autoriza, por si só:

- marcar B06 como homologado;
- promover V8 a release final;
- executar migração no banco real;
- publicar dados operacionais no GitHub.

O próximo passo é reconciliar a árvore controlada em branch própria, executar a suíte operacional recuperada, comparar com a auditoria canônica e somente depois promover mudanças ao `main`.
