# Roadmap Oficial — Axiom Tools

Versão: 1.1  
Data: 16/08/2026

Este documento consolida a sequência oficial de Sprints do Axiom Tools. A ordem foi ajustada para iniciar pela criação e atualização segura das estruturas de pastas, conforme decisão do projeto em 16/08/2026.

Toda Sprint deverá respeitar `docs/decisions/` e a arquitetura oficial.

## AXT-000 — Fundação

Objetivo: criar a base institucional e técnica do projeto.

Escopo:

- repositório oficial;
- README;
- configuração Python;
- estrutura modular;
- diretórios de documentação;
- regras permanentes;
- arquitetura;
- roadmap.

Status: concluída como fundação documental/estrutural.

## AXT-001 — Estrutura de Pastas PF/PJ e Funcionários

Objetivo: construir e homologar primeiro o motor seguro de criação, reconhecimento, correção e atualização das estruturas físicas de clientes e funcionários.

Escopo previsto:

- estrutura oficial PJ;
- estrutura oficial PF;
- diferenças PF/PJ;
- criação incremental;
- atualização conservadora;
- reconhecimento de equivalências de acentuação/nomenclatura;
- compatibilidade com BATs anteriores;
- reconhecimento de `estrutura.cfg`;
- localização de `Funcionários` ou `Empregados`;
- estrutura individual de funcionário;
- preservação de estruturas legadas, inclusive `Exames` quando já existente;
- `Corrigir Estrutura`;
- simulação/relatório antes de operações em lote;
- testes de não destruição.

Critério essencial: criar somente o que falta, sem excluir, mover, substituir ou sobrescrever arquivos existentes.

## AXT-002 — Núcleo de Clientes, Importação e Configurações

Objetivo: criar o núcleo cadastral que passará a consumir o motor homologado da AXT-001.

Escopo previsto:

- persistência local;
- cadastro PF/PJ;
- CPF/CNPJ;
- nome/razão social;
- status;
- caminho físico;
- busca;
- cadastro manual;
- edição;
- inativação/reativação;
- exclusão cadastral controlada;
- importação de planilha de clientes;
- tratamento de duplicidades;
- configurações de caminhos;
- histórico mínimo de alterações.

Critério essencial: excluir um cadastro não poderá excluir a pasta física do cliente.

## AXT-003 — OCR e Classificação Documental

Objetivo: transformar a entrada documental em fluxo inteligente de identificação e classificação.

Escopo previsto:

- área de entrada;
- leitura de PDF;
- OCR quando necessário;
- DARF/DCTFWeb;
- FGTS Digital;
- contracheques;
- pró-labore;
- identificação por CPF/CNPJ;
- identificação por nome quando necessário;
- nível de confiança;
- fila de revisão;
- renomeação sugerida;
- detecção de conflito;
- preservação do original.

Critério essencial: baixa confiança não pode gerar decisão destrutiva automática.

## AXT-004 — Competências e Roteamento

Objetivo: organizar documentos reconhecidos por cliente, tipo e competência.

Escopo previsto:

- extração/validação de competência;
- organização mensal;
- caminhos de destino configuráveis;
- roteamento de DARF;
- roteamento de FGTS;
- roteamento de contracheques;
- roteamento de pró-labore;
- regras para documentos sem movimento;
- relatórios de itens não roteados;
- validação antes do processamento em lote.

Critério essencial: competência não deve ser presumida apenas pela data do arquivo.

## AXT-005 — Conferências

Objetivo: permitir conferência operacional antes de impressão, consolidação e fechamento de lotes.

Escopo previsto:

- visão por cliente;
- visão por competência;
- A–Z;
- encontrados x faltantes;
- não reconhecidos;
- pendentes de classificação;
- divergências;
- sem movimento confirmado;
- relatórios de conferência;
- visualização de PDFs.

Critério essencial: o usuário deve enxergar claramente o que o sistema entendeu e o que permanece pendente.

## AXT-006 — Impressão e Consolidação

Objetivo: automatizar preparação e impressão de documentos em lote.

Escopo previsto:

- seleção de clientes;
- ordenação A–Z;
- agrupamento por empresa;
- DARF + FGTS por empresa;
- tipos separados;
- arquivo único consolidado;
- múltiplos arquivos;
- pré-visualização;
- relatório do lote;
- impressão controlada.

Critério essencial: o lote deve ser reproduzível e rastreável sem alterar os originais.

## Capacidades transversais

As seguintes capacidades atravessam as Sprints e serão implementadas quando suas dependências estiverem maduras:

- auditoria/logs;
- tratamento de erros;
- conflitos de nomes;
- visualização PDF;
- integrações assistidas com eCAC, eSocial e Sintegra/SEFAZ GO;
- abertura do navegador;
- recebimento organizado de downloads;
- empacotamento para Windows;
- testes automatizados;
- simulação segura de operações de filesystem.

## Regra para novas Sprints

Novas Sprints poderão ser adicionadas após AXT-006. Mudanças futuras de ordem ou escopo estrutural deverão ser registradas formalmente, sem apagar o histórico das decisões anteriores.