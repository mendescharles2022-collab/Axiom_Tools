# AXT-006 — Conferências e Visualização de PDF

Versão: 1.0  
Data: 16/08/2026  
Status: **Planejada**

## Dependências

- AXT-005 homologada;
- DEC-001;
- DEC-003;
- DEC-004.

## Objetivo

Criar uma camada de conferência operacional que permita ao usuário revisar o entendimento do sistema antes de impressão, consolidação ou fechamento de lotes.

## Escopo

- visão por cliente;
- visão por competência;
- ordenação A–Z;
- documentos encontrados;
- documentos faltantes;
- não reconhecidos;
- baixa confiança;
- cliente não identificado;
- competência não identificada;
- divergências;
- sem movimento somente quando confirmado pela regra aplicável;
- visualização de PDF;
- filtros e busca;
- relatórios de conferência;
- status de conferência.

## Regras

- o usuário deve enxergar claramente o que foi reconhecido e o que continua pendente;
- visualização não altera o arquivo original;
- ausência de arquivo não equivale automaticamente a sem movimento;
- pendências não devem ser escondidas para produzir um “lote limpo” artificial.

## Fora de escopo

- impressão efetiva em lote;
- consolidação final para impressão;
- integrações com portais.

## Critérios de aceite

- conferência por cliente e competência funcional;
- PDFs visualizáveis com segurança;
- pendências e divergências explícitas;
- relatórios reproduzíveis;
- nenhum documento original alterado pela conferência.