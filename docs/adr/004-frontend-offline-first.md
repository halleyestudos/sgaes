# ADR 004: Frontend offline-first

## Decisão

A tela de chamada usa React + Vite. Chamadas pendentes são armazenadas em IndexedDB por meio do Dexie, com uma chave lógica de turma/data/ordem. Quando a conexão volta, a fila é reenviada ao endpoint idempotente do backend.

A interface inicial reúne o fluxo do professor e o painel gestor no mesmo MVP, reduzindo o tempo de validação com usuários municipais. O servidor continua sendo a fonte da verdade; uma sincronização aceita pelo servidor remove o item local.

## Alternativas descartadas

- `localStorage`: não oferece uma fila estruturada nem boa evolução para registros maiores.
- Bloquear a chamada sem rede: inviabiliza o uso em escolas com conectividade instável.
- Conflito por mesclagem automática: a chamada inteira é enviada ao endpoint idempotente, e a última versão aceita pelo servidor prevalece.
