# Axiom Tools — Status Atual

Data: 26/08/2026  
Status: **Operacional em servidor / V5.6.14V7 estável / V8 em reformulação**

## Instalação estável confirmada

**V5.6.14V7 — Ciclo Mensal com Fechamento Automático**

A instalação V7 foi aplicada com sucesso no servidor em 26/08/2026, preservando banco, serviços, histórico e retificações.

### Capacidades operacionais existentes

- cadastro de clientes PF/PJ e parâmetros operacionais;
- processamento em fila com worker;
- leitura nativa de PDFs e OCR como fallback;
- classificação documental e extração analítica;
- motores especialistas Domínio, eSocial, e-CAC/DARF e FGTS Digital;
- competência, valores, identidade e dados operacionais;
- repositório documental;
- Central de Conferência;
- eConsignado MTE/Dataprev;
- afastamentos e ocorrências;
- Central de Entregas;
- Centro de Impressão;
- relatórios e auditoria;
- Fechamento Mensal;
- histórico e retificação inteligente versionada;
- máscaras e grafias técnicas em padrão brasileiro.

## Situação da V8

A V8 **não está concluída** e não deve ser considerada versão de instalação.

A reformulação aprovada em 26/08/2026 redefine responsabilidades entre três áreas:

1. **Fechamento Mensal** — somente abrir competência e exibir a evolução/status dos clientes.
2. **Processamento de Arquivos** — operar dentro da competência aberta, sem misturar apurações históricas na visão operacional.
3. **Central de Conferência** — resolver exceções, justificar ausências, marcar sem movimento na competência, anexar documentos e reprocessar sem sair da tela.

O fechamento do cliente passa a ser resultado automático do batimento/conferência concluída.

## Regras já aprovadas e preservadas

- sem movimento permanente do cadastro é diferente de sem movimento de uma competência específica;
- sem movimento mensal não deve ser herdado silenciosamente no mês seguinte;
- retificação de competência fechada é detectada por mudança material e preserva versões anteriores;
- dados repetidos não criam retificação;
- saída automática fica bloqueada enquanto houver retificação candidata pendente;
- DARF deve ser conferido pela composição aplicável: previdenciário, IRRF, PIS folha, SENAR/Funrural e outros débitos reconhecidos;
- FGTS só é esperado quando aplicável ao perfil/evidências do cliente;
- eConsignado só aparece quando houver evidência positiva;
- clientes eletrônicos recebem DARF e FGTS separados por padrão; unificação é opt-in;
- contracheques de entrega eletrônica podem ser agrupados por empresa;
- impressão prioriza retirada/office-boy, mantendo seleção manual de outros clientes.

## Atenção — sincronização do repositório

A documentação da `main` foi atualizada para refletir o sistema real. A árvore histórica de código do GitHub ainda é anterior às atualizações operacionais instaladas entre 17 e 26/08/2026. Antes de usar a `main` como fonte byte a byte para nova implementação, deve-se concluir a ressincronização integral do código com uma cópia atual do servidor.

## Próximo trabalho

Concluir a V8 com:

- Fechamento Mensal simplificado;
- Processamento totalmente orientado pela competência aberta;
- Conferência como mesa operacional de resolução;
- isolamento visual/funcional entre competências;
- anexar/reprocessar diretamente na Conferência;
- fechamento automático por regras aplicáveis;
- testes de regressão sobre os fluxos já homologados da V7.
