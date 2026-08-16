# AXT-001 — Segurança, Preservação e Rastreabilidade

Status: Aprovado e permanente  
Data: 16/08/2026

## Decisão

O Axiom Tools adota política não destrutiva por padrão.

## Regras obrigatórias

1. Arquivos originais nunca serão excluídos automaticamente.
2. Arquivos existentes não serão sobrescritos sem tratamento explícito de conflito.
3. Exclusão cadastral de cliente não implica exclusão de pasta física.
4. Inativação, baixa ou transferência de cliente não implica exclusão documental.
5. Toda rotina em lote deverá produzir resultado rastreável.
6. Operações de OCR/classificação com baixa confiança deverão ser encaminhadas para revisão.
7. Antes de uma movimentação definitiva, o sistema deverá validar origem, destino e conflito de nome.
8. Quando houver necessidade de gerar uma versão classificada/renomeada, o original deverá permanecer preservado conforme a política do projeto.
9. O sistema deverá evitar reconstruir estruturas já existentes; deve completar o que falta.
10. Conteúdo legado desconhecido deverá ser preservado.

## Cadastro x filesystem

O cadastro interno e o filesystem são camadas distintas.

O usuário poderá excluir um registro cadastral importado quando ele não fizer mais sentido para a base operacional. Essa ação, por si só, jamais autoriza o sistema a apagar a pasta ou os documentos correspondentes no servidor.

## Grafia e normalização

O dado legal/original deve ser preservado. Formatações de exibição podem normalizar apresentação, mas não podem destruir a grafia de origem.

Exceções de grafia e siglas devem ser tratáveis sem forçar caixa alta generalizada.

## Portais externos

Autenticação, CAPTCHA, certificado digital, confirmações e demais ações críticas permanecem sob controle do usuário.

O Axiom Tools pode apoiar navegação, preparação de caminhos e tratamento de arquivos após o download, mas não deve tentar contornar mecanismos de segurança.

## Consequência arquitetural

Toda implementação futura de `folders`, `ocr`, `printing` e `integrations` deverá obedecer a esta decisão. Qualquer exceção exige nova decisão formal documentada.