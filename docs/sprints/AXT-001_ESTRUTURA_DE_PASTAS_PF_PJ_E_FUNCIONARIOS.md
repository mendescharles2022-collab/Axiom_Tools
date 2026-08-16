# AXT-001 — Estrutura de Pastas PF/PJ e Funcionários

Versão: 2.0  
Data: 16/08/2026  
Status: **Atual — pronta para implementação do zero**  
Prioridade: Crítica

## Dependências obrigatórias

- `docs/STATUS_ATUAL.md`
- `docs/decisions/DEC-001_SEGURANCA_DOCUMENTAL_E_NAO_DESTRUICAO.md`
- `docs/decisions/DEC-002_ESTRUTURAS_PF_PJ_FUNCIONARIOS_E_LEGADO.md`
- `docs/decisions/DEC-005_REINICIO_DA_IMPLEMENTACAO_E_FONTE_DE_VERDADE.md`
- `docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md`

## 1. Objetivo

Construir do zero o primeiro módulo funcional do Axiom Tools: um motor seguro para criar, reconhecer, inspecionar e corrigir estruturas de pastas de clientes PF/PJ e funcionários sem destruir conteúdo existente.

A regra central é:

> **Criar somente o que estiver faltando e preservar tudo o que já existir.**

## 2. Escopo

Implementar:

- estrutura oficial de novo cliente PJ;
- estrutura oficial de novo cliente PF;
- criação incremental;
- inspeção somente leitura;
- planejamento/simulação sem alteração física;
- aplicação segura após plano;
- idempotência;
- equivalências legadas de acentuação/nomenclatura;
- compatibilidade com `Funcionários`, `Funcionarios` e `Empregados`;
- estrutura individual de funcionário;
- preservação de `Exames` legado;
- reconhecimento e criação controlada de `estrutura.cfg`;
- conflitos entre variantes equivalentes;
- conflito entre arquivo e diretório esperado;
- resultado estruturado/auditável;
- CLI/script mínimo para homologação técnica;
- testes automatizados em diretórios temporários.

## 3. Fora de escopo

Não implementar nesta Sprint:

- Login;
- Dashboard;
- interface gráfica completa;
- Axiom Framework;
- cadastro persistente de clientes;
- importação de planilha;
- SQLite;
- OCR;
- competência;
- conferência;
- visualização PDF;
- impressão;
- integrações com portais;
- mecanismo definitivo de demissão/reativação de funcionário.

Esses itens pertencem às Sprints posteriores.

## 4. Estrutura oficial — PJ

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

## 5. Estrutura oficial — PF

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

PF não cria `DAS - Simples Nacional`, `CNPJ e Inscrição Estadual` nem `Contrato Social e Alterações`.

## 6. Funcionários

Área funcional válida:

- `Funcionários`;
- `Funcionarios`;
- `Empregados`.

Novo funcionário:

```text
<Nome Completo do Funcionário>/
├── Documentos Pessoais/
├── Documentos Gerados/
├── Documentos Escaneados/
└── Rescisão/
```

`Exames` não é criada em funcionário novo. Se existir no legado, deve permanecer intocada.

## 7. `estrutura.cfg`

Na raiz do cliente.

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

Se já existir:

- ler sem destruir;
- preservar chaves desconhecidas;
- não sobrescrever silenciosamente;
- divergência de tipo gera conflito;
- não converter PF↔PJ automaticamente.

## 8. Planejamento e aplicação

Fluxo obrigatório:

```text
Inspecionar → Planejar/Simular → Revisar conflitos → Confirmar → Revalidar → Aplicar → Relatar
```

A simulação é 100% somente leitura. Ela não pode criar nem a pasta raiz.

Estados mínimos do plano:

- `EXISTE`;
- `CRIAR_PASTA`;
- `CRIAR_ARQUIVO_CONFIG`;
- `EQUIVALENTE_LEGADO`;
- `PRESERVAR`;
- `CONFLITO`;
- `IGNORADO_COM_SEGURANCA`.

## 9. Conflitos

São exemplos de conflito:

- `Tipo=PF` solicitado como PJ;
- `Tipo=PJ` solicitado como PF;
- `Declarações/` e `Declaracoes/` coexistindo como representações equivalentes;
- `Funcionários/` e `Empregados/` coexistindo com conteúdo relevante;
- arquivo existente onde o catálogo exige diretório;
- estado do filesystem alterado entre planejamento e aplicação.

Em conflito, preservar conteúdo e impedir apenas a ação incompatível.

## 10. Organização de código

Trabalhar principalmente em:

```text
src/axiom_tools/modules/folders/
```

Separar, no mínimo, as responsabilidades de:

- catálogo;
- modelos/resultado;
- matching/equivalências;
- inspeção;
- planejamento;
- aplicação/serviço;
- relatório.

A nomenclatura interna pode variar. Preferir arquivos próximos de 300 linhas e evitar ultrapassar 500 sem justificativa.

A CLI não pode conter regra de negócio que deveria estar no módulo `folders`.

## 11. CLI de homologação

Pode usar `argparse` da biblioteca padrão.

Deve permitir, no mínimo:

- informar pasta-base de teste;
- PF/PJ;
- nome do cliente;
- simular;
- visualizar plano;
- aplicar somente após confirmação explícita;
- apontar pasta existente;
- informar funcionário;
- simular/corrigir funcionário.

Nunca vir configurada para apontar automaticamente para a árvore real do escritório.

## 12. Testes obrigatórios

Todos em diretórios temporários isolados.

Cobrir:

- árvore exata PJ;
- árvore exata PF;
- ausência de DAS para PF;
- `Notas Fiscais` para PF e PJ;
- segunda execução idempotente;
- equivalências sem acento;
- case-insensitive esperado no Windows;
- `Funcionários`/`Funcionarios`/`Empregados`;
- funcionário novo com exatamente quatro subpastas;
- preservação de `Exames`;
- preservação de pasta desconhecida;
- preservação byte a byte de arquivos existentes;
- `mtime` de arquivos existentes não alterado pelo motor;
- `estrutura.cfg` novo/existente;
- chaves desconhecidas preservadas;
- divergência PF/PJ bloqueante;
- conflito entre equivalentes coexistentes;
- conflito arquivo x diretório;
- simulação criando zero artefatos;
- revalidação antes de aplicar;
- nenhuma exclusão/movimentação automática.

## 13. Critérios de aceite

A Sprint só pode ser homologada se:

1. todos os testes automatizados passarem;
2. simulação for realmente somente leitura;
3. criação de PF/PJ for exata;
4. segunda execução não criar duplicidade;
5. legado for reconhecido sem renomear/mover;
6. conflitos forem reportados sem conversão automática;
7. arquivos existentes permanecerem intactos;
8. regras estiverem separadas da CLI;
9. não houver código destrutivo no fluxo funcional;
10. a implementação não antecipar AXT-002 ou posteriores.

## 14. Entrega esperada do executor

O executor deve fornecer arquivos completos, com caminho, função e conteúdo, conforme o fluxo operacional adotado pelo usuário.

Ao final, produzir `RELATORIO_AXT-001.md` contendo:

- arquivos criados/alterados;
- arquitetura implementada;
- testes executados e resultados;
- confirmação de uso exclusivo de diretórios temporários nos testes;
- limitações reais restantes.

Não criar Sprint corretiva para defeitos encontrados na própria AXT-001: corrigir dentro dela antes de homologação.