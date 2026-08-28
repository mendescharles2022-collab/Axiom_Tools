# Auditoria canônica V8 — Etapa 36

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

A Etapa 36 aprofundou B06 e B42 — divergência entre repositório/runtime e proveniência do build.

## 2. Achados confirmados

A auditoria canônica utilizou o pacote operacional `Axiom_Tools(20260827-175623).zip`, com módulos e testes que não estão integralmente presentes no `main` atual.

O `main` também mantém metadado de versão `0.1.0`, enquanto a linha operacional documentada está na família V5.6.14V7/V8/V8F2.

Consequência: hoje não existe prova automática de que commit, código testado, schema, instalador e runtime instalado sejam o mesmo artefato.

## 3. Protocolo criado

Foi criado `PROTOCOLO_RECONCILIACAO_RUNTIME_REPOSITORIO_V8.md`.

Ele exige inventário por arquivo/hashes e classificação do que pode ou não ser versionado.

## 4. Não fazer cópia cega

A reconciliação não autoriza commit de raiz operacional completa.

Devem permanecer fora do Git:

- SQLite operacional;
- documentos/PDFs reais;
- certificados;
- tokens/credenciais;
- logs sensíveis;
- backups;
- cache/temp/downloads reais.

A reconciliação deve importar apenas código e artefatos controlados.

## 5. Commit-base

Antes das correções finais será necessário estabelecer um commit-base que represente o runtime auditado com fidelidade suficiente para reproduzir:

- módulos;
- rotas;
- templates;
- testes;
- scripts/migrações;
- comportamento baseline.

As correções V8 devem ocorrer sobre essa árvore, não sobre a fundação reduzida atual.

## 6. Proveniência final

O pacote final deve conter manifesto com:

- versão release;
- commit SHA;
- schema version;
- data/build;
- plataforma/Python alvo;
- hashes do payload controlado.

Runtime, health, logs, instalador e relatório técnico devem apontar para a mesma identidade.

## 7. Estado dos bloqueadores

- B06 permanece `CONFIRMADO_RUNTIME`, não corrigido;
- B42 permanece `CONFIRMADO_RUNTIME`, não corrigido;
- o protocolo define a prova necessária, mas não substitui a reconciliação real;
- nenhum pacote final pode ser produzido antes dessa etapa operacional.

## 8. Próxima frente

Auditar concorrência lógica e escrita obsoleta em estados mensais, candidatos, decisões e chamadas, além da concorrência física já tratada pelo SQLite/WAL.
