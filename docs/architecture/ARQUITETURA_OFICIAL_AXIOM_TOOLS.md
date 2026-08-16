# Arquitetura Oficial — Axiom Tools

Versão: 2.0  
Data: 16/08/2026  
Status: Oficial e vigente

## 1. Objetivo arquitetural

O Axiom Tools deve permanecer uma aplicação operacional modular, orientada ao ambiente Windows do escritório e capaz de atuar sobre estruturas reais de arquivos com comportamento conservador, auditável e testável.

A arquitetura deve permitir crescimento incremental sem acoplar interface, cadastro, OCR ou impressão diretamente às regras de filesystem.

## 2. Princípios

1. Segurança documental antes de conveniência.
2. Regras de negócio independentes da interface.
3. Filesystem real tratado como recurso externo sensível.
4. Simulação e planejamento antes de operações críticas quando aplicável.
5. Persistência não controla nem destrói o acervo físico.
6. Módulos pequenos, responsabilidades claras e testes isolados.
7. Dependências pesadas entram somente na Sprint que precisa delas.
8. Interface Axiom consome o Axiom Framework; não cria Design System paralelo.
9. Implementação deve ser substituível por módulo sem exigir reconstrução do projeto inteiro.
10. Documentação oficial precede implementação.

## 3. Tecnologias-base

- Python 3.12 ou superior;
- Windows como ambiente operacional principal;
- filesystem como repositório dos documentos reais;
- SQLite previsto para persistência local a partir da AXT-003;
- empacotamento Windows definido na AXT-008;
- bibliotecas de OCR/PDF escolhidas e fixadas apenas na Sprint correspondente;
- camada de interface introduzida na AXT-002.

A AXT-001 não deve depender de framework web, banco de dados, OCR ou biblioteca de PDF.

## 4. Organização conceitual

```text
src/axiom_tools/
├── core/
│   ├── config/
│   ├── logging/
│   ├── errors/
│   └── contracts/
├── modules/
│   ├── folders/
│   ├── clients/
│   ├── ocr/
│   ├── documents/
│   ├── printing/
│   ├── integrations/
│   └── settings/
├── interface/
└── utils/
```

Nem todos os diretórios precisam existir desde a AXT-001. Eles serão introduzidos quando a Sprint responsável começar.

## 5. Camadas

### 5.1 Domínio / regras

Contém regras do negócio e contratos de operação. Não conhece HTML, navegador ou detalhes de apresentação.

### 5.2 Serviços

Orquestram casos de uso, como planejar estrutura, aplicar plano, importar clientes, classificar documento e consolidar lote.

### 5.3 Infraestrutura

Implementa acesso ao filesystem, persistência, OCR, PDF, impressão, navegador e outras dependências externas.

### 5.4 Interface

Será introduzida na AXT-002. Deve consumir os serviços e nunca reimplementar regras de filesystem.

## 6. Módulos

### `folders`

Responsável por:

- catálogo canônico de estruturas;
- equivalências legadas;
- inspeção;
- planejamento;
- aplicação segura;
- conflitos;
- `estrutura.cfg`;
- funcionários/empregados;
- relatórios de operação.

É o único domínio funcional da AXT-001.

### `clients`

Introduzido na AXT-003:

- cadastro PF/PJ;
- CPF/CNPJ;
- nome legal/original;
- status;
- caminho físico;
- importação;
- busca;
- prevenção de duplicidade.

### `ocr`

Introduzido na AXT-004:

- extração de texto/dados;
- classificadores por documento;
- identificação de cliente;
- confiança;
- revisão.

### `documents`

Pode ser introduzido a partir da AXT-004/005 para representar documento, competência, destino, conflito e estado de processamento sem misturar isso ao módulo de OCR.

### `printing`

Introduzido progressivamente na AXT-006/007:

- conferência;
- ordenação A–Z;
- consolidação PDF;
- lotes;
- impressão.

### `integrations`

Introduzido na AXT-008:

- abertura assistida de portais;
- integração com navegador;
- recebimento organizado de downloads;
- sem contorno de autenticação ou CAPTCHA.

### `settings`

Introduzido na AXT-003 e ampliado nas Sprints seguintes:

- caminhos;
- preferências;
- parâmetros operacionais.

## 7. Arquitetura do motor de filesystem

O motor de pastas deve seguir fluxo explícito:

```text
Solicitação
   ↓
Inspeção somente leitura
   ↓
Plano de operação
   ↓
Validação de conflitos
   ↓
[simulação termina aqui]
   ↓
Confirmação do chamador
   ↓
Revalidação do estado atual
   ↓
Aplicação somente de ações seguras
   ↓
Resultado auditável
```

A fase de planejamento não pode criar a pasta raiz nem qualquer outro artefato.

## 8. Persistência

A persistência local será introduzida somente na AXT-003.

Quando existir, deverá registrar conforme necessário:

- clientes;
- configurações;
- caminhos;
- histórico operacional;
- classificações;
- estados de conferência.

A exclusão de um registro nunca autoriza a exclusão automática de arquivos ou pastas físicas.

## 9. Interface e Axiom Framework

A AXT-002 será responsável por definir e implementar a camada visual.

Regras:

- o Axiom Framework é a autoridade de UX/UI do Ecossistema Axiom;
- não copiar o Axiom Tables como fonte normativa;
- não criar CSS, tokens ou componentes paralelos quando houver equivalente oficial;
- a interface deve consumir os serviços do Axiom Tools por contratos claros;
- Login/Dashboard não podem ser dependência da AXT-001.

A tecnologia concreta da camada web/local deverá ser definida e registrada na AXT-002 após inspeção do mecanismo efetivamente disponível no Axiom Framework. Não inventar integração inexistente.

## 10. OCR e fluxo documental

Fluxo conceitual futuro:

```text
Entrada
  ↓
Preservação do original
  ↓
Leitura/OCR
  ↓
Identificação de cliente/tipo/competência
  ↓
Nível de confiança
  ├── insuficiente → Revisão
  └── suficiente → Sugestão
                      ↓
                 Verificação de conflito
                      ↓
                 Roteamento gerenciado
                      ↓
                 Conferência
                      ↓
                 Consolidação/Impressão
```

## 11. Regras de código

- preferir arquivos de aproximadamente 300 linhas;
- evitar ultrapassar 500 linhas sem justificativa;
- não criar módulo monolítico;
- não espalhar caminhos hardcoded;
- não colocar regra de filesystem dentro da CLI ou UI;
- testes automatizados usam diretórios temporários isolados;
- operações críticas devem ser exercitáveis sem tocar a árvore real do escritório;
- erros de conflito são dados do domínio, não exceções engolidas silenciosamente.

## 12. Compatibilidade com legado

- reconhecer estruturas de BATs anteriores;
- considerar `estrutura.cfg`;
- comparar caminhos segundo comportamento case-insensitive esperado no Windows;
- reconhecer equivalências conhecidas de acentuação;
- preservar conteúdo desconhecido;
- atualizar significa completar de forma incremental, nunca apagar e reconstruir.

## 13. Recomeço da implementação

A reorganização de 16/08/2026 declara que a implementação funcional da AXT-001 será reiniciada do zero.

Código produzido em tentativas locais anteriores não deve ser copiado como base. Ideias só podem ser reaproveitadas se forem novamente justificadas e compatíveis com a documentação oficial.

Detalhamento em `docs/decisions/DEC-005_REINICIO_DA_IMPLEMENTACAO_E_FONTE_DE_VERDADE.md`.

## 14. Evolução

Cada Sprint deve implementar somente seu domínio aprovado. Alterações estruturais futuras exigem atualização documental antes do código.