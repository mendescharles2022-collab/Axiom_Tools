# AXT-004 — Conferência, Impressão e Integrações Assistidas

Status: Aprovado  
Data: 16/08/2026

## 1. Conferência operacional

Antes de impressão, consolidação ou processamento em lote, o Axiom Tools deverá oferecer conferência dos arquivos envolvidos.

A conferência deverá permitir visualizar, por cliente e competência:

- documentos encontrados;
- documentos faltantes;
- arquivos não reconhecidos;
- divergências de cliente;
- divergências de competência;
- classificações pendentes;
- condição sem movimento, quando confirmada pela regra aplicável.

## 2. Ordem

Listagens e lotes deverão suportar ordenação A–Z por cliente.

## 3. Impressão em lote

O sistema deverá suportar:

- impressão agrupada por empresa;
- DARF + FGTS agrupados por empresa quando solicitado;
- impressão dos tipos separadamente;
- seleção de clientes/documentos;
- consolidação em arquivo único;
- geração de múltiplos arquivos quando preferível;
- visualização/conferência antes de enviar à impressora.

A impressão não deve depender da destruição ou alteração dos arquivos de origem.

## 4. PDF

O Axiom Tools deverá possuir capacidade de visualização e manipulação operacional de PDFs para conferência e consolidação.

Quando páginas externas puderem ser salvas legitimamente como PDF, o sistema poderá apoiar esse fluxo e encaminhar o resultado à entrada documental.

## 5. Integrações assistidas

Integrações com portais governamentais ou externos serão assistidas, não clandestinamente automatizadas.

Portais prioritários discutidos:

- eCAC;
- eSocial;
- Sintegra/SEFAZ GO;
- outros portais necessários às rotinas futuras.

Fluxo padrão:

1. Axiom Tools abre o portal/página no navegador configurado;
2. o usuário realiza login, certificado, CAPTCHA e confirmações necessárias;
3. o usuário solicita/baixa o documento no portal;
4. o arquivo é salvo em pasta configurada;
5. Axiom Tools detecta/recebe o arquivo;
6. OCR, classificação, competência e conferência dão continuidade ao processamento local.

## 6. Proibição

O Axiom Tools não deverá:

- burlar CAPTCHA;
- esconder autenticação do usuário;
- executar ação governamental crítica sem ciência do operador;
- presumir que um portal mantém sempre o mesmo HTML/fluxo;
- tratar automação de navegador como substituta das regras oficiais do portal.

## 7. Rastreabilidade

A geração de lotes, consolidações e integrações assistidas deverá registrar informações suficientes para reconstruir o que foi processado, sem exigir alteração dos arquivos originais.