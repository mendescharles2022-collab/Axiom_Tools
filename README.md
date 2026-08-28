# Axiom Tools

Aplicação operacional local para Departamento Pessoal, organização documental, processamento inteligente, conferência mensal, entregas, impressão e integrações assistidas.

## Estado operacional

- **Referência estável confirmada:** V5.6.14V7 — instalada em 26/08/2026.
- **V8:** em auditoria/correção; **não homologada**.
- A auditoria de 28/08/2026 catalogou 50 bloqueadores e transformou 28 casos reais de 08/2026 em regressão objetiva.
- Nenhum pacote final V8 está autorizado enquanto a árvore operacional não for reconciliada com o repositório e testada.

Consulte primeiro:

- [`docs/STATUS_ATUAL.md`](docs/STATUS_ATUAL.md)
- [`docs/auditoria/MAPA_COBERTURA_BLOQUEADORES_V8.md`](docs/auditoria/MAPA_COBERTURA_BLOQUEADORES_V8.md)
- [`docs/auditoria/MATRIZ_REGRESSAO_V8_AGOSTO_2026.md`](docs/auditoria/MATRIZ_REGRESSAO_V8_AGOSTO_2026.md)

## Atenção — `main` ainda não é o runtime operacional completo

A documentação do repositório reflete as decisões, achados e contratos da auditoria atual.

A árvore de código da `main`, porém, ainda não espelha integralmente a implementação operacional auditada no servidor/ZIP canônico. O inventário atual confirma `src/axiom_tools` reduzido e ausência da suíte operacional completa em `tests/`.

Portanto:

- commit documental não significa correção de runtime;
- o código V8 final deve ser reconciliado e versionado antes da homologação;
- banco real, documentos de clientes, certificados, credenciais, logs, caches e dados sensíveis não entram nessa reconciliação;
- o pacote final deverá ser gerado da mesma árvore que passar pelos testes e pela migração.

Protocolo: [`docs/auditoria/PROTOCOLO_RECONCILIACAO_RUNTIME_REPOSITORIO_V8.md`](docs/auditoria/PROTOCOLO_RECONCILIACAO_RUNTIME_REPOSITORIO_V8.md).

## Princípios permanentes

1. Nenhum arquivo original é excluído automaticamente.
2. Nenhum arquivo existente é sobrescrito silenciosamente.
3. Cadastro e filesystem são domínios distintos.
4. OCR é fallback; leitura nativa vem primeiro e o conteúdo lido deve ser reutilizado.
5. Processamento deve ser idempotente, incremental, rastreável e preparado para lotes grandes.
6. Baixa confiança ou conflito de identidade gera revisão humana, nunca decisão destrutiva.
7. Grafia legal/original do cliente é preservada.
8. Retificações preservam a versão anterior e promovem nova versão apenas após validação.
9. Impressão e Entregas dependem de gate único de backend e da versão de fechamento autorizadora.
10. `PROCESSADO`, `100%`, `PRONTA` ou retorno positivo de API não equivalem a `CONFERIDO`/`FECHADO`.

## Arquitetura operacional V8

Fluxo principal de evidências:

`Domínio → eSocial → e-CAC/DARF → FGTS Digital → cruzamento incremental`

A consulta eConsignado é contextual ao ciclo e deve usar somente o universo da competência/chamada aplicável.

Motores especialistas principais:

- Domínio;
- eSocial;
- e-CAC/DARF;
- FGTS Digital.

Especialistas reutilizáveis incluem identidade, competência, valores, pessoas, dados operacionais, eConsignado e validação/cruzamento.

## Separação funcional aprovada

- **Fechamento Mensal:** abre a competência e acompanha o ciclo; não processa arquivos.
- **Processamento de Arquivos:** trabalha somente dentro da competência/chamada aberta e produz evidências técnicas.
- **Central de Conferência:** resolve divergências, ausências, sem movimento mensal, justificativas, anexos e reprocessamento; abrir a tela deve ser leitura sem efeito colateral.
- **Fechado:** é consequência do estado canônico das obrigações aplicáveis e da versão vigente, não de um botão nem de status técnico.

Detalhes: [`docs/architecture/ARQUITETURA_OPERACIONAL_FECHAMENTO_V8.md`](docs/architecture/ARQUITETURA_OPERACIONAL_FECHAMENTO_V8.md).

## Critério de entrega V8

A V8 só pode ser considerada homologada quando:

1. runtime e GitHub forem reconciliados;
2. baseline/suíte original passarem;
3. bloqueadores forem corrigidos na árvore oficial;
4. regressão dos 28 casos passar;
5. migração e invariantes do SQLite forem validados em cópia;
6. benchmark e segurança forem validados;
7. o mesmo build for instalado no Windows com backup e rollback comprovados.
