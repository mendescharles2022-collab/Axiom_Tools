# Arquitetura Oficial — Axiom Tools

Versão: 1.0  
Data: 16/08/2026

## 1. Objetivo arquitetural

O Axiom Tools deve permanecer uma aplicação utilitária modular, voltada ao ambiente Windows do escritório e capaz de operar sobre estruturas reais de arquivos sem acoplamento destrutivo ao filesystem.

A arquitetura deve permitir crescimento incremental do antigo conjunto de BATs para uma aplicação com persistência, interface, OCR, conferência, PDF, impressão e integrações assistidas.

## 2. Tecnologias-base

Base definida para o repositório:

- Python 3.12;
- persistência local própria;
- SQLite como banco local previsto para cadastro, configurações e histórico;
- filesystem como repositório dos documentos reais;
- empacotamento para Windows a ser definido na Sprint apropriada;
- bibliotecas de OCR/PDF escolhidas e fixadas apenas quando a implementação correspondente for iniciada.

O banco não substitui os documentos físicos. Ele indexa, configura e registra operações.

## 3. Organização de código

```text
src/axiom_tools/
├── core/
├── modules/
│   ├── folders/
│   ├── ocr/
│   ├── printing/
│   ├── integrations/
│   └── settings/
└── utils/
```

A implementação poderá ganhar novos submódulos conforme as Sprints, especialmente para clientes, funcionários, documentos, PDF e persistência, desde que preserve separação de responsabilidades.

## 4. Responsabilidades

### core

Infraestrutura compartilhada:

- inicialização;
- persistência;
- logging/auditoria;
- tratamento de erros;
- serviços comuns;
- contratos internos entre módulos.

### clients

Quando implementado como domínio próprio:

- cadastro PF/PJ;
- CPF/CNPJ;
- importação de planilha;
- busca;
- status;
- vínculo com caminhos físicos;
- prevenção de duplicidade.

### folders

- criação incremental de estrutura;
- validação de estrutura existente;
- compatibilidade com estruturas legadas/BAT;
- PF/PJ;
- funcionários;
- versionamento de estrutura;
- política de conflitos.

### ocr

- extração de texto/dados;
- classificadores por tipo documental;
- identificação de cliente;
- identificação de competência;
- nível de confiança;
- encaminhamento para revisão;
- sugestão de nome e destino.

### printing

- conferência;
- seleção;
- ordenação A–Z;
- agrupamento por cliente;
- consolidação PDF;
- impressão em lote;
- relatórios operacionais.

### integrations

- abertura assistida de portais;
- monitoramento de pastas de download/entrada quando aprovado;
- encaminhamento de arquivos baixados ao processamento local;
- nunca contornar autenticação/CAPTCHA.

### settings

- caminhos configuráveis;
- preferências operacionais;
- convenções de estrutura;
- parâmetros de OCR/conferência;
- parâmetros de impressão;
- configuração do navegador e entradas/saídas.

### utils

Somente funções realmente compartilhadas e pequenas. Não deverá virar depósito genérico de regras de negócio.

## 5. Persistência

A persistência deverá manter, conforme evolução:

- clientes;
- tipo PF/PJ;
- CPF/CNPJ normalizado;
- nome legal/original;
- status;
- caminho físico;
- configurações;
- versão de estrutura;
- histórico de operações;
- resultado de classificações;
- estados de conferência.

Registros não devem ser usados para destruir automaticamente o acervo físico.

## 6. Fluxo documental

Fluxo conceitual:

```text
Entrada
  ↓
Preservação do original
  ↓
Leitura/OCR
  ↓
Identificação do cliente
  ↓
Identificação do documento
  ↓
Identificação da competência
  ↓
Validação de confiança
  ├── baixa confiança → Revisão
  └── confiança suficiente
          ↓
     Sugestão de nome/destino
          ↓
     Verificação de conflito
          ↓
     Cópia/versão gerenciada
          ↓
     Conferência
          ↓
     Impressão/uso operacional
```

## 7. Regras de código

- arquivos pequenos e responsabilidades claras;
- evitar monólitos;
- separar modelo, serviço, interface e integração quando a complexidade justificar;
- regras de filesystem não devem ficar espalhadas pela interface;
- caminhos não devem ficar hardcoded em múltiplos arquivos;
- classificadores OCR devem ser extensíveis;
- operações em lote devem ser testáveis sem executar destruição real;
- rotinas críticas devem possuir modo de simulação/validação sempre que tecnicamente aplicável.

## 8. Compatibilidade com legado

O Axiom Tools nasce de rotinas que já criavam estruturas reais. Portanto:

- a aplicação deve reconhecer árvores existentes;
- metadados como `estrutura.cfg` devem ser considerados;
- estruturas antigas podem conter nomes/pastas diferentes;
- conteúdo desconhecido deve ser preservado;
- atualização significa completar/evoluir, não apagar e reconstruir.

## 9. Segurança documental

A decisão AXT-001 é vinculante para toda a arquitetura.

Nenhum módulo pode adotar comportamento destrutivo por conveniência local.

## 10. Evolução

A arquitetura deve crescer pelas Sprints oficiais registradas em `docs/sprints/`, evitando antecipar dependências pesadas antes da funcionalidade que realmente as necessita.