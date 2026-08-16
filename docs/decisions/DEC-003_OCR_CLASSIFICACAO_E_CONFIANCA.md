# DEC-003 — OCR, Classificação e Confiança

Versão: 1.0  
Data: 16/08/2026  
Status: Permanente e vinculante

## Decisão

O OCR do Axiom Tools é um mecanismo assistivo de leitura e classificação documental. Ele não autoriza decisões destrutivas automáticas.

## Tipos documentais iniciais previstos

- DARF/DCTFWeb;
- FGTS Digital;
- contracheques;
- pró-labore;
- demais documentos aprovados em Sprint específica.

## Regras

- preservar o arquivo original;
- identificar cliente por CPF/CNPJ quando possível;
- usar nome apenas como apoio quando necessário;
- identificar tipo documental;
- identificar competência por evidência documental, não apenas pela data do arquivo;
- atribuir nível de confiança;
- baixa confiança deve gerar revisão humana;
- conflito de nome/destino deve interromper apenas a ação conflitante;
- ausência de documento não significa automaticamente “sem movimento”;
- renomeação e destino devem ser sugeridos/validados antes de processamento em lote.

## Competência

A competência deverá ser extraída ou inferida a partir de evidências confiáveis do documento e validada pelas regras da AXT-005.

## Rastreabilidade

O resultado de classificação deverá ser representável de forma estruturada, incluindo:

- arquivo de origem;
- cliente sugerido;
- tipo sugerido;
- competência sugerida;
- confiança;
- evidências relevantes;
- pendência de revisão;
- destino proposto;
- conflito, quando houver.

## Limites

OCR não substitui validação humana em documentos ambíguos e não pode eliminar o original após processamento.

Esta decisão vincula as Sprints de OCR, competências, conferência e roteamento.