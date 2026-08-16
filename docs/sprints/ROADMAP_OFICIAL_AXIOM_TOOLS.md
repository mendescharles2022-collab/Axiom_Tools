# Roadmap Oficial — Axiom Tools

Versão: 2.0  
Data: 16/08/2026  
Status: Oficial

## Regra de leitura

- `AXT-*` identifica Sprint de execução.
- `DEC-*` identifica decisão permanente.
- A Sprint seguinte só deve iniciar após homologação da anterior, salvo decisão formal em contrário.
- Nenhum executor deve antecipar funcionalidades de Sprint futura.

## Sequência oficial

### AXT-000 — Fundação Documental e Arquitetural

Status: **Concluída**

Documento: `AXT-000_FUNDACAO_DOCUMENTAL_E_ARQUITETURAL.md`

Entregou repositório, estrutura documental, arquitetura, decisões e roadmap.

---

### AXT-001 — Estrutura de Pastas PF/PJ e Funcionários

Status: **Atual — pronta para implementação do zero**

Documento: `AXT-001_ESTRUTURA_DE_PASTAS_PF_PJ_E_FUNCIONARIOS.md`

Objetivo: motor seguro de inspeção, planejamento, criação e correção incremental de estruturas PF/PJ e funcionários, com legado e testes de não destruição.

**Não inclui interface gráfica, Login ou Dashboard.**

---

### AXT-002 — Login, Shell e Dashboard

Status: **Planejada**

Documento: `AXT-002_LOGIN_SHELL_DASHBOARD.md`

Objetivo: criar a camada visual base, autenticação inicial, shell, Dashboard e fluxo visual para o motor da AXT-001, obedecendo ao Axiom Framework.

---

### AXT-003 — Núcleo de Clientes, Importação e Configurações

Status: **Planejada**

Documento: `AXT-003_NUCLEO_CLIENTES_IMPORTACAO_CONFIGURACOES.md`

Objetivo: persistência local, cadastro PF/PJ, importação de planilha, busca, status, caminhos e configurações.

---

### AXT-004 — OCR e Classificação Documental

Status: **Planejada**

Documento: `AXT-004_OCR_CLASSIFICACAO_DOCUMENTAL.md`

Objetivo: entrada documental, leitura/OCR, classificação, confiança, revisão e preservação do original.

---

### AXT-005 — Competências e Roteamento

Status: **Planejada**

Documento: `AXT-005_COMPETENCIAS_E_ROTEAMENTO.md`

Objetivo: validar competência e rotear documentos reconhecidos para destinos configuráveis de forma segura.

---

### AXT-006 — Conferências e Visualização de PDF

Status: **Planejada**

Documento: `AXT-006_CONFERENCIAS_E_VISUALIZACAO_PDF.md`

Objetivo: permitir conferência por cliente/competência, visualizar PDFs e evidenciar pendências e divergências.

---

### AXT-007 — Impressão e Consolidação

Status: **Planejada**

Documento: `AXT-007_IMPRESSAO_E_CONSOLIDACAO.md`

Objetivo: preparar lotes A–Z, agrupar documentos, consolidar PDFs e imprimir com rastreabilidade.

---

### AXT-008 — Integrações Assistidas e Operação Windows

Status: **Planejada**

Documento: `AXT-008_INTEGRACOES_ASSISTIDAS_E_OPERACAO_WINDOWS.md`

Objetivo: integrar fluxos assistidos com portais externos, organizar downloads e consolidar execução/empacotamento Windows.

## Dependências transversais

Todas as Sprints respeitam:

- `docs/decisions/DEC-001_SEGURANCA_DOCUMENTAL_E_NAO_DESTRUICAO.md`;
- `docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md`;
- `docs/CONSOLIDACAO_OFICIAL_AXIOM_TOOLS.md`.

Sprints específicas citam decisões adicionais.

## Mudanças futuras

Qualquer alteração de ordem, fusão, divisão ou renumeração deverá atualizar:

1. este roadmap;
2. `docs/STATUS_ATUAL.md`;
3. `README.md`;
4. a consolidação oficial quando o escopo estrutural for afetado.

O histórico anterior permanece preservado pelo Git; documentos obsoletos não devem continuar ativos ao lado de documentos substitutos.