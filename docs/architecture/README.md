# Arquitetura

Esta pasta concentra a documentação técnica da arquitetura do Axiom Tools.

## Documento oficial

- `ARQUITETURA_OFICIAL_AXIOM_TOOLS.md` — arquitetura consolidada, responsabilidades dos módulos, persistência, fluxo documental, compatibilidade com legado e regras de evolução.

## Diretrizes permanentes

- aplicação modular;
- Python 3.12 como base de execução;
- persistência local própria e filesystem documental preservado;
- separação entre infraestrutura e módulos funcionais;
- caminhos e regras de armazenamento configuráveis;
- operações destrutivas evitadas por padrão;
- OCR desacoplado das regras de organização de pastas;
- integrações externas tratadas como adaptadores assistidos;
- testes automatizados para regras de classificação e movimentação;
- compatibilidade segura com estruturas legadas/BAT.

As decisões de `docs/decisions/` são vinculantes para a implementação.