# AXT-001 — Estrutura de Pastas PF/PJ e Funcionários

Versão: 1.0  
Data: 16/08/2026  
Prioridade: Crítica  
Tipo: Fundação funcional / Filesystem seguro

## Dependências

- AXT-000 — Fundação do Axiom Tools
- `docs/decisions/AXT-001_SEGURANCA_PRESERVACAO_E_RASTREABILIDADE.md`
- `docs/decisions/AXT-002_CLIENTES_PF_PJ_E_ESTRUTURA_DE_PASTAS.md`
- `docs/architecture/ARQUITETURA_OFICIAL_AXIOM_TOOLS.md`

---

# IMPORTANTE AO MATT

Esta é a primeira Sprint funcional do Axiom Tools.

Ela **não cria o cadastro completo de clientes**.

Ela **não implementa OCR**.

Ela **não implementa competências, conferência mensal ou impressão em lote**.

Ela **não deve criar um sistema monolítico**.

O objetivo é construir e homologar primeiro o componente mais sensível do projeto: o **motor seguro de criação, reconhecimento, correção e atualização das estruturas físicas de pastas de clientes e funcionários**.

O Axiom Tools trabalhará futuramente sobre arquivos reais do escritório. Portanto, nesta Sprint, segurança do filesystem é requisito funcional e não detalhe técnico.

A regra principal é simples:

> **criar somente o que estiver faltando e preservar absolutamente tudo o que já existe.**

Nenhuma implementação será aceita se puder apagar, substituir, sobrescrever, mover ou reconstruir automaticamente documentos já existentes.

---

# 1. OBJETIVO

Entregar um motor modular capaz de:

1. criar a estrutura oficial de um novo cliente PJ;
2. criar a estrutura oficial de um novo cliente PF;
3. reconhecer uma estrutura já existente;
4. reconhecer equivalentes legados sem acentuação;
5. atualizar/corrigir uma estrutura existente criando somente pastas ausentes;
6. localizar tanto `Funcionários` quanto `Empregados`;
7. criar a pasta individual de um funcionário;
8. corrigir a estrutura de um funcionário existente;
9. reconhecer e preservar conteúdo legado;
10. gerar uma simulação/plano antes de modificar o filesystem;
11. produzir resultado auditável da operação;
12. ser idempotente: executar duas vezes não deve criar duplicidades.

---

# 2. PRINCÍPIO NÃO DESTRUTIVO

São proibições absolutas nesta Sprint:

- excluir arquivos;
- excluir pastas;
- mover arquivos existentes automaticamente;
- mover pastas existentes automaticamente;
- sobrescrever arquivos;
- substituir arquivos existentes;
- limpar conteúdo de diretórios;
- renomear automaticamente pasta legada apenas para padronizar acentuação;
- mesclar automaticamente duas pastas equivalentes que já possuam conteúdo;
- reconstruir a árvore apagando a anterior;
- alterar arquivos desconhecidos;
- usar `shutil.rmtree`, exclusões recursivas ou comportamento equivalente no fluxo funcional.

Se uma situação não puder ser resolvida com segurança, o motor deverá **reportar a divergência e não tomar uma decisão destrutiva**.

---

# 3. ESTRUTURA OFICIAL — PESSOA JURÍDICA

Para novos clientes PJ, usar os nomes canônicos em Português (Brasil), com acentuação:

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

Não simplificar, reorganizar ou trocar esses nomes sem decisão posterior aprovada.

---

# 4. ESTRUTURA OFICIAL — PESSOA FÍSICA

Para novos clientes PF:

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

## Diferenças obrigatórias PF x PJ

PF:

- **não** cria `DAS - Simples Nacional`;
- usa `Inscrições - CAEPF, CEI e Estadual`;
- **não** cria `CNPJ e Inscrição Estadual`;
- **não** cria `Contrato Social e Alterações`.

A estrutura textual aprovada para PF manteve as demais pastas da PJ, inclusive `Notas Fiscais`.

---

# 5. COMPATIBILIDADE COM OS BATs ANTERIORES

O escritório já utilizou BATs para criar estruturas.

Por isso, o motor não pode considerar diferenças de acentuação como pastas diferentes.

Exemplos de equivalência que devem ser reconhecidos:

| Canônico atual | Legado conhecido |
|---|---|
| `CNPJ e Inscrição Estadual` | `CNPJ e Inscricao Estadual` |
| `Inscrições - CAEPF, CEI e Estadual` | `Inscricoes - CAEPF, CEI e Estadual` |
| `Declarações` | `Declaracoes` |
| `Relatórios` | `Relatorios` |
| `Funcionários` | `Funcionarios` |
| `Rescisão` | `Rescisao` |

A comparação no Windows também deverá respeitar a natureza case-insensitive do filesystem e evitar duplicidades apenas por variação de maiúsculas/minúsculas.

## Regra

Se a pasta legada equivalente já existir:

- reutilizar a pasta existente;
- não criar a versão acentuada ao lado dela;
- não renomear automaticamente;
- não mover o conteúdo;
- registrar no resultado que foi reconhecida uma equivalência legada.

---

# 6. AMBIGUIDADES E CONFLITOS

Se duas estruturas equivalentes coexistirem, por exemplo:

```text
Funcionários/
Empregados/
```

ou duas variantes que representem o mesmo papel funcional e ambas possuam conteúdo, o motor **não deverá mesclar nem mover nada automaticamente**.

Deverá:

1. sinalizar `CONFLITO`;
2. descrever as duas localizações;
3. interromper somente a operação que depende dessa escolha;
4. preservar integralmente as duas árvores.

O restante do plano que não dependa do conflito poderá continuar, desde que seja seguro.

---

# 7. `estrutura.cfg`

Estruturas anteriores podem conter arquivo `estrutura.cfg`.

Formato legado conhecido:

```text
Tipo=PJ
VersaoEstrutura=1.0
```

ou:

```text
Tipo=PF
VersaoEstrutura=1.0
```

## Regras

- reconhecer `estrutura.cfg` quando existir;
- não apagar o arquivo;
- não substituir silenciosamente seu conteúdo;
- preservar chaves desconhecidas;
- detectar divergência entre `Tipo` informado e tipo solicitado;
- em divergência, reportar conflito e não converter a estrutura automaticamente;
- para nova estrutura, manter compatibilidade com as chaves `Tipo` e `VersaoEstrutura`;
- nesta Sprint, usar `VersaoEstrutura=1.0`, pois é o formato efetivamente conhecido do legado; qualquer nova versão exige decisão posterior explícita.

---

# 8. FUNCIONÁRIOS / EMPREGADOS

O histórico do projeto determinou que a rotina procure uma área chamada:

- `Funcionários`; ou
- `Empregados`.

A existência de `Empregados` deve ser tratada como estrutura legada válida.

## Regra de localização

- se existir somente `Funcionários`, usar essa pasta;
- se existir somente `Funcionarios`, reconhecer como equivalente;
- se existir somente `Empregados`, usar essa pasta;
- se nenhuma existir, em uma nova estrutura oficial criar `Funcionários`;
- se mais de uma área equivalente existir com conteúdo, reportar conflito e não mesclar automaticamente.

---

# 9. ESTRUTURA INDIVIDUAL DO FUNCIONÁRIO

A pasta individual deverá usar o **nome completo informado**.

A estrutura nova aprovada é exatamente:

```text
<Nome Completo do Funcionário>/
├── Documentos Pessoais/
├── Documentos Gerados/
├── Documentos Escaneados/
└── Rescisão/
```

Não adicionar novas subpastas por iniciativa própria.

## `Exames` legado

BATs anteriores também criavam:

```text
Exames/
```

O escopo posteriormente aprovado passou a utilizar quatro subpastas novas.

Portanto:

- **não criar `Exames` automaticamente em novo funcionário**;
- se `Exames` já existir em funcionário legado, preservar integralmente;
- `Corrigir Estrutura` não poderá remover `Exames`;
- conteúdo adicional desconhecido dentro da pasta do funcionário também deverá ser preservado.

---

# 10. SITUAÇÃO DO FUNCIONÁRIO

No histórico do projeto foram aprovadas funções futuras de:

- `Alterar Situação`;
- `Reativar Funcionário`;
- `Corrigir Estrutura`.

Nesta AXT-001, implementar integralmente **`Corrigir Estrutura`**.

`Alterar Situação` e `Reativar Funcionário` deverão ter seus contratos/encaixes previstos, mas **não inventar nesta Sprint um mecanismo de movimentação ou renomeação para representar demissão**, pois o mecanismo exato de persistência do status será consolidado junto ao núcleo cadastral.

Nenhuma mudança de situação poderá, futuramente, excluir documentos.

---

# 11. MOTOR DE PLANEJAMENTO

Toda alteração deverá passar primeiro por um plano de operação.

O motor deverá separar pelo menos duas fases:

## Fase A — Planejar / Simular

Inspeciona a árvore e retorna ações propostas, por exemplo:

- `EXISTE`;
- `CRIAR_PASTA`;
- `CRIAR_ARQUIVO_CONFIG`;
- `EQUIVALENTE_LEGADO`;
- `PRESERVAR`;
- `CONFLITO`;
- `IGNORADO_COM_SEGURANCA`.

Nenhuma alteração física ocorre nesta fase.

## Fase B — Aplicar

Executa somente as ações seguras produzidas pelo plano.

O código de execução não deverá descobrir uma nova regra destrutiva durante o `apply`. Se a realidade do filesystem mudar entre planejamento e execução, revalidar e abortar a ação conflitante.

---

# 12. OPERAÇÕES PRINCIPAIS

O módulo deverá expor serviços claros para, no mínimo:

1. `planejar_estrutura_cliente`;
2. `criar_ou_corrigir_estrutura_cliente`;
3. `planejar_estrutura_funcionario`;
4. `criar_ou_corrigir_estrutura_funcionario`;
5. `inspecionar_estrutura`;
6. `resolver_equivalencias_conhecidas`.

Os nomes internos podem seguir convenção Python em inglês ou português, desde que a responsabilidade seja equivalente e o relatório ao usuário use Português (Brasil).

Não concentrar toda a implementação em um único arquivo.

---

# 13. ORGANIZAÇÃO MÍNIMA DO CÓDIGO

Trabalhar dentro de:

```text
src/axiom_tools/modules/folders/
```

Separar responsabilidades, por exemplo:

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

A nomenclatura pode ser ajustada se houver justificativa, mas as responsabilidades deverão continuar separadas.

Evitar arquivos excessivamente grandes. Preferir arquivos de até aproximadamente 300 linhas; somente ultrapassar isso quando realmente necessário e sem criar arquivo monolítico.

---

# 14. INTERFACE MÍNIMA DE HOMOLOGAÇÃO

Não construir interface gráfica completa nesta Sprint.

Entregar uma forma simples e segura de homologar o motor localmente, por CLI/script, permitindo:

- informar pasta-base de teste;
- informar PF ou PJ;
- informar nome do cliente;
- simular criação/correção;
- visualizar o plano;
- executar após confirmação explícita;
- apontar uma pasta de cliente existente;
- informar nome completo de funcionário;
- simular/corrigir estrutura do funcionário.

A simulação deverá ser a ação padrão.

Nenhum script de homologação poderá vir configurado para apontar automaticamente para a pasta real dos clientes do escritório.

---

# 15. TESTES AUTOMATIZADOS OBRIGATÓRIOS

Usar diretórios temporários isolados.

Nunca executar testes automatizados sobre a árvore real do escritório.

Cobrir no mínimo:

### Cliente PJ novo

- cria exatamente a árvore oficial PJ;
- cria `DAS - Simples Nacional`;
- cria `Notas Fiscais`;
- cria `CNPJ e Inscrição Estadual`;
- cria `Contrato Social e Alterações`.

### Cliente PF novo

- cria exatamente a árvore oficial PF;
- não cria `DAS - Simples Nacional`;
- não cria `CNPJ e Inscrição Estadual`;
- não cria `Contrato Social e Alterações`;
- cria `Inscrições - CAEPF, CEI e Estadual`;
- cria `Notas Fiscais`.

### Idempotência

- executar a mesma atualização duas vezes não duplica nenhuma pasta;
- segunda execução resulta essencialmente em `EXISTE/PRESERVAR`.

### Acentuação / legado

- `Funcionarios` é reconhecido como `Funcionários`;
- `Declaracoes` é reconhecido como `Declarações`;
- `Relatorios` é reconhecido como `Relatórios`;
- `CNPJ e Inscricao Estadual` é reconhecido como equivalente;
- `Inscricoes - CAEPF, CEI e Estadual` é reconhecido como equivalente;
- não cria duplicatas acentuadas.

### Funcionários / Empregados

- estrutura com `Funcionários` é localizada;
- estrutura com `Empregados` é localizada;
- nova estrutura usa `Funcionários`;
- novo funcionário recebe exatamente as quatro subpastas aprovadas;
- `Exames` legado é preservado, mas não criado para funcionário novo.

### Preservação

Criar arquivos fictícios em diversas pastas antes da correção e comprovar que após a execução:

- continuam existentes;
- conteúdo permanece byte a byte idêntico;
- timestamps não são alterados intencionalmente pelo motor;
- não houve substituição.

### Pastas desconhecidas

- criar subpastas não previstas;
- executar correção;
- comprovar que permanecem intactas.

### Conflitos

- `Funcionários` e `Empregados` coexistindo;
- duas variantes equivalentes coexistindo;
- `estrutura.cfg` com tipo divergente;
- confirmar que o motor reporta e não mescla/apaga/converte automaticamente.

### `estrutura.cfg`

- reconhecer arquivo existente;
- preservar chaves desconhecidas;
- criar arquivo para estrutura nova;
- não sobrescrever silenciosamente arquivo existente.

---

# 16. RELATÓRIO DA OPERAÇÃO

A execução deverá produzir um resultado estruturado contendo, no mínimo:

- caminho-base;
- tipo PF/PJ;
- nome do cliente ou funcionário;
- data/hora;
- ações planejadas;
- ações executadas;
- pastas já existentes;
- equivalências legadas encontradas;
- itens preservados;
- conflitos;
- erros;
- resultado final.

Não é necessário nesta Sprint criar banco de auditoria definitivo; o resultado estruturado deve estar preparado para ser persistido futuramente pela AXT-002.

---

# 17. FORA DO ESCOPO

Não implementar nesta Sprint:

- cadastro completo de clientes;
- importação XLS/XLSX;
- banco definitivo de clientes;
- OCR;
- classificação documental;
- competência mensal;
- impressão em lote;
- integrações governamentais;
- exclusão cadastral;
- movimentação automática de clientes inativos;
- regras definitivas de demissão/reativação de funcionário;
- interface web completa;
- instalador final do Axiom Tools.

---

# 18. CRITÉRIOS DE ACEITE

A AXT-001 será considerada aprovada somente se:

1. a árvore PJ for criada conforme este documento;
2. a árvore PF for criada conforme este documento;
3. as diferenças PF/PJ estiverem corretas;
4. estruturas existentes forem atualizadas sem perda de conteúdo;
5. equivalências legadas forem reconhecidas sem duplicação;
6. `Funcionários` e `Empregados` forem tratados corretamente;
7. funcionário novo possuir exatamente as quatro subpastas aprovadas;
8. `Exames` legado for preservado;
9. reexecução for idempotente;
10. `estrutura.cfg` for tratado com segurança;
11. conflitos não produzirem merge/movimentação destrutiva;
12. a simulação mostrar claramente o que será feito;
13. todos os testes automatizados obrigatórios passarem;
14. nenhum teste depender de pasta real do escritório;
15. nenhuma rotina funcional apagar, mover, substituir ou sobrescrever arquivo existente;
16. o código permanecer modular e preparado para ser consumido pela AXT-002.

---

# 19. ENTREGÁVEIS DO MATT

Entregar um único pacote:

```text
AXIOM_TOOLS_AXT-001.zip
```

O pacote deverá conter:

- repositório/código atualizado da AXT-001;
- testes automatizados;
- interface mínima de homologação;
- `RELATORIO_AXT-001.md`;
- instruções simples de execução e teste.

O `RELATORIO_AXT-001.md` deverá informar:

- arquivos criados;
- arquivos alterados;
- arquitetura implementada;
- regras de equivalência;
- proteção contra operações destrutivas;
- testes executados e respectivos resultados;
- limitações reais ainda existentes;
- qualquer divergência encontrada no legado;
- confirmação explícita de que testes não foram executados na árvore real do escritório.

---

# 20. ORIENTAÇÃO DE ENTREGA

Não criar uma AXT-001A ou Sprint corretiva para defeitos encontrados durante a própria implementação.

Antes da entrega, realizar auditoria integral da AXT-001 e corrigir dentro desta mesma Sprint todo defeito tecnicamente solucionável.

A entrega deverá chegar pronta para nossa validação e homologação, preservando integralmente as decisões históricas consolidadas no repositório.