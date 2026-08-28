# Regressão confirmada — links rápidos Sintegra na ficha do cliente

Data: 28/08/2026
Status: **falha confirmada / correção obrigatória no pacote consolidado**

## Sintoma

Na ficha do cliente foram removidos visualmente os links de acesso rápido ao **Sintegra Nacional** e ao **Sintegra Goiás**.

Essa remoção não foi solicitada. A alteração pedida anteriormente dizia respeito ao tratamento/organização da Inscrição Estadual, e não à retirada dos atalhos externos de consulta.

## Evidência no ZIP canônico

O backend atual em `web/views/clients_views.py` continua entregando ao template:

- `sintegra_nacional = https://www.sintegra.gov.br/`
- `sintegra_go = https://appasp.sefaz.go.gov.br/Sintegra/Consulta/default.html`

Entretanto, o template atual `web/templates/clients/detail.html` não renderiza mais essas variáveis.

Backups anteriores presentes no próprio ZIP comprovam o comportamento aprovado: a seção de inscrições possuía os botões **Sintegra Nacional** e **Sintegra Goiás** diretamente no cabeçalho da área de inscrições.

## Correção aprovada

Restaurar os dois atalhos na ficha do cliente, preservando integralmente as mudanças mais recentes da área de Inscrição Estadual.

A correção não deve reverter a nova modelagem de IE, nem misturar validação matemática local com consulta externa.

Princípio:

- IE e seus estados/regras permanecem na modelagem atual;
- Sintegra Nacional e Sintegra Goiás permanecem como **atalhos rápidos de consulta assistida**;
- os links devem abrir em nova aba e continuar disponíveis na própria ficha do cliente.

## Teste de regressão

Antes da entrega final, validar que:

1. a ficha de cliente PJ exibe os dois atalhos;
2. ambos abrem em nova aba;
3. a área nova de Inscrição Estadual continua intacta;
4. nenhum link é removido em clientes sem IE cadastrada;
5. a alteração não interfere em CAEPF, CNO, CEI ou NIT/PIS.
