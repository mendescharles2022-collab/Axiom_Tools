# Axiom Tools — Status Atual

Data: 16/08/2026  
Status: Oficial

## Onde estamos

O projeto está documentalmente organizado e pronto para reiniciar a implementação funcional de forma limpa.

### Concluído

- AXT-000 — Fundação documental e arquitetural.
- Consolidação oficial do escopo.
- Arquitetura oficial.
- Decisões permanentes de segurança, estruturas, OCR e operação.
- Roadmap reorganizado.

### Sprint atual

**AXT-001 — Estrutura de Pastas PF/PJ e Funcionários**

Situação: **pronta para implementação do zero**.

A AXT-001 deve implementar somente:

- motor seguro de estruturas PF/PJ;
- funcionários/empregados;
- equivalências legadas;
- `estrutura.cfg`;
- planejamento/simulação;
- aplicação segura;
- relatórios de operação;
- testes automatizados.

Não fazem parte da AXT-001:

- Login;
- Dashboard;
- interface gráfica completa;
- cadastro de clientes;
- SQLite;
- OCR;
- competências;
- conferência;
- impressão;
- integrações externas.

## Próxima Sprint

**AXT-002 — Login, Shell e Dashboard**

Será iniciada somente depois da homologação da AXT-001.

## Regra para executores

Qualquer executor deve:

1. ler este arquivo;
2. ler a Sprint atual;
3. ler as decisões permanentes citadas como dependência;
4. respeitar a arquitetura oficial;
5. não antecipar Sprint futura;
6. não reaproveitar automaticamente código de tentativas anteriores;
7. entregar código testável e modular.

## Fonte de verdade

- Sprints: `docs/sprints/`
- Decisões: `docs/decisions/`
- Arquitetura: `docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md`
- Consolidação: `docs/CONSOLIDACAO_OFICIAL_AXIOM_TOOLS.md`

Em caso de dúvida, a Sprint atual e suas decisões permanentes específicas prevalecem sobre descrições genéricas.