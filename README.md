# Axiom Tools

Aplicação operacional local do Ecossistema Axiom para Departamento Pessoal, organização documental, processamento inteligente, conferência mensal, entregas, impressão e integrações assistidas.

## Estado operacional atual

- **Instalação estável confirmada:** V5.6.14V7 — 26/08/2026.
- **V8:** em reformulação arquitetural; ainda não homologada nem instalada.
- O ambiente oficial Windows opera com backend `5201`, gateway `5200` e worker de processamento.
- O sistema já possui cadastro de clientes, processamento documental, especialistas Domínio/eSocial/e-CAC/FGTS, eConsignado, Central de Conferência, Central de Entregas, Centro de Impressão, Afastamentos e Fechamento Mensal.

> Importante: a documentação deste repositório foi atualizada em 26/08/2026 para refletir o sistema real. A árvore histórica de código da `main` ainda precisa de ressincronização integral com a cópia operacional do servidor antes de ser tratada como espelho byte a byte da instalação.

Consulte primeiro [`docs/STATUS_ATUAL.md`](docs/STATUS_ATUAL.md).

## Princípios permanentes

1. Nenhum arquivo original é excluído automaticamente.
2. Nenhum arquivo existente é sobrescrito silenciosamente.
3. Cadastro e filesystem são domínios distintos.
4. OCR é fallback; leitura nativa vem primeiro e o conteúdo lido deve ser reutilizado.
5. Processamento deve ser idempotente, incremental, rastreável e preparado para lotes grandes.
6. Baixa confiança ou conflito de identidade gera revisão humana, nunca decisão destrutiva.
7. Grafia legal/original do cliente é preservada.
8. Retificações preservam o fechamento anterior e criam nova versão comparável.
9. Entregas e impressão usam documentos vigentes e respeitam o perfil do cliente.
10. A interface deve manter identidade visual única e não criar trabalho manual desnecessário.

## Arquitetura operacional

Fluxo documental principal:

`Domínio → eSocial → e-CAC/DARF → FGTS Digital → cruzamento incremental`

Motores especialistas principais:

- Domínio;
- eSocial;
- e-CAC/DARF;
- FGTS Digital.

Especialistas reutilizáveis incluem identidade, competência, valores, pessoas, dados operacionais, eConsignado e validação/cruzamento.

## Fechamento mensal — direção aprovada para V8

A separação de responsabilidades aprovada é:

- **Fechamento Mensal:** abre a competência e acompanha o status dos clientes; não executa processamento nem exige fechamento manual.
- **Processamento de Arquivos:** trabalha somente no contexto de competência(s) aberta(s) no Fechamento Mensal e executa leitura, classificação, extração e reprocessamento.
- **Central de Conferência:** é a mesa de trabalho para divergências, ausências, sem movimento mensal, justificativas, anexos e reprocessamento.
- **Fechado:** deve ser consequência automática da conferência aplicável concluída, e não de um botão manual.

Detalhes: [`docs/architecture/ARQUITETURA_OPERACIONAL_FECHAMENTO_V8.md`](docs/architecture/ARQUITETURA_OPERACIONAL_FECHAMENTO_V8.md).
