# AXT-003 — OCR, Classificação e Competências

Status: Aprovado  
Data: 16/08/2026

## 1. Objetivo

O OCR do Axiom Tools não será apenas leitor de texto. Ele deverá apoiar identificação do cliente, tipo documental, competência, nome final e destino do documento.

## 2. Entrada

O sistema deverá possuir uma área de entrada para arquivos aguardando processamento.

Arquivos recebidos deverão permanecer preservados até a conclusão segura do fluxo.

## 3. Tipos documentais prioritários

O motor deverá ser preparado para reconhecer inicialmente:

- DARF relacionado à DCTFWeb;
- documentos do FGTS Digital;
- contracheques;
- pró-labore;
- documentos/relatórios que indiquem ausência de movimento, quando identificável;
- outros tipos aprovados em Sprints futuras.

O reconhecimento deverá ser extensível, sem concentrar todos os classificadores em um único arquivo.

## 4. Identificação do cliente

A classificação deverá cruzar dados extraídos com o cadastro interno, priorizando identificadores confiáveis como CPF/CNPJ e, subsidiariamente, nome/razão social.

Resultados ambíguos não deverão ser classificados silenciosamente como definitivos.

## 5. Competência

Para documentos periódicos, o sistema deverá tentar identificar competência e organizá-la segundo convenção configurada.

A competência deverá ser tratada como informação própria do documento e não inferida exclusivamente pela data do arquivo.

Exemplo de apresentação: `Agosto/2026`.

## 6. Renomeação

O nome final deverá ser previsível e padronizado, combinando somente informações validadas.

Antes de gravar o arquivo classificado, o sistema deverá verificar conflito de nome no destino.

Não haverá sobrescrita silenciosa.

## 7. Destinos configuráveis

O projeto deverá permitir configurar caminhos distintos para, entre outros:

- contratos/alterações;
- movimentações mensais;
- DARF;
- FGTS;
- contracheques;
- pró-labore;
- conferência;
- entrada de OCR.

## 8. Confiança e revisão

Cada classificação automatizada deverá poder resultar em:

- reconhecido com segurança;
- reconhecido com necessidade de conferência;
- não reconhecido.

Itens de baixa confiança ou sem correspondência deverão permanecer disponíveis para revisão humana.

## 9. Preservação

A classificação gerará uma versão organizada/cópia gerenciada no destino aplicável, preservando o arquivo original conforme AXT-001.

Nenhum OCR poderá usar sucesso de extração como justificativa automática para apagar a origem.

## 10. Sem movimento

A condição `sem movimento` deverá ser tratada como informação operacional vinculada a cliente, documento e competência quando houver evidência suficiente.

O sistema não deverá criar informação de sem movimento apenas pela ausência de arquivo; a ausência deve aparecer como pendência de conferência até que a regra funcional defina o contrário.