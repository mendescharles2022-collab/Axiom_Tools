# AXT-002 — Login, Shell e Dashboard

Versão: 1.0  
Data: 16/08/2026  
Status: **Planejada**

## Dependências

- AXT-001 homologada;
- `docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md`;
- Axiom Framework vigente.

## Objetivo

Introduzir a camada visual base do Axiom Tools sem misturar regras de filesystem à interface.

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

A referência aprovada é composta pelos mockups de Login e Dashboard definidos no projeto.

A implementação deve obedecer ao Axiom Framework como autoridade de UX/UI. Não criar Design System local paralelo e não usar o Axiom Tables como fonte normativa.

## Dashboard

Deve priorizar dados reais. Enquanto outros módulos não existirem:

- não inventar números;
- não inventar clientes;
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

Na AXT-002, apenas Dashboard e Estrutura de Pastas precisam ter fluxo funcional completo.

## Fora de escopo

- cadastro completo de clientes;
- perfis/permissões complexos;
- OCR;
- competências;
- impressão;
- integrações governamentais;
- SSO definitivo com Axiom Enterprise, salvo decisão específica posterior.

## Critérios de aceite

- login e logout funcionais;
- telas internas protegidas;
- interface não reimplementa regra de filesystem;
- Dashboard sem dados fictícios apresentados como reais;
- motor AXT-001 acessível por fluxo visual seguro;
- temas e responsividade funcionais;
- nenhum componente local divergente quando houver equivalente oficial no Framework;
- testes da interface e dos fluxos críticos aprovados.

A AXT-002 não pode alterar o contrato funcional homologado da AXT-001.