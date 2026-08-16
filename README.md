# Axiom Tools

Ferramentas operacionais do Ecossistema Axiom para automação local de arquivos, organização documental, OCR, conferência e apoio às rotinas do escritório.

## Objetivo

O Axiom Tools evolui rotinas locais anteriormente executadas por BATs para uma aplicação modular, rastreável e segura, voltada principalmente para:

- cadastro/indexação de clientes PF e PJ;
- criação e atualização padronizada das pastas de clientes;
- organização documental e estruturas de funcionários;
- identificação, renomeação e classificação de PDFs por OCR;
- separação de documentos por cliente e competência;
- conferência e impressão em lote;
- abertura assistida de portais externos;
- preservação dos documentos originais e rastreabilidade das operações.

## Princípios

1. Nenhum arquivo original deve ser excluído automaticamente.
2. Exclusão cadastral de cliente não exclui sua pasta física.
3. Operações de movimentação devem ser rastreáveis.
4. A classificação automática deve permitir conferência humana.
5. Integrações governamentais devem respeitar autenticação, CAPTCHA e demais interações humanas obrigatórias.
6. A estrutura deve permanecer modular.
7. A grafia legal/original do cliente deve ser preservada.

## Documentação oficial

A consolidação do histórico do projeto está registrada em:

- [`docs/CONSOLIDACAO_OFICIAL_AXIOM_TOOLS.md`](docs/CONSOLIDACAO_OFICIAL_AXIOM_TOOLS.md) — documento mestre de escopo e regras;
- [`docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md`](docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md) — arquitetura oficial;
- [`docs/decisions/`](docs/decisions/) — decisões permanentes;
- [`docs/sprints/ROADMAP_OFICIAL_AXIOM_TOOLS.md`](docs/sprints/ROADMAP_OFICIAL_AXIOM_TOOLS.md) — sequência de Sprints recuperada do planejamento.

## Estrutura do repositório

```text
Axiom_Tools/
├── config/
├── docs/
│   ├── architecture/
│   ├── decisions/
│   └── sprints/
├── scripts/
├── src/
│   └── axiom_tools/
│       ├── core/
│       ├── modules/
│       │   ├── folders/
│       │   ├── ocr/
│       │   ├── printing/
│       │   ├── integrations/
│       │   └── settings/
│       └── utils/
└── tests/
```

## Roadmap

- AXT-000 — Fundação;
- AXT-001 — Núcleo de clientes, importação e configurações;
- AXT-002 — Estrutura de pastas PF/PJ e funcionários;
- AXT-003 — OCR e classificação documental;
- AXT-004 — Competências e roteamento;
- AXT-005 — Conferências;
- AXT-006 — Impressão e consolidação.

## Estado

Fundação e consolidação documental concluídas. A implementação funcional deverá seguir as Sprints oficiais e respeitar as decisões permanentes do projeto.