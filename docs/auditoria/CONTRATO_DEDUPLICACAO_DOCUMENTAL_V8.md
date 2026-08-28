# Contrato V8 — Deduplicação, reemissão e identidade documental

Data: 28/08/2026
Status: **contrato de auditoria / implementação e regressão pendentes**

## 1. Problema

A V8 precisa tratar documentos que podem ser:

- exatamente o mesmo arquivo;
- reemissão do mesmo fato econômico;
- versão sucessora que substitui a anterior;
- documento complementar;
- documento de unidade/matrícula diferente;
- documento distinto que compõe a mesma obrigação;
- arquivo fisicamente diferente, porém semanticamente equivalente.

Uma única regra baseada em hash ou nome de arquivo não resolve esses cenários.

## 2. Três identidades diferentes

### 2.1 Identidade física

Pergunta: **os bytes são os mesmos?**

Chave principal:

- SHA-256 do arquivo.

Uso:

- evitar ingestão física idêntica repetida;
- cache de leitura;
- prova de integridade.

Hash igual implica conteúdo binário igual.

Hash diferente **não implica obrigação diferente**.

## 3. Identidade documental lógica

Pergunta: **os dois PDFs representam o mesmo documento/fato documental?**

Fingerprint deve considerar, conforme tipo:

- fonte;
- tipo documental;
- cliente/identidade principal;
- inscrição/matrícula/estabelecimento;
- competência/período de apuração;
- número/identificador oficial da guia/documento;
- natureza mensal/rescisória;
- valores centrais;
- vencimento quando material;
- identificadores de emissão/protocolo quando disponíveis.

O fingerprint não precisa ser uma única string universal; pode ser estratégia por tipo documental.

## 4. Identidade econômica da obrigação

Pergunta: **os valores representam componentes distintos que devem ser somados/comparados ou são repetição da mesma obrigação?**

A identidade econômica pode divergir da identidade documental.

Exemplo Jair Ferreira Camargo:

- dois Extratos de matrículas distintas;
- federal R$ 511,43 repetido em ambos = uma obrigação federal consolidada;
- FGTS R$ 129,68 e R$ 259,36 = componentes distintos e aditivos;
- GFD consolidada R$ 389,04.

Logo, o mesmo par de documentos pode ser duplicado para uma dimensão e aditivo para outra.

## 5. Relações entre documentos

Persistir/classificar relação explícita quando aplicável:

```text
IDENTICO_FISICO
REEMISSAO_EQUIVALENTE
VERSAO_SUCESSORA
SUBSTITUI_DOCUMENTO
COMPLEMENTAR
UNIDADE_DISTINTA
COMPONENTE_ADITIVO
SEM_RELACAO
RELACAO_INDETERMINADA
```

Evitar apagar o documento anterior apenas porque existe sucessor.

## 6. Reemissão

Uma reemissão pode:

- ter hash diferente;
- possuir nova data de emissão;
- manter mesma competência, identificador econômico e valor;
- representar exatamente a mesma obrigação.

Nesse caso:

- não somar valores;
- preservar ambos no histórico;
- marcar qual é a versão/documento preferencial vigente para apresentação/saída;
- não criar retificação material se nada econômico mudou.

## 7. Versão sucessora material

Quando novo documento substitui o anterior e altera dado relevante:

- ingerir como nova evidência;
- comparar delta;
- se cliente ainda aberto, recompor a obrigação;
- se cliente já FECHADA, criar retificação candidata;
- não apagar versão anterior.

## 8. Múltiplas matrículas/unidades

Não deduplicar apenas por:

- mesmo CPF/CNPJ raiz;
- mesmo cliente_id;
- mesmo valor federal;
- mesmo nome de arquivo base.

Preservar inscrição/matrícula de origem.

A unidade de consolidação é definida por obrigação, não pela identidade cadastral.

## 9. Caso Leosmar

Dois Extratos vigentes de 08/2026 possuem os mesmos valores centrais e FGTS zero.

Esse cenário é controle contra soma cega.

Regressão:

- identificar se são reemissão/equivalentes ou outra relação válida;
- não duplicar federal;
- não inventar componente FGTS;
- preservar evidências e justificativa da classificação.

## 10. Múltiplas GFD / FGTS

Antes de somar duas guias, classificar:

- mensal;
- rescisória;
- antecipada;
- reemissão;
- substituta;
- complementar;
- unidade/matrícula distinta.

Somar somente componentes economicamente distintos.

## 11. Nome do arquivo

Nome pode ajudar no matching, mas nunca é chave suficiente.

Arquivos podem:

- ser renomeados pelo usuário;
- chegar com nomes genéricos;
- ser reemitidos com outro nome;
- compartilhar nome em pastas diferentes.

## 12. Momento da deduplicação

Deduplicação ocorre em camadas:

1. **ingestão física** — hash;
2. **após extração/identidade** — fingerprint documental;
3. **na composição da obrigação** — identidade econômica.

Não decidir tudo na entrada, antes de conhecer cliente, competência e natureza do documento.

## 13. Persistência

Guardar, quando aplicável:

- hash físico;
- fingerprint lógico;
- grupo de equivalência;
- relação com documento anterior/sucessor;
- motivo/regra da classificação;
- confiança;
- decisão humana quando houver ambiguidade.

## 14. Ambiguidade

Quando o sistema não conseguir provar se dois documentos são reemissões ou componentes distintos:

- não somar automaticamente;
- não descartar automaticamente;
- classificar `RELACAO_INDETERMINADA`;
- encaminhar à revisão com documentos lado a lado.

## 15. Idempotência

Reprocessar ou redescobrir o mesmo arquivo não deve:

- criar documento vigente duplicado;
- duplicar obrigação;
- duplicar pessoa extraída;
- duplicar ocorrência;
- criar nova retificação sem mudança material.

## 16. Regressões obrigatórias

1. mesmo SHA-256 ingerido duas vezes = uma evidência física canônica, sem duplicação de obrigação;
2. hashes diferentes, mesma reemissão = não somar;
3. versão sucessora com valor alterado = delta/retificação conforme estado do cliente;
4. Jair = federal uma vez, FGTS somado por matrícula;
5. Leosmar = documentos equivalentes não somados indevidamente;
6. GFD mensal + rescisória distintas = composição válida;
7. GFD reemitida = não dobra FGTS;
8. arquivo renomeado com mesmo hash = não duplica;
9. nome igual com conteúdo/identidade diferente = não deduplica cegamente;
10. relação ambígua = revisão, não decisão destrutiva.

## 17. Critério de aceite

A V8 não estará homologada enquanto 'duplicado' significar apenas `hash igual` ou enquanto 'há dois documentos' significar automaticamente `somar`.
