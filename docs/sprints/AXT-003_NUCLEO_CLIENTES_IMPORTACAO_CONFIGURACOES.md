# AXT-003 — Núcleo de Clientes, Importação e Configurações

Versão: 1.0  
Data: 16/08/2026  
Status: **Planejada**

## Dependências

- AXT-001 homologada;
- AXT-002 homologada;
- DEC-001;
- arquitetura oficial.

## Objetivo

Criar a persistência local e o cadastro/indexação de clientes que passarão a consumir o motor de pastas já homologado.

## Escopo

- SQLite local;
- cadastro PF/PJ;
- CPF/CNPJ;
- nome legal/original;
- status operacional;
- caminho físico associado;
- cadastro manual;
- edição;
- busca;
- inativação/reativação;
- exclusão somente cadastral quando necessária;
- prevenção de duplicidade por documento;
- importação XLS/XLSX da relação de clientes;
- tratamento de registros antigos/inativos/baixados sem exigir limpeza prévia da planilha;
- configurações de caminhos;
- histórico mínimo de alterações;
- integração do cadastro com criação/correção de estrutura pela AXT-001.

## Regras

- excluir cadastro nunca exclui pasta física;
- nome legal/original deve ser preservado;
- normalização pode ser usada para busca/matching, sem destruir o dado original;
- importação deve permitir revisão antes de consolidar alterações sensíveis;
- caminho de cliente deve ser configurável e validável.

## Fora de escopo

- OCR;
- classificação documental;
- competência;
- impressão;
- integrações governamentais.

## Critérios de aceite

- persistência íntegra;
- importação reproduzível e testada;
- duplicidades controladas;
- edição/inativação/reativação funcionais;
- exclusão cadastral sem efeito no filesystem;
- integração com motor de pastas sem duplicar regras;
- configurações centralizadas e sem caminhos críticos espalhados no código.