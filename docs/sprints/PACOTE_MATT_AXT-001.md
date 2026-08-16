# PACOTE MATT — AXT-001

Versão: 1.0  
Data: 16/08/2026  
Status: Arquivo único para execução pelo Matt

> Este é o único arquivo que Charles precisa encaminhar ao Matt para executar a AXT-001.
> Ele consolida Sprint funcional, UX/UI, regras de segurança, estrutura oficial de pastas e diretrizes necessárias do Axiom Framework.

---

# 1. OBJETIVO DA ENTREGA

Entregar a primeira versão funcional do Axiom Tools contendo:

- motor seguro de criação/correção de estruturas de pastas PF/PJ;
- estrutura de funcionários;
- compatibilidade com estruturas legadas dos BATs;
- simulação antes de executar alterações;
- login funcional;
- logout e sessão;
- shell principal do sistema;
- dashboard operacional;
- acesso visual ao módulo Estrutura de Pastas;
- tema claro, escuro e automático;
- testes automatizados;
- pacote completo do repositório.

Não implementar ainda OCR, competências, conferência mensal, impressão em lote ou cadastro completo/importação de clientes.

---

# 2. BASE TÉCNICA

- Python: 3.12 ou superior.
- Aplicação modular.
- Para CLI de homologação, preferir `argparse` da stdlib.
- Evitar dependências externas sem necessidade real.
- Entregar o repositório completo, não apenas `folders/`.

---

# 3. REGRA ABSOLUTA DE SEGURANÇA

O Axiom Tools trabalhará futuramente sobre arquivos reais do escritório.

Portanto:

- não excluir arquivos;
- não excluir pastas;
- não mover arquivos existentes automaticamente;
- não mover pastas existentes automaticamente;
- não sobrescrever arquivos;
- não substituir arquivos;
- não limpar diretórios;
- não reconstruir árvores apagando o conteúdo anterior;
- não mesclar estruturas ambíguas automaticamente;
- não renomear pasta legada apenas por acentuação;
- preservar pastas e arquivos desconhecidos.

A regra é: **criar apenas o que faltar e preservar tudo que já existir**.

Se houver conflito, reportar e não tomar decisão destrutiva.

---

# 4. ESTRUTURA OFICIAL — PJ

```text
<Cliente PJ>/
├── Arquivos/
│   ├── Atestados/
│   ├── Recolhimentos/
│   │   ├── DARF DCTFWeb/
│   │   ├── FGTS Digital/
│   │   ├── DAS - Simples Nacional/
│   │   └── Outros/
│   ├── Declarações/
│   ├── Relatórios/
│   ├── Notas Fiscais/
│   └── Arquivos Diversos/
├── CNPJ e Inscrição Estadual/
├── Contrato Social e Alterações/
├── Documentos Diversos/
├── Documentos do Responsável/
└── Funcionários/
```

---

# 5. ESTRUTURA OFICIAL — PF

```text
<Cliente PF>/
├── Inscrições - CAEPF, CEI e Estadual/
├── Arquivos/
│   ├── Atestados/
│   ├── Recolhimentos/
│   │   ├── DARF DCTFWeb/
│   │   ├── FGTS Digital/
│   │   └── Outros/
│   ├── Declarações/
│   ├── Relatórios/
│   ├── Notas Fiscais/
│   └── Arquivos Diversos/
├── Documentos do Responsável/
├── Documentos Diversos/
└── Funcionários/
```

Diferenças PF x PJ:

- PF não cria `DAS - Simples Nacional`;
- PF usa `Inscrições - CAEPF, CEI e Estadual`;
- PF não cria `CNPJ e Inscrição Estadual`;
- PF não cria `Contrato Social e Alterações`.

---

# 6. EQUIVALÊNCIAS LEGADAS

Reconhecer como equivalentes sem duplicar:

- `CNPJ e Inscricao Estadual` = `CNPJ e Inscrição Estadual`;
- `Inscricoes - CAEPF, CEI e Estadual` = `Inscrições - CAEPF, CEI e Estadual`;
- `Declaracoes` = `Declarações`;
- `Relatorios` = `Relatórios`;
- `Funcionarios` = `Funcionários`;
- `Rescisao` = `Rescisão`.

Também respeitar case-insensitive do Windows.

Se a pasta legada existir, usar a existente. Não renomear automaticamente.

---

# 7. FUNCIONÁRIOS / EMPREGADOS

A área funcional pode se chamar:

- `Funcionários`;
- `Funcionarios`;
- `Empregados`.

Se existir apenas uma delas, usar a existente.

Se não existir nenhuma, criar `Funcionários` em nova estrutura.

Se coexistirem estruturas equivalentes com conteúdo, reportar conflito e não mesclar.

Estrutura nova do funcionário:

```text
<Nome Completo do Funcionário>/
├── Documentos Pessoais/
├── Documentos Gerados/
├── Documentos Escaneados/
└── Rescisão/
```

Não criar `Exames` para funcionário novo.

Se `Exames` já existir no legado, preservar integralmente.

Implementar `Corrigir Estrutura`.

Não inventar nesta Sprint mecanismo definitivo de demissão/reativação.

---

# 8. ESTRUTURA.CFG

Fica na raiz da pasta do cliente.

Para nova PJ:

```text
Tipo=PJ
VersaoEstrutura=1.0
```

Para nova PF:

```text
Tipo=PF
VersaoEstrutura=1.0
```

Se já existir:

- reconhecer;
- preservar chaves desconhecidas;
- não sobrescrever silenciosamente;
- detectar divergência de tipo;
- em divergência, reportar conflito.

---

# 9. MOTOR DE PLANEJAMENTO

Toda alteração deve ter duas fases.

## Simular / Planejar

Não altera o filesystem.

Estados mínimos:

- `EXISTE`;
- `CRIAR_PASTA`;
- `CRIAR_ARQUIVO_CONFIG`;
- `EQUIVALENTE_LEGADO`;
- `PRESERVAR`;
- `CONFLITO`;
- `IGNORADO_COM_SEGURANCA`.

## Aplicar

Executar somente ações seguras já planejadas.

Se o filesystem mudar entre simulação e aplicação, revalidar antes de executar.

A simulação deve ser o comportamento padrão.

---

# 10. ORGANIZAÇÃO DE CÓDIGO

Trabalhar em:

```text
src/axiom_tools/modules/folders/
```

Separar responsabilidades. Estrutura sugerida:

```text
folders/
├── __init__.py
├── catalog.py
├── models.py
├── matcher.py
├── planner.py
├── service.py
└── report.py
```

Pode ajustar nomes, mas não concentrar tudo em um arquivo monolítico.

Preferir arquivos em torno de 300 linhas; ultrapassar somente quando necessário.

---

# 11. INTERFACE DE HOMOLOGAÇÃO DO MOTOR

Entregar também CLI/script simples que permita:

- escolher pasta-base de teste;
- informar PF/PJ;
- informar nome do cliente;
- simular;
- mostrar plano;
- aplicar após confirmação explícita;
- apontar cliente existente;
- informar funcionário;
- corrigir estrutura do funcionário.

Nunca apontar automaticamente para a árvore real do escritório.

---

# 12. UX/UI DO AXIOM TOOLS

A interface deve seguir o Axiom Framework.

Regras principais consolidadas:

- Bootstrap 5.3 como base;
- usar tokens oficiais do Framework;
- não criar Design System paralelo;
- não espalhar HEX/RGB próprios pelo projeto;
- usar `--ax-system-primary` para cor predominante;
- uma ação primária por contexto;
- labels sempre visíveis;
- controles com altura mínima de 44 px;
- estados loading, vazio, erro, sucesso, disabled e sem permissão;
- foco acessível;
- tema claro/escuro/automático;
- layout responsivo;
- sem scroll horizontal global.

Shell oficial:

```text
ax-shell
├── ax-sidebar
└── ax-workspace
    ├── ax-topbar
    ├── ax-content
    └── ax-footer
```

Desktop:

- sidebar 272 px;
- recolhida 72 px;
- topbar mínimo 64 px;
- grid 12 colunas;
- gutters 24 px.

---

# 13. LOGIN

Entregar tela de login funcional em tela cheia.

Elementos:

- Axiom Tools;
- subtítulo `Automação documental e organização operacional`;
- campo `Usuário`;
- campo `Senha`;
- mostrar/ocultar senha;
- botão `Entrar`;
- indicação `Ambiente interno do escritório`;
- tema Claro/Escuro/Automático;
- sessão funcional;
- logout funcional;
- proteção das telas internas.

`Manter conectado` somente se houver implementação segura correspondente.

Não exibir `Esqueci minha senha` se não houver fluxo real.

Comportamento obrigatório:

- loading;
- impedir duplo envio;
- erro inline;
- preservar usuário após erro;
- Enter envia formulário;
- foco no primeiro erro.

A referência visual é o mockup aprovado de login que Charles enviará junto deste arquivo.

---

# 14. DASHBOARD

A dashboard deve seguir o mockup aprovado, mas sem números fictícios apresentados como reais.

Menu lateral:

- Dashboard;
- Estrutura de Pastas;
- Clientes;
- OCR;
- Competências;
- Conferência;
- Impressão;
- Configurações.

Nesta Sprint, somente `Dashboard` e `Estrutura de Pastas` precisam estar realmente funcionais.

Demais módulos devem aparecer como `Em implantação` e não abrir páginas vazias sem contexto.

Dashboard com:

- título `Dashboard`;
- subtítulo `Visão geral das rotinas do Axiom Tools`;
- KPIs reais do motor de pastas, quando houver dados;
- card `Estruturas de Pastas`;
- ação `Criar / Corrigir Estrutura`;
- `Fila de atenção`;
- `Últimas operações`;
- `Atividade recente`;
- atalhos de módulos.

Se ainda não houver dados, usar estado vazio orientativo em vez de inventar números/clientes.

A referência visual é o mockup aprovado de dashboard que Charles enviará junto deste arquivo.

---

# 15. FLUXO VISUAL DE ESTRUTURA DE PASTAS

O fluxo da interface deve refletir a segurança do motor:

1. selecionar cliente/pasta;
2. indicar PF ou PJ quando necessário;
3. inspecionar estrutura;
4. simular correção/criação;
5. mostrar plano de ações;
6. destacar conflitos;
7. permitir revisão;
8. confirmar explicitamente;
9. aplicar somente ações seguras;
10. exibir relatório final.

Nunca pular diretamente da seleção para alteração silenciosa do filesystem.

---

# 16. TESTES AUTOMATIZADOS

Usar apenas diretórios temporários isolados.

Cobrir no mínimo:

- criação correta PJ;
- criação correta PF;
- ausência de DAS para PF;
- idempotência;
- equivalências legadas;
- `Funcionários` / `Funcionarios` / `Empregados`;
- funcionário novo com exatamente quatro subpastas;
- preservação de `Exames` legado;
- pastas desconhecidas preservadas;
- conflitos sem merge automático;
- `estrutura.cfg`;
- preservação byte a byte de arquivos existentes;
- `mtime` de arquivos existentes não alterado pelo motor;
- login correto/incorreto;
- proteção de rota/tela interna;
- logout;
- troca de tema;
- estados vazios da dashboard.

Não é necessário controlar `atime` do filesystem.

---

# 17. RELATÓRIO FINAL

Criar:

```text
RELATORIO_AXT-001.md
```

Formato Markdown organizado, sem template visual obrigatório.

Informar:

- arquivos criados;
- arquivos alterados;
- arquitetura implementada;
- motor de pastas;
- equivalências legadas;
- proteção não destrutiva;
- login/dashboard implementados;
- testes executados;
- resultados dos testes;
- limitações reais;
- divergências encontradas;
- confirmação explícita de que nenhum teste automatizado foi executado na árvore real do escritório.

---

# 18. ENTREGA

Entregar um único pacote:

```text
AXIOM_TOOLS_AXT-001.zip
```

O ZIP deve conter o repositório completo atualizado, incluindo:

- código;
- templates/interface;
- testes;
- scripts necessários;
- documentação;
- `RELATORIO_AXT-001.md`;
- instruções simples para executar e homologar.

Não criar AXT-001A para corrigir defeitos encontrados durante a implementação.

Auditar e corrigir a própria entrega antes de encaminhá-la.

---

# 19. O QUE CHARLES ENVIARÁ AO MATT

Para executar esta Sprint, Matt receberá apenas:

1. este arquivo `PACOTE_MATT_AXT-001.md`;
2. mockup visual aprovado da tela de login;
3. mockup visual aprovado da dashboard.

Nenhum outro MD é necessário para a execução desta Sprint.
