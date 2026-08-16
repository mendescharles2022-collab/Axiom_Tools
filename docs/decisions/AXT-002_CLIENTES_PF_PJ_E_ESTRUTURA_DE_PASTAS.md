# AXT-002 — Clientes PF/PJ e Estrutura de Pastas

Status: Aprovado  
Data: 16/08/2026

## 1. Cadastro de clientes

O Axiom Tools deverá trabalhar com clientes Pessoa Física (PF) e Pessoa Jurídica (PJ).

Cada cliente terá identificação cadastral suficiente para indexar documentos e localizar sua estrutura física, incluindo nome/razão social, CPF ou CNPJ, tipo PF/PJ, status e caminho de armazenamento.

O documento deverá ser único após normalização e servirá como chave de prevenção de duplicidade.

A base inicial poderá ser alimentada por planilha. O usuário deverá poder cadastrar, editar, inativar, reativar e excluir registros cadastrais que não devam permanecer na relação operacional.

A exclusão cadastral não exclui arquivos nem diretórios físicos.

## 2. Atualização de estruturas

A criação/atualização de pastas deve ser incremental:

- criar o que estiver faltando;
- reconhecer estrutura já existente;
- não excluir pastas desconhecidas;
- não recriar pasta apenas para corrigir estrutura;
- preservar documentos e subpastas existentes;
- registrar versão da estrutura quando aplicável.

Estruturas legadas produzidas por BATs devem ser reconhecidas e evoluídas com segurança.

## 3. Estrutura de referência — PJ

Estrutura consolidada de referência:

```text
<Cliente PJ>/
├── Arquivos/
│   ├── Atestados/
│   ├── Recolhimentos/
│   │   ├── DARF DCTFWeb/
│   │   ├── FGTS Digital/
│   │   ├── DAS SN/
│   │   └── Outros/
│   ├── Declarações/
│   ├── Relatórios/
│   ├── Notas Fiscais/
│   └── Arquivos Diversos/
├── CNPJ e IE/
├── Contrato Social e Alterações/
├── Documentos Diversos/
├── Documentos do Responsável/
└── Funcionários/
```

O sistema deverá permitir evolução futura sem quebrar estruturas existentes.

## 4. Estrutura de referência — PF

Estrutura consolidada de referência:

```text
<Cliente PF>/
├── Inscrições/
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
├── Documentos Diversos/
├── Documentos do Responsável/
└── Funcionários/
```

A estrutura PF não deve criar `DAS SN` por padrão.

A pasta `Inscrições` poderá receber documentos como CAEPF, CEI, Inscrição Estadual e CNO conforme a realidade do cliente e as regras aprovadas em Sprint.

## 5. Funcionários/empregados

O sistema deverá reconhecer a área de funcionários existente e criar estruturas individuais sem destruir conteúdo anterior.

Estrutura funcional consolidada:

```text
<Funcionário>/
├── Documentos Pessoais/
├── Documentos Escaneados/
├── Documentos Gerados/
└── Rescisão/
```

Pastas legadas adicionais, inclusive `Exames`, deverão ser preservadas quando existentes.

O sistema deverá suportar a identificação de empregado demitido sem apagar seu histórico. A marcação `Demitido` poderá ser utilizada na convenção de organização, desde que a implementação preserve rastreabilidade e documentos.

## 6. Nomes

O nome físico da pasta deverá seguir regra de normalização controlada e previsível, sem destruir a grafia legal armazenada no cadastro.

Casos especiais e siglas devem poder ser preservados.

## 7. Arquivo de estrutura legado

Estruturas anteriores podem conter metadados como `estrutura.cfg`, incluindo tipo do cliente e versão da estrutura.

O Axiom Tools deverá tratar esse tipo de metadado como fonte de compatibilidade, não como autorização para apagar/recriar a árvore.