# Axiom Tools — Consolidação Oficial do Projeto

Versão: 2.0  
Data: 16/08/2026  
Status: Documento mestre permanente

## 1. Finalidade

O Axiom Tools é uma aplicação operacional local do Ecossistema Axiom destinada a organizar e automatizar rotinas de arquivos do escritório, evoluindo ferramentas antes executadas por BATs para uma solução modular, auditável, configurável e segura.

Seu escopo consolidado inclui:

- estruturas de pastas PF/PJ e funcionários;
- cadastro/indexação de clientes;
- OCR e classificação documental;
- competências e roteamento;
- conferência e visualização de PDF;
- impressão e consolidação em lote;
- integrações assistidas com portais externos;
- configurações e histórico operacional.

## 2. Fonte oficial de verdade

A partir desta versão:

1. este repositório é a fonte oficial de requisitos do Axiom Tools;
2. decisões permanentes usam prefixo `DEC-*`;
3. Sprints de execução usam prefixo `AXT-*`;
4. nenhum número de decisão corresponde automaticamente ao número de uma Sprint;
5. implementações locais anteriores à reorganização documental de 16/08/2026 não são referência técnica e não devem ser reaproveitadas automaticamente;
6. quando houver divergência, prevalece a ordem: decisão permanente mais específica → Sprint vigente → arquitetura oficial → consolidação mestre → README.

## 3. Princípio central: não destruição

O Axiom Tools trabalhará sobre documentos reais do escritório. Segurança documental prevalece sobre conveniência.

São regras permanentes:

- não excluir arquivos originais automaticamente;
- não apagar pastas por exclusão/inativação cadastral;
- não sobrescrever arquivos existentes silenciosamente;
- não mover ou mesclar conteúdo legado de forma automática apenas para padronização;
- preservar arquivos e pastas desconhecidos;
- planejar/simular operações críticas antes de aplicá-las quando tecnicamente possível;
- revalidar conflitos antes da execução;
- manter rastreabilidade operacional;
- encaminhar baixa confiança para revisão humana.

Detalhamento: `docs/decisions/DEC-001_SEGURANCA_DOCUMENTAL_E_NAO_DESTRUICAO.md`.

## 4. Estruturas PF/PJ e funcionários

A primeira Sprint funcional é dedicada exclusivamente ao motor seguro de estrutura de pastas.

A estrutura oficial, equivalências de legado, tratamento de `estrutura.cfg`, `Funcionários`/`Empregados`, preservação de `Exames` legado e regras de conflitos ficam consolidadas em:

- `docs/decisions/DEC-002_ESTRUTURAS_PF_PJ_FUNCIONARIOS_E_LEGADO.md`;
- `docs/sprints/AXT-001_ESTRUTURA_DE_PASTAS_PF_PJ_E_FUNCIONARIOS.md`.

A AXT-001 não implementa Login, Dashboard, cadastro completo de clientes, OCR, competências, conferência ou impressão.

## 5. Interface, Login e Dashboard

A interface base passa a ser uma Sprint própria: **AXT-002**.

Ela deverá introduzir:

- tela de login;
- sessão e logout;
- shell principal;
- sidebar e topbar;
- Dashboard;
- temas claro/escuro/automático;
- integração visual com o Axiom Framework;
- fluxo visual para consumir o motor homologado da AXT-001.

A interface não poderá alterar as regras de segurança do filesystem.

## 6. Clientes e persistência

O cadastro/indexação de clientes será introduzido somente após a homologação do motor de pastas e da base de interface.

O núcleo deverá suportar futuramente:

- PF/PJ;
- CPF/CNPJ;
- nome legal/original;
- status;
- caminho físico;
- cadastro manual;
- edição;
- inativação/reativação;
- exclusão apenas cadastral quando necessária;
- importação de planilha;
- prevenção de duplicidades;
- configurações de caminhos;
- histórico mínimo.

A persistência será local e não substituirá o acervo físico.

## 7. OCR e classificação

O Axiom Tools deverá possuir uma área de entrada documental e evoluir para reconhecer, entre outros:

- DARF/DCTFWeb;
- FGTS Digital;
- contracheques;
- pró-labore;
- documentos adicionais aprovados em Sprint.

O motor deverá identificar cliente, tipo documental e competência, atribuir nível de confiança e encaminhar incertezas para revisão.

Detalhamento permanente: `docs/decisions/DEC-003_OCR_CLASSIFICACAO_E_CONFIANCA.md`.

## 8. Competências e roteamento

Documentos mensais deverão poder ser organizados por cliente, tipo e competência, com caminhos configuráveis.

A competência não será inferida apenas pela data do arquivo. Roteamento em lote deverá ser validável antes da execução.

## 9. Conferência e PDF

O sistema deverá permitir conferência antes de impressão ou fechamento de lotes, incluindo:

- encontrados x faltantes;
- não reconhecidos;
- baixa confiança;
- divergências;
- itens sem competência;
- visualização de PDF;
- relatórios de conferência.

## 10. Impressão e consolidação

O Axiom Tools deverá permitir:

- seleção de clientes;
- ordenação A–Z;
- agrupamento por empresa;
- DARF + FGTS quando solicitado;
- tipos documentais separados;
- PDF consolidado ou múltiplos arquivos;
- pré-visualização;
- relatório do lote;
- impressão controlada.

## 11. Integrações assistidas

Portais como eCAC, eSocial e Sintegra/SEFAZ GO serão tratados em fluxo assistido:

1. sistema abre o portal/navegador;
2. usuário autentica e executa ações obrigatórias;
3. documento é baixado/salvo;
4. Axiom Tools recebe o arquivo em local configurado;
5. processamento local continua.

Não haverá contorno de CAPTCHA, autenticação forte ou confirmação humana.

Detalhamento: `docs/decisions/DEC-004_CONFERENCIA_IMPRESSAO_E_INTEGRACOES_ASSISTIDAS.md`.

## 12. Arquitetura e tecnologia

Base atual:

- Python 3.12 ou superior;
- Windows como ambiente operacional principal;
- filesystem como repositório dos documentos reais;
- SQLite previsto para persistência local a partir da Sprint apropriada;
- módulos separados por domínio;
- interface desacoplada das regras de filesystem;
- dependências de OCR/PDF introduzidas somente quando necessárias;
- interface visual consumidora do Axiom Framework quando a AXT-002 iniciar.

A arquitetura detalhada está em `docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md`.

## 13. Roadmap oficial

- **AXT-000 — Fundação documental e arquitetural:** concluída;
- **AXT-001 — Motor seguro de estruturas PF/PJ e funcionários:** atual, implementação reiniciada do zero;
- **AXT-002 — Login, Shell e Dashboard:** planejada;
- **AXT-003 — Núcleo de clientes, importação e configurações:** planejada;
- **AXT-004 — OCR e classificação documental:** planejada;
- **AXT-005 — Competências e roteamento:** planejada;
- **AXT-006 — Conferências e visualização de PDF:** planejada;
- **AXT-007 — Impressão e consolidação:** planejada;
- **AXT-008 — Integrações assistidas e operação Windows:** planejada.

## 14. Regra de evolução

Nenhuma Sprint futura deve ser antecipada dentro da Sprint atual por conveniência do executor.

Mudanças de arquitetura, escopo, estrutura de pastas ou ordem do roadmap devem ser registradas antes da implementação correspondente.