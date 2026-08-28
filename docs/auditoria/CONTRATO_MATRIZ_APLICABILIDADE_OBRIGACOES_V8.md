# Contrato V8 — Matriz de aplicabilidade das obrigações

Data: 28/08/2026
Status: **contrato obrigatório de auditoria / implementação ainda não homologada**

## 1. Objetivo

Definir como o Axiom Tools decide **quais obrigações/fontes devem ser esperadas** para cada `cliente + competência`, antes de procurar documentos faltantes ou gerar divergências.

O motor não pode adotar a regra simplista:

```text
arquivo não encontrado = pendência
```

Primeiro deve determinar se a obrigação é aplicável e qual resultado é esperado.

## 2. Fontes de decisão

A aplicabilidade deve combinar, nesta ordem lógica:

1. composição mensal da competência;
2. perfil cadastral do cliente;
3. identidade e inscrições vinculadas;
4. movimento efetivamente identificado na competência;
5. pessoas/vínculos/afastamentos/rescisões relevantes;
6. valores/bases apurados nas fontes autorizadas;
7. evidências documentais e externas;
8. justificativas/impedimentos específicos da fonte.

O cadastro histórico é base estrutural; a realidade mensal é soberana quando houver evidência específica da competência.

## 3. Saída do motor de aplicabilidade

Para cada obrigação, produzir pelo menos:

- `fonte_obrigacao`;
- `aplicabilidade`: `APLICAVEL`, `NAO_APLICAVEL`, `INDETERMINADA`;
- motivo/regra;
- valor esperado, quando conhecido;
- evidências usadas;
- proveniência;
- necessidade documental;
- estado inicial da Conferência.

## 4. Regra geral de valor zero

Valor esperado igual a zero não é sinônimo de erro nem de obrigação inexistente.

O motor deve distinguir:

- obrigação não aplicável;
- obrigação aplicável com saldo zero por dedução/compensação;
- obrigação com base/remuneração zero por afastamento/faltas;
- obrigação substituída por documento/regime específico;
- valor ainda indeterminado por falta de evidência.

## 5. MEI

Regra V8 aprovada:

- cliente cadastrado como MEI não recebe expectativa mensal genérica de guia FGTS Digital autônoma;
- a referência operacional normal é a regra/documento DAE aplicável ao MEI;
- eventual situação extraordinária deve ser tratada como exceção explícita e não transformar GFD em expectativa mensal padrão.

Casos de regressão:

- Elenice Batista Santos Silva;
- Luriel Ferreira Malheiros.

## 6. Empregador doméstico

Quando o perfil cadastral indicar empregador doméstico, a expectativa deve seguir o fluxo específico de DAE/eSocial Doméstico definido pelo produto.

Não aplicar automaticamente a mesma matriz documental de empresa PJ comum.

## 7. Pessoa física rural / CAEPF

Princípios:

- CPF identifica o cliente PF;
- CAEPF/matrículas são inscrições vinculadas 1:N;
- múltiplas inscrições não criam múltiplos clientes;
- evidências podem ser aditivas por inscrição/matrícula para determinadas obrigações;
- tributos consolidados repetidos não devem ser somados sem prova de obrigação econômica distinta.

Casos:

- Jair Ferreira Camargo;
- Delfino Pereira Ribeiro;
- Marcos Augusto Pimentel Daibert.

## 8. Diretor/pró-labore sem empregados

A presença de uma pessoa com `Situação: Trabalhando` não cria expectativa automática de FGTS.

A natureza do vínculo e os totais do relatório devem prevalecer.

Controle real:

- P DA SILVA CARMO: diretor/contribuinte, 0 empregados, FGTS zero, federal positivo.

Outro cenário:

- Larissa B Maia: sem empregados e com pró-labore; FGTS zero pode ser legítimo enquanto a obrigação federal permanece aplicável.

## 9. Afastamento integral

Quando a evidência da competência comprovar afastamento integral e ausência de remuneração/base aplicável, as obrigações correspondentes podem resultar em `NAO_APLICAVEL` ou saldo zero conforme a fonte.

Isso deve ser explicado, não apresentado como guia ausente.

Casos:

- Gold Pallace Hotel;
- Marcos Augusto Pimentel Daibert.

O motor não deve generalizar todo afastamento como ausência de FGTS: natureza do afastamento e evidências da competência continuam necessárias.

Controle contrário:

- GL Auto Center, em que o contexto de afastamento por acidente exige tratamento específico e não autoriza simplesmente zerar toda expectativa.

## 10. Faltas integrais / remuneração zerada

Quando as evidências demonstrarem faltas em todos os dias e remuneração/bases efetivamente zeradas, ausência legítima de guia não vira pendência artificial.

Caso:

- Wilmar Ferreira Pires.

## 11. Deduções e saldo federal zero

Quando o Extrato Domínio demonstrar obrigação previdenciária/federal cuja composição resulte em `Saldo à recolher = 0,00`, a saída deve distinguir:

```text
obrigacao_aplicavel = SIM
saldo_esperado = 0,00
emissao_documento = NAO_NECESSARIA
```

Caso:

- Denes Mariano de Castro, com deduções/salário-família zerando o saldo.

## 12. Rescisão e FGTS

Contexto rescisório não deve ser reduzido a `FGTS mensal ausente`.

O motor deve avaliar separadamente:

- FGTS mensal;
- FGTS rescisório;
- recolhimento antecipado;
- guia reemitida;
- garantias relacionadas ao consignado, quando aplicável.

Casos:

- Alex Douglas de Andrade;
- Comercial Faria;
- Empório Frios Itapaci;
- Predileta;
- Ribeiro e Nascimento Art Vidros.

## 13. DARF sob responsabilidade de outro setor

Responsabilidade operacional configurada por fonte deve afetar a cobrança do DP sem apagar a obrigação nem liberar outras fontes.

Exemplo:

- Predileta: DARF emitida/conduzida pela equipe Fiscal.

O estado da fonte DARF pode ser resolvido por regra administrativa parametrizada, mantendo FGTS/eConsignado independentes.

## 14. Impedimento externo

Ausência de documento causada por impedimento externo legítimo, como procuração revogada/expirada, deve ser classificada na fonte correspondente.

Casos:

- Casa das Carnes e Panificadora Lago Azul;
- Maria Virginia S Souto.

Isso não justifica automaticamente outras obrigações.

## 15. eConsignado

eConsignado só se torna obrigação de cruzamento quando houver evidência positiva/contextualmente aplicável.

A decisão deve considerar:

- vínculo;
- remuneração;
- desligamento;
- afastamento;
- pagamento direto informado;
- rescisão;
- garantias;
- contrato.

Retorno residual/incompatível não cria bloqueio sozinho.

## 16. Sem movimento nesta competência

É decisão mensal, não alteração do cadastro permanente.

Quando explicitamente marcada e coerente com as evidências:

- reduz expectativas incompatíveis da competência;
- não é herdada silenciosamente para o mês seguinte;
- reversão recompõe as expectativas e mantém histórico.

A marcação não deve apagar evidência real conflitante. Se documentos/valores materiais demonstrarem movimento, o caso exige revisão.

## 17. Chamada futura

Cliente em próxima chamada:

- continua pertencendo à competência;
- fica fora das cobranças e jobs da chamada corrente;
- volta ao universo somente quando a chamada correspondente for efetivamente aberta/liberada.

Não converter chamada futura em `NAO_APLICAVEL` permanente.

## 18. Resultado indeterminado

Quando as evidências forem insuficientes ou conflitantes, o motor deve retornar `INDETERMINADA`/revisão.

É proibido escolher automaticamente o cenário que produz menos pendências.

## 19. Proveniência

Toda decisão de aplicabilidade deve poder explicar:

- qual perfil cadastral foi usado;
- qual composição mensal foi usada;
- quais documentos/valores/pessoas influenciaram;
- qual regra foi aplicada;
- se houve decisão administrativa específica.

## 20. Regressões mínimas

1. MEI não recebe GFD genérica mensal.
2. DAE é considerado no perfil específico correspondente.
3. PF com dois CAEPFs continua um cliente.
4. diretor `Trabalhando` sem empregado não gera FGTS artificial.
5. saldo federal zero por dedução não gera ausência de DARF.
6. afastamento integral comprovado não gera guia fictícia.
7. faltas integrais com bases zeradas não geram pendência artificial.
8. afastamento por acidente não é tratado pela regra genérica de afastamento integral sem contexto.
9. rescisão permite múltiplos componentes FGTS.
10. DARF do Fiscal resolve apenas a fonte DARF.
11. procuração revogada resolve/impede apenas a fonte correspondente.
12. eConsignado residual sem contexto não bloqueia sozinho.
13. sem movimento mensal não altera cadastro permanente.
14. chamada futura fica fora do ciclo atual sem virar N/A.
15. evidência conflitante produz revisão, não fechamento conveniente.

## 21. Relação com bloqueadores

Principalmente B13, B14, B16, B18, B19, B20, B21, B22, B23, B26, B27, B29, B30, B31 e B37.
