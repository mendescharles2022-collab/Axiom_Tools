# AXT-007 — Impressão e Consolidação

Versão: 1.0  
Data: 16/08/2026  
Status: **Planejada**

## Dependências

- AXT-006 homologada;
- DEC-001;
- DEC-004.

## Objetivo

Automatizar a preparação, consolidação e impressão controlada de documentos já conferidos.

## Escopo

- seleção de clientes;
- ordenação A–Z;
- agrupamento por empresa;
- agrupamento DARF + FGTS quando solicitado;
- impressão por tipo documental;
- geração de PDF único consolidado;
- geração de múltiplos arquivos;
- pré-visualização;
- relatório do lote;
- impressão controlada;
- identificação dos documentos incluídos no lote;
- rastreabilidade da geração.

## Regras

- somente documentos conferidos/selecionados entram no lote;
- o lote não altera nem apaga os originais;
- o usuário deve poder revisar a composição antes de imprimir;
- o mesmo conjunto de entrada e parâmetros deve permitir reproduzir o lote;
- erros de impressão não podem marcar automaticamente todos os documentos como concluídos.

## Critérios de aceite

- A–Z correto;
- agrupamentos reproduzíveis;
- PDF consolidado e saídas separadas funcionando;
- pré-visualização coerente com impressão;
- relatório completo do lote;
- originais preservados.