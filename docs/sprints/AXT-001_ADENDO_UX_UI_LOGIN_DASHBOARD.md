# AXT-001 — Adendo Obrigatório de UX/UI: Login e Dashboard

Versão: 1.0  
Data: 16/08/2026  
Status: Obrigatório e integrante da AXT-001  
Tipo: Especificação funcional de UX/UI do produto

> Este documento **não é uma nova Sprint**. Deve ser executado junto com `AXT-001_ESTRUTURA_DE_PASTAS_PF_PJ_E_FUNCIONARIOS.md`.

---

# IMPORTANTE AO MATT

A referência visual aprovada para o Axiom Tools é composta por dois mockups definidos na homologação do projeto:

1. login corporativo em tela cheia, com painel legível sobre fundo relacionado a documentos/organização;
2. dashboard operacional com sidebar, topbar, KPIs, painel de estruturas, fila de atenção, operações e atividade recente.

Os mockups definem **composição, densidade, hierarquia e sensação visual**. Eles não autorizam copiar CSS arbitrário ou criar um Design System próprio.

O Axiom Tools é consumidor do **Axiom Framework**.

Leitura obrigatória no repositório `Axiom_Framework`:

- `006_Interface/AFX-071_Interface_Standards.md`;
- `006_Interface/AFX-072_Design_System.md`;
- `006_Interface/AFX-073_Layout_Guidelines.md`;
- `006_Interface/AFX-074_Forms.md`;
- `006_Interface/AFX-075_Buttons_and_Actions.md`;
- `006_Interface/AFX-076_Navigation.md`;
- `006_Interface/AFX-079_Accessibility.md`;
- `006_Interface/AFX-080_Responsive_Design.md`;
- `002_Architecture/AFX-026_Shared_Components.md`.

É proibido duplicar localmente componente, CSS ou template oficial do Framework quando houver componente compartilhado equivalente.

---

# 1. OBJETIVO

A AXT-001 deverá entregar, além do motor de pastas:

- tela de login funcional;
- logout funcional;
- sessão autenticada;
- proteção das telas internas;
- shell principal do Axiom Tools;
- dashboard operacional funcional;
- menu lateral;
- topbar;
- tema claro, escuro e automático;
- acesso funcional ao módulo `Estrutura de Pastas`;
- estados visuais obrigatórios;
- responsividade básica homologável.

A interface não deve ser uma demonstração estática. Tudo que aparecer como funcional deverá possuir comportamento real ou estado explícito de `Em implantação`.

---

# 2. PRINCÍPIO VISUAL

A aparência deve transmitir:

- software corporativo maduro;
- ambiente interno do escritório;
- organização documental;
- segurança;
- clareza;
- baixa poluição visual;
- alto aproveitamento da tela;
- consistência com os demais produtos Axiom.

Evitar:

- aparência de CRUD genérico;
- gradientes exagerados;
- excesso de cor;
- cards puramente decorativos;
- grandes áreas vazias sem função;
- efeitos chamativos;
- glassmorphism que reduza legibilidade;
- ícones sem rótulo quando a função não for inequívoca.

---

# 3. DESIGN SYSTEM E CORES

Usar obrigatoriamente tokens e componentes do Axiom Framework.

O código do Axiom Tools não deverá espalhar HEX/RGB próprios para reproduzir o mockup.

A cor predominante deverá entrar por:

```css
--ax-system-primary
```

A tonalidade azul mostrada no mockup é **direção visual**, não autorização para criar paleta paralela. Enquanto a cor oficial do Axiom Tools não estiver homologada no Axiom Framework, manter a implementação preparada para receber `--ax-system-primary` sem retrabalho.

Estados `success`, `warning`, `danger` e `info` continuam usando os tokens semânticos do Framework.

---

# 4. ARQUITETURA DO SHELL

O shell deverá seguir a arquitetura oficial:

```text
ax-shell
├── ax-sidebar
└── ax-workspace
    ├── ax-topbar
    ├── ax-content
    └── ax-footer
```

Desktop:

- sidebar: 272 px;
- recolhida: 72 px;
- topbar: mínimo 64 px;
- conteúdo principal com grid de 12 colunas;
- gutter padrão: 24 px;
- largura útil máxima controlada pelo Framework;
- sem scroll horizontal global.

A sidebar deverá ser recolhível e lembrar a preferência do usuário.

---

# 5. TELA DE LOGIN

## 5.1 Composição

A tela de login deverá ocupar 100% da viewport.

Estrutura visual:

```text
┌──────────────────────────────────────────────────────────────┐
│ Axiom Tools                          Claro Escuro Automático │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────────────┐        fundo documental           │
│   │ logo + Axiom Tools   │        discreto e desfocado       │
│   │ subtítulo            │                                   │
│   │                      │        elementos conceituais:      │
│   │ Usuário              │        pastas / PDFs / OCR         │
│   │ [______________]     │                                   │
│   │ Senha                │                                   │
│   │ [______________] 👁  │                                   │
│   │                      │                                   │
│   │ [ ] Manter conectado│                                   │
│   │                      │                                   │
│   │      [ Entrar ]      │                                   │
│   │                      │                                   │
│   │ Ambiente interno     │                                   │
│   └──────────────────────┘                                   │
│                                                              │
│            Axiom Tools · versão                              │
└──────────────────────────────────────────────────────────────┘
```

## 5.2 Painel

O painel deverá:

- ficar preferencialmente à esquerda no desktop;
- possuir largura confortável aproximada de 480–560 px;
- usar superfície sólida/translúcida somente se o contraste for comprovado;
- ter borda, raio e sombra via tokens do Framework;
- manter hierarquia visual limpa;
- não ficar excessivamente estreito ou flutuando como pequeno modal.

## 5.3 Identidade

Exibir:

- símbolo/logotipo oficial disponível do Axiom Tools;
- nome `Axiom Tools`;
- subtítulo: `Automação documental e organização operacional`;
- indicação discreta `Ambiente interno do escritório`.

Não inventar slogan próprio do produto além do que estiver aprovado.

## 5.4 Campos

Campos mínimos:

- `Usuário`;
- `Senha`;
- controle de mostrar/ocultar senha;
- `Manter conectado`, se houver implementação segura correspondente.

Labels devem permanecer visíveis. Placeholder não substitui label.

Altura mínima dos controles: 44 px.

## 5.5 Ação principal

Uma única ação primária:

`Entrar`

Comportamentos obrigatórios:

- loading após envio;
- bloquear duplo envio;
- erro inline acionável;
- preservar usuário informado após erro;
- senha não deve permanecer exposta;
- foco vai ao primeiro campo inválido;
- Enter envia o formulário quando apropriado.

## 5.6 Recuperação de senha

Não exibir link falso ou sem comportamento.

Se recuperação de senha não fizer parte da autenticação inicial, ocultar `Esqueci minha senha` até existir fluxo real. O mockup não autoriza criar ação morta.

## 5.7 Tema

Disponibilizar:

- Claro;
- Escuro;
- Automático.

`Automático` segue preferência do sistema operacional/navegador.

A seleção deverá persistir.

---

# 6. AUTENTICAÇÃO DA AXT-001

Esta Sprint não deve construir o módulo definitivo de usuários, perfis e permissões.

Entretanto, o login precisa ser real.

Implementar uma autenticação local de fundação, desacoplada do módulo de pastas e preparada para substituição futura pela autenticação central do Ecossistema Axiom.

Requisitos mínimos:

- senha nunca em texto puro no repositório;
- armazenamento de credencial temporária por hash seguro ou configuração protegida;
- sessão autenticada;
- expiração de sessão configurável;
- logout;
- rotas internas protegidas;
- cookie de sessão com flags de segurança adequadas ao ambiente;
- nenhum segredo versionado no GitHub;
- arquitetura que permita trocar o provedor de autenticação sem reescrever templates e módulos funcionais.

Não implementar nesta Sprint gestão completa de usuários/perfis/permissões.

---

# 7. DASHBOARD — COMPOSIÇÃO

Após login, o usuário deverá cair no `Dashboard`.

Estrutura:

```text
┌───────────────┬─────────────────────────────────────────────┐
│ Sidebar       │ Topbar                                      │
│               ├─────────────────────────────────────────────┤
│ Dashboard     │ Dashboard                                   │
│ Estrutura     │ Visão geral das rotinas do Axiom Tools      │
│ Clientes      │                                             │
│ OCR           │ [KPI] [KPI] [KPI] [KPI]                    │
│ Competências  │                                             │
│ Conferência   │ [ Estruturas de Pastas ] [Fila de atenção] │
│ Impressão     │ [ PF             PJ      ]                  │
│ Configurações │                                             │
│               │ [ Últimas operações ] [Atividade recente]  │
└───────────────┴─────────────────────────────────────────────┘
```

---

# 8. SIDEBAR

Ordem visual aprovada:

1. Dashboard
2. Estrutura de Pastas
3. Clientes
4. OCR
5. Competências
6. Conferência
7. Impressão
8. Configurações

Na AXT-001:

- `Dashboard` funcional;
- `Estrutura de Pastas` funcional;
- demais módulos podem aparecer como `Em implantação`, desde que não pareçam links funcionais quebrados;
- não criar páginas vazias apenas para preencher menu;
- item atual deve ter destaque e `aria-current`;
- sidebar recolhível no desktop;
- no móvel, usar offcanvas conforme Framework.

O nome dos módulos deve permanecer em Português (Brasil), preservando siglas técnicas.

---

# 9. TOPBAR

A topbar deverá conter, conforme disponibilidade funcional:

- botão de menu/recolhimento;
- pesquisa global quando houver conteúdo pesquisável real;
- identificação do contexto `Painel Operacional`;
- saudação ao usuário autenticado;
- seletor/atalho de tema;
- avatar/iniciais;
- menu do usuário com `Sair`.

Não exibir busca global fake nesta Sprint. Se ainda não houver índice pesquisável, omitir ou apresentar estado claramente indisponível sem ocupar protagonismo.

Notificações só deverão aparecer quando existir fonte real de notificações/pendências.

---

# 10. KPIs DO DASHBOARD NA AXT-001

O mockup contém números ilustrativos. **Nunca gravar números fictícios na aplicação.**

Na AXT-001, os KPIs devem derivar de dados reais da execução do motor de pastas.

KPIs recomendados:

1. `Estruturas analisadas`;
2. `Correções pendentes`;
3. `Conflitos detectados`;
4. `Ações concluídas hoje`.

Se ainda não houver operações:

- mostrar `0`;
- apresentar texto útil;
- não inventar dados demonstrativos em produção.

---

# 11. CARD PRINCIPAL — ESTRUTURAS DE PASTAS

Este é o principal bloco funcional da dashboard na AXT-001.

Título:

`Estruturas de Pastas`

Dividir visualmente em:

- `PF — Pessoa Física`;
- `PJ — Pessoa Jurídica`.

Apresentar somente métricas reais disponíveis, como:

- analisadas;
- conformes;
- correções pendentes;
- conflitos;
- estruturas legadas reconhecidas.

A ação primária do bloco:

`Criar / Corrigir Estrutura`

Essa ação leva ao fluxo funcional do módulo de pastas.

Não executar alteração física imediatamente ao clicar. O fluxo deve respeitar:

`Selecionar → Inspecionar → Simular → Revisar plano → Confirmar → Aplicar → Resultado`.

---

# 12. FILA DE ATENÇÃO

Card lateral `Fila de atenção`.

Categorias possíveis, quando realmente existentes:

- `Estrutura incompleta`;
- `Pasta legada detectada`;
- `Conflito de nomenclatura`;
- `Funcionário sem estrutura`;
- `estrutura.cfg divergente`.

Cada item deverá apresentar:

- ícone;
- rótulo textual;
- quantidade;
- acesso ao detalhe quando funcional.

Cor não poderá ser o único indicador de severidade.

---

# 13. ÚLTIMAS OPERAÇÕES

Tabela compacta com colunas:

- Cliente/Pasta;
- Tipo;
- Ação;
- Status;
- Data/Hora.

Status possíveis:

- `Simulado`;
- `Concluído`;
- `Atenção`;
- `Conflito`;
- `Falhou`.

A tabela deve vir de resultados reais da camada de operações da AXT-001.

Não usar dados fictícios fora de ambiente explicitamente marcado como demonstração/teste.

---

# 14. ATIVIDADE RECENTE

Exibir eventos reais como:

- estrutura criada;
- estrutura corrigida;
- equivalência legada reconhecida;
- conflito detectado;
- funcionário criado/corrigido;
- simulação concluída.

A atividade recente deverá possuir estado vazio digno:

`Nenhuma operação registrada ainda. Use “Criar / Corrigir Estrutura” para iniciar.`

---

# 15. MÓDULOS

O mockup possui atalhos de módulos.

Na AXT-001:

- `Estrutura de Pastas`: ativo;
- módulos futuros: visualmente identificados como `Em implantação` ou omitidos;
- não permitir clique que leve a tela vazia/404;
- não utilizar cards apenas ornamentais.

---

# 16. FLUXO UX — CRIAR / CORRIGIR ESTRUTURA

O fluxo principal deverá ser visual e seguro.

## Etapa 1 — Origem

Usuário escolhe:

- Pessoa Física ou Pessoa Jurídica;
- nova estrutura ou estrutura existente;
- pasta-base/diretório alvo;
- nome do cliente quando aplicável.

## Etapa 2 — Inspeção

Sistema lê a árvore sem alterá-la.

Exibir:

- estrutura reconhecida;
- equivalências legadas;
- itens ausentes;
- itens desconhecidos preservados;
- conflitos.

## Etapa 3 — Simulação

Exibir plano agrupado por status:

- Criar;
- Já existe;
- Legado reconhecido;
- Preservar;
- Atenção;
- Conflito.

## Etapa 4 — Confirmação

Botão primário:

`Aplicar alterações seguras`

Botão secundário:

`Voltar`

Se houver conflito bloqueante, não liberar a ação correspondente sem resolução segura.

## Etapa 5 — Resultado

Exibir resumo:

- criadas;
- preservadas;
- equivalências;
- conflitos não alterados;
- erros;
- caminho processado;
- data/hora.

A próxima ação deve ser clara.

---

# 17. ESTADOS OBRIGATÓRIOS

Todas as telas/componentes relevantes deverão tratar:

- loading;
- vazio;
- erro;
- sucesso;
- atenção;
- conflito;
- desabilitado;
- sem permissão, quando aplicável futuramente.

Hover não pode deslocar layout.

Focus deve permanecer visível por teclado.

Mensagens de erro devem ficar próximas à origem e explicar o que o usuário pode fazer.

---

# 18. RESPONSIVIDADE

Testar obrigatoriamente:

- 360 px;
- 768 px;
- 1024 px;
- 1440 px;
- zoom 200%.

Regras:

### Até 767 px

- uma coluna;
- sidebar em offcanvas;
- dashboard empilhado;
- ações principais em largura adequada;
- tabelas adaptadas, sem scroll horizontal da página inteira.

### 768–1199 px

- conteúdo prioritário em largura total;
- complementos em até duas colunas;
- sidebar conforme comportamento oficial.

### ≥1200 px

- dashboard próximo à composição do mockup;
- KPIs em linha quando houver espaço;
- bloco principal + fila de atenção em composição lateral;
- sem esticar cards apenas para preencher tela.

---

# 19. ACESSIBILIDADE E TECLADO

Requisitos mínimos:

- navegação completa por teclado;
- foco visível;
- labels persistentes;
- `aria-current` no menu atual;
- nomes acessíveis para botões de ícone;
- contraste adequado nos dois temas;
- mensagens não dependem apenas de cor;
- Escape fecha offcanvas/dropdowns quando apropriado;
- ordem visual e semântica equivalentes.

---

# 20. ESTRUTURA SUGERIDA DE INTERFACE

A implementação deverá respeitar a arquitetura real do projeto e o pacote compartilhado do Framework.

Separação funcional sugerida:

```text
src/axiom_tools/
├── web/ ou ui/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   └── folders.py
│   ├── services/
│   │   └── dashboard_service.py
│   └── view_models/
├── modules/
│   └── folders/
└── core/
    └── auth/
```

Templates devem estender/consumir componentes oficiais do Framework quando disponíveis.

Não misturar regras de filesystem diretamente dentro de template, JavaScript ou rota HTTP.

Dashboard apenas lê resultados/serviços; quem altera filesystem continua sendo o módulo `folders` da AXT-001.

---

# 21. CRITÉRIOS VISUAIS DE ACEITE

A entrega será reprovada visualmente se:

- parecer CRUD genérico;
- sidebar/topbar divergirem do Axiom Framework;
- login parecer modal pequeno no centro sem relação com o mockup;
- dashboard for apenas uma página vazia com botões;
- houver cards decorativos sem dado/ação real;
- existirem textos em inglês na interface sem justificativa técnica;
- tema escuro estiver incompleto;
- houver valores mockados apresentados como dados reais;
- o layout quebrar em 1024 ou 1440 px;
- a página gerar scroll horizontal global;
- forem copiados CSS/templates do Framework para customização local;
- o módulo de pastas tiver lógica duplicada dentro da camada de interface.

---

# 22. CRITÉRIOS FUNCIONAIS DE ACEITE

Além dos critérios originais da AXT-001:

1. login funciona;
2. credencial não fica em texto puro;
3. rota interna sem sessão redireciona ao login;
4. logout encerra sessão;
5. tema Claro/Escuro/Automático funciona e persiste;
6. dashboard abre após login;
7. `Estrutura de Pastas` abre pelo menu;
8. `Criar / Corrigir Estrutura` inicia o fluxo seguro;
9. simulação precede qualquer alteração física;
10. dashboard não apresenta dados fictícios como reais;
11. itens futuros não levam a páginas quebradas;
12. estados vazios e erros possuem tratamento visual;
13. navegação funciona por teclado;
14. responsividade mínima é homologada;
15. componentes compartilhados são consumidos do Framework sem bifurcação local.

---

# 23. RELATÓRIO DO MATT

O `RELATORIO_AXT-001.md` deverá ganhar uma seção `UX/UI`, informando:

- estrutura da interface implementada;
- arquivos de interface criados/alterados;
- versão/referência do Axiom Framework consumida;
- componentes oficiais reutilizados;
- comportamento da autenticação temporária;
- comportamento de temas;
- testes de responsividade;
- testes de teclado;
- estados vazios/erro/loading testados;
- divergências justificadas em relação aos mockups;
- confirmação de que nenhum dado fictício aparece como dado operacional real.

---

# 24. REGRA FINAL

O objetivo não é reproduzir uma imagem pixel a pixel.

O objetivo é entregar o **mesmo produto visual e a mesma experiência percebida**, usando corretamente o Axiom Framework, mantendo o Axiom Tools funcional, seguro e evolutivo.

Quando houver conflito entre detalhe ilustrativo do mockup e regra normativa do Axiom Framework, prevalece o Framework, preservando-se a intenção visual do mockup.