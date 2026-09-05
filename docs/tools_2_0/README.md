# Axiom Tools 2.0 — Programa de Reformulação Integral

Data de instituição: 04/09/2026  
Status: **planejamento canônico / implementação ainda não iniciada**  
Prefixo do programa: `AXT2`  
Repositório oficial: `mendescharles2022-collab/Axiom_Tools`

## 1. Por que este programa existe

O Axiom Tools evoluiu rapidamente entre agosto de 2026, saindo de automações de filesystem e upload para um sistema de processamento documental, fechamento mensal, conferência, impressão, entregas e integrações assistidas.

Essa evolução produziu patrimônio valioso, mas também acumulou acoplamentos, mudanças sucessivas de fluxo, estados ambíguos, divergência entre runtime e GitHub e correções que foram testadas no tooling sem necessariamente chegarem à instalação operacional.

O **Axiom Tools 2.0** nasce para consolidar, de forma definitiva, tudo o que funcionou e tudo o que falhou.

Não é um simples pacote corretivo da V8.

É uma **reformulação integral orientada por domínio, evidência, regressão e operação real do escritório**, preservando dados e documentos e evitando repetir os erros das versões 14C–V8.

## 2. Bases obrigatórias do Tools 2.0

O programa usa quatro fontes combinadas:

1. decisões funcionais e operacionais registradas nas conversas do projeto;
2. documentação já versionada no repositório;
3. achados da auditoria V8, incluindo B01–B50;
4. casos reais da competência 08/2026 transformados em regressão.

A referência operacional estável permanece **V5.6.14V7**, instalada em 26/08/2026.

A V8 permanece **não homologada** e deve ser tratada como fonte de aprendizado, contratos, tooling, cenários de regressão e partes comprovadamente reutilizáveis — nunca como base automaticamente confiável.

## 3. Regra de autoridade documental

Para o desenvolvimento futuro do Tools 2.0, a ordem de autoridade passa a ser:

1. `docs/tools_2_0/TOOLS_2_0_CONSTITUICAO_E_ESCOPO.md`;
2. decisões específicas e contratos do programa Tools 2.0;
3. `TOOLS_2_0_ARQUITETURA_ALVO.md`;
4. `TOOLS_2_0_REQUISITOS_FUNCIONAIS_A_Z.md`;
5. `TOOLS_2_0_PLANO_MIGRACAO_E_SPRINTS.md`;
6. `TOOLS_2_0_MATRIZ_RASTREABILIDADE.md`;
7. documentação V8 e decisões históricas, quando não conflitarem;
8. documentação AXT-000–AXT-008 de 16/08/2026, como patrimônio histórico.

Nada nesta pasta declara que a instalação operacional atual já é Tools 2.0.

## 4. Documentos canônicos do programa

- `TOOLS_2_0_CONSTITUICAO_E_ESCOPO.md` — identidade, princípios, escopo e regras permanentes;
- `TOOLS_2_0_RETROSPECTIVA_ACERTOS_FALHAS.md` — análise do que funcionou, do que falhou e por quê;
- `TOOLS_2_0_ARQUITETURA_ALVO.md` — arquitetura técnica e operacional de destino;
- `TOOLS_2_0_REQUISITOS_FUNCIONAIS_A_Z.md` — catálogo funcional completo;
- `TOOLS_2_0_PLANO_MIGRACAO_E_SPRINTS.md` — sequência de implementação e critérios de avanço;
- `TOOLS_2_0_MATRIZ_RASTREABILIDADE.md` — ligação entre histórico, bloqueadores, casos reais e componentes do 2.0;
- `TOOLS_2_0_CRITERIOS_DE_HOMOLOGACAO.md` — gates técnicos, funcionais e operacionais para liberar versão.

## 5. Decisão fundamental de implementação

O Tools 2.0 seguirá a regra:

> **preservar patrimônio, reconstruir contratos, migrar com prova.**

Isso significa:

- não apagar a V7;
- não instalar a V8 como etapa intermediária obrigatória;
- não copiar cegamente módulos do runtime antigo;
- não reescrever parsers e regras que já estejam comprovadamente corretos sem necessidade;
- não tocar banco ou acervo real durante desenvolvimento;
- criar migração versionada, idempotente, simulável e reversível;
- manter uma suíte de regressão baseada em casos reais do escritório;
- só promover código ao runtime quando GitHub, build e instalação forem a mesma árvore comprovada.

## 6. Resultado esperado

Ao final do programa, o Axiom Tools deve operar como uma plataforma local confiável para:

- cadastro e contexto operacional de clientes;
- administração segura das estruturas documentais;
- abertura e acompanhamento de competências;
- processamento documental em lotes;
- leitura nativa com OCR apenas como fallback;
- motores especialistas por fonte;
- conferência por obrigação e componente;
- tratamento de exceções, justificativas e chamadas;
- retificação versionada;
- eConsignado contextual;
- regras rurais, MEI/DAE, afastamentos, faltas e rescisões;
- impressão e entregas somente após autorização canônica;
- integrações assistidas com portais;
- auditoria, observabilidade, backup, rollback e reconciliação banco ↔ filesystem.

## 7. Regra de execução

Nenhuma Sprint AXT2 pode ser considerada concluída apenas porque:

- a tela apareceu;
- um teste unitário isolado passou;
- um contrato foi documentado;
- o tooling validou uma simulação;
- um status foi ocultado na interface.

Cada Sprint deve demonstrar implementação real, testes automatizados, regressão aplicável e evidência de integração.

O programa termina somente quando o mesmo código que passou pelos gates gerar o pacote Windows efetivamente homologado.