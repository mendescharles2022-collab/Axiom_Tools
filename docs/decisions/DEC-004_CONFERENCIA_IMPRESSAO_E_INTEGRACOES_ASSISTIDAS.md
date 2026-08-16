# DEC-004 — Conferência, Impressão e Integrações Assistidas

Versão: 1.0  
Data: 16/08/2026  
Status: Permanente e vinculante

## 1. Conferência

Antes de impressão, consolidação ou fechamento de lote, o usuário deve conseguir visualizar claramente:

- documentos encontrados;
- documentos faltantes;
- documentos não reconhecidos;
- cliente não identificado;
- competência não identificada;
- baixa confiança;
- conflitos;
- itens sem movimento somente quando houver confirmação/regra apropriada.

A conferência deve mostrar o que o sistema entendeu e o que continua pendente.

## 2. Visualização de PDF

A aplicação deverá evoluir para permitir visualização de PDF antes de ações em lote, sem alterar o arquivo original apenas para exibi-lo.

## 3. Impressão e consolidação

Devem ser suportados futuramente:

- ordenação A–Z;
- seleção de clientes;
- agrupamento por empresa;
- agrupamento DARF + FGTS quando solicitado;
- tipos documentais separados;
- PDF único consolidado ou múltiplos arquivos;
- pré-visualização;
- relatório do lote;
- impressão controlada.

O lote deverá ser reproduzível e rastreável.

## 4. Integrações assistidas

Portais externos podem ser abertos e auxiliados pelo sistema, inclusive eCAC, eSocial e Sintegra/SEFAZ GO.

Fluxo aprovado:

1. Axiom Tools abre o portal/navegador;
2. usuário realiza autenticação, CAPTCHA e confirmações obrigatórias;
3. documento é baixado/salvo;
4. Axiom Tools recebe o arquivo na pasta configurada;
5. processamento local continua.

## 5. Restrições

- não contornar CAPTCHA;
- não burlar autenticação forte;
- não automatizar clandestinamente ação crítica em nome do usuário;
- não apagar o download original como efeito automático de classificação;
- não imprimir lote sem possibilidade de conferência prévia.

Esta decisão vincula AXT-006, AXT-007 e AXT-008.