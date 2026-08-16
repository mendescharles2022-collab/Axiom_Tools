# Axiom Tools

Aplicação operacional local do Ecossistema Axiom para organização segura de arquivos, estruturas de clientes, OCR, conferência, impressão e integrações assistidas.

## Estado oficial

- **AXT-000 — Fundação documental e arquitetural:** concluída.
- **AXT-001 — Motor seguro de estruturas PF/PJ e funcionários:** Sprint funcional atual; implementação reiniciada do zero.
- Implementações locais anteriores à reorganização documental de 16/08/2026 não constituem referência técnica e não devem ser reaproveitadas automaticamente.
- A documentação deste repositório é a fonte oficial de verdade do projeto.

Consulte primeiro [`docs/STATUS_ATUAL.md`](docs/STATUS_ATUAL.md).

## Princípios permanentes

1. Nenhum arquivo original é excluído automaticamente.
2. Nenhum arquivo existente é sobrescrito silenciosamente.
3. Cadastro e filesystem são domínios distintos: excluir/inativar cadastro não elimina pasta física.
4. Operações sobre arquivos devem ser planejáveis, rastreáveis e conservadoras.
5. Estruturas legadas são reconhecidas e preservadas.
6. Baixa confiança em OCR gera revisão humana, nunca decisão destrutiva.
7. A grafia legal/original do cliente é preservada.
8. Autenticação, CAPTCHA e ações críticas em portais externos permanecem sob controle humano.
9. O código deve permanecer modular e testável.
10. Interface e identidade visual devem obedecer ao Axiom Framework quando introduzidas.

## Documentação oficial

- [`docs/STATUS_ATUAL.md`](docs/STATUS_ATUAL.md) — situação atual e próximo passo;
- [`docs/CONSOLIDACAO_OFICIAL_AXIOM_TOOLS.md`](docs/CONSOLIDACAO_OFICIAL_AXIOM_TOOLS.md) — escopo e regras do produto;
- [`docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md`](docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md) — arquitetura oficial;
- [`docs/decisions/`](docs/decisions/) — decisões permanentes, identificadas por `DEC-*`;
- [`docs/sprints/`](docs/sprints/) — Sprints oficiais, identificadas por `AXT-*`;
- [`docs/sprints/ROADMAP_OFICIAL_AXIOM_TOOLS.md`](docs/sprints/ROADMAP_OFICIAL_AXIOM_TOOLS.md) — sequência oficial.

## Roadmap

- AXT-000 — Fundação documental e arquitetural;
- AXT-001 — Motor seguro de estruturas PF/PJ e funcionários;
- AXT-002 — Login, Shell e Dashboard;
- AXT-003 — Núcleo de clientes, importação e configurações;
- AXT-004 — OCR e classificação documental;
- AXT-005 — Competências e roteamento;
- AXT-006 — Conferências e visualização de PDF;
- AXT-007 — Impressão e consolidação;
- AXT-008 — Integrações assistidas e operação Windows.

## Estrutura-base do código

```text
src/axiom_tools/
├── core/
├── modules/
│   ├── folders/
│   ├── clients/          # introduzido quando a AXT-003 começar
│   ├── ocr/
│   ├── printing/
│   ├── integrations/
│   └── settings/
└── utils/
```

A estrutura pode evoluir pelas Sprints, sem concentrar regras de negócio em arquivos monolíticos.