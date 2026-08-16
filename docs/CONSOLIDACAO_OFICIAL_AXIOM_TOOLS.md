# Axiom Tools — Consolidação Oficial do Projeto

Versão: 1.0  
Data de consolidação: 16/08/2026  
Status: Documento mestre permanente

## 1. Finalidade

O Axiom Tools é uma aplicação utilitária independente do Ecossistema Axiom destinada a automatizar e organizar rotinas locais de arquivos do escritório, com foco em estrutura de pastas de clientes, documentos de Departamento Pessoal, OCR, classificação, competências, conferência, impressão em lote e integrações assistidas com portais externos.

O projeto evolui ferramentas e rotinas anteriormente executadas por arquivos BAT para uma aplicação estruturada, auditável, configurável e segura.

## 2. Princípio central

O Axiom Tools trabalha sobre documentos reais do escritório. Por isso, segurança documental prevalece sobre conveniência.

Regras permanentes:

1. Arquivos originais não serão excluídos automaticamente.
2. Arquivos existentes não serão sobrescritos silenciosamente.
3. A exclusão ou inativação de um cliente no cadastro interno não poderá excluir sua pasta física nem seus documentos.
4. Toda movimentação automatizada deverá ser rastreável.
5. Classificações por OCR deverão permitir conferência humana.
6. Operações de baixa confiança deverão ir para revisão, e não para decisão destrutiva.
7. A grafia legal/original do cliente deverá ser preservada no dado cadastrado; normalizações visuais não poderão destruir a informação original.
8. Portais governamentais continuarão sob controle humano nas etapas de autenticação, CAPTCHA, confirmação e demais ações críticas.

## 3. Escopo funcional consolidado

### 3.1 Clientes

O sistema deverá manter cadastro interno de clientes PF e PJ, identificados por CPF ou CNPJ.

O cadastro servirá como índice para localizar pastas, reconhecer documentos e executar rotinas em lote.

Deverá existir:

- inclusão manual;
- importação de relação de clientes por planilha;
- busca por nome e documento;
- edição;
- inativação/reativação;
- exclusão cadastral controlada quando necessária para limpeza da lista importada;
- prevenção de duplicidade por documento;
- associação do cliente ao caminho físico correspondente;
- status operacional, sem uso do status para apagar automaticamente arquivos.

A lista importada pode conter clientes que já saíram do escritório ou foram baixados. O usuário deverá poder tratar esses casos dentro do Axiom Tools sem precisar corrigir previamente a planilha de origem.

### 3.2 Estrutura de pastas

O sistema deverá criar, conferir e atualizar estruturas padronizadas de pastas para PF e PJ, respeitando diferenças entre os dois tipos de cliente.

A atualização de uma estrutura existente deverá criar somente o que estiver ausente e preservar todo conteúdo já existente.

O sistema deverá reconhecer estruturas legadas produzidas pelos BATs anteriores e evoluí-las sem destruição.

### 3.3 Funcionários

Dentro de cada cliente, o Axiom Tools deverá administrar a estrutura de funcionários/empregados.

Deverá suportar:

- localização tanto de `Funcionários` quanto de estruturas legadas equivalentes;
- criação de pasta individual do empregado;
- documentos pessoais;
- documentos escaneados;
- documentos gerados;
- rescisão;
- preservação de pastas legadas adicionais, como exames, quando já existentes;
- identificação do empregado demitido sem perda do histórico documental.

### 3.4 OCR e classificação documental

O Axiom Tools deverá possuir uma área de entrada para documentos a classificar.

O motor deverá evoluir para reconhecer, entre outros:

- DARF/DCTFWeb;
- FGTS Digital;
- contracheques;
- pró-labore;
- documentos sem movimento, quando identificáveis;
- documentos relacionados a contratos e alterações, conforme regras futuras da classificação.

A classificação deverá buscar cliente, tipo documental e competência, renomear de forma padronizada e encaminhar uma cópia/versão gerenciada ao destino adequado, mantendo o original conforme a política de segurança.

### 3.5 Competências

Os documentos mensais deverão poder ser organizados por competência, com caminhos configuráveis e estrutura de ano/mês ou mês/ano definida pelo sistema.

Exemplo conceitual: `Agosto/2026`.

O reconhecimento de competência deverá ser validável antes de movimentações em lote.

### 3.6 Conferência

O sistema deverá oferecer rotinas de conferência antes da impressão ou consolidação, permitindo identificar:

- documentos encontrados;
- documentos faltantes;
- documentos sem cliente reconhecido;
- documentos sem competência reconhecida;
- classificações de baixa confiança;
- clientes sem movimento, quando aplicável;
- divergências entre documentos esperados e encontrados.

### 3.7 Impressão em lote

O Axiom Tools deverá permitir impressão e preparação de lotes em ordem alfabética A–Z.

Deverá suportar:

- impressão agrupada por empresa;
- agrupamento de DARF + FGTS quando solicitado;
- impressão por tipo documental separadamente;
- geração de arquivo único consolidado ou múltiplos arquivos;
- conferência antes da impressão.

### 3.8 Integrações assistidas

O projeto poderá abrir portais e páginas externas para apoiar o usuário, inclusive eCAC, eSocial e Sintegra/SEFAZ GO.

O fluxo esperado é assistido:

1. abrir o portal no navegador;
2. usuário realiza autenticação e ações obrigatórias;
3. documento é baixado/salvo;
4. Axiom Tools recebe o arquivo na pasta configurada;
5. OCR e classificação continuam o fluxo local.

O sistema não deverá tentar contornar CAPTCHA, autenticação forte ou outras proteções.

### 3.9 PDF

O projeto deverá evoluir para:

- visualizar PDFs;
- receber PDFs em uma área de entrada;
- identificar e classificar PDFs;
- salvar em PDF conteúdo externo quando tecnicamente permitido;
- consolidar documentos para conferência/impressão;
- manter os originais preservados.

### 3.10 Configurações

Caminhos operacionais deverão ser configuráveis, incluindo, conforme a implantação:

- base de clientes;
- contratos e alterações;
- movimentações mensais;
- DARF;
- FGTS;
- contracheques;
- pró-labore;
- conferência;
- entrada de OCR;
- saídas temporárias e consolidadas.

Nenhum caminho crítico deverá ficar espalhado de forma rígida pelo código.

## 4. Dados e persistência

O Axiom Tools deverá possuir persistência própria para cadastro/indexação de clientes, configurações, histórico operacional e informações necessárias ao funcionamento local.

A persistência não substitui os arquivos físicos: ela referencia e organiza o acervo existente.

## 5. Arquitetura funcional

O projeto será modular. Os domínios principais são:

- `core`: infraestrutura comum;
- `folders`: estrutura e manutenção de pastas;
- `ocr`: reconhecimento e classificação;
- `printing`: conferência, consolidação e impressão;
- `integrations`: portais e integrações assistidas;
- `settings`: configurações;
- `utils`: utilitários compartilhados.

A implementação deverá continuar fracionada em arquivos pequenos e responsabilidades claras, evitando arquivos monolíticos.

## 6. Fora de escopo ou restrições

Não fazem parte do comportamento automático seguro:

- apagar pastas de clientes porque um cadastro foi excluído;
- excluir arquivos originais após OCR;
- sobrescrever documentos silenciosamente;
- realizar autenticação governamental em nome do usuário de forma clandestina;
- contornar CAPTCHA;
- executar ações críticas em portais sem controle do usuário.

## 7. Roadmap recuperado

A construção foi organizada conceitualmente nas seguintes etapas:

- AXT-000 — Fundação;
- AXT-001 — Núcleo de clientes, importação e configurações;
- AXT-002 — Estrutura de pastas PF/PJ e funcionários;
- AXT-003 — OCR e classificação documental;
- AXT-004 — Competências e roteamento;
- AXT-005 — Conferências;
- AXT-006 — Impressão e consolidação em lote.

Integrações assistidas, visualização de PDF, auditoria e refinamentos de segurança são capacidades transversais e deverão ser introduzidas nas Sprints correspondentes sem quebrar os princípios permanentes deste documento.

## 8. Regra de precedência

Este documento consolida as decisões recuperadas do histórico do projeto e passa a ser referência oficial do repositório.

Quando uma Sprint futura detalhar uma funcionalidade, ela poderá evoluir a implementação, mas não deverá violar as regras permanentes de preservação documental, rastreabilidade e controle humano sem uma decisão formal registrada em `docs/decisions/`.
