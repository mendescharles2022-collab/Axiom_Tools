# DEC-002 — Estruturas PF/PJ, Funcionários e Legado

Versão: 1.0  
Data: 16/08/2026  
Status: Permanente e vinculante

## 1. Estrutura oficial — Pessoa Jurídica

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

## 2. Estrutura oficial — Pessoa Física

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

## 3. Diferenças obrigatórias PF x PJ

PF:

- não cria `DAS - Simples Nacional`;
- usa `Inscrições - CAEPF, CEI e Estadual`;
- não cria `CNPJ e Inscrição Estadual`;
- não cria `Contrato Social e Alterações`;
- mantém `Notas Fiscais`.

## 4. Equivalências legadas conhecidas

Reconhecer sem duplicar:

| Canônico | Legado conhecido |
|---|---|
| `CNPJ e Inscrição Estadual` | `CNPJ e Inscricao Estadual` |
| `Inscrições - CAEPF, CEI e Estadual` | `Inscricoes - CAEPF, CEI e Estadual` |
| `Declarações` | `Declaracoes` |
| `Relatórios` | `Relatorios` |
| `Funcionários` | `Funcionarios` |
| `Rescisão` | `Rescisao` |

No Windows, considerar equivalência de maiúsculas/minúsculas conforme comportamento case-insensitive esperado do filesystem.

Se o legado equivalente existir:

- usar o existente;
- não criar versão acentuada ao lado;
- não renomear automaticamente;
- não mover conteúdo;
- registrar `EQUIVALENTE_LEGADO` no resultado.

## 5. Funcionários / Empregados

A área funcional pode existir como:

- `Funcionários`;
- `Funcionarios`;
- `Empregados`.

Regras:

- se apenas uma existir, usar a existente;
- se nenhuma existir em estrutura nova, criar `Funcionários`;
- se mais de uma equivalente coexistir com conteúdo, registrar conflito e não mesclar.

## 6. Estrutura individual do funcionário

Para novos funcionários:

```text
<Nome Completo do Funcionário>/
├── Documentos Pessoais/
├── Documentos Gerados/
├── Documentos Escaneados/
└── Rescisão/
```

Não adicionar subpastas por iniciativa própria.

### `Exames` legado

- não criar `Exames` em funcionário novo;
- se já existir em estrutura antiga, preservar integralmente;
- corrigir estrutura nunca remove `Exames` nem conteúdo desconhecido.

## 7. Situação do funcionário

As funções `Alterar Situação` e `Reativar Funcionário` são futuras.

A AXT-001 implementa somente `Corrigir Estrutura`. Não inventar mecanismo de demissão por renomeação ou movimentação de pasta.

## 8. `estrutura.cfg`

Fica na raiz da pasta do cliente.

PJ:

```text
Tipo=PJ
VersaoEstrutura=1.0
```

PF:

```text
Tipo=PF
VersaoEstrutura=1.0
```

Regras:

- reconhecer quando existir;
- preservar chaves desconhecidas;
- não sobrescrever silenciosamente;
- detectar divergência entre `Tipo` existente e solicitado;
- divergência de tipo é `CONFLITO` bloqueante para ações incompatíveis;
- nunca converter automaticamente PF em PJ ou PJ em PF;
- novas estruturas da AXT-001 usam `VersaoEstrutura=1.0` até decisão posterior explícita.

## 9. Conflitos de representação

Se um arquivo ocupar caminho onde a estrutura exige diretório, registrar conflito. Não tratar arquivo como pasta existente.

Se duas variantes equivalentes coexistirem, não criar terceira variante, não mesclar e não mover conteúdo.

Esta decisão é dependência obrigatória da AXT-001.