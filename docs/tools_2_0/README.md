# Axiom Tools 2.0 — Programa de Incorporação ao Axiom Enterprise

Data de instituição: 04/09/2026  
Status: **planejamento canônico migrado para o Axiom Enterprise**  
Repositório de destino: `mendescharles2022-collab/Axiom_Enterprise`  
Repositório histórico de origem: `mendescharles2022-collab/Axiom_Tools`

## 1. Decisão vigente

Em 04/09/2026 foi aprovada a incorporação integral do patrimônio válido do Axiom Tools ao **Axiom Enterprise**.

O Axiom Tools não continuará evoluindo como aplicação independente.

O nome **Axiom Tools 2.0** passa a designar o programa de migração, reconstrução e incorporação das capacidades do antigo Tools aos domínios canônicos do Enterprise.

Não será criado um monólito `Tools` dentro do Enterprise.

As capacidades serão distribuídas entre:

- Cadastro;
- Fechamento de Folha;
- Guias e Documentos;
- Consignados;
- Certificados e Acessos;
- Referencial Técnico;
- Raio-X do Cliente;
- Relatórios Gerenciais;
- Core compartilhado do Enterprise.

## 2. Fonte oficial do destino

A partir desta decisão, novas especificações arquiteturais e funcionais do Tools 2.0 devem ser registradas no repositório:

`mendescharles2022-collab/Axiom_Enterprise`

Documentos-mãe no destino:

- `docs/decisions/AXM-029_INCORPORACAO_AXIOM_TOOLS_2_0_AO_ENTERPRISE.md`;
- `docs/auditoria/RETROSPECTIVA_AXIOM_TOOLS_V7_V8_PARA_ENTERPRISE_20260904.md`;
- `docs/roadmap/PROGRAMA_AXIOM_TOOLS_2_0_INCORPORACAO_ENTERPRISE.md`;
- `docs/roadmap/AXIOM_TOOLS_2_0_REQUISITOS_A_Z.md`;
- `docs/sprints/ENT-006_INCORPORACAO_AXIOM_TOOLS_2_0_OPERACAO_DP.md`;
- `docs/homologacao/ENT-006_MATRIZ_RASTREABILIDADE_HOMOLOGACAO_TOOLS_2_0.md`.

## 3. Papel deste repositório

O repositório Axiom_Tools permanece preservado como patrimônio histórico e técnico enquanto a migração não for homologada.

Ele continua sendo fonte para:

- decisões históricas;
- contratos V8;
- auditorias;
- bloqueadores B01–B50;
- matriz de regressão da competência 08/2026;
- tooling de reconciliação;
- regras de segurança documental;
- histórico das versões 14C–V8;
- caracterização de parsers e comportamentos do runtime legado.

Ele não deve ser arquivado nem apagado antes da conclusão da ENT-006.

## 4. Estado do legado

A referência operacional estável permanece **V5.6.14V7**, instalada em 26/08/2026.

A V8 permanece **não homologada** e deve ser tratada como fonte de aprendizado, contratos, tooling, cenários de regressão e partes comprovadamente reutilizáveis — nunca como base automaticamente confiável.

## 5. Princípio de migração

> **Migrar função, regra, evidência e aprendizado; não copiar acoplamento, dívida técnica ou estado confuso.**

Isso significa:

- não apagar a V7;
- não instalar a V8 como etapa obrigatória;
- não copiar cegamente a aplicação para dentro do Enterprise;
- não importar banco real sem mapeamento e dry-run;
- não reescrever parser comprovado sem caracterização;
- não transportar reprocessamento destrutivo, estados ambíguos, bypass de saída ou mutações em leitura;
- preservar documentos físicos;
- migrar com versionamento, idempotência, regressão, backup e rollback;
- garantir que commit, build e runtime homologado sejam a mesma árvore.

## 6. O que deve ser preservado

Patrimônio obrigatório:

- não destruição documental;
- leitura nativa antes de OCR;
- OCR apenas como fallback e reutilização do texto lido;
- processamento por lotes;
- idempotência, hash, cache e checkpoints;
- motores especialistas Domínio, eSocial, e-CAC/DARF e FGTS Digital;
- especialistas de Identidade, Competência, Valores, Pessoas, Dados Operacionais, Aplicabilidade, eConsignado e Validação/Cruzamento;
- competência única do fechamento;
- chamadas;
- conferência por obrigação/fonte;
- retificação versionada;
- gate único de saída;
- regras MEI/DAE, rural, afastamentos, faltas, rescisões e consignados;
- 50 bloqueadores V8;
- 28 casos reais de regressão e controles adicionais.

## 7. Regra de execução

A próxima evolução arquitetural acontece no Enterprise.

Correções emergenciais no runtime legado do Tools podem ser realizadas enquanto ele continuar em produção, mas não devem criar nova arquitetura paralela.

A migração efetiva começa pelo inventário e reconciliação do runtime real, não por movimentação cega de arquivos ou banco.

## 8. Encerramento futuro

O Axiom Tools legado só poderá ser formalmente encerrado quando:

- a ENT-006 estiver homologada;
- dados necessários tiverem sido reconciliados/migrados;
- regressões estiverem aprovadas;
- operação Windows estiver validada;
- backup e rollback estiverem comprovados;
- o Enterprise operar sem dependência funcional do runtime legado.

Até lá, este repositório permanece intacto como fonte histórica e de prova.