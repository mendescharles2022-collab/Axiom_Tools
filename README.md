# Axiom Tools

Ferramentas operacionais do Ecossistema Axiom para automação local de arquivos, organização documental, OCR, conferência e apoio às rotinas do escritório.

## Objetivo

O Axiom Tools nasce como uma aplicação utilitária independente, voltada principalmente para:

- criação e atualização padronizada das pastas de clientes;
- organização documental de pessoas físicas e jurídicas;
- identificação, renomeação e classificação de PDFs por OCR;
- separação de documentos por cliente e competência;
- conferência e impressão em lote;
- abertura assistida de portais externos e encaminhamento dos arquivos baixados para o fluxo de classificação;
- preservação dos documentos originais e rastreabilidade das operações.

## Princípios

1. Nenhum arquivo original deve ser excluído automaticamente.
2. Operações de movimentação devem ser rastreáveis.
3. A classificação automática deve permitir conferência humana.
4. Integrações governamentais devem respeitar autenticação, CAPTCHA e demais interações humanas obrigatórias.
5. A estrutura deve permanecer modular para permitir evolução sem transformar o projeto em um monólito.

## Estrutura inicial

```text
Axiom_Tools/
├── config/                  # exemplos e definições de configuração
├── docs/
│   ├── architecture/        # arquitetura e decisões técnicas
│   ├── decisions/           # decisões permanentes do projeto
│   └── sprints/             # sprints oficiais
├── scripts/                 # scripts de instalação, manutenção e suporte
├── src/
│   └── axiom_tools/
│       ├── core/            # infraestrutura compartilhada
│       ├── modules/
│       │   ├── folders/     # criação e manutenção de pastas
│       │   ├── ocr/         # identificação e classificação documental
│       │   ├── printing/    # conferência e impressão em lote
│       │   ├── integrations/# integrações e portais assistidos
│       │   └── settings/    # configurações do aplicativo
│       └── utils/           # utilitários compartilhados
└── tests/                   # testes automatizados
```

## Estado

Fundação inicial do repositório. A implementação funcional será conduzida por Sprints oficiais.
