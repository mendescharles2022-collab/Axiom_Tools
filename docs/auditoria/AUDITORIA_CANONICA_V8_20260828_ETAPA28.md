# Auditoria canônica V8 — Etapa 28

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Confrontar a implementação V8F2 com `CONTRATO_MATRIZ_APLICABILIDADE_OBRIGACOES_V8.md`.

## 2. Violações comprovadas no runtime

### 2.1 MEI / DAE

O status V8F2 registra que Elenice Batista Santos Silva, cadastrada como MEI, continua sendo tratada pela lógica genérica de FGTS/DARF na Conferência.

Isso viola a regra canônica:

- MEI usa expectativa específica de DAE;
- não recebe expectativa mensal genérica de GFD autônoma;
- eventual exceção não pode virar padrão mensal.

B20 permanece `CONFIRMADO_RUNTIME`.

### 2.2 FGTS zero

O status V8F2 registra que o sistema ainda pode exigir FGTS Digital quando `FGTS Domínio = R$ 0,00`.

Isso confirma que a presença/ausência de guia ainda pode ser avaliada antes da aplicabilidade/valor esperado.

B19 permanece `CONFIRMADO_RUNTIME`.

## 3. Ordem obrigatória de decisão

A implementação precisa obedecer:

1. identificar perfil e composição mensal;
2. determinar pessoas/vínculos/movimento;
3. calcular aplicabilidade da obrigação;
4. determinar valor esperado;
5. decidir se documento é necessário;
6. somente então procurar/bater guia.

É proibido começar pela ausência física do arquivo.

## 4. Estados distintos para valor zero

A V8 precisa distinguir pelo menos:

- `NAO_APLICAVEL`;
- `APLICAVEL_SALDO_ZERO_SEM_GUIA`;
- `APLICAVEL_VALOR_POSITIVO`;
- `INDETERMINADA`.

A UI pode traduzir os rótulos, mas o motor deve preservar a semântica.

## 5. Casos de regressão

### MEI

- Elenice Batista Santos Silva;
- Luriel Ferreira Malheiros.

Resultado esperado: DAE como referência normal e nenhuma GFD autônoma exigida por regra genérica.

### FGTS zero

- Alex Douglas, com contexto rescisório;
- Larissa B Maia, sem empregados;
- cenários de diretor/pró-labore sem empregados;
- afastamentos/faltas com bases zeradas quando aplicável.

Ausência da GFD só é pendência se a obrigação efetivamente exigir guia.

## 6. DARF com saldo zero

A mesma ordem vale para federal/previdenciário.

Quando a composição resulta em `Saldo à recolher = 0,00`, o sistema deve registrar obrigação explicada sem exigir DARF inexistente.

Casos de controle já definidos incluem deduções/salário-família e afastamentos integrais.

## 7. Evidência conflitante

Perfil cadastral não pode apagar evidência material do mês.

Exemplo de regra:

- MEI normalmente usa DAE;
- se surgir evidência extraordinária incompatível com o perfil, o sistema abre revisão;
- não cria expectativa genérica permanente nem ignora o documento.

## 8. Relação com decisão por fonte

A aplicabilidade produz o estado inicial da obrigação.

Uma justificativa humana posterior atua somente naquela fonte e não deve ser usada para compensar erro do motor de aplicabilidade.

## 9. Regressão técnica mínima

Para cada caso, testar diretamente o serviço de aplicabilidade e depois a Conferência:

- entrada de perfil/movimento/evidências;
- aplicabilidade esperada;
- valor esperado;
- necessidade de documento;
- ocorrência resultante;
- estado agregado do cliente.

A ausência de um arquivo não pode alterar a própria aplicabilidade calculada.

## 10. Estado final

- B19 — confirmado, não corrigido;
- B20 — confirmado, não corrigido;
- B21/B22 — contratos obrigatórios a validar no runtime;
- B18 — decisão por fonte permanece necessária;
- nenhum item passa a homologado nesta etapa.
