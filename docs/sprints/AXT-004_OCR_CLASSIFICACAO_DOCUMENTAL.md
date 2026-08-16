# AXT-004 — OCR e Classificação Documental

Versão: 1.0  
Data: 16/08/2026  
Status: **Planejada**

## Dependências

- AXT-003 homologada;
- DEC-001;
- DEC-003;
- arquitetura oficial.

## Objetivo

Criar a entrada documental inteligente do Axiom Tools, preservando originais e encaminhando incertezas para revisão humana.

## Escopo

- área/pasta de entrada;
- leitura de PDF textual;
- OCR quando necessário;
- classificação inicial de DARF/DCTFWeb;
- FGTS Digital;
- contracheques;
- pró-labore;
- identificação de cliente por CPF/CNPJ e apoio por nome;
- identificação do tipo documental;
- extração preliminar de competência;
- nível de confiança;
- fila de revisão;
- sugestão de renomeação;
- sugestão de destino;
- detecção de conflito;
- preservação integral do original;
- resultado estruturado da classificação.

## Regras

- baixa confiança não executa decisão destrutiva;
- original não é apagado após OCR;
- ausência de documento não significa `sem movimento`;
- competência não deve depender apenas da data do arquivo;
- conflito de nome/destino deve ser apresentado antes de processamento em lote.

## Fora de escopo

- roteamento mensal definitivo;
- conferência completa;
- impressão;
- integrações com portais.

## Critérios de aceite

- classificadores testados com amostras controladas;
- original preservado;
- confiança e revisão funcionando;
- cliente/tipo/competência sugeridos de forma estruturada;
- nenhuma movimentação destrutiva automática;
- dependências OCR/PDF documentadas e fixadas.