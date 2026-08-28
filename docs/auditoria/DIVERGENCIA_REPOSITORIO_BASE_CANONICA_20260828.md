# Divergência entre repositório e base canônica — 28/08/2026

Status: **achado de governança da auditoria V8**

## 1. Constatação

A auditoria canônica de 28/08/2026 foi executada sobre o pacote operacional `Axiom_Tools(20260827-175623).zip`, que contém a árvore efetiva em `app/src/axiom_tools`, testes empacotados e banco operacional usado para evidência.

O branch `main` atual do repositório `mendescharles2022-collab/Axiom_Tools` não é um espelho integral dessa implementação operacional.

Na árvore atual de `src/axiom_tools`, o repositório expõe apenas a fundação reduzida `core`, `modules` e `utils`; dentro de `modules`, os subdiretórios visíveis são fundações mínimas como `folders`, `integrations`, `ocr`, `printing` e `settings`, sem a árvore operacional V8 auditada no ZIP (por exemplo, os módulos web/processing/conference/delivery efetivamente examinados na base canônica).

## 2. Consequência

Os documentos de auditoria registrados no GitHub são válidos como histórico e contrato de correção, mas o código do `main` não pode, neste momento, ser tratado como prova de que um defeito do ZIP foi corrigido ou ainda existe.

Da mesma forma, uma alteração feita apenas na árvore reduzida do repositório não pode ser considerada correção da instalação canônica sem reconciliação explícita.

## 3. Regra para a continuidade

Antes da implementação final da V8 e antes de gerar pacote de homologação:

1. confrontar a árvore operacional do pacote canônico com o repositório;
2. definir qual árvore de código será o espelho oficial;
3. sincronizar o código-fonte aplicável sem versionar banco operacional, documentos de clientes, credenciais ou dados sensíveis;
4. preservar histórico de commits e documentação já existente;
5. executar a regressão sobre a mesma árvore que será empacotada para o Windows;
6. gerar o pacote final a partir dessa árvore reconciliada.

## 4. Proibição de conclusão falsa

Enquanto houver divergência entre `main` e a implementação efetivamente auditada:

- commit documental não significa correção de código;
- teste executado em árvore diferente não homologa o ZIP canônico;
- pacote final não deve ser declarado V8 homologado sem rastreabilidade entre fonte, testes e instalador.

## 5. Estado

Este achado não bloqueia a continuidade da auditoria funcional e documental, mas é requisito de governança para a fase de correção e homologação final.
