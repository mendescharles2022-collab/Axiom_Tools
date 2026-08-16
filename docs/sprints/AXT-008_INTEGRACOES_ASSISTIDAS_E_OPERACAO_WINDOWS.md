# AXT-008 — Integrações Assistidas e Operação Windows

Versão: 1.0  
Data: 16/08/2026  
Status: **Planejada**

## Dependências

- AXT-007 homologada;
- DEC-001;
- DEC-004;
- arquitetura oficial.

## Objetivo

Consolidar a operação do Axiom Tools no ambiente Windows do escritório e introduzir integrações assistidas com portais externos sem burlar controles humanos obrigatórios.

## Escopo

- abertura assistida de eCAC;
- abertura assistida de eSocial;
- abertura assistida de Sintegra/SEFAZ GO;
- configuração do navegador quando necessária;
- pastas de entrada/download configuráveis;
- recepção organizada de documentos baixados;
- encaminhamento ao fluxo local de OCR/classificação;
- empacotamento/execução Windows;
- configuração de caminhos operacionais;
- logs de integração;
- instruções simples de instalação/atualização;
- testes em ambiente Windows compatível.

## Regras

- autenticação permanece com o usuário;
- CAPTCHA permanece com o usuário;
- certificados, confirmações e ações críticas não são burlados;
- a integração deve continuar útil mesmo quando o portal exigir interação manual;
- downloads recebidos entram no fluxo local sem apagar o original;
- caminhos não podem ficar hardcoded em vários pontos do código.

## Critérios de aceite

- abertura e retorno ao fluxo local funcionando;
- downloads processáveis a partir de caminhos configurados;
- nenhuma tentativa de contorno de proteção do portal;
- empacotamento Windows documentado;
- inicialização confiável no ambiente definido;
- configuração e logs suficientes para diagnóstico operacional.