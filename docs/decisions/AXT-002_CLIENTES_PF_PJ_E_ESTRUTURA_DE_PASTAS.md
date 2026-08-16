# AXT-002 — Clientes PF/PJ e Estrutura de Pastas

Status: Aprovado e corrigido conforme histórico do projeto  
Data: 16/08/2026

## 1. Regra de precedência

Este documento registra a estrutura de pastas efetivamente discutida e aprovada no histórico do Axiom Tools e substitui interpretações anteriores que tenham divergido desses nomes ou comportamentos.

A implementação deverá reconhecer estruturas legadas criadas pelos BATs anteriores, inclusive versões sem acentuação, sem duplicar pastas equivalentes.

## 2. Atualização conservadora

A criação/atualização de pastas deve ser incremental e não destrutiva:

- criar somente o que estiver faltando;
- localizar equivalentes com diferenças de acentuação ou nomenclatura já conhecidas;
- não duplicar pastas equivalentes;
- não excluir pastas;
- não excluir arquivos;
- não mover arquivos existentes automaticamente;
- não sobrescrever ou substituir arquivos existentes;
- preservar documentos e subpastas desconhecidas;
- corrigir/completar a estrutura sem apagar e reconstruir a árvore.

## 3. Estrutura oficial — Cliente PJ

A estrutura aprovada para Pessoa Jurídica é:

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

## 4. Estrutura oficial — Cliente PF

A estrutura aprovada para Pessoa Física utiliza a mesma base operacional da PJ, com as diferenças próprias de PF.

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

### Diferenças PF x PJ

- PF não cria `DAS - Simples Nacional`.
- PF utiliza `Inscrições - CAEPF, CEI e Estadual` no lugar de `CNPJ e Inscrição Estadual`.
- PF não utiliza `Contrato Social e Alterações`.
- A estrutura textual aprovada para PF manteve as demais pastas da PJ, inclusive `Notas Fiscais`.

### Compatibilidade com BAT legado

Os BATs anteriores podem apresentar nomes sem acentuação, como:

- `CNPJ e Inscricao Estadual`;
- `Inscricoes - CAEPF, CEI e Estadual`;
- `Declaracoes`;
- `Relatorios`;
- `Funcionarios`;
- `Rescisao`.

Esses nomes devem ser reconhecidos como equivalentes às formas atuais acentuadas. A atualização não deverá criar uma segunda pasta apenas por diferença de acentuação.

Algumas estruturas PF legadas podem não possuir `Notas Fiscais`; isso não autoriza exclusão ou reconstrução. A atualização deverá apenas completar a estrutura oficial quando executada.

## 5. Funcionários / Empregados

No fluxo de funcionário, o Axiom Tools deverá localizar tanto uma pasta chamada `Funcionários` quanto uma pasta legada chamada `Empregados`.

Não deverá criar `Funcionários` ao lado de `Empregados` se uma área equivalente já existir.

A pasta individual do funcionário deverá usar o nome completo informado.

A estrutura nova aprovada para funcionário é:

```text
<Nome Completo do Funcionário>/
├── Documentos Pessoais/
├── Documentos Gerados/
├── Documentos Escaneados/
└── Rescisão/
```

### Compatibilidade com estrutura antiga de funcionário

BATs anteriores também criavam a pasta `Exames`.

A regra atual é:

- se `Exames` já existir, preservar integralmente;
- não apagar nem mover seu conteúdo;
- a estrutura nova mínima aprovada possui quatro subpastas e não exige criar `Exames` automaticamente.

## 6. Situação do funcionário

O histórico do projeto aprovou funcionalidades de:

- `Alterar Situação`;
- `Reativar Funcionário`;
- `Corrigir Estrutura`.

A alteração de situação/demissão nunca poderá apagar o histórico do funcionário ou seus documentos.

Como o mecanismo exato de representação do status no filesystem não ficou consolidado de forma inequívoca no material recuperado, nenhuma Sprint poderá inventar movimentação destrutiva, exclusão ou substituição de arquivos para representar a situação.

## 7. `estrutura.cfg`

Estruturas legadas podem conter `estrutura.cfg` com metadados como:

```text
Tipo=<PF ou PJ>
VersaoEstrutura=1.0
```

O Axiom Tools deverá reconhecer esse arquivo como metadado de compatibilidade.

Sua existência não autoriza apagar/recriar a estrutura.

## 8. Nomes e equivalências

A aplicação deverá usar nomes canônicos em Português (Brasil), com acentuação, nas novas estruturas.

Ao atualizar estruturas existentes, deverá localizar equivalências conhecidas de acento/nomenclatura e reutilizar a pasta existente em vez de duplicá-la.

O nome original/legal do cliente ou funcionário deve ser preservado; normalização não poderá destruir a grafia de origem.