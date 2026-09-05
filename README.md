# Axiom Tools

> **Direção vigente desde 04/09/2026:** o Axiom Tools será incorporado ao **Axiom Enterprise**. O nome **Axiom Tools 2.0** identifica o programa de migração e reconstrução por domínio; não haverá nova aplicação independente nem um módulo monolítico `Tools` no Enterprise.
>
> Desenvolvimento arquitetural do destino: `mendescharles2022-collab/Axiom_Enterprise`  
> Decisão: `docs/decisions/AXM-029_INCORPORACAO_AXIOM_TOOLS_2_0_AO_ENTERPRISE.md` no Enterprise  
> Sprint mestra planejada: `docs/sprints/ENT-006_INCORPORACAO_AXIOM_TOOLS_2_0_OPERACAO_DP.md` no Enterprise  
> Handoff local: [`docs/tools_2_0/MIGRACAO_PARA_AXIOM_ENTERPRISE.md`](docs/tools_2_0/MIGRACAO_PARA_AXIOM_ENTERPRISE.md)

Este repositório permanece preservado como **origem histórica, técnica, de auditoria e regressão** até a homologação integral da migração. Não arquivar, apagar ou tratar como descartável antes do encerramento formal da ENT-006.

Aplicação operacional local para Departamento Pessoal, organização documental, processamento inteligente, conferência mensal, entregas, impressão e integrações assistidas.

## Estado operacional do legado

- **Referência estável confirmada:** V5.6.14V7 — instalada em 26/08/2026.
- **V8:** em auditoria/correção; **não homologada**.
- A auditoria de 28/08/2026 catalogou 50 bloqueadores e transformou 28 casos reais de 08/2026 em regressão objetiva.
- Nenhum pacote final V8 está autorizado enquanto a árvore operacional não for reconciliada com o repositório e testada.
- A evolução arquitetural futura deve ser registrada no Axiom Enterprise; correções emergenciais do runtime legado não mudam essa direção.

Consulte primeiro:

- [`docs/tools_2_0/README.md`](docs/tools_2_0/README.md) — direção Tools 2.0 / Enterprise;
- [`docs/tools_2_0/MIGRACAO_PARA_AXIOM_ENTERPRISE.md`](docs/tools_2_0/MIGRACAO_PARA_AXIOM_ENTERPRISE.md) — handoff arquitetural;
- [`docs/STATUS_ATUAL.md`](docs/STATUS_ATUAL.md);
- [`docs/auditoria/RASTREADOR_EXECUCAO_CORRECAO_V8.md`](docs/auditoria/RASTREADOR_EXECUCAO_CORRECAO_V8.md) — estado vivo da correção/homologação do legado;
- [`docs/auditoria/MAPA_COBERTURA_BLOQUEADORES_V8.md`](docs/auditoria/MAPA_COBERTURA_BLOQUEADORES_V8.md);
- [`docs/auditoria/MATRIZ_REGRESSAO_V8_AGOSTO_2026.md`](docs/auditoria/MATRIZ_REGRESSAO_V8_AGOSTO_2026.md).

## Atenção — `main` ainda não é o runtime operacional completo

A documentação do repositório reflete as decisões, achados e contratos da auditoria atual.

A árvore de código da `main`, porém, ainda não espelha integralmente a implementação operacional auditada no servidor/ZIP canônico. O inventário atual confirma `src/axiom_tools` reduzido e ausência da suíte operacional completa em `tests/`.

Portanto:

- commit documental não significa correção de runtime;
- o código do legado deve ser reconciliado antes de ser usado como fonte de migração;
- banco real, documentos de clientes, certificados, credenciais, logs, caches e dados sensíveis não entram no Git;
- nenhum banco deve ser importado diretamente no Enterprise sem mapeamento, dry-run, invariantes e rollback;
- o destino homologado deverá ser gerado da mesma árvore que passar pelos testes e regressões.

Protocolo: [`docs/auditoria/PROTOCOLO_RECONCILIACAO_RUNTIME_REPOSITORIO_V8.md`](docs/auditoria/PROTOCOLO_RECONCILIACAO_RUNTIME_REPOSITORIO_V8.md).

## Infraestrutura de reconciliação já versionada

A `main` já contém tooling específico para retirar o bloqueio `main ≠ runtime` de forma controlada:

- `scripts/export_runtime_reconciliation.py` — exportador seguro por whitelist;
- `scripts/export_runtime_reconciliation.ps1` — launcher Windows;
- `scripts/audit_runtime_reconciliation.py` — valida manifesto e compara runtime × repositório;
- `tests/test_export_runtime_reconciliation.py`;
- `tests/test_audit_runtime_reconciliation.py`;
- `tests/test_reconciliation_pipeline_e2e.py`;
- `.github/workflows/reconciliation-tests.yml`.

Estado histórico registrado da infraestrutura:

- **18 testes já aprovados** nas revisões executadas;
- **3 testes end-to-end adicionais versionados**, aguardando execução comprovada;
- workflow do GitHub Actions presente, mas sem prova suficiente para substituir a validação do runtime físico.

Detalhes: [`tests/README.md`](tests/README.md).

## Princípios permanentes a migrar

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

## Arquitetura operacional do patrimônio V8

Fluxo principal de evidências:

`Domínio → eSocial → e-CAC/DARF → FGTS Digital → cruzamento incremental`

A consulta eConsignado é contextual ao ciclo e deve usar somente o universo da competência/chamada aplicável.

Motores especialistas principais:

- Domínio;
- eSocial;
- e-CAC/DARF;
- FGTS Digital.

Especialistas reutilizáveis incluem identidade, competência, valores, pessoas, dados operacionais, eConsignado e validação/cruzamento.

Esses conceitos devem ser incorporados ao Enterprise pelos domínios correspondentes, não copiados como um novo monólito.

## Separação funcional que deve sobreviver à migração

- **Fechamento Mensal → Fechamento de Folha no Enterprise:** abre a competência e acompanha o ciclo; não processa arquivos.
- **Processamento de Arquivos → Guias e Documentos:** trabalha dentro da competência/chamada aberta e produz evidências técnicas.
- **Central de Conferência → Guias e Documentos integrado ao Fechamento:** resolve divergências, ausências, sem movimento mensal, justificativas, anexos e reprocessamento; abrir a tela deve ser leitura sem efeito colateral.
- **Fechado:** é consequência do estado canônico das obrigações aplicáveis e da versão vigente, não de um botão nem de status técnico.
- **eConsignado → Consignados:** usa o universo mensal elegível e participa da conferência por fonte.
- **Regras normativas:** devem consumir o Referencial Técnico do Enterprise quando houver fonte homologada.

Detalhes históricos: [`docs/architecture/ARQUITETURA_OPERACIONAL_FECHAMENTO_V8.md`](docs/architecture/ARQUITETURA_OPERACIONAL_FECHAMENTO_V8.md).

## Critério para encerrar o legado

O Axiom Tools independente só pode ser encerrado quando:

1. runtime legado e GitHub forem reconciliados para o handoff;
2. patrimônio necessário tiver destino explícito no Enterprise;
3. B01–B50 estiverem encerrados na matriz da ENT-006;
4. regressão dos 28 casos e controles adicionais passar;
5. migração e invariantes do banco forem validadas em cópia e produção;
6. benchmark, segurança e permissões forem validados;
7. o mesmo build aprovado for instalado no Windows com backup e rollback comprovados;
8. o Enterprise operar sem dependência funcional do runtime legado.
