# Auditoria canônica V8 — Etapa 33

Data: 28/08/2026
Status: **auditoria em andamento / V8 NÃO HOMOLOGADA**

## 1. Escopo

Revisão consolidada dos bloqueadores B43, B44, B46 e B47 contra contratos já registrados, sem criar arquitetura duplicada.

## 2. Pendências e Monitor — B43/B46

O contrato `CONTRATO_PENDENCIAS_TECNICAS_VS_CONFERENCIA_V8.md` já registra dois defeitos comprovados:

- a mesma sessão pode persistir `COM_PENDENCIAS` e ser apresentada como `PROCESSAMENTO_CONCLUIDO` ao atingir 100%;
- a aba Pendências ainda expõe PROC/chaves como eixo operacional para isolar a competência.

Regra final:

- status da sessão = execução técnica;
- pendência técnica = falha de processamento;
- pendência de negócio = Central de Conferência.

A competência operacional deve ser o filtro primário do usuário; PROC permanece detalhe diagnóstico.

B43 e B46 continuam `CONFIRMADO_RUNTIME` e não homologados.

## 3. Relatório A4 — B44

`CONTRATO_RELATORIOS_IMPRESSAO_V8.md` registra falha funcional confirmada: relatório de pendências pode ultrapassar a área imprimível A4 retrato.

A homologação exige preview/impressão real no Windows com:

- primeira/intermediária/última página;
- nome longo;
- justificativa longa;
- múltiplas fontes;
- cabeçalho repetido;
- ausência de corte horizontal;
- fonte ainda legível.

B44 permanece `CONFIRMADO_RUNTIME`.

## 4. Sintegra/SEFAZ GO — B47

A regressão visual dos atalhos Sintegra Goiás/Nacional já foi registrada anteriormente.

A arquitetura `INTEGRACAO_ASSISTIDA_SINTEGRA_CLIENTES.md` foi atualizada após a observação operacional de que a consulta pública de Goiás não apresenta CAPTCHA no fluxo validado.

Estratégia vigente:

1. restaurar atalhos Sintegra Goiás e Nacional;
2. Goiás: consulta direta assistida primeiro;
3. comparação `Atual × SEFAZ GO`;
4. confirmação humana antes de gravar;
5. fallback via navegador/WebExtension se a consulta direta deixar de funcionar;
6. não generalizar a estratégia GO para outras UFs.

B47 só pode ser homologado após validação na ficha real do cliente.

## 5. Regra contra correção cosmética

Nenhum destes bloqueadores é resolvido por trocar rótulo/CSS isoladamente:

- Monitor precisa de uma única verdade persistida;
- Pendências precisa de escopo funcional correto;
- A4 precisa de saída física legível;
- Sintegra precisa de ação e integração funcionais, não apenas links decorativos.

## 6. Regressão integrada

No runtime final:

1. abrir Processamento na competência ativa;
2. validar Monitor técnico;
3. abrir Pendências sem informar PROC;
4. provar isolamento da competência;
5. imprimir relatório A4;
6. abrir ficha de cliente e validar Sintegra GO/Nacional;
7. indisponibilidade externa não altera cadastro;
8. consulta SEFAZ GO só aplica dados após revisão.

## 7. Estado final

- B43 — confirmado, não corrigido/homologado;
- B44 — confirmado, não corrigido/homologado;
- B46 — confirmado, não corrigido/homologado;
- B47 — regressão/implementação pendente de validação funcional;
- nenhum item recebe `CORRIGIDO_HOMOLOGADO` nesta etapa.

## 8. Próxima frente

Auditar capacidade/desempenho para carteira >600 clientes e cargas documentais de centenas de arquivos sem reintroduzir varreduras globais ou N+1.
