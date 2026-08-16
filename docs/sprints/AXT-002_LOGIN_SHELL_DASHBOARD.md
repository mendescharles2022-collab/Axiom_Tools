# AXT-002 — Login, Shell e Dashboard

Versão: 1.1  
Data: 16/08/2026  
Status: **Planejada**

## Dependências

- AXT-001 homologada;
- `docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md`;
- Axiom Framework vigente.

## Objetivo

Introduzir a camada visual base do Axiom Tools sem misturar regras de filesystem à interface.

## Referências visuais oficiais

Os mockups aprovados desta Sprint estão versionados no próprio repositório:

- `docs/mockups/AXT-002_LOGIN_REFERENCIA.jpg`
- `docs/mockups/AXT-002_DASHBOARD_REFERENCIA.jpg`

Eles devem ser usados como **referência obrigatória de composição, hierarquia visual, organização de conteúdo e experiência desejada**.

Os mockups não autorizam copiar literalmente:

- números fictícios;
- nomes fictícios de clientes;
- datas ilustrativas;
- conteúdos ainda não existentes no sistema;
- componentes que contrariem o Axiom Framework vigente.

### Regra de precedência visual

1. O **Axiom Framework** é a autoridade técnica para tokens, componentes, acessibilidade, responsividade, temas e padrões de UX/UI.
2. Os **mockups da AXT-002** são a autoridade para a composição visual específica do Axiom Tools: disposição do Login, shell, Dashboard, cards, navegação e densidade visual.
3. Quando o mockup apresentar dado meramente ilustrativo, a implementação deve usar dado real, estado vazio ou indicação `Em implantação`.
4. Não criar um Design System local paralelo para reproduzir o mockup.

## Escopo

- tecnologia de interface definida e registrada;
- tela de login;
- autenticação local inicial ou abstração equivalente, sem inventar integração inexistente;
- sessão;
- logout;
- proteção das telas internas;
- shell principal;
- sidebar;
- topbar;
- Dashboard;
- temas claro/escuro/automático;
- estados loading, vazio, erro, sucesso e indisponível;
- acesso visual ao módulo Estrutura de Pastas;
- fluxo `Inspecionar → Simular → Revisar → Confirmar → Aplicar → Resultado` consumindo os serviços homologados da AXT-001;
- responsividade e acessibilidade compatíveis com o Axiom Framework.

## Direção visual

A experiência deve manter a linguagem aprovada nos mockups: aplicação corporativa madura, clara, limpa e de alta legibilidade, com navegação consistente e foco operacional.

### Login

O mockup de Login orienta:

- página em tela cheia;
- identidade `Axiom Tools` claramente visível;
- formulário de acesso em card de destaque;
- campos de usuário e senha com labels permanentes;
- ação principal `Entrar` inequívoca;
- opção de permanência conectada somente se tecnicamente segura;
- recuperação de senha somente se houver fluxo implementado;
- seletor/controle de tema conforme Framework;
- fundo contextual documental/operacional sem comprometer legibilidade.

Não implementar links ou funcionalidades decorativas que não funcionem.

### Shell interno

O shell deverá seguir o conceito visual do mockup de Dashboard:

- sidebar fixa/recolhível conforme Framework;
- identidade Axiom Tools no topo;
- topbar com contexto operacional;
- área central de trabalho;
- identificação do usuário autenticado;
- controles globais somente quando funcionais;
- hierarquia clara entre navegação, título da página, KPIs e conteúdo operacional.

## Dashboard

A Dashboard deve seguir a composição do mockup oficial, priorizando:

- visão geral das rotinas;
- indicadores operacionais;
- destaque para `Estruturas de Pastas`;
- fila de atenção/conflitos quando houver dados reais;
- últimas operações;
- atividade recente quando houver fonte real;
- atalhos para módulos existentes;
- indicação clara para módulos futuros.

Enquanto outros módulos não existirem:

- não inventar números;
- não inventar clientes;
- não usar dados fictícios como se fossem reais;
- usar estados vazios orientativos;
- marcar módulos futuros como `Em implantação` quando necessário;
- não criar páginas vazias apenas para preencher menu.

Menu planejado:

- Dashboard;
- Estrutura de Pastas;
- Clientes;
- OCR;
- Competências;
- Conferência;
- Impressão;
- Configurações.

Na AXT-002, apenas `Dashboard` e `Estrutura de Pastas` precisam ter fluxo funcional completo. Os demais itens podem ser apresentados como indisponíveis/em implantação, sem rotas vazias enganosas.

## Integração com a AXT-001

A interface não poderá executar alterações físicas sem respeitar o fluxo seguro homologado:

`Inspecionar → Simular → Revisar → Confirmar → Aplicar → Resultado`

A fase `Simular` deve continuar estritamente não destrutiva e não pode alterar o filesystem.

Conflitos detectados pelo motor da AXT-001 devem ser apresentados ao usuário de forma explícita; a UI não pode ocultá-los, convertê-los automaticamente nem oferecer atalho que burle a confirmação.

## Fora de escopo

- cadastro completo de clientes;
- perfis/permissões complexos;
- OCR;
- competências;
- impressão;
- integrações governamentais;
- SSO definitivo com Axiom Enterprise, salvo decisão específica posterior.

## Critérios de aceite

- Login visualmente coerente com `docs/mockups/AXT-002_LOGIN_REFERENCIA.jpg`;
- Dashboard visualmente coerente com `docs/mockups/AXT-002_DASHBOARD_REFERENCIA.jpg`;
- login e logout funcionais;
- telas internas protegidas;
- interface não reimplementa regra de filesystem;
- Dashboard sem dados fictícios apresentados como reais;
- motor AXT-001 acessível por fluxo visual seguro;
- temas e responsividade funcionais;
- nenhum componente local divergente quando houver equivalente oficial no Framework;
- estados vazio, erro, loading, sucesso e indisponível tratados;
- testes da interface e dos fluxos críticos aprovados.

A AXT-002 não pode alterar o contrato funcional homologado da AXT-001.