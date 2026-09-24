# Axiom Tools — Linha do Tempo Recuperada dos Chats

Data de consolidação: 23/09/2026

## Nota de método

Esta linha do tempo registra marcos recuperados das conversas do projeto.  
Quando uma conversa e um canônico posterior divergem, a divergência é preservada em vez de “corrigida retroativamente”.

Isso é importante porque o histórico do Tools passou por reinícios documentais, versões locais, patches e uma auditoria que depois concluiu que GitHub e runtime não eram espelhos integrais.

## 16/08/2026 — fundação/reorganização formal

O repositório Axiom_Tools foi estruturado formalmente com:

- Python 3.12;
- arquitetura modular;
- segurança documental;
- não destruição;
- rastreabilidade;
- decisões DEC-001–005;
- roadmap AXT-000–AXT-008.

Uma memória de conversa do próprio dia registra AXT-001 com 120/120 testes, AXT-002 homologada e máscaras com 73/73 testes.

Porém, os documentos canônicos atualmente presentes no repositório, também datados de 16/08, declaram reinício da implementação funcional da AXT-001 “do zero”.

**Classificação:** CONTRADIÇÃO HISTÓRICA PRESERVADA.

Interpretação segura:

- existiu implementação/testagem anterior;
- depois houve decisão formal de não usá-la automaticamente como base;
- o patrimônio anterior não deve ser apagado, mas não deve ser tratado como baseline sem recuperar a árvore correspondente.

## 17/08/2026 — filesystem, documentos e instalação Windows

As conversas aprofundaram:

- configuração de roots físicos;
- separação entre “caminho base” e “estrutura interna”;
- indexação de PDFs;
- versões Original/Retificada;
- impressão em lote;
- infraestrutura Windows;
- backend 5201;
- gateway 5200;
- instalação em E:\Programas\Axiom_Tools;
- usuários individuais;
- SQLite;
- backup/rollback;
- acesso pela rede.

Também amadureceu a ideia de que PDFs físicos ficam fora do banco e são indexados.

## 18/08/2026 — estrutura por perfil e entregas

Marcos:

- MEI com DAE específico;
- doméstico com DAE;
- preservação de cadastro e documentos em upgrades;
- fluxo Simular → Revisar → Confirmar → Aplicar para pastas;
- regras de entrega presencial/office-boy versus eletrônica;
- possibilidade de PDF/ZIP/arquivos individuais;
- “Ignorar” como ação padronizada em conciliações/itens protegidos.

## 19–20/08/2026 — Central Documental e motores

As conversas passaram a exigir:

- leitura recursiva de arquivos em pastas vinculadas;
- busca, filtros, paginação e preview;
- upload múltiplo/drag-and-drop;
- painel lateral de PDF;
- Motor Domínio;
- leitura nativa antes de OCR;
- persistência de tipo/parser/dados/confiança/hash/texto;
- separação entre motor e tela;
- Motor de Conferência cruzando fontes.

## 21/08/2026 — arquitetura de escala

Foi consolidada a arquitetura de processamento:

    Domínio → eSocial → e-CAC/DARF → FGTS Digital → cruzamento incremental

Requisitos:

- triador/orquestrador;
- quatro motores especialistas;
- especialistas internos de Identidade, Competência, Valores, Pessoas, Dados Operacionais, eConsignado e Validação;
- processamento em lotes;
- assíncrono/incremental;
- idempotente;
- hash/cache/checkpoint;
- OCR fallback único;
- conteúdo lido reutilizado;
- calendário de competência 25→09;
- exceções para dezembro/13º.

Também foram detalhadas fila e sessão PROC.

## 24/08/2026 — identidade e revisão

Ajustes de identificação:

- CPF/CNPJ explícito como prioridade;
- impedir falso CNPJ derivado de código de barras;
- vincular CLIENTE_NAO_IDENTIFICADO sem reler/OCR;
- persistir vínculo;
- não criar nova sessão desnecessariamente apenas para corrigir associação.

## 25/08/2026 — saídas e entregas

A operação foi dividida em:

- Central de Entregas;
- Centro de Impressão.

Regras:

- clientes físicos versus eletrônicos;
- pasta de saída cliente→ano→mês;
- DARF/FGTS separados ou unificados conforme parâmetro;
- contracheques/pró-labore agrupáveis;
- documentos prontos somente após gate.

## 26–27/08/2026 — reformulação Fechamento × Processamento × Conferência

Esse foi um dos maiores marcos funcionais.

Decisão:

### Fechamento
Abre competência e acompanha.

### Processamento
Recebe/processa/reprocessa.

### Conferência
Resolve ausência/divergência/justificativa/anexo/reprocessamento.

A competência passa a ser aberta uma única vez.

Foram definidos:

- composição mensal;
- chamadas sucessivas;
- sem movimento;
- estados coerentes;
- fechamento automático;
- retificação;
- ações dentro da própria ocorrência;
- múltiplas guias de FGTS;
- regra MEI/DAE;
- semântica de 100% técnico.

## 27–28/08/2026 — casos reais e início da auditoria forte

Casos reais passaram a dirigir o desenho:

- afastamento integral;
- procuração revogada;
- rescisões;
- consignados/garantias;
- reprocessamento que não incorporou nova evidência;
- cliente indevidamente na chamada errada;
- faltas integrais;
- rural com múltiplas matrículas;
- diretor/pró-labore confundido com empregado.

Foi formalizada a regra rural de DARF consolidada versus FGTS aditivo por matrícula.

A V8 passa a ser tratada como não homologada.

## 28–31/08/2026 — auditoria V8 e reconciliação

A auditoria cresceu para:

- B01–B50;
- casos C01–C28;
- contratos de reprocessamento;
- GET puro;
- gate único de saída;
- estados;
- composição;
- identidade;
- eConsignado;
- parser Domínio;
- banco;
- segurança;
- monitor;
- Sintegra;
- retenção;
- filesystem;
- benchmark.

Etapas chegaram a 84.

Conclusão mais importante:

**o runtime Windows real ainda não estava reconciliado integralmente com o GitHub.**

## 04–05/09/2026 — handoff para Enterprise

Foi decidido distribuir o patrimônio do Tools pelos domínios do Enterprise, e não criar Tools 2.0 monolítico.

O repositório Axiom_Tools passou a ser explicitamente preservado como origem histórica/técnica/auditável.

Referência estável conhecida permaneceu V5.6.14V7.  
V8 permaneceu não homologada.

## 08/09/2026 — auditoria patrimonial orientada pelo uso real

O usuário reforçou:

- não usar V8 como baseline;
- procurar todas as versões, documentos, código, logs, bancos, backups e históricos;
- priorizar falhas reais;
- auditar Extrato Mensal Domínio;
- FGTS mensal/rescisório;
- antecipação/multa;
- consignado/garantia;
- rural/Funrural/SENAR/INCRA;
- recibos eSocial;
- janela 25→09;
- retificações;
- reprocessamento;
- bloqueios de impressão;
- contingências manuais.

Essa orientação é autoridade metodológica para qualquer recuperação posterior.

## 22–23/09/2026 — reaproveitamento no Axiom Essence

Ao planejar Arquivo Digital/Storage do Essence, surgiu a necessidade de não redesenhar do zero antes de vasculhar o Tools.

Foram retomados:

- estrutura de pastas;
- motor de grafia;
- roots;
- watcher;
- conciliação banco↔filesystem;
- indexação;
- OCR;
- classificação;
- regras de legado;
- UX;
- motores;
- decisões operacionais.

Em 23/09/2026 foi confirmado que o GitHub sozinho não contém todo o runtime histórico.

A partir disso foi criado o conjunto docs/patrimonio_historico para preservar o apanhado transversal das conversas.

## Regra final da linha do tempo

Quando houver conflito entre “o que o chat dizia que estava pronto” e “o que o canônico posterior declarou reiniciado/não homologado”:

1. não apagar nenhuma das duas evidências;
2. marcar a divergência;
3. localizar o código/runtime correspondente;
4. decidir autoridade apenas depois da prova técnica.

História de projeto não deve ser reescrita para parecer mais linear do que realmente foi.
