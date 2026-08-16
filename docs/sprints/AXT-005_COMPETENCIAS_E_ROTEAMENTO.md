# AXT-005 — Competências e Roteamento

Versão: 1.0  
Data: 16/08/2026  
Status: **Planejada**

## Dependências

- AXT-004 homologada;
- DEC-001;
- DEC-003.

## Objetivo

Organizar documentos reconhecidos por cliente, tipo e competência, com roteamento seguro para destinos configurados.

## Escopo

- extração/validação de competência;
- organização mensal;
- caminhos de destino configuráveis;
- roteamento de DARF/DCTFWeb;
- roteamento de FGTS Digital;
- roteamento de contracheques;
- roteamento de pró-labore;
- regras controladas para documentos sem movimento;
- relatório de itens não roteados;
- validação antes do processamento em lote;
- conflito de destino;
- rastreabilidade das cópias/versões gerenciadas.

## Regras

- competência não deve ser presumida apenas pela data do arquivo;
- ausência de documento não gera automaticamente `sem movimento`;
- destino existente deve passar por política de conflito;
- original permanece preservado;
- roteamento em lote precisa de prévia conferência do plano.

## Fora de escopo

- conferência operacional completa;
- impressão;
- automação de portal.

## Critérios de aceite

- competência validável;
- caminhos configuráveis;
- lote simulável antes de aplicar;
- conflitos de destino tratados sem sobrescrita silenciosa;
- itens não roteados claramente relatados;
- original preservado.