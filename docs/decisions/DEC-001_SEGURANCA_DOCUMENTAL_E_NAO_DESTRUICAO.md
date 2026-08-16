# DEC-001 — Segurança Documental e Não Destruição

Versão: 1.0  
Data: 16/08/2026  
Status: Permanente e vinculante

## Decisão

O Axiom Tools opera sobre arquivos reais do escritório. Qualquer funcionalidade que manipule filesystem deve adotar comportamento conservador por padrão.

## Regras obrigatórias

- não excluir arquivos automaticamente;
- não excluir pastas automaticamente;
- não sobrescrever arquivos existentes silenciosamente;
- não substituir conteúdo existente para corrigir estrutura;
- não mover arquivos ou pastas legadas apenas para padronizar nomes;
- não mesclar automaticamente estruturas equivalentes com conteúdo;
- não reconstruir uma árvore apagando a anterior;
- não usar exclusão recursiva no fluxo funcional normal;
- preservar arquivos e pastas desconhecidos;
- separar exclusão cadastral de exclusão física;
- inativação, transferência ou encerramento cadastral não apagam documentos;
- revalidar estado do filesystem antes de aplicar um plano previamente calculado.

## Simulação

Quando uma operação puder alterar o filesystem, o sistema deverá oferecer fase de planejamento/simulação sempre que tecnicamente aplicável.

A simulação deve ser somente leitura. Ela não pode criar sequer a pasta raiz do cliente.

## Conflitos

Quando houver ambiguidade, divergência de tipo, colisão entre arquivo e diretório ou equivalentes legados coexistentes:

1. registrar o conflito;
2. preservar o estado atual;
3. não tomar decisão destrutiva;
4. permitir que operações independentes e seguras continuem, se possível.

## Auditoria e rastreabilidade

Toda operação relevante deverá produzir resultado estruturado suficiente para registrar futuramente:

- ação solicitada;
- caminho afetado;
- estado anterior conhecido;
- ação planejada;
- ação efetivamente executada;
- conflito/aviso;
- resultado final.

## OCR e automações futuras

- arquivos originais permanecem preservados;
- baixa confiança vai para revisão humana;
- ausência de arquivo não implica automaticamente “sem movimento”;
- portais externos permanecem sob controle humano em autenticação, CAPTCHA e confirmações críticas.

## Testes

Testes automatizados devem usar diretórios temporários isolados. A árvore real do escritório nunca será alvo de suíte automática.

Esta decisão vincula todas as Sprints do Axiom Tools.